import requests
from bs4 import BeautifulSoup
import sqlite3

# URL principal
base_url = "https://www.geonames.org"

# Función para extraer enlaces de países
def extract_country_links():
    url = f"{base_url}/countries/"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error al acceder a la página: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', class_='restable')  # Identificar la tabla principal
    rows = table.find_all('tr')[1:]  # Ignorar la fila de encabezado

    country_links = []
    for row in rows:
        cols = row.find_all('td')
        country_name = cols[4].text.strip()
        country_link = cols[4].find('a')['href']
        country_links.append((country_name, f"{base_url}{country_link}"))

    return country_links

# Función para extraer detalles de un país
def extract_country_details(country_url):
    response = requests.get(country_url)
    if response.status_code != 200:
        print(f"Error al acceder a la página: {country_url}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    country_info = {}

    # Extraer detalles clave
    country_info['name'] = soup.find('h3').text.strip()
    details_table = soup.find('table', cellpadding='5')  # Usar atributos específicos
    if details_table:
        rows = details_table.find_all('tr')  # Todas las filas de la tabla
        for row in rows:
            cols = row.find_all('td')  # Todas las celdas de una fila
            if len(cols) == 2:  # Verificar que haya exactamente 2 columnas
                key = cols[0].text.strip().replace(":", "")  # Primera columna como clave
                value = cols[1].text.strip()  # Segunda columna como valor
                country_info[key] = value

    return country_info

# Crear base de datos y tabla
def setup_database():
    conn = sqlite3.connect('countries_details.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            population TEXT,
            area TEXT,
            capital TEXT,
            currency TEXT,
            other_details TEXT
        )
    ''')
    conn.commit()
    return conn

# Insertar datos en la base de datos
def insert_country_to_db(conn, country_data):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO countries (name, population, area, capital, currency, other_details)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        country_data.get('name'),
        country_data.get('Population'),
        country_data.get('Area'),
        country_data.get('Capital'),
        country_data.get('Currency'),
        str(country_data)  # Almacenar detalles adicionales como JSON o string
    ))
    conn.commit()

# Flujo principal
if __name__ == "__main__":
    print("Extrayendo enlaces de países...")
    country_links = extract_country_links()
    if not country_links:
        print("No se encontraron países.")
    else:
        print("Configurando la base de datos...")
        connection = setup_database()

        for name, link in country_links:
            print(f"Extrayendo detalles de {name}...")
            details = extract_country_details(link)
            if details:
                insert_country_to_db(connection, details)

        connection.close()
        print("Proceso completado. Los datos se almacenaron en 'countries_details.db'.")
