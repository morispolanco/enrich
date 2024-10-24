import streamlit as st
import openai
import requests
from docx import Document

# Configuración de las API keys usando Secrets de Streamlit
openai_api_key = st.secrets["OPENROUTER_API_KEY"]
serper_api_key = st.secrets["SERPER_API_KEY"]

# Función para procesar el documento Docx
def enrich_document(doc):
    enriched_text = ""
    for paragraph in doc.paragraphs:
        enriched_text += enrich_text(paragraph.text)
    return enriched_text

# Función para enriquecer un texto utilizando las API
def enrich_text(text):
    # Consultar OpenRouter API
    response_openrouter = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}"
        },
        json={
            "model": "openai/gpt-4o-mini",
            "messages": [{"role": "user", "content": f"Enrich this text: {text}"}]
        }
    )
    response_data = response_openrouter.json()
    enriched_text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")

    # Consultar Serper API (opcional, si quieres buscar datos adicionales en Google)
    response_serper = requests.post(
        "https://google.serper.dev/search",
        headers={
            "X-API-KEY": serper_api_key,
            "Content-Type": "application/json"
        },
        json={"q": text}
    )
    search_results = response_serper.json().get("organic", [])
    if search_results:
        enriched_text += f"\n\nDatos adicionales:\n{search_results[0].get('snippet', '')}"

    return enriched_text

# Configuración de la aplicación Streamlit
st.title("Enriquecedor de Documentos Docx")

uploaded_file = st.file_uploader("Sube un archivo Docx", type="docx")
if uploaded_file is not None:
    # Cargar el documento
    doc = Document(uploaded_file)
    enriched_content = enrich_document(doc)
    
    # Mostrar el contenido enriquecido en la aplicación
    st.subheader("Contenido Enriquecido")
    st.write(enriched_content)
    
    # Descargar el documento enriquecido
    enriched_doc = Document()
    enriched_doc.add_paragraph(enriched_content)
    enriched_doc_bytes = st.download_button(
        label="Descargar Documento Enriquecido",
        data=enriched_doc,
        file_name="documento_enriquecido.docx"
    )
