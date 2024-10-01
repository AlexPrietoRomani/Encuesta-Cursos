import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import os

uri = "mongodb+srv://AlexPrieto:Prueba01@cluster1.3wq19np.mongodb.net/?retryWrites=true&w=majority&appName=cluster1"

# Crear un nuevo cliente y conectar al servidor
client = MongoClient(uri, server_api=ServerApi('1'))

# Seleccionar la base de datos y la colección
db = client['Clase1']
collection = db['Encuestas']

st.title("Reporte de la Encuesta")

# Obtener los datos desde MongoDB
data = list(collection.find())
if data:
    df = pd.DataFrame(data)

    # Eliminar la columna '_id' que agrega MongoDB
    if '_id' in df.columns:
        df = df.drop(columns=['_id'])

    st.subheader("Datos Recopilados")
    st.dataframe(df)

    # Gráfico de barras para cada pregunta
    preguntas = {
        'Carrera': '1. ¿De qué carrera es?',
        'Conocimiento_Estadistico': '2. ¿Tienes conocimientos en diseños estadísticos?',
        'Sector_Trabajo': '3. Sector en el que trabajas:',
        'Rango_Edad': '4. Rango de edad:',
        'Experiencia': '5. Experiencia profesional (años):'
    }

    for columna, pregunta in preguntas.items():
        st.subheader(pregunta)
        fig, ax = plt.subplots()
        sns.countplot(x=columna, data=df, ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)

    # Mapa de palabras para la pregunta de expectativas
    st.subheader("6. Mapa de palabras de las expectativas del curso")
    texto = ' '.join(df['Expectativas'].dropna().tolist())
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(texto)
    plt.figure(figsize=(15, 7.5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(plt)
else:
    st.info("Aún no hay datos disponibles.")
