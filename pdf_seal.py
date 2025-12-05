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
    
    # Configuración del sello (esquina inferior izquierda) - MÁS PEQUEÑO
    margin = 0.4 * inch
    seal_width = 2.5 * inch  # Reducido de 2.8 a 2.5
    seal_height = 0.95 * inch  # Reducido de 1.1 a 0.95
    x = margin
    y = margin
    
    # Colores
    border_color = HexColor('#2ecc71')  # Verde
    bg_color = HexColor('#f0fff4')      # Verde muy claro
    text_color = HexColor('#27ae60')    # Verde oscuro
    
    # Dibujar fondo del sello
    c.setFillColor(bg_color)
    c.setStrokeColor(border_color)
    c.setLineWidth(1.5)  # Reducido de 2 a 1.5
    c.roundRect(x, y, seal_width, seal_height, 5, fill=1, stroke=1)
    
    # Título del sello - MÁS PEQUEÑO
    c.setFillColor(text_color)
    c.setFont("Helvetica-Bold", 11)  # Reducido de 14 a 11
    c.drawString(x + 8, y + seal_height - 18, "✓ FIRMADO DIGITALMENTE")
    
    # Línea separadora
    c.setStrokeColor(border_color)
    c.setLineWidth(0.8)
    c.line(x + 8, y + seal_height - 22, x + seal_width - 8, y + seal_height - 22)
    
    # Información de la firma - LÍNEAS MÁS JUNTAS
    c.setFont("Helvetica", 7.5)  # Reducido de 9 a 7.5
    c.setFillColor(HexColor('#2c3e50'))  # Gris oscuro
    
    # Fecha
    c.drawString(x + 8, y + seal_height - 36, f"Fecha: {fecha_firma}")
    
    # Firmante - DIVIDIDO EN DOS LÍNEAS SI ES LARGO
    if len(firmante) > 35:
        # Dividir en dos líneas
        c.drawString(x + 8, y + seal_height - 48, "Firmante:")
        c.setFont("Helvetica", 7)
        c.drawString(x + 8, y + seal_height - 58, firmante[:40])
        if len(firmante) > 40:
            c.drawString(x + 8, y + seal_height - 67, firmante[40:80])
        hash_y = y + seal_height - 78
    else:
        c.drawString(x + 8, y + seal_height - 48, f"Firmante: {firmante[:35]}")
        hash_y = y + seal_height - 60
    
    # Hash (truncado para que quepa)
    hash_display = f"{hash_documento[:20]}..." if len(hash_documento) > 20 else hash_documento
    c.setFont("Helvetica", 6.5)  # Reducido de 8 a 6.5
    c.drawString(x + 8, hash_y, f"Hash: {hash_display}")
    
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
