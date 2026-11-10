"""D-2 – Pruebas E2E de login y registro: mostrar contraseña, accesibilidad de
errores, diseño responsive y capturas de evidencia (CAPTURAS=1)."""
import os
from pathlib import Path

import pytest
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.e2e.test_acceptance import PASSWORD, SUBMIT, TIMEOUT, driver  # noqa: F401
from tests.e2e.test_interfaz_d1_e2e import TAMANOS, viewport

CAPTURAS_DIR = Path(__file__).resolve().parents[2] / "docs" / "evidencias" / "capturas" / "D-2"


@pytest.mark.parametrize("nombre,campo", [("login", "id_password"), ("register", "id_password1")])
def test_mostrar_y_ocultar_contrasena(driver, live_server, nombre, campo):
    driver.get(live_server.url + reverse(nombre))
    entrada = driver.find_element(By.ID, campo)
    boton = driver.find_element(By.CSS_SELECTOR, f'[data-password-toggle][aria-controls="{campo}"]')
    assert boton.is_displayed()  # visible solo con JavaScript activo
    entrada.send_keys("Secreta123")

    boton.click()
    assert entrada.get_attribute("type") == "text"
    assert boton.get_attribute("aria-pressed") == "true"
    assert boton.get_attribute("aria-label") == "Ocultar contraseña"

    boton.click()
    assert entrada.get_attribute("type") == "password"
    assert boton.get_attribute("aria-pressed") == "false"
    assert entrada.get_attribute("value") == "Secreta123"


def test_errores_asociados_al_campo(driver, live_server):
    driver.get(live_server.url + reverse("register"))
    driver.find_element(By.ID, "id_username").send_keys("prueba_e2e")
    driver.find_element(By.ID, "id_password1").send_keys(PASSWORD)
    driver.find_element(By.ID, "id_password2").send_keys("Distinta123!")
    driver.find_element(By.CSS_SELECTOR, SUBMIT).click()
    WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.ID, "id_password2_errores")))
    campo = driver.find_element(By.ID, "id_password2")
    assert campo.get_attribute("aria-invalid") == "true"
    assert "id_password2_errores" in campo.get_attribute("aria-describedby").split()


def test_ayuda_asociada_al_campo(driver, live_server):
    driver.get(live_server.url + reverse("register"))
    descrito = driver.find_element(By.ID, "id_username").get_attribute("aria-describedby")
    assert "id_username_ayuda" in descrito.split()


@pytest.mark.parametrize("nombre", ["login", "register"])
def test_panel_visible_solo_en_escritorio(driver, live_server, nombre):
    driver.get(live_server.url + reverse(nombre))
    viewport(driver, 1440, 900)
    assert driver.find_element(By.CSS_SELECTOR, ".auth-panel").is_displayed()
    viewport(driver, 834, 1112)
    assert not driver.find_element(By.CSS_SELECTOR, ".auth-panel").is_displayed()


@pytest.mark.parametrize("nombre", ["login", "register"])
def test_sin_desbordamiento_horizontal(driver, live_server, nombre):
    driver.get(live_server.url + reverse(nombre))
    for ancho, alto in TAMANOS.values():
        viewport(driver, ancho, alto)
        ancho_doc = driver.execute_script("return document.documentElement.scrollWidth")
        assert ancho_doc <= ancho, f"{nombre} desborda a {ancho}px ({ancho_doc}px)"


@pytest.mark.skipif(os.environ.get("CAPTURAS") != "1", reason="Solo con CAPTURAS=1")
def test_generar_capturas(driver, live_server):
    CAPTURAS_DIR.mkdir(parents=True, exist_ok=True)
    for viejo in CAPTURAS_DIR.glob("*.png"):
        viejo.unlink()

    def capturar(nombre):
        driver.execute_script("document.activeElement && document.activeElement.blur()")
        driver.save_screenshot(str(CAPTURAS_DIR / f"{nombre}.png"))

    for etiqueta, (ancho, alto) in TAMANOS.items():
        viewport(driver, ancho, alto)
        for ruta in ("login", "register"):
            driver.get(live_server.url + reverse(ruta))
            capturar(f"{ruta}_{etiqueta}")

    viewport(driver, 1440, 900)
    driver.get(live_server.url + reverse("login"))
    driver.find_element(By.ID, "id_username").send_keys("no_existe")
    driver.find_element(By.ID, "id_password").send_keys("mala")
    driver.find_element(By.CSS_SELECTOR, SUBMIT).click()
    WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.errorlist")))
    capturar("login_error_escritorio")

    driver.get(live_server.url + reverse("register"))
    driver.find_element(By.ID, "id_username").send_keys("prueba")
    driver.find_element(By.ID, "id_password1").send_keys(PASSWORD)
    driver.find_element(By.ID, "id_password2").send_keys("Distinta123!")
    driver.find_element(By.CSS_SELECTOR, SUBMIT).click()
    WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.ID, "id_password2_errores")))
    capturar("register_error_escritorio")
