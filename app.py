import streamlit as st
from docx import Document
from io import BytesIO

# Función para dividir el documento en secciones y poner títulos
def divide_document(doc):
    section_counter = 1
    divided_sections = []
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():  # Solo procesar párrafos que no estén vacíos
            section_title = f"Sección {section_counter}"
            divided_sections.append((section_title, paragraph.text))
            section_counter += 1
    return divided_sections

# Función para agregar las secciones con títulos al documento
def add_sections_to_document(sections, doc):
    for section_title, section_content in sections:
        doc.add_heading(section_title, level=2)
        doc.add_paragraph(section_content)

# Configuración de la aplicación Streamlit
st.title("Divisor de Documentos Docx en Secciones")

uploaded_file = st.file_uploader("Sube un archivo Docx", type="docx")
if uploaded_file is not None:
    # Cargar el documento
    doc = Document(uploaded_file)
    divided_sections = divide_document(doc)
    
    # Crear un nuevo documento con las secciones divididas
    divided_doc = Document()
    add_sections_to_document(divided_sections, divided_doc)

    # Guardar el documento en un objeto BytesIO
    divided_doc_io = BytesIO()
    divided_doc.save(divided_doc_io)
    divided_doc_io.seek(0)
    
    # Descargar el documento dividido
    st.download_button(
        label="Descargar Documento Dividido",
        data=divided_doc_io,
        file_name="documento_dividido.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
