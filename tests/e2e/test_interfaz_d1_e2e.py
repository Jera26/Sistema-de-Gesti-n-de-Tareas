"""D-1 – Pruebas E2E de la estructura visual: menú lateral móvil, teclado,
cierre de sesión desde la barra lateral y capturas de evidencia (CAPTURAS=1)."""
import os
from pathlib import Path

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from base.models import Task
from tests.e2e.test_acceptance import PASSWORD, SUBMIT, TIMEOUT, driver  # noqa: F401

CAPTURAS_DIR = Path(__file__).resolve().parents[2] / "docs" / "evidencias" / "capturas" / "D-1"
TAMANOS = {"escritorio": (1440, 900), "tablet": (834, 1112), "movil": (390, 844)}


def viewport(driver, ancho, alto):
    """Fija el viewport exacto. Chrome no admite ventanas de menos de ~500 px,
    así que se usa la emulación de dispositivo del protocolo DevTools."""
    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
        "width": ancho, "height": alto, "deviceScaleFactor": 1, "mobile": ancho < 768})
    assert driver.execute_script("return innerWidth") == ancho


@pytest.fixture
def usuario(db):
    u = User.objects.create_user("operaria", password=PASSWORD, first_name="Laura", last_name="Vega")
    Task.objects.create(user=u, created_by=u, title="Revisar molde de inyección")
    Task.objects.create(user=u, created_by=u, title="Clasificar lote de PET", complete=True)
    return u


def _iniciar_sesion(driver, live_server, usuario):
    driver.get(live_server.url + reverse("login"))
    driver.find_element(By.ID, "id_username").send_keys(usuario.username)
    driver.find_element(By.ID, "id_password").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, SUBMIT).click()
    WebDriverWait(driver, TIMEOUT).until(EC.url_to_be(live_server.url + reverse("tasks")))


def _esperar_sidebar_quieto(driver, izquierda):
    WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script(
        "return Math.round(document.getElementById('sidebar').getBoundingClientRect().left)") == izquierda)


def test_estilos_locales_cargados(driver, live_server, usuario):
    _iniciar_sesion(driver, live_server, usuario)
    fondo = driver.execute_script("return getComputedStyle(document.body).backgroundColor")
    assert fondo == "rgb(249, 249, 255)"  # --color-fondo #f9f9ff


def test_sin_desbordamiento_horizontal(driver, live_server, usuario):
    _iniciar_sesion(driver, live_server, usuario)
    for ancho, alto in TAMANOS.values():
        viewport(driver, ancho, alto)
        for ruta in ("tasks", "task-create"):
            driver.get(live_server.url + reverse(ruta))
            ancho_doc = driver.execute_script("return document.documentElement.scrollWidth")
            assert ancho_doc <= ancho, f"{ruta} desborda a {ancho}px ({ancho_doc}px)"


def test_menu_movil_abre_y_cierra(driver, live_server, usuario):
    _iniciar_sesion(driver, live_server, usuario)
    viewport(driver, 390, 844)
    boton = driver.find_element(By.CSS_SELECTOR, "[data-sidebar-toggle]")
    sidebar = driver.find_element(By.ID, "sidebar")
    # Al reducir el viewport el menú se oculta tras su transición de 200 ms.
    WebDriverWait(driver, TIMEOUT).until(EC.invisibility_of_element(sidebar))
    assert boton.is_displayed()

    boton.click()
    WebDriverWait(driver, TIMEOUT).until(EC.visibility_of(sidebar))
    assert boton.get_attribute("aria-expanded") == "true"

    driver.switch_to.active_element.send_keys(Keys.ESCAPE)
    WebDriverWait(driver, TIMEOUT).until(EC.invisibility_of_element(sidebar))
    assert boton.get_attribute("aria-expanded") == "false"
    assert driver.switch_to.active_element == boton  # el foco vuelve al botón

    boton.click()
    WebDriverWait(driver, TIMEOUT).until(EC.visibility_of(sidebar))
    driver.execute_script("document.querySelector('[data-sidebar-backdrop]').click()")
    WebDriverWait(driver, TIMEOUT).until(EC.invisibility_of_element(sidebar))


def test_sidebar_visible_en_escritorio(driver, live_server, usuario):
    _iniciar_sesion(driver, live_server, usuario)
    viewport(driver, 1440, 900)
    assert driver.find_element(By.ID, "sidebar").is_displayed()
    assert not driver.find_element(By.CSS_SELECTOR, "[data-sidebar-toggle]").is_displayed()


def test_enlace_saltar_al_contenido_con_teclado(driver, live_server, usuario):
    _iniciar_sesion(driver, live_server, usuario)
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.TAB)
    enlace = driver.switch_to.active_element
    assert enlace.get_attribute("href").endswith("#contenido")
    # Aparece con una transición de 150 ms al recibir el foco.
    WebDriverWait(driver, TIMEOUT).until(EC.visibility_of(enlace))


def test_cerrar_sesion_desde_sidebar(driver, live_server, usuario):
    _iniciar_sesion(driver, live_server, usuario)
    viewport(driver, 1440, 900)
    driver.find_element(By.CSS_SELECTOR, "#sidebar form button[type='submit']").click()
    WebDriverWait(driver, TIMEOUT).until(EC.url_to_be(live_server.url + reverse("login")))
    driver.get(live_server.url + reverse("tasks"))
    assert reverse("login") in driver.current_url


@pytest.mark.skipif(os.environ.get("CAPTURAS") != "1", reason="Solo con CAPTURAS=1")
def test_generar_capturas(driver, live_server, usuario):
    CAPTURAS_DIR.mkdir(parents=True, exist_ok=True)
    for viejo in CAPTURAS_DIR.glob("*.png"):
        viejo.unlink()

    def capturar(nombre):
        driver.execute_script("document.activeElement && document.activeElement.blur()")
        driver.save_screenshot(str(CAPTURAS_DIR / f"{nombre}.png"))

    for etiqueta, (ancho, alto) in TAMANOS.items():
        viewport(driver, ancho, alto)
        driver.get(live_server.url + reverse("login"))
        capturar(f"login_{etiqueta}")

    _iniciar_sesion(driver, live_server, usuario)
    for etiqueta, (ancho, alto) in TAMANOS.items():
        viewport(driver, ancho, alto)
        for ruta, nombre in (("tasks", "lista"), ("task-create", "nueva_tarea")):
            driver.get(live_server.url + reverse(ruta))
            capturar(f"{nombre}_{etiqueta}")

    viewport(driver, 390, 844)
    driver.get(live_server.url + reverse("tasks"))
    driver.find_element(By.CSS_SELECTOR, "[data-sidebar-toggle]").click()
    WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_element_located((By.ID, "sidebar")))
    _esperar_sidebar_quieto(driver, 0)
    driver.save_screenshot(str(CAPTURAS_DIR / "menu_movil_abierto.png"))
