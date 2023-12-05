import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import CONSTANTES as cnst
import pandas as pd

conexion = mysql.connector.connect(
    host=cnst.HOST,
    user=cnst.USER,
    password=cnst.PASSWORD,
    database=cnst.DATABASE
)

with conexion.cursor() as cursor:
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
                insert_jugador = cnst.INSERT_JUGADOR
                valores_jugador = (nombre_texto, edad_texto, posicion_texto, nacionalidad_texto)
                cursor.execute(insert_jugador, valores_jugador)
                ###Parte uno

            if page < 8:
                next_page_button = navegador.find_element(By.XPATH, "//a[@title='A la página siguiente']")
                next_page_button.click()
                time.sleep(5)
        ##PARTE DOS
    except Exception as e:
        ##PARTE TRES

        print(f"Error: {e}")
    finally:
        ##PARTE CUATRO
        navegador.quit()

campos = cnst.CAMPOS
data = pd.DataFrame(datos)
jugadores = data.to_csv(cnst.JUGADORES)

print(f"Los datos se han guardado en {cnst.JUGADORES}")
#PARTE CINCO