import streamlit as st
import requests
from docx import Document

# Configuración de las API keys usando Secrets de Streamlit
serper_api_key = st.secrets["SERPER_API_KEY"]

# Función para procesar el documento Docx
def enrich_document(doc):
    enriched_paragraphs = []
    for paragraph in doc.paragraphs:
        enriched_text = enrich_paragraph(paragraph.text)
        enriched_paragraphs.append(enriched_text)
    return enriched_paragraphs

# Función para enriquecer un párrafo utilizando la API de Serper
def enrich_paragraph(paragraph_text):
    # Si el párrafo no está vacío, realizar una búsqueda con Serper
    if paragraph_text.strip():
        response_serper = requests.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": serper_api_key,
                "Content-Type": "application/json"
            },
            json={"q": paragraph_text}
        )
        response_data = response_serper.json()
        search_results = response_data.get("organic", [])

        # Si hay resultados, añade datos adicionales al párrafo
        if search_results:
            snippet = search_results[0].get('snippet', '')
            enriched_text = f"{paragraph_text}\n\nDatos adicionales:\n{snippet}"
        else:
            enriched_text = paragraph_text
    else:
        enriched_text = paragraph_text

    return enriched_text

# Configuración de la aplicación Streamlit
st.title("Enriquecedor de Documentos Docx")

uploaded_file = st.file_uploader("Sube un archivo Docx", type="docx")
if uploaded_file is not None:
    # Cargar el documento
    doc = Document(uploaded_file)
    enriched_paragraphs = enrich_document(doc)
    
    # Crear un nuevo documento enriquecido
    enriched_doc = Document()
    for enriched_paragraph in enriched_paragraphs:
        enriched_doc.add_paragraph(enriched_paragraph)

    # Mostrar el contenido enriquecido en la aplicación
    st.subheader("Contenido Enriquecido")
    for enriched_paragraph in enriched_paragraphs:
        st.write(enriched_paragraph)
    
    # Descargar el documento enriquecido
    enriched_doc_bytes = st.download_button(
        label="Descargar Documento Enriquecido",
        data=enriched_doc,
        file_name="documento_enriquecido.docx"
    )
