import streamlit as st
import requests
from docx import Document
from io import BytesIO

# Configuración de las API keys usando Secrets de Streamlit
serper_api_key = st.secrets["SERPER_API_KEY"]

# Función para procesar y ampliar el documento completo
def enrich_document(doc):
    full_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    enriched_text = expand_text(full_text)
    return enriched_text

# Función para ampliar el texto completo del documento utilizando la API de Serper
def expand_text(text):
    # Si el texto no está vacío, realizar una búsqueda con Serper
    if text.strip():
        response_serper = requests.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": serper_api_key,
                "Content-Type": "application/json"
            },
            json={"q": text}
        )
        response_data = response_serper.json()
        search_results = response_data.get("organic", [])

        # Si hay resultados, ampliar el texto con información adicional
        if search_results:
            snippet = search_results[0].get('snippet', '')
            enriched_text = f"{text}\n\nInformación adicional:\n{snippet}\n"
        else:
            enriched_text = text + "\n\n(No se encontraron datos adicionales para este documento)\n"
    else:
        enriched_text = text

    return enriched_text

# Configuración de la aplicación Streamlit
st.title("Ampliador de Documentos Docx")

uploaded_file = st.file_uploader("Sube un archivo Docx", type="docx")
if uploaded_file is not None:
    # Cargar el documento
    doc = Document(uploaded_file)
    enriched_content = enrich_document(doc)
    
    # Crear un nuevo documento enriquecido
    enriched_doc = Document()
    enriched_doc.add_paragraph(enriched_content)

    # Guardar el documento en un objeto BytesIO
    enriched_doc_io = BytesIO()
    enriched_doc.save(enriched_doc_io)
    enriched_doc_io.seek(0)
    
    # Descargar el documento enriquecido
    st.download_button(
        label="Descargar Documento Ampliado",
        data=enriched_doc_io,
        file_name="documento_ampliado.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
