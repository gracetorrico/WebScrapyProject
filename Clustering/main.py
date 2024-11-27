import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
from sklearn.decomposition import PCA  # Asegurando uso correcto de sklearn
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Crear la conexión a la base de datos SQLite
conn = sqlite3.connect('countries.db')

# Crear la tabla si no existe
conn.execute('''
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

# Crear un DataFrame vacío para almacenar los datos
columns = ['country_name', 'iso_code', 'fips_code', 'capital', 'area_km2', 'population', 'currency', 'languages']
countries_df = pd.DataFrame(columns=columns)

for link in country_links:
    country_url = f"{base_url}{link['href']}"
    print(f"Procesando país: {link.text} - URL: {country_url}")

    country_response = requests.get(country_url)
    country_soup = BeautifulSoup(country_response.content, 'html.parser')

    # Extraer detalles del país
    country_name = link.text

    # Buscar la tabla donde están los datos del país
    data_table = country_soup.find_all('table')[1]  # La segunda tabla contiene los datos relevantes
    rows = data_table.find_all('tr') if data_table else []

    country_data = {
        'country_name': country_name,
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
                country_data['iso_code'] = value or None
            elif 'fips code' in label:
                country_data['fips_code'] = value or None
            elif 'capital' in label:
                country_data['capital'] = value or None
            elif 'area' in label:
                try:
                    country_data['area_km2'] = float(value.split()[0].replace(',', ''))
                except ValueError:
                    country_data['area_km2'] = None
            elif 'population' in label:
                try:
                    country_data['population'] = int(value.replace(',', ''))
                except ValueError:
                    country_data['population'] = None
            elif 'currency' in label:
                country_data['currency'] = value or None
            elif 'languages' in label:
                country_data['languages'] = value or None

    # Agregar los datos al DataFrame
    new_row = pd.DataFrame([country_data])
    countries_df = pd.concat([countries_df, new_row], ignore_index=True)

# Reemplazar valores vacíos por None (NULL en SQLite)
countries_df = countries_df.where(pd.notnull(countries_df), None)

# Guardar en la base de datos SQLite
for _, row in countries_df.iterrows():
    conn.execute('''
        INSERT INTO countries (country_name, iso_code, fips_code, capital, area_km2, population, currency, languages)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', tuple(row))

# Confirmar los cambios y cerrar conexión
conn.commit()
conn.close()

# Guardar los datos en un archivo CSV
countries_csv_path = "countries.csv"
countries_df.to_csv(countries_csv_path, index=False)
print(f"Datos guardados en {countries_csv_path}")

# Reducción de Dimensionalidad con PCA
print("Aplicando PCA para reducción de dimensionalidad...")
features = countries_df[['population', 'area_km2']].dropna().values  # Eliminar filas con valores nulos
pca = PCA(n_components=2)
reduced_data = pca.fit_transform(features)

# Visualización en 2D
plt.scatter(reduced_data[:, 0], reduced_data[:, 1], alpha=0.5)
plt.title('Reducción de Dimensiones con PCA')
plt.xlabel('Componente Principal 1')
plt.ylabel('Componente Principal 2')
plt.show()

# Clustering con K-means
print("Aplicando clustering con K-means...")
kmeans = KMeans(n_clusters=3, random_state=42)
clusters = kmeans.fit_predict(reduced_data)

# Visualización de los clusters
plt.scatter(reduced_data[:, 0], reduced_data[:, 1], c=clusters, cmap='viridis', alpha=0.5)
plt.title('Clustering con K-means')
plt.xlabel('Componente Principal 1')
plt.ylabel('Componente Principal 2')
plt.colorbar(label='Cluster')
plt.show()

print("Proceso finalizado.")
