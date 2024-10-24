import streamlit as st
from docx import Document
from io import BytesIO

# Configuración de las API keys usando Secrets de Streamlit
openai_api_key = st.secrets["OPENROUTER_API_KEY"]

# Función para procesar el documento Docx mejorando la redacción y agregando divisiones
def refine_document(doc):
    refined_paragraphs = []
    for paragraph in doc.paragraphs:
        refined_text = refine_text(paragraph.text)
        refined_paragraphs.append(refined_text)
    return refined_paragraphs

# Función para mejorar la redacción utilizando la API de OpenRouter
def refine_text(text):
    if text.strip():
        response_openrouter = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai_api_key}"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": f"Please improve the following text: {text}"}]
            }
        )
        response_data = response_openrouter.json()
        refined_text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
    else:
        refined_text = text

    return refined_text

# Función para agregar divisiones en el documento
def add_divisions(doc):
    doc.add_paragraph("\n--- División del documento ---\n")

# Configuración de la aplicación Streamlit
st.title("Mejora y División de Documentos Docx")

uploaded_file = st.file_uploader("Sube un archivo Docx", type="docx")
if uploaded_file is not None:
    # Cargar el documento
    doc = Document(uploaded_file)
    refined_paragraphs = refine_document(doc)
    
    # Crear un nuevo documento refinado con divisiones
    refined_doc = Document()
    for i, refined_paragraph in enumerate(refined_paragraphs):
        refined_doc.add_paragraph(refined_paragraph)
        # Agregar divisiones entre cada párrafo
        if i < len(refined_paragraphs) - 1:
            add_divisions(refined_doc)

    # Guardar el documento en un objeto BytesIO
    refined_doc_io = BytesIO()
    refined_doc.save(refined_doc_io)
    refined_doc_io.seek(0)
    
    # Descargar el documento refinado
    st.download_button(
        label="Descargar Documento Refinado",
        data=refined_doc_io,
        file_name="documento_refinado.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
