# pdf_seal.py
"""
Módulo para agregar sellos visuales a documentos PDF firmados.
"""
import os
import tempfile
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor


def crear_sello_firma(fecha_firma, hash_documento, firmante="GPG Key"):
    """
    Crea un PDF temporal con el sello de firma.
    
    Args:
        fecha_firma: Fecha y hora de la firma (str)
        hash_documento: Hash SHA-256 del documento (str)
        firmante: Nombre del firmante (str)
    
    Returns:
        str: Ruta al archivo PDF temporal con el sello
    """
    # Crear archivo temporal
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_path = temp_file.name
    temp_file.close()
    
    # Crear canvas de ReportLab
    c = canvas.Canvas(temp_path, pagesize=letter)
    width, height = letter
    
    # Configuración del sello - BARRA HORIZONTAL EN LA PARTE INFERIOR
    margin = 0.2 * inch
    y = margin  # Parte inferior del documento
    
    # Colores
    border_color = HexColor('#2ecc71')  # Verde
    text_color = HexColor('#27ae60')    # Verde oscuro
    
    # Preparar texto en una sola línea
    c.setFont("Helvetica-Bold", 7)
    
    # Hash truncado a 16 caracteres
    hash_display = hash_documento[:16]
    
    # Texto completo en una línea
    texto_sello = f"✓ FIRMADO DIGITALMENTE | Fecha: {fecha_firma} | Firmante: {firmante} | Hash: {hash_display}"
    
    # Calcular el ancho del texto
    text_width = c.stringWidth(texto_sello, "Helvetica-Bold", 7)
    padding_horizontal = 20  # Padding interno (10 a cada lado)
    
    # Dimensiones del sello basadas en el texto
    seal_width = text_width + padding_horizontal
    seal_height = 0.25 * inch  # Altura de una sola línea
    
    # Asegurar que el sello no sea más ancho que la página
    max_width = width - (2 * margin)
    if seal_width > max_width:
        seal_width = max_width
    
    x = margin
    
    # Dibujar borde del sello (sin relleno para no tapar contenido)
    c.setStrokeColor(border_color)
    c.setLineWidth(1.5)
    c.roundRect(x, y, seal_width, seal_height, 3, fill=0, stroke=1)
    
    # Dibujar el texto centrado verticalmente en la barra
    c.setFillColor(text_color)
    text_y = y + (seal_height / 2) - 2  # Centrado vertical
    c.drawString(x + 10, text_y, texto_sello)
    
    # Guardar el PDF
    c.save()
    
    return temp_path


def agregar_sello_a_pdf(ruta_pdf_original, fecha_firma, hash_documento, firmante="GPG Key"):
    """
    Agrega un sello visual a la primera página de un PDF.
    
    Args:
        ruta_pdf_original: Ruta al PDF original (str)
        fecha_firma: Fecha y hora de la firma (str)
        hash_documento: Hash del documento (str)
        firmante: Nombre del firmante (str)
    
    Returns:
        bytes: Contenido del PDF con el sello agregado
    """
    # Crear el sello
    ruta_sello = crear_sello_firma(fecha_firma, hash_documento, firmante)
    
    try:
        # Leer el PDF original
        pdf_reader = PdfReader(ruta_pdf_original)
        pdf_writer = PdfWriter()
        
        # Leer el sello
        sello_reader = PdfReader(ruta_sello)
        sello_page = sello_reader.pages[0]
        
        # Procesar cada página
        for i, page in enumerate(pdf_reader.pages):
            if i == 0:  # Solo agregar sello a la primera página
                # Combinar la página original con el sello
                page.merge_page(sello_page)
            pdf_writer.add_page(page)
        
        # Escribir a un archivo temporal
        temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf_writer.write(temp_output)
        temp_output.close()
        
        # Leer el contenido del PDF resultante
        with open(temp_output.name, 'rb') as f:
            pdf_con_sello = f.read()
        
        # Limpiar archivos temporales
        os.unlink(temp_output.name)
        os.unlink(ruta_sello)
        
        return pdf_con_sello
        
    except Exception as e:
        # Limpiar en caso de error
        if os.path.exists(ruta_sello):
            os.unlink(ruta_sello)
        raise Exception(f"Error al agregar sello al PDF: {str(e)}")


if __name__ == "__main__":
    # Prueba del módulo
    print("🧪 Probando generación de sello...")
    sello = crear_sello_firma("05/12/2024 02:23:00", "abc123def456", "Test User")
    print(f"✅ Sello creado: {sello}")
    if os.path.exists(sello):
        os.unlink(sello)
        print("✅ Prueba completada")
