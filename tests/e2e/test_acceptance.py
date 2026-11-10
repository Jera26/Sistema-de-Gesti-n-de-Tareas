import os

import pytest
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PASSWORD = "Pass12345!"
# Botón de envío del formulario principal (la barra lateral tiene su propio
# formulario POST de cierre de sesión). Localizador autorizado en D-1.
SUBMIT = 'main form [type="submit"]'
TIMEOUT = 10


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    # Ejecutar sin ventana: definir la variable de entorno E2E_HEADLESS=1
    if os.environ.get("E2E_HEADLESS") == "1":
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")
    d = webdriver.Chrome(options=options)
    d.implicitly_wait(5)
    yield d
    d.quit()


def test_flujo_completo_registro_y_tarea(driver, live_server):
    lista_url = live_server.url + reverse("tasks")

    # 1. Registro
    driver.get(live_server.url + reverse("register"))
    driver.find_element(By.ID, "id_username").send_keys("selenium_user")
    driver.find_element(By.ID, "id_password1").send_keys(PASSWORD)
    driver.find_element(By.ID, "id_password2").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, SUBMIT).click()

    # Tras registrarse queda en la lista de tareas (URL exacta, no un prefijo)
    WebDriverWait(driver, TIMEOUT).until(EC.url_to_be(lista_url))

    # 2. Crear tarea
    driver.get(live_server.url + reverse("task-create"))
    driver.find_element(By.ID, "id_title").send_keys("Revisar moldes")
    driver.find_element(By.ID, "id_description").send_keys("Turno de la mañana")
    driver.find_element(By.CSS_SELECTOR, SUBMIT).click()

    # 3. Verificar que aparece en la lista: esperar la redirección y el enlace de la tarea
    WebDriverWait(driver, TIMEOUT).until(EC.url_to_be(lista_url))
    WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.LINK_TEXT, "Revisar moldes"))
    )
    assert "Revisar moldes" in driver.page_source


def test_login_incorrecto_muestra_error(driver, live_server):
    driver.get(live_server.url + reverse("login"))
    driver.find_element(By.ID, "id_username").send_keys("no_existe")
    driver.find_element(By.ID, "id_password").send_keys("mala")
    driver.find_element(By.CSS_SELECTOR, SUBMIT).click()

    # Esperar a que el servidor responda con el error del formulario
    WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ul.errorlist"))
    )
    assert reverse("login") in driver.current_url
