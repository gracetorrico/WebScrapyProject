import sqlite3
import matplotlib.pyplot as plt

# Función para obtener datos desde SQLite
def fetch_data_from_db():
    conn = sqlite3.connect('countries_details.db')
    cursor = conn.cursor()

    # Consultar los 5 países con mayor población
    cursor.execute('''
        SELECT name, population FROM countries 
        ORDER BY population DESC 
        LIMIT 5
    ''')
    top_population = cursor.fetchall()

    # Consultar los 5 países con mayor área
    cursor.execute('''
        SELECT name, area FROM countries 
        ORDER BY area DESC 
        LIMIT 5
    ''')
    top_area = cursor.fetchall()

    conn.close()
    return top_population, top_area

# Función para generar gráficos
def generate_visualizations(top_population, top_area):
    # Gráfico de los 5 países con mayor población
    if top_population:
        countries_pop, populations = zip(*top_population)
        plt.figure(figsize=(10, 6))
        plt.bar(countries_pop, populations, color="skyblue")
        plt.title("Top 5 países por población")
        plt.xlabel("País")
        plt.ylabel("Población")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    # Gráfico de los 5 países con mayor área
    if top_area:
        countries_area, areas = zip(*top_area)
        plt.figure(figsize=(10, 6))
        plt.bar(countries_area, areas, color="lightgreen")
        plt.title("Top 5 países por área")
        plt.xlabel("País")
        plt.ylabel("Área (km²)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

# Flujo principal
if __name__ == "__main__":
    print("Obteniendo datos de la base de datos...")
    top_population, top_area = fetch_data_from_db()

    if top_population or top_area:
        print("Generando gráficos...")
        generate_visualizations(top_population, top_area)
    else:
        print("No se encontraron datos en la base de datos.")
