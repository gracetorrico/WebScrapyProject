import requests
from bs4 import BeautifulSoup
import sqlite3

# Crear la conexión a la base de datos SQLite
conn = sqlite3.connect('countries.db')
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS countries (
        country_name TEXT,
        iso_code TEXT,
        fips_code TEXT,
        capital TEXT,
        area_km2 REAL,
        population INTEGER,
        currency TEXT,
        languages TEXT
    )
''')

# URL principal
base_url = "https://www.geonames.org"
countries_url = f"{base_url}/countries/"

# Hacer la solicitud a la página principal
response = requests.get(countries_url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extraer los enlaces a los países
countries_table = soup.find('table', {'id': 'countries'})
country_links = countries_table.find_all('a', href=True)

for link in country_links:
    country_url = f"{base_url}{link['href']}"
    print(f"Procesando país: {link.text} - URL: {country_url}")  # Print para verificar URLs de países
    
    country_response = requests.get(country_url)
    country_soup = BeautifulSoup(country_response.content, 'html.parser')

    # Extraer detalles del país
    country_name = link.text
    
    # Buscar la tabla donde están los datos del país
    data_table = country_soup.find_all('table')[1]  # La segunda tabla contiene los datos relevantes
    rows = data_table.find_all('tr') if data_table else []

    country_data = {
        'iso_code': None,
        'fips_code': None,
        'capital': None,
        'area_km2': None,
        'population': None,
        'currency': None,
        'languages': None
    }

    # Iterar por las filas de la tabla para obtener la información
    for row in rows:
        cells = row.find_all('td')
        if len(cells) == 2:
            label = cells[0].text.strip().lower()
            value = cells[1].text.strip()

            # Asignar el valor según la etiqueta correspondiente
            if 'iso code' in label:
                country_data['iso_code'] = value
            elif 'fips code' in label:
                country_data['fips_code'] = value
            elif 'capital' in label:
                country_data['capital'] = value
            elif 'area' in label:
                try:
                    country_data['area_km2'] = float(value.split()[0].replace(',', ''))
                except ValueError:
                    pass  # Si no se puede convertir a flotante, no hacer nada
            elif 'population' in label:
                try:
                    country_data['population'] = int(value.replace(',', ''))
                except ValueError:
                    pass  # Si no se puede convertir a entero, no hacer nada
            elif 'currency' in label:
                country_data['currency'] = value
            elif 'languages' in label:
                country_data['languages'] = value

    # Verificar los datos extraídos
    print(f"Datos extraídos para {country_name}: {country_data}")

    # Guardar en la base de datos
    cursor.execute('''
        INSERT INTO countries (country_name, iso_code, fips_code, capital, area_km2, population, currency, languages)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        country_name,
        country_data['iso_code'],
        country_data['fips_code'],
        country_data['capital'],
        country_data['area_km2'],
        country_data['population'],
        country_data['currency'],
        country_data['languages']
    ))
    conn.commit()

    print(f"Datos guardados para {country_name} en la base de datos.\n")  # Print para verificar guardado

# Cerrar la conexión
conn.close()
print("Finalizado. Todos los datos han sido procesados.")
