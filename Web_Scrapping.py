from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import CONSTANTES as cnst
import pandas as pd

s = Service(ChromeDriverManager().install())
opc = Options()
opc.add_argument("--window-size=1020,1200")

navegador = webdriver.Chrome(service=s, options=opc)
navegador.get(cnst.LINK)
time.sleep(5)
datos = []

try:
    for page in range(9):
        filas = navegador.find_elements(By.XPATH, "//table[@class='items']/tbody/tr")
        for fila in filas:
            elementos = fila.find_elements(By.TAG_NAME, "td")
            nombre_texto = elementos[3].text
            posicion_texto = elementos[4].text
            edad_texto = elementos[5].text
            valor_texto = elementos[8].text
            valor_texto = valor_texto.replace(',', '')
            valor_texto = valor_texto.replace(' mill. €', '')
            img_nac = elementos[6].find_element(By.TAG_NAME, "img")
            nacionalidad_texto = img_nac.get_attribute("alt")
            img_equipo = elementos[7].find_element(By.TAG_NAME, "img")
            equipo_texto = img_equipo.get_attribute("title")
            datos.append({
                "Posicion": posicion_texto,
                "Nombre": nombre_texto,
                "Edad": edad_texto,
                "Valor de mercado": valor_texto,
                "Nacionalidad": nacionalidad_texto,
                "Equipo": equipo_texto
            })
