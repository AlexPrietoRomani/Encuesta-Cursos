import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

uri = "mongodb+srv://AlexPrieto:Prueba01@cluster1.3wq19np.mongodb.net/?retryWrites=true&w=majority&appName=cluster1"

# Create a new client and connect to the server
client = MongoClient(uri)
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Seleccionar la base de datos
db = client['Clase1']
collection = db['Encuestas']

# Ocultar el menú de Streamlit y pie de página
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("Encuesta de Curso")

# Preguntas de la encuesta
carrera = st.selectbox(
    "1. ¿De qué carrera es?",
    ["Agronomía", "Biología", "Zootecnia", "Forestales", "Industrial", "Administrativo", "Otros"]
)

conocimiento_estadistico = st.radio(
    "2. ¿Tienes conocimientos en diseños estadísticos?",
    ["Sí", "No"]
)

sector_trabajo = st.selectbox(
    "3. Sector en el que trabajas:",
    ["Agroindustria", "Investigación", "Producción", "Otros"]
)

rango_edad = st.selectbox(
    "4. Rango de edad:",
    ["De 18 a 25", "De 26 a 30", "De 31 a 35", "De 36 a 40", "De 41 a 45", "De 45 a más"]
)

experiencia = st.selectbox(
    "5. Experiencia profesional (años):",
    ["0", "1-3", "4-7", "8 a más"]
)

expectativas = st.text_area(
    "6. ¿Qué esperas del curso? (Máximo 30 caracteres):",
    max_chars=30
)

# Botón para enviar respuestas
if st.button("Enviar"):
    data = {
        'Carrera': carrera,
        'Conocimiento_Estadistico': conocimiento_estadistico,
        'Sector_Trabajo': sector_trabajo,
        'Rango_Edad': rango_edad,
        'Experiencia': experiencia,
        'Expectativas': expectativas
    }
    # Insertar los datos en la colección de MongoDB
    collection.insert_one(data)
    st.success("¡Gracias por participar en la encuesta!")