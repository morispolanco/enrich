import streamlit as st
from docx import Document
from docx.shared import Pt
import io
import requests

# Configuración de la página
st.set_page_config(
    page_title="📄 Agregador de Subtítulos para Documentos DOCX",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📄 Agregador de Subtítulos para Documentos DOCX")
st.write("""
    Sube tu documento en formato DOCX, y esta aplicación agregará subtítulos al contenido utilizando la API de OpenRouter.
""")

# Subida de archivo
uploaded_file = st.file_uploader("Sube tu documento DOCX", type=["docx"])

if uploaded_file is not None:
    try:
        # Leer el documento DOCX
        doc = Document(uploaded_file)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        original_text = '\n'.join(full_text)

        st.subheader("Contenido Original del Documento")
        st.text_area("", original_text, height=300)

        # Función para generar subtítulos usando OpenRouter
        def generate_subtitles(text):
            prompt = (
                "Analiza el siguiente texto y agrega subtítulos apropiados donde sea relevante. "
                "Los subtítulos deben ser claros y resumir el contenido que sigue. "
                "Devuelve el texto modificado con los subtítulos añadidos, utilizando '## ' antes de cada subtítulo.\n\n"
                f"{text}"
            )
            api_key = st.secrets["OPENROUTER_API_KEY"]
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            data = {
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                response_json = response.json()
                if 'choices' in response_json and 'message' in response_json['choices'][0]:
                    modified_text = response_json['choices'][0]['message']['content']
                    return modified_text
                else:
                    st.error("Formato de respuesta inesperado de la API de OpenRouter.")
                    return None
            else:
                st.error(f"Error en la API de OpenRouter: {response.status_code}")
                st.error(response.text)
                return None

        with st.spinner("Agregando subtítulos al documento..."):
            subtitled_text = generate_subtitles(original_text)

        if subtitled_text:
            st.subheader("Documento con Subtítulos Agregados")
            st.text_area("", subtitled_text, height=300)

            # Crear un nuevo documento DOCX con los subtítulos
            new_doc = Document()
            for line in subtitled_text.split('\n'):
                if line.strip().startswith("## "):
                    # Subtítulos de nivel 1
                    new_doc.add_heading(line.replace("## ", "").strip(), level=1)
                else:
                    new_doc.add_paragraph(line.strip())

            # Guardar el nuevo documento en un objeto BytesIO
            byte_io = io.BytesIO()
            new_doc.save(byte_io)
            byte_io.seek(0)

            st.success("¡Documento con subtítulos creado con éxito!")
            st.download_button(
                label="📥 Descargar Documento con Subtítulos",
                data=byte_io,
                file_name="documento_con_subtitulos.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        else:
            st.warning("No se pudo generar el documento con subtítulos.")
    except Exception as e:
        st.error(f"Ocurrió un error al procesar el documento: {e}")
