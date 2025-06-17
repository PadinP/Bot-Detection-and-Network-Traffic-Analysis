import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
import json
import os

def create_json_file_if_not_exists(filename='products.json'):
    if not os.path.exists(filename):
        with open(filename, 'w') as json_file:
            json.dump({"clothes": [], "accesories": [], "art": []}, json_file, indent=4)

def safe_json_load(filename='products.json'):
    """Carga el JSON de forma segura. Si falla, devuelve una estructura válida."""
    if not os.path.exists(filename):
        return {"clothes": [], "accesories": [], "art": []}
    with open(filename, 'r') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            print("Error al cargar JSON, restaurando estructura vacía.")
            return {"clothes": [], "accesories": [], "art": []}

def update_json_category(category, data, filename='products.json'):
    """Actualiza la categoría especificada en el archivo JSON de forma segura."""
    json_data = safe_json_load(filename)
    json_data[category] = data
    with open(filename, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

def get_clothes():
    browser.find_element(By.ID, 'category-3').click()
    clothes = browser.find_elements(By.CLASS_NAME, 'product-description')
    clothes_data = []
    for element in clothes:
        # Se separa el texto por salto de línea
        parts = element.text.split('\n')
        # Se verifica que se hayan obtenido al menos dos partes (nombre y precio)
        if len(parts) >= 2:
            clothes_data.append({
                'name': parts[0],
                'price': parts[1]
            })
    update_json_category('clothes', clothes_data)
    time.sleep(random.randint(5, 10))

def get_accessories():
    browser.find_element(By.ID, 'category-6').click()
    accs = browser.find_elements(By.CLASS_NAME, 'product-description')
    accs_data = []
    for element in accs:
        parts = element.text.split('\n')
        if len(parts) >= 2:
            accs_data.append({
                'name': parts[0],
                'price': parts[1]
            })
    update_json_category('accesories', accs_data)
    time.sleep(random.randint(7, 12))

def get_art():
    browser.find_element(By.ID, 'category-9').click()
    arts = browser.find_elements(By.CLASS_NAME, 'product-description')
    art_data = []
    for element in arts:
        parts = element.text.split('\n')
        if len(parts) >= 2:
            art_data.append({
                'name': parts[0],
                'price': parts[1]
            })
    update_json_category('art', art_data)
    time.sleep(random.randint(7, 11))

def get_discount():
    browser.find_element(By.CLASS_NAME, 'logo').click()
    browser.find_element(By.CLASS_NAME, 'all-product-link').click()
    time.sleep(random.randint(6, 13))

def login():
    browser.find_element(By.CLASS_NAME, 'user-info').click()
    browser.find_element(By.NAME, 'email').send_keys('alexpp2809@gmail.com')
    browser.find_element(By.NAME, 'password').send_keys('Qwe1234567@rs*')
    browser.find_element(By.ID, 'submit-login').click()
    time.sleep(10)

if __name__ == '__main__':
    # Configuración del servicio y opciones para Firefox
    service = FirefoxService(executable_path='/usr/local/bin/geckodriver')
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.headless = True
    browser = webdriver.Firefox(options=firefox_options, service=service)
    
    browser.get('http://172.18.0.3')
    print('Current page: %s' % browser.current_url)
    
    login()
    
    create_json_file_if_not_exists()  # Se asegura de crear el archivo si no existe
    browser.implicitly_wait(10)
    
    while True:
        get_clothes()
        get_accessories()
        get_art()
        get_discount()
        time.sleep(random.randint(10, 30))
