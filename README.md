# 🔐 Firmador y Verificador de PDF con GPG

Sistema web para firmar digitalmente documentos PDF usando GPG (GNU Privacy Guard) y verificar su integridad.

## 🚀 Características

- ✍️ **Firma digital de PDFs**: Firma documentos con tu clave GPG privada
- 🔍 **Verificación de integridad**: Comprueba si un PDF ha sido modificado después de firmarlo
- 📊 **Información detallada**: Muestra fecha de firma, tamaño, hash SHA-256 del documento
- 🔒 **Firmas destacadas**: Genera archivos `.asc` separados para las firmas
- 💾 **Descarga automática**: Descarga el PDF firmado automáticamente
- 🧹 **Interfaz limpia**: Diseño Bootstrap responsive y moderno

## 📋 Requisitos previos

- Python 3.8+
- GPG instalado en el sistema
- Una clave GPG configurada

### Instalar GPG

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get install gnupg
```

**macOS:**
```bash
brew install gnupg
```

**Verificar instalación:**
```bash
gpg --version
```

## 🔧 Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/tu-usuario/pdf-gpg-signer.git
cd pdf-gpg-signer
```

2. **Crear entorno virtual (recomendado):**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno:**
```bash
cp .env.example .env
nano .env  # Editar y agregar tu contraseña GPG
```

Contenido del `.env`:
```env
GPG_PASSPHRASE=tu_contraseña_gpg_aqui
```

5. **Verificar tu clave GPG:**
```bash
gpg --list-secret-keys
```

Si no tienes una clave, créala:
```bash
gpg --full-generate-key
```

## ▶️ Uso

1. **Iniciar el servidor:**
```bash
python app.py
```

2. **Acceder a la aplicación:**
```
http://localhost:5000
```

3. **Firmar un documento:**
   - Selecciona un PDF en la sección "Firmar Documento PDF"
   - Haz clic en "Firmar PDF"
   - El documento se descargará automáticamente como `documento_firmado.pdf`
   - Se guardará la firma en `firmas/[hash].asc`

4. **Verificar un documento:**
   - Sube el PDF firmado en la sección "Verificar Integridad"
   - El sistema mostrará si el documento es auténtico o ha sido alterado

## 📁 Estructura del proyecto

```
pdf-gpg-signer/
├── app.py                      # Aplicación Flask principal
├── requirements.txt            # Dependencias Python
├── .env                        # Variables de entorno (no en Git)
├── .gitignore                 # Archivos ignorados por Git
├── README.md                  # Este archivo
├── templates/
│   └── index.html             # Interfaz web
├── static/
│   └── style.css              # Estilos personalizados
├── documentos_firmados/       # PDFs firmados (no en Git)
├── firmas/                    # Firmas .asc (no en Git)
└── signatures/                # Firmas adicionales (no en Git)
```

## 🔐 Seguridad

- **No subas tu archivo `.env` a GitHub** (ya está en `.gitignore`)
- Las contraseñas se cargan desde variables de entorno
- Los documentos firmados se almacenan localmente
- El hash SHA-256 garantiza la integridad del documento

## 🛠️ Tecnologías utilizadas

- **Backend**: Flask (Python)
- **Criptografía**: GPG (python-gnupg)
- **Frontend**: Bootstrap 5
- **Hash**: SHA-256

## 📝 Cómo funciona

1. **Firma**: 
   - Se calcula el hash SHA-256 del contenido del PDF
   - GPG firma el documento con la clave privada
   - Se genera un archivo `.asc` con la firma destacada
   - El hash se usa como nombre único para la firma

2. **Verificación**:
   - Se calcula el hash del PDF subido
   - Se busca la firma correspondiente
   - GPG verifica si la firma coincide con el contenido
   - Si el contenido cambió, el hash será diferente y la verificación fallará

## 👨‍💻 Autor

**Jenrry Soto Dextre**
- Web: [https://dextre.xyz](https://dextre.xyz)

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 🐛 Problemas conocidos

- Requiere GPG instalado en el sistema
- La contraseña debe configurarse antes de usar

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Si tienes problemas o preguntas, abre un issue en GitHub.
