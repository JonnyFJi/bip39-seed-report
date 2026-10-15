# Registro de cambios

## Unreleased

### Endurecimiento del contenedor cifrado — octubre de 2026

- Rechazo de claves JSON duplicadas, incluidas claves anidadas,
  y de constantes NaN e infinitos.
- Validación de las claves exactas del contenedor versión 1 y de sus
  objetos cipher y kdf.
- Comprobaciones de tipos, algoritmos y perfil scrypt admitido.
- Límites de tamaño para el contenedor, plaintext y datos base64.
- Validación de longitudes de salt, nonce y ciphertext antes de
  ejecutar la KDF.
- Límites equivalentes para la lectura del formato histórico,
  conservando su derivación de contraseña y su alias de compatibilidad.
- Conservación de la versión 1 del formato, el perfil scrypt,
  AES-256-GCM y la construcción de AAD existentes.

### Pruebas del contenedor — 15 de octubre de 2026

- Incorporación de test/test_contenedor_report.py con 18 métodos
  de prueba y múltiples subcasos.
- Comprobaciones de rechazo antes de llamar a la KDF y control positivo
  que confirma su acceso cuando la estructura es admisible.
- Pruebas de fronteras con límites temporales y mocks.
- Round-trip con scrypt real y Unicode.
- Pruebas de compatibilidad histórica y del alias de descifrado.
- Dos ejecuciones satisfactorias comunicadas por el mantenedor en
  Linux con Python 3.10.12; ambas finalizaron con código de salida 0.
- Actualización de test/README.md con ejecución, alcance y limitaciones.

La escritura sin sobrescritura concurrente, los permisos efectivos,
la durabilidad del directorio y la lectura limitada desde disco
permanecen pendientes.

### Organización aplicada en la rama principal

- Movimiento de la suite a test/vectors.json.
- Ruta predeterminada relativa a la ubicación del script.
- Documentación de seguridad y mantenimiento.
- Registro de versiones directas del entorno utilizado para las pruebas.
- Instalación y suites verificadas en el entorno virtual Linux comunicado
  por el mantenedor el 12 de octubre de 2026.
- Plantillas de issues y pull requests.
- Licencia MIT para el código original del proyecto.
- Advertencias y procedimiento de contribuciones en README.
- SECURITY.md y exclusiones locales mediante .gitignore.
- Configuración descriptiva mínima en pyproject.toml.
- Versiones directas declaradas en requirements.txt.
- Inventario inicial y avisos de terceros en THIRD_PARTY_NOTICES.md.

Esta sección no representa una release formal.

## Base de desarrollo revisada — octubre de 2026

- Identidad de aplicación bip39-seed-report.
- Eliminación del filtro de palabras repetidas.
- Sustitución del score por indicadores descriptivos.
- Exportación nueva con scrypt y AES-256-GCM.
- Compatibilidad de descifrado histórico.
- Comprobación de wordlist embebida y efectiva.
- Entrada oculta centralizada, TTY y rechazo de GetPassWarning.
- Confirmación de passphrase NFKD y cancelación inicial.
- Permiso explícito para secretos por CLI.
- Pruebas BIP39, cifrado y entrada segura.
- Documentación de límites y trabajo pendiente.

No constituye una auditoría independiente para producción.
