# 📊 Aplicación de Encuesta y Dashboard de Análisis de Cursos

Este repositorio contiene el código fuente de una aplicación web interactiva desarrollada con Streamlit y conectada a una base de datos MongoDB. La aplicación tiene dos componentes principales:

1.  **Una encuesta dinámica** para recopilar información y expectativas de los alumnos de un curso.
2.  **Un dashboard de reportería interactivo** para visualizar y analizar los datos recopilados en tiempo real.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://TU-LINK-DE-STREAMLIT-AQUI.streamlit.app/)
*(Reemplaza el link de arriba con el enlace de tu aplicación una vez desplegada)*

---

## 🚀 Características Principales

### Encuesta
- **Formulario Inteligente:** Preguntas condicionales que se adaptan a las respuestas del usuario.
- **Entrada de Datos Rica:** Uso de sliders para calificaciones, selectores múltiples y áreas de texto.
- **Captura de Metadatos:** Registro automático de fecha y hora de envío con manejo de zonas horarias.
- **Conexión Segura a Base de Datos:** Los datos se almacenan directamente en una colección de MongoDB.

### Dashboard de Análisis
- **Visualización Interactiva:** Gráficos dinámicos creados con Plotly que permiten explorar los datos.
- **Filtros Avanzados:** Filtra los resultados por rango de fechas y perfil del encuestado (ej. carrera).
- **Métricas Clave (KPIs):** Resumen rápido del número de respuestas, promedios y otros indicadores.
- **Análisis de Datos Complejos:** Procesamiento y visualización de respuestas de selección múltiple y datos de calificación.
- **Análisis de Sentimiento:** Cálculo y visualización de la polaridad promedio de las expectativas de los alumnos.
- **Exportación de Datos:** Permite descargar los datos filtrados en formato CSV para un análisis más profundo.

---

## 🛠️ Tecnologías Utilizadas

- **Frontend y Backend:** [Streamlit](https://streamlit.io/)
- **Base de Datos:** [MongoDB Atlas](https://www.mongodb.com/atlas)
- **Análisis y Manipulación de Datos:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Visualización de Datos:** [Plotly](https://plotly.com/), [Matplotlib](https://matplotlib.org/), [WordCloud](https://github.com/amueller/word_cloud/)
- **Procesamiento de Lenguaje Natural (NLP):** [TextBlob](https://textblob.readthedocs.io/)
- **Manejo de Fechas y Zonas Horarias:** [Pytz](https://pypi.org/project/pytz/)

---

## ⚙️ Configuración y Puesta en Marcha Local

Para ejecutar esta aplicación en tu máquina local, sigue estos pasos:

### 1. Prerrequisitos
- Python 3.9+
- Una cuenta de MongoDB Atlas y una cadena de conexión (URI).

### 2. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/Encuesta-Cursos.git
cd Encuesta-Cursos
```

### 3. Crear y Activar un Ambiente Virtual (Recomendado)
```bash
# Crear el ambiente
python -m venv venv

# Activar en Windows
.\venv\Scripts\activate

# Activar en macOS/Linux
source venv/bin/activate
```

### 4. Instalar Dependencias
El archivo `requirements.txt` contiene todas las librerías necesarias.
```bash
pip install -r requirements.txt
```

### 5. Configurar los Secretos
La aplicación utiliza el gestor de secretos de Streamlit para manejar las credenciales de la base de datos de forma segura.

- Crea una carpeta `.streamlit` en la raíz del proyecto.
- Dentro de esa carpeta, crea un archivo llamado `secrets.toml`.
- Añade el siguiente contenido, reemplazando con tu URI de conexión de MongoDB:
  ```toml
  # .streamlit/secrets.toml
  [mongo]
  uri = "mongodb+srv://tu_usuario:tu_contraseña@tu_cluster.mongodb.net/?retryWrites=true&w=majority"
  ```
**Importante:** El archivo `secrets.toml` está incluido en el `.gitignore` y no debe ser subido al repositorio.

### 6. Ejecutar la Aplicación
```bash
streamlit run encuesta_app.py.py
```
La aplicación se abrirá automáticamente en tu navegador web.

---

## ☁️ Despliegue

Esta aplicación está diseñada para ser desplegada en [Streamlit Community Cloud](https://share.streamlit.io/). El proceso es el siguiente:

1.  Asegúrate de que tu repositorio en GitHub tenga el archivo `requirements.txt`.
2.  Inicia sesión en Streamlit Community Cloud y crea una "New App", conectándola a este repositorio.
3.  En la configuración avanzada (`Advanced settings...`), copia y pega el contenido de tu archivo local `secrets.toml` en la sección de "Secrets".
4.  ¡Despliega!