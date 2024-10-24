import streamlit as st
import requests
from docx import Document
from io import BytesIO

# Configuración de las API keys usando Secrets de Streamlit
openai_api_key = st.secrets["OPENROUTER_API_KEY"]

# Función para dividir el documento en secciones lógicas y generar títulos para cada sección
def divide_and_title_document(doc):
    sections = []
    current_section = []
    
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():  # Solo considerar párrafos que no estén vacíos
            current_section.append(paragraph.text)
        else:
            if current_section:
                # Unir los párrafos de la sección actual en un solo texto
                section_text = "\n".join(current_section)
                section_title = generate_section_title(section_text)
                sections.append((section_title, section_text))
                current_section = []
    
    # Añadir la última sección si existe
    if current_section:
        section_text = "\n".join(current_section)
        section_title = generate_section_title(section_text)
        sections.append((section_title, section_text))
    
    return sections

# Función para generar un título para cada sección utilizando la API de OpenRouter
def generate_section_title(text):
    try:
        response_openrouter = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai_api_key}"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": f"Generate a concise and appropriate title for the following text: {text}"}]
            }
        )
        # Verificar si la respuesta es exitosa
        if response_openrouter.status_code == 200:
            response_data = response_openrouter.json()
            title = response_data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return title if title else "Sección sin título"
        else:
            st.error("Error con la API de OpenRouter: " + response_openrouter.text)
            return "Sección sin título"
    except Exception as e:
        st.error(f"Error al conectar con la API de OpenRouter: {e}")
        return "Sección sin título"

# Función para agregar las secciones con títulos al documento
def add_sections_to_document(sections, doc):
    for section_title, section_content in sections:
        doc.add_heading(section_title, level=2)
        doc.add_paragraph(section_content)

# Configuración de la aplicación Streamlit
st.title("Divisor Lógico de Documentos Docx en Secciones")

uploaded_file = st.file_uploader("Sube un archivo Docx", type="docx")
if uploaded_file is not None:
    # Cargar el documento
    doc = Document(uploaded_file)
    logical_sections = divide_and_title_document(doc)
    
    # Crear un nuevo documento con las secciones divididas y tituladas
    divided_doc = Document()
    add_sections_to_document(logical_sections, divided_doc)

    # Guardar el documento en un objeto BytesIO
    divided_doc_io = BytesIO()
    divided_doc.save(divided_doc_io)
    divided_doc_io.seek(0)
    
    # Descargar el documento dividido y titulado
    st.download_button(
        label="Descargar Documento Dividido",
        data=divided_doc_io,
        file_name="documento_dividido.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
