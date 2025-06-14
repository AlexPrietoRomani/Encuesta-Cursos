import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import pytz

# --- CONFIGURACIÓN DE LA PÁGINA ---
# Es buena práctica configurar la página al inicio del script.
st.set_page_config(page_title="Encuesta del Curso", layout="centered")

# --- ESTILOS PERSONALIZADOS ---
# Ocultar elementos de la UI de Streamlit para un look más limpio y enfocado.
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- CONEXIÓN A LA BASE DE DATOS ---
# Usamos un bloque try-except para manejar errores de conexión de forma elegante.
# st.secrets es la forma segura y recomendada por Streamlit para manejar credenciales.
try:
    uri = st.secrets["mongo"]["uri"]
    client = MongoClient(uri, server_api=ServerApi('1'))
    client.admin.command('ping') # Confirma que la conexión es exitosa.
except Exception as e:
    st.error(f"No se pudo conectar a la base de datos. Error: {e}", icon="🚨")
    st.stop() # Detiene la ejecución del script si no hay conexión a la DB.

# Seleccionar la base de datos y la colección.
# Nota: Es convención usar nombres en plural para las colecciones (ej. 'encuestas').
db = client['Encuestas']
collection = db['encuesta']

# --- CUERPO DE LA ENCUESTA ---

st.title("📊 Encuesta de Mejora del Curso")
st.markdown("¡Tu opinión es muy valiosa! Por favor, ayúdanos a mejorar completando esta breve encuesta.")

# st.form es esencial para agrupar inputs. Evita que la app se recargue con cada cambio
# y envía todos los datos juntos con un solo botón.
with st.form("survey_form"):
    
    st.subheader("Información General")
    carrera = st.selectbox(
        "1. ¿A qué carrera o área perteneces?",
        ("Agronomía", "Biología", "Zootecnia", "Forestales", "Ingeniería Industrial", "Administración", "Otro")
    )
    rango_edad = st.select_slider(
        "2. ¿Cuál es tu rango de edad?",
        options=["18-25", "26-30", "31-35", "36-40", "41-45", "46 a más"]
    )
    experiencia = st.selectbox(
        "3. ¿Cuántos años de experiencia profesional tienes?",
        ("0 (Estudiante)", "1-3", "4-7", "8-12", "13 a más")
    )
    sector_trabajo = st.selectbox(
        "4. ¿En qué sector trabajas principalmente?",
        ("Agroindustria", "Investigación Académica", "Producción / Campo", "Consultoría", "Gobierno", "Otro")
    )

    st.subheader("Conocimientos y Expectativas")
    conocimiento_estadistico = st.radio(
        "5. ¿Tienes conocimientos previos en diseños estadísticos experimentales?",
        ("Sí, sólidos", "Sí, básicos", "No, ninguno"),
        horizontal=True,
        help="Esto nos ayuda a nivelar el contenido del curso."
    )

    # --- LÓGICA CONDICIONAL ---
    # La encuesta se adapta al usuario. Si no tiene conocimientos, no le preguntamos por software.
    # Esto mejora la experiencia de usuario y la calidad de los datos.
    if conocimiento_estadistico != "No, ninguno":
        software_conocido = st.multiselect(
            "6. ¿Qué software estadístico o de programación has utilizado?",
            ["R", "Python (Pandas, Scipy)", "SPSS", "Minitab", "SAS", "Statistica", "Excel (avanzado)", "Otro"]
        )
    else:
        # Guardamos una lista vacía para mantener una estructura de datos consistente en MongoDB.
        software_conocido = []

    # --- CALIFICACIÓN DE INTERÉS (DATO CUANTITATIVO) ---
    # Usar sliders nos da un dato mucho más rico que una simple selección.
    # Ahora podemos saber QUÉ TANTO interés hay en cada tema.
    st.subheader("7. Califica tu interés en los siguientes temas (1=Poco, 5=Mucho)")
    temas_interes = {} # Usamos un diccionario para guardar el par tema-calificación.
    temas_a_calificar = [
        "Diseño de Experimentos Agricolas",
        "Aprendizaje de software estadístico R",
        "Analisis estadístico de datos experimentales",
        "Diseños estadisticos de Experimentos Agrícolas",
        "Estadistica Descriptiva y Visualización de Datos"
    ]
    for tema in temas_a_calificar:
        temas_interes[tema] = st.slider(f"**{tema}**", 1, 5, 3) # El valor por defecto es 3.

    expectativas = st.text_area(
        "8. En una frase, ¿qué es lo más importante que esperas aprender o lograr con este curso?",
        max_chars=200,
        placeholder="Ej: Aplicar diseños factoriales en mis experimentos de campo."
    )
    
    # El botón de envío debe estar DENTRO del st.form.
    submitted = st.form_submit_button("✅ Enviar mis respuestas")

    if submitted:
        # --- PROCESAMIENTO POST-ENVÍO ---
        # Usamos pytz para asegurar que la fecha tenga una zona horaria asignada (timezone-aware).
        # Esto es crucial para la robustez del manejo de fechas.
        peru_tz = pytz.timezone("America/Lima")
        fecha_envio = datetime.now(peru_tz)

        # Creamos el documento que se insertará en MongoDB.
        data = {
            'carrera': carrera,
            'rango_edad': rango_edad,
            'experiencia': experiencia,
            'sector_trabajo': sector_trabajo,
            'conocimiento_estadistico': conocimiento_estadistico,
            'software_conocido': software_conocido,
            'temas_interes': temas_interes, # Guardamos el diccionario completo.
            'expectativas': expectativas,
            'fecha_envio': fecha_envio
        }

        # Insertamos el documento en la colección.
        collection.insert_one(data)
        st.success("¡Muchas gracias por tu tiempo! Tus respuestas han sido enviadas correctamente.")
        st.balloons() # Una pequeña recompensa visual para el usuario.