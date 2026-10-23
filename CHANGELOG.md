# Registro de cambios

## Unreleased

### Resultados Windows — comunicados el 22 de octubre de 2026

- Ensayo en Windows 10 Home x64, versión 10.0.19045, con Python 3.10.11.
- Instalación satisfactoria de las dependencias directas fijadas y
  pip check sin requisitos rotos.
- Vectores BIP39, cifrado, entrada segura y contenedor satisfactorios.
- Suite de escritura: 10 métodos aprobados y 5 omitidos.
- Omisiones: dos métodos POSIX, dos de enlaces simbólicos no disponibles
  y uno multiproceso específico de Linux.
- Batería manual: 17 exportaciones y 14 verificaciones posteriores
  satisfactorias; tres exports adicionales sin verificación visible.
- Preservación del primer export comprobada mediante hash en una
  ejecución sucesiva con nombre repetido.
- Los dos errores de consulta de versiones mediante Python -c se
  atribuyen al comando auxiliar de PowerShell, no al script.
- Evidencia y límites registrados en ANALISIS_COMPATIBILIDAD_SO.md.

### Escritura sin reemplazo — octubre de 2026

- Sustitución de la publicación mediante os.replace() por os.link()
  sobre un temporal completo, sincronizado y situado junto al destino.
- Reintentos secuenciales ante colisiones sin repetir el cifrado.
- Ausencia de alternativa con reemplazo si fallan los enlaces duros.
- write_secure_file() falla si su destino exacto ya existe.
- generate_sequential_path() se conserva como propuesta de nombre,
  no como reserva exclusiva.
- Resolución del padre sin seguir el enlace del nombre final.
- Aplicación de 0o600 mediante fchmod antes de publicar en POSIX,
  propagando sus errores.
- Incorporación de test/test_escritura_report.py con 15 métodos.
- Ensayo Linux comunicado: 15 métodos correctos, sin omisiones,
  con Python 3.10.12.
- Dos exports reales sucesivos autenticados y verificados.

### Auxiliar manual de laboratorio

- Incorporación de test/verificar_export_laboratorio.py.
- Lectura exterior limitada y contraseña de exportación sin eco.
- Comprobaciones JSON de BIP39, seed y estructura de derivaciones.
- Comprobaciones de autenticación, cabecera y red para texto.
- No imprime plaintext ni constituye verificación independiente
  de todas las direcciones.

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

Tras estos cambios permanecen pendientes la durabilidad del directorio,
la lectura limitada desde disco para todos los consumidores, las ACL
de Windows y la cobertura de los casos omitidos en esa plataforma.

La publicación sin reemplazo requiere enlaces duros y una carpeta
de confianza; no protege frente a modificaciones hostiles del padre.

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
