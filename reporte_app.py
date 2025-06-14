import streamlit as st
import pandas as pd
import numpy as np
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.express as px
from collections import Counter
from textblob import TextBlob
import pytz

# --- CONFIGURACIÓN DE LA PÁGINA Y CONEXIÓN A DB ---
st.set_page_config(page_title="Reporte de Encuesta", layout="wide")

st.title("📈 Reporte Interactivo de la Encuesta del Curso")
st.markdown("Análisis de las respuestas recopiladas para la mejora continua.")

# --- CONEXIÓN A LA BASE DE DATOS ---
try:
    uri = st.secrets["mongo"]["uri"]
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client['Encuestas']
    collection = db['encuesta']
except Exception as e:
    st.error(f"No se pudo conectar a la base de datos. Error: {e}", icon="🚨")
    st.stop()

# --- DEFINICIÓN DE FUNCIONES ---
# Es buena práctica definir todas las funciones al principio del script.

@st.cache_data(ttl=600) # Cachear los datos por 10 minutos para no sobrecargar la DB.
def load_data():
    """
    Carga los datos desde MongoDB, los convierte a un DataFrame de Pandas
    y estandariza la columna de fecha a UTC.
    Esta función está optimizada para ser llamada una sola vez gracias al caché.
    """
    data = list(collection.find())
    if not data:
        return pd.DataFrame() # Devuelve un DataFrame vacío si no hay datos.
    
    df = pd.DataFrame(data)
    
    if '_id' in df.columns:
        df = df.drop(columns=['_id'])

    # Proceso de fechas robusto:
    # 1. Asegurarse de que la columna existe.
    # 2. Convertir a datetime.
    # 3. Localizar a UTC, que es como MongoDB guarda las fechas internamente.
    # La conversión a la zona horaria de visualización se hará FUERA de esta función.
    if 'fecha_envio' in df.columns:
        df['fecha_envio'] = pd.to_datetime(df['fecha_envio']).dt.tz_localize('UTC')
    
    return df

def analizar_sentimiento(texto):
    """Analiza el sentimiento de un texto y devuelve su polaridad (-1 a 1)."""
    if isinstance(texto, str):
        return TextBlob(texto).sentiment.polarity
    return 0 # Devuelve 0 si el texto no es válido (ej. NaN).

@st.cache_data
def convertir_df_a_csv(df_a_convertir):
    """Convierte un DataFrame a CSV para su descarga."""
    return df_a_convertir.to_csv(index=False).encode('utf-8')

# --- CARGA INICIAL DE DATOS ---
df_completo = load_data()

# Si no hay datos, mostrar un mensaje amigable y detener.
if df_completo.empty:
    st.info("Aún no hay datos disponibles en la encuesta para generar el reporte.")
    st.stop()

# --- BARRA LATERAL CON FILTROS Y OPCIONES ---
st.sidebar.header("Opciones de Visualización")
display_tz_str = st.sidebar.selectbox(
    'Ver fechas en la zona horaria:',
    options=['America/Lima', 'Europe/Madrid', 'America/New_York', 'UTC'],
    index=0
)
display_tz = pytz.timezone(display_tz_str)

st.sidebar.header("Filtros del Reporte")

# --- CONVERSIÓN DE ZONA HORARIA (SE HACE AQUÍ) ---
# Convertimos la fecha a la zona horaria seleccionada DESPUÉS de cargar los datos.
# Esto asegura que el reporte se actualice cuando el usuario cambie la opción.
df_completo['fecha_envio_display'] = df_completo['fecha_envio'].dt.tz_convert(display_tz)

# Filtro de rango de fechas (usa la fecha convertida para el selector)
min_date = df_completo['fecha_envio_display'].min().date()
max_date = df_completo['fecha_envio_display'].max().date()

start_date = st.sidebar.date_input('Fecha de inicio', min_value=min_date, value=min_date)
end_date = st.sidebar.date_input('Fecha de fin', max_value=max_date, value=max_date)

if start_date > end_date:
    st.sidebar.error("Error: La fecha de inicio no puede ser posterior a la fecha de fin.")
    st.stop()

# Filtro por Carrera
carreras_unicas = ["Todos"] + df_completo['carrera'].unique().tolist()
carrera_filtro = st.sidebar.selectbox("Filtrar por Carrera", carreras_unicas)

# --- APLICACIÓN DE FILTROS ---
# Creamos el DataFrame 'df' que será el que usaremos para todas las visualizaciones.
# Es más limpio y eficiente aplicar todos los filtros de una vez.

# 1. Filtro de fecha (convertimos las fechas del input a datetime conscientes de la zona horaria)
start_datetime = pd.to_datetime(start_date).tz_localize(display_tz)
end_datetime = pd.to_datetime(end_date).tz_localize(display_tz) + pd.Timedelta(days=1)
df = df_completo[(df_completo['fecha_envio_display'] >= start_datetime) & (df_completo['fecha_envio_display'] < end_datetime)]

# 2. Filtro de carrera
if carrera_filtro != "Todos":
    df = df[df['carrera'] == carrera_filtro]

# Si el DataFrame filtrado está vacío, detener.
if df.empty:
    st.warning("No hay datos que coincidan con los filtros seleccionados.")
    st.stop()

# --- PROCESAMIENTO ADICIONAL SOBRE DATOS FILTRADOS ---
df['sentimiento_expectativa'] = df['expectativas'].apply(analizar_sentimiento)

# --- DASHBOARD PRINCIPAL ---
st.subheader("Métricas Clave")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Respuestas (General)", len(df_completo))
col2.metric("Respuestas Filtradas", len(df))

# Cálculo robusto del promedio de experiencia
exp_map = {"0 (Estudiante)": 0, "1-3": 2, "4-7": 5.5, "8-12": 10, "13 a más": 15}
avg_exp = df['experiencia'].map(exp_map).mean()
col3.metric("Promedio Años de Experiencia", f"{avg_exp:.1f} años" if not np.isnan(avg_exp) else "N/A")
col4.metric("Sentimiento Promedio", f"{df['sentimiento_expectativa'].mean():.2f}" if not df['sentimiento_expectativa'].empty else "N/A")


# Visualizaciones en pestañas
tab1, tab2, tab3 = st.tabs(["Perfil del Alumno", "Conocimientos y Expectativas", "Datos Crudos"])

with tab1:
    st.header("Perfil del Alumno")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribución por Carrera")
        fig = px.pie(df, names='carrera', hole=.3, title='Proporción de Carreras')
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Distribución por Sector de Trabajo")
        fig = px.bar(df['sector_trabajo'].value_counts(),
                     title='Cantidad de Alumnos por Sector',
                     text_auto=True)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Conocimientos y Expectativas del Curso")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Conocimiento Previo en Diseños Experimentales")
        fig = px.pie(df, names='conocimiento_estadistico', title='Nivel de Conocimiento Previo', hole=.3)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Software Estadístico Utilizado")
        lista_software = [item for sublist in df['software_conocido'] for item in sublist]
        if lista_software:
            software_counts = Counter(lista_software)
            df_software = pd.DataFrame(software_counts.items(), columns=['Software', 'Cantidad']).sort_values('Cantidad', ascending=False)
            fig_software = px.bar(df_software, x='Software', y='Cantidad', title='Popularidad de Software', text='Cantidad')
            st.plotly_chart(fig_software, use_container_width=True)
        else:
            st.info("No hay datos de software para el filtro seleccionado.")

    with col2:
        st.subheader("Temas de Mayor Interés (Calificación Promedio)")
        # --- LÓGICA CORREGIDA PARA ANALIZAR CALIFICACIONES ---
        # Extraemos los diccionarios, nos aseguramos de que no estén vacíos
        temas_data = df['temas_interes'].dropna().tolist()
        if temas_data:
            df_temas = pd.DataFrame.from_records(temas_data)
            df_temas_mean = df_temas.mean().sort_values(ascending=True).reset_index()
            df_temas_mean.columns = ['Tema', 'Calificación Promedio']
            
            fig_temas = px.bar(df_temas_mean, 
                               y='Tema', 
                               x='Calificación Promedio', 
                               title='Temas Más Solicitados (Calificación Promedio)', 
                               text=df_temas_mean['Calificación Promedio'].apply(lambda x: f'{x:.2f}'), 
                               orientation='h')
            fig_temas.update_layout(xaxis_title="Calificación Promedio (1 a 5)")
            st.plotly_chart(fig_temas, use_container_width=True)
        else:
            st.info("No hay datos de temas de interés para el filtro seleccionado.")

    st.subheader("Nube de Palabras sobre Expectativas")
    texto = ' '.join(df['expectativas'].dropna().tolist())
    if texto:
        wordcloud = WordCloud(width=800, height=400, background_color='white', collocations=False).generate(texto)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    else:
        st.info("No hay texto de expectativas para mostrar.")

with tab3:
    st.header("Explorador de Datos Crudos")
    st.markdown("Aquí puedes ver y descargar los datos según los filtros aplicados.")
    
    st.dataframe(df) # Mostramos el dataframe filtrado
    
    csv = convertir_df_a_csv(df)
    st.download_button(
        label="📥 Descargar datos filtrados como CSV",
        data=csv,
        file_name='reporte_filtrado.csv',
        mime='text/csv',
    )