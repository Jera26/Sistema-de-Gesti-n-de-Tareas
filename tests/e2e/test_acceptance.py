import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PASSWORD = "Pass12345!"
SUBMIT = "input[type='submit'], button[type='submit']"


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless=new")   # descomenta para correr sin ventana
    options.add_argument("--window-size=1280,900")
    d = webdriver.Chrome(options=options)
    d.implicitly_wait(5)
    yield d
    d.quit()


def test_flujo_completo_registro_y_tarea(driver, live_server):
    # 1. Registro
    driver.get(live_server.url + reverse("register"))
    driver.find_element(By.ID, "id_username").send_keys("selenium_user")
    driver.find_element(By.ID, "id_password1").send_keys(PASSWORD)
    driver.find_element(By.ID, "id_password2").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, SUBMIT).click()
    WebDriverWait(driver, 5).until(EC.url_contains(reverse("tasks")))

    # 2. Crear tarea
    driver.get(live_server.url + reverse("task-create"))
    driver.find_element(By.ID, "id_title").send_keys("Revisar moldes")
    driver.find_element(By.ID, "id_description").send_keys("Turno de la mañana")
    driver.find_element(By.CSS_SELECTOR, SUBMIT).click()

    # 3. Verificar que aparece en la lista
    WebDriverWait(driver, 5).until(EC.url_contains(reverse("tasks")))
    assert "Revisar moldes" in driver.page_source


def test_login_incorrecto_muestra_error(driver, live_server):
    driver.get(live_server.url + reverse("login"))
    driver.find_element(By.ID, "id_username").send_keys("no_existe")
    driver.find_element(By.ID, "id_password").send_keys("mala")
    driver.find_element(By.CSS_SELECTOR, SUBMIT).click()
    assert reverse("login") in driver.current_url


