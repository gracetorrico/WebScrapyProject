import requests
from bs4 import BeautifulSoup
import sqlite3

# URL de la página
url = "https://www.scrapethissite.com/pages/simple/"

# Función para extraer datos de países
def extract_country_data():
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error al acceder a la página: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    countries = soup.find_all('div', class_='country')  # Cambiar según la estructura HTML
    country_data = []

    for country in countries:
        name = country.find('h3', class_='country-name').text.strip()
        capital = country.find('span', class_='country-capital').text.strip()
        population = int(country.find('span', class_='country-population').text.strip().replace(',', ''))
        area = float(country.find('span', class_='country-area').text.strip().replace(',', ''))
        
        country_data.append((name, capital, population, area))
    
    return country_data

# Crear base de datos y tabla
def setup_database():
    conn = sqlite3.connect('countries.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            capital TEXT NOT NULL,
            population INTEGER NOT NULL,
            area REAL NOT NULL
        )
    ''')
    conn.commit()
    return conn

# Insertar datos en la base de datos
def insert_data_to_db(conn, data):
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT INTO countries (name, capital, population, area)
        VALUES (?, ?, ?, ?)
    ''', data)
    conn.commit()

# Flujo principal
if __name__ == "__main__":
    # Extraer datos
    print("Extrayendo datos de la página...")
    countries = extract_country_data()
    if not countries:
        print("No se encontraron datos.")
    else:
        # Configurar la base de datos
        print("Configurando la base de datos...")
        connection = setup_database()
        
        # Insertar datos
        print("Insertando datos en la base de datos...")
        insert_data_to_db(connection, countries)
        
        # Cerrar la conexión
        connection.close()
        print("Proceso completado. Los datos se almacenaron en 'countries.db'.")
