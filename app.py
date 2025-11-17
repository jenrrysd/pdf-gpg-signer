# app.py
import os
import hashlib
import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, send_file, session
import gnupg
import tempfile
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)
app.secret_key = 'clave_secreta_pdf'
app.config['SESSION_TYPE'] = 'filesystem'

# 📁 Carpetas
CARPETA_DOCUMENTOS_FIRMADOS = os.path.join(os.getcwd(), 'documentos_firmados')
CARPETA_FIRMAS = os.path.join(os.getcwd(), 'firmas')

os.makedirs(CARPETA_DOCUMENTOS_FIRMADOS, exist_ok=True)
os.makedirs(CARPETA_FIRMAS, exist_ok=True)

# 🔐 GPG
gpg = gnupg.GPG(gnupghome=os.path.expanduser("~/.gnupg"))

# 🔑 Contraseña GPG (cámbiala por tu contraseña real)
# IMPORTANTE: En producción, usa variables de entorno
GPG_PASSPHRASE = os.getenv('GPG_PASSPHRASE', '')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sign', methods=['POST'])
def firmar_pdf():
    if 'file' not in request.files:
        flash('❌ No se seleccionó ningún archivo.', 'error')
        return redirect(url_for('index'))

    archivo_subido = request.files['file']
    nombre_original = archivo_subido.filename

    if not nombre_original or not nombre_original.lower().endswith('.pdf'):
        flash('❌ Solo se permiten archivos PDF.', 'error')
        return redirect(url_for('index'))

    try:
        # 📥 1. Guardar en temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            archivo_subido.save(tmp.name)
            ruta_temporal = tmp.name

        # 🔍 2. Leer contenido y calcular hash
        with open(ruta_temporal, 'rb') as f:
            contenido_pdf = f.read()
        hash_contenido = hashlib.sha256(contenido_pdf).hexdigest()[:16]

        # 📁 3. Rutas definitivas
        ruta_pdf_guardado = os.path.join(
            CARPETA_DOCUMENTOS_FIRMADOS, nombre_original)
        ruta_firma = os.path.join(CARPETA_FIRMAS, f"{hash_contenido}.asc")

        # ✅ 4. Guardar PDF original (sin cambios)
        with open(ruta_pdf_guardado, 'wb') as f:
            f.write(contenido_pdf)

        # ✍️ 5. Firmar desde el temporal
        with open(ruta_temporal, 'rb') as f:
            resultado = gpg.sign_file(
                f, detach=True, binary=False, output=ruta_firma, passphrase=GPG_PASSPHRASE)

        if resultado.status != 'signature created':
            # Rollback
            os.unlink(ruta_pdf_guardado)
            raise Exception(f"Firma fallida: {resultado.stderr}")

        # 🕒 6. Fecha de firma
        fecha_firma = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # 🧹 Borrar solo el temporal (el guardado se mantiene)
        os.unlink(ruta_temporal)

        # 📊 Información del documento
        tamanio_kb = len(contenido_pdf) / 1024

        # Guardar nombre del archivo para descarga
        nombre_base, ext = os.path.splitext(nombre_original)
        nombre_descarga = f"{nombre_base}_firmado{ext}"
        session['archivo_firmado'] = nombre_original
        session['nombre_descarga'] = nombre_descarga

        return render_template(
            'index.html',
            signed=True,
            fecha_firma=fecha_firma,
            nombre_documento=nombre_original,
            tamanio_documento=f"{tamanio_kb:.2f} KB",
            hash_documento=hash_contenido,
            trigger_download=True
        )

    except Exception as error:
        # 🧹 Limpieza
        try:
            if 'ruta_temporal' in locals() and os.path.exists(ruta_temporal):
                os.unlink(ruta_temporal)
            if 'ruta_pdf_guardado' in locals() and os.path.exists(ruta_pdf_guardado):
                os.unlink(ruta_pdf_guardado)
        except:
            pass
        flash(f'❌ Error: {str(error)}', 'error')
        return redirect(url_for('index'))


@app.route('/download')
def descargar_firmado():
    if 'archivo_firmado' not in session:
        flash('❌ No hay archivo para descargar.', 'error')
        return redirect(url_for('index'))

    archivo = session.get('archivo_firmado')
    nombre_descarga = session.get('nombre_descarga', archivo)
    ruta_archivo = os.path.join(CARPETA_DOCUMENTOS_FIRMADOS, archivo)

    if not os.path.exists(ruta_archivo):
        flash('❌ Archivo no encontrado.', 'error')
        return redirect(url_for('index'))

    # Limpiar sesión
    session.pop('archivo_firmado', None)
    session.pop('nombre_descarga', None)

    return send_file(
        ruta_archivo,
        as_attachment=True,
        download_name=nombre_descarga,
        mimetype='application/pdf'
    )


@app.route('/verify', methods=['POST'])
def verificar_pdf():
    if 'file' not in request.files:
        flash('❌ No se seleccionó ningún archivo.', 'error')
        return redirect(url_for('index'))

    archivo_subido = request.files['file']
    nombre = archivo_subido.filename

    if not nombre or not nombre.lower().endswith('.pdf'):
        flash('❌ Solo PDFs.', 'error')
        return redirect(url_for('index'))

    ruta_temporal = None
    try:
        # 📥 Guardar temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            archivo_subido.save(tmp.name)
            ruta_temporal = tmp.name

        # 🔍 Hash del PDF subido
        with open(ruta_temporal, 'rb') as f:
            contenido = f.read()
        hash_subido = hashlib.sha256(contenido).hexdigest()[:16]
        tamanio_kb = len(contenido) / 1024

        # 📁 Buscar firma
        ruta_firma = os.path.join(CARPETA_FIRMAS, f"{hash_subido}.asc")

        if not os.path.exists(ruta_firma):
            # Buscar por contenido
            for sig in os.listdir(CARPETA_FIRMAS):
                if sig.endswith('.asc'):
                    candidata = os.path.join(CARPETA_FIRMAS, sig)
                    with open(candidata, 'rb') as sig_f:
                        verif = gpg.verify_file(sig_f, ruta_temporal)
                    if verif and verif.valid:
                        ruta_firma = candidata
                        break
            else:
                os.unlink(ruta_temporal)
                return render_template(
                    'index.html',
                    verified=True,
                    status='incorrect',
                    nombre_documento=nombre,
                    tamanio_documento=f"{tamanio_kb:.2f} KB",
                    hash_documento=hash_subido
                )

        # ✅ Verificar (usando rutas → igual que terminal)
        with open(ruta_firma, 'rb') as sig_f:
            verificacion = gpg.verify_file(sig_f, ruta_temporal)

        os.unlink(ruta_temporal)

        if verificacion and verificacion.valid:
            fecha = datetime.datetime.fromtimestamp(
                int(verificacion.sig_timestamp))
            return render_template(
                'index.html',
                verified=True,
                status='ok',
                fecha_firma=fecha.strftime("%d/%m/%Y %H:%M:%S"),
                nombre_documento=nombre,
                tamanio_documento=f"{tamanio_kb:.2f} KB",
                hash_documento=hash_subido,
                firmante=verificacion.username if hasattr(
                    verificacion, 'username') else 'GPG Key'
            )
        else:
            fecha_ref = "desconocida"
            try:
                mtime = os.path.getmtime(ruta_firma)
                fecha_ref = datetime.datetime.fromtimestamp(
                    mtime).strftime("%d/%m/%Y %H:%M:%S")
            except:
                pass
            return render_template(
                'index.html',
                verified=True,
                status='altered',
                fecha_firma=fecha_ref,
                nombre_documento=nombre,
                tamanio_documento=f"{tamanio_kb:.2f} KB",
                hash_documento=hash_subido
            )

    except Exception as e:
        if ruta_temporal and os.path.exists(ruta_temporal):
            os.unlink(ruta_temporal)
        flash(f'❌ Error: {str(e)}', 'error')
        return redirect(url_for('index'))


if __name__ == '__main__':
    print("✅ Iniciando servidor...")
    print(f"📁 Carpeta de PDFs firmados: {CARPETA_DOCUMENTOS_FIRMADOS}")
    print(f"🔐 Carpeta de firmas: {CARPETA_FIRMAS}")
    app.run(debug=True, host='0.0.0.0', port=4040)
