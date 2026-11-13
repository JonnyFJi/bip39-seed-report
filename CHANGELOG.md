# Registro de cambios

## Unreleased

### Revisión documental local — 11 de noviembre de 2026

- Actualización de los análisis de compatibilidad y entropy para incorporar
  la preparación y comprobación de otra copia, sin reinterpretar los
  resultados históricos.
- Distinción entre el entorno original con pip 26.3 y el venv nuevo
  con pip 22.0.2.
- Separación entre inventario de runtimes, reinstalación de paquetes Python
  y recompilación Java; no se declara instalación completa desde cero.
- Conservación por separado de las baterías automáticas, los seis ensayos
  manuales originales y los tres casos manuales posteriores.
- Actualización de exclusiones locales para compilación, dependencias,
  respaldos, evidencia y auxiliares de preparación de la publicación.
- Alineación del cierre del análisis de entropy con la advertencia editorial:
  el proyecto permanece educativo y no ha sido auditado de forma independiente
  para custodia o producción. La decisión de uso corresponde al usuario.
  Los resultados y pruebas no se presentan como certificación de seguridad
  para custodiar fondos.

Estos cambios documentales y de exclusiones no modifican el núcleo
ni convierten las pruebas locales en una release o auditoría independiente.

### Inventario de runtimes y comprobación de otra copia — 10 de noviembre de 2026

Estado: ensayos locales posteriores a la integración, con el mismo núcleo
b29675e5d91f52fd6c109a777b820945c01c12ef88e6f9926f61cc6e204e20d6.
Sin atribuir commit remoto ni release.

#### Inventario posterior

- Registro separado de Python 3.10.12, OpenJDK 11.0.33, javac 11.0.33
  y Node v24.22.2, con consultas terminadas en código 0.
- Identificación de ejecutables, configuración y clase Java existente.
- Conservación de los hashes de seis fuentes y configuraciones
  respecto del manifiesto de la batería original.
- El inventario no instala runtimes ni recompila la clase existente.
- Los datos posteriores no se incorporan retrospectivamente al
  entorno.json ni al manifiesto de la batería original.

Detalle:
[Inventario de runtimes Linux](docs/RUNTIMES_ENTROPY_LINUX_2026-11-10.md).

#### Preparación de otra copia

- 64 archivos seleccionados copiados y verificados en un laboratorio
  separado del proyecto de referencia.
- Venv nuevo e instalación de dependencias desde requirements.txt,
  con pip check e importaciones principales satisfactorios.
- CPython 3.10.12; mnemonic 0.21; bip-utils 2.9.3; cryptography 44.0.3.
- pip 22.0.2 en la copia, frente a pip 26.3 en la batería original.
- Recompilación de las dos fuentes Java para el classpath de la copia,
  con código 0 y hashes de clases registrados antes de la batería.
- Reutilización de los runtimes base existentes del mismo equipo.
- Sin identidad binaria entre la clase Java histórica y la recompilada;
  no se atribuye una causa concreta ni se declara compilación reproducible.
- Las clases compiladas no forman parte del manifiesto de 49 archivos.

#### Evidencia automática

- Suite individual del ejecutor: 33 métodos satisfactorios y código 0.
- Batería proyecto/output/bateria_local_zelv2gy3:
  25 etapas, 362 métodos unittest, inventario 73/73 y código 0.
- Cero fallos, errores, omisiones, fallos esperados, éxitos inesperados
  o errores de registro; ninguna etapa incompleta.
- Conservación de los 49 nombres y hashes del manifiesto.
- Antes de los manuales: 71 archivos registrados del origen sin cambios
  y ninguna ausencia; no se declara comprobación posterior a esos manuales.
- Los conteos de 64 archivos copiados, 49 entradas protegidas y
  71 archivos del origen corresponden a conjuntos distintos.
- Los 33 métodos individuales no se suman otra vez a 362.
  La repetición de la batería no representa 724 métodos distintos.

#### Evidencia manual separada

- Redundante, 12 palabras, testnet: cuatro proveedores aceptados y utilizados;
  generación y verificador con código 0.
- Current explícito, 12 palabras, testnet: solo python_os y los otros tres
  proveedores no intentados; creación y verificación satisfactorias por
  mensajes, sin códigos separados capturados para ambas invocaciones.
- Interactivo, 24 palabras, testnet y passphrase BIP39 vacía:
  cuatro proveedores utilizados, verificación satisfactoria e inspector
  terminado con código 0.
- El mantenedor confirmó que la ventana temporal se abrió, mostró
  el reporte y se cerró al pulsar Enter.
- No se declara repetición de todos los casos del menú, timeout
  o cancelación, ni borrado seguro.
- Los tres casos nuevos no sustituyen los seis manuales anteriores
  ni reescriben manual_terminal_tests del resumen automático.

Detalle:
[Resultados de preparación de otra copia](test/RESULTADOS_COPIA_ENTROPY_2026-11-10.md).

La comprobación corresponde a otra copia en el mismo equipo, con paquetes
Python instalados de nuevo y Java recompilado sobre runtimes existentes.
No acredita instalación completa desde cero, recuperación offline de
un reporte antiguo en otro equipo ni soporte nuevo Windows/macOS.
Tampoco prueba independencia de fuentes, imprevisibilidad ni verificación
independiente de todas las derivaciones.

### Integración entropy CLI y manifiesto JavaScript — 10 de noviembre de 2026

Estado de la integración original: revisión local ensayada; sin atribuir
commit remoto ni release. Esta entrada no documenta una instalación limpia;
el inventario y la preparación posterior de otra copia se registran por separado.

#### Generación e interfaz

- Generación nueva con `--entropy-mode redundant` predeterminado, experimental.
- Proveedores: `python_os`, `java_secure_random`, `javascript_webcrypto`
  y `python_secrets`, sujetos a la política de selección.
- `--entropy-mode current` explícito conserva `os.urandom()` y no intenta
  los otros proveedores.
- `--entropy-timeout`: positivo y finito, 10 segundos por proveedor por defecto;
  no es un plazo global.
- Registro de modos, método, versiones y estados en `entropy_generation`;
  descripción en TXT y avisos dentro del reporte privado.
- La importación de material y la búsqueda de última palabra no se mezclan
  con generación nueva por estas opciones.
- Se conservan conversiones BIP39, seed, derivaciones, perfil scrypt,
  AES-GCM y publicación sin reemplazo; la integración sí modifica el núcleo
  respecto del hito histórico de noviembre 5.

SHA-256 del núcleo local ensayado:

```text
b29675e5d91f52fd6c109a777b820945c01c12ef88e6f9926f61cc6e204e20d6
```

#### Batería y corrección posterior

- Se mantienen las diez etapas anteriores y se añaden quince suites entropy.
- Validación de configuración e inventario; fuentes y archivos obligatorios
  protegidos, incluidos ejecutor, su suite y README de pruebas.
- Fuentes `.py`, `.java`, `.js`, `.cjs` y `.mjs`; exclusiones documentadas.
- Los auxiliares `node_entropy_probe.cjs` y `webcrypto_provider.cjs` pasan
  a ser obligatorios. También se descubre `test/js/test_webcrypto_provider.cjs`.
- La suite del ejecutor pasa de 20 a 31 y luego a 33 métodos.
- Batería previa `bateria_local_082q7ze7`: 25 etapas, 360 métodos, 46 archivos.
- Batería corregida `bateria_local_8jy797o3`: 25 etapas, 362 métodos,
  inventario 73/73, 49 archivos y conjunto conservados, código 0.
- Cero fallos, errores, omisiones, fallos esperados, éxitos inesperados
  o registros rechazados en la batería corregida.

#### Entorno y alcance

Linux Mint 21.3, x86_64, kernel 5.15.0-203-generic; CPython 3.10.12;
mnemonic 0.21, bip-utils 2.9.3, cryptography 44.0.3 y pip 26.3.
Datos del `entorno.json` de la batería corregida. No registra versiones
ni hashes completos de Java/Node; no se deducen del nombre de una carpeta.

Seis ensayos manuales originales comunicados y consolidados por separado;
no se reescribe `manual_terminal_tests`. La incidencia inicial TXT
correspondió al verificador auxiliar y la repetición utilizó el mismo reporte.
Estos seis ensayos no acreditan una repetición del menú GNOME.
La comprobación visual posterior de la ventana se registra en el ensayo
de otra copia; no se declara soporte nuevo Windows/macOS.

Detalle: [Resultados de integración entropy CLI](test/RESULTADOS_ENTROPY_CLI_2026-11-10.md).

El combinador sigue siendo experimental, sin auditoría independiente.
Las interfaces pueden compartir fuentes; metadatos y suites no certifican
independencia, imprevisibilidad ni todas las derivaciones. Los historiales
siguientes conservan sus identidades y conteos.

### Endurecimiento del inspector y del ejecutor — 5 de noviembre de 2026

#### Inspector

- Rechazo de claves JSON duplicadas en raíz y objetos anidados.
- Rechazo de NaN e infinitos en el contenido JSON interno.
- Tipos exactos para bits e índices, excluyendo booleanos y flotantes.
- Validación de objetos, listas, rutas y direcciones como texto no vacío.
- Conservación de extensiones legítimas del reporte.
- Ampliación de la suite de 32 a 42 métodos sin retirar los anteriores.
- Conservación del menú, timeout y política de revelación.

#### Ejecutor

- Registro del worker obligatorio, acotado y validado estrictamente.
- Correspondencia entre código registrado y código del proceso.
- Evaluación de fallos, errores y éxitos inesperados unittest.
- Detección de suites vacías, omisiones y fallos esperados.
- Distinción de etapas que no utilizan unittest.
- Normalización de códigos de salida booleanos a enteros.
- Nueva suite de 20 métodos e incorporación de la décima etapa.
- Manifiesto ampliado de 13 a 14 archivos protegidos.

#### Evidencia automática

- Dos ejecuciones individuales del inspector con 42 métodos OK.
- Dos baterías de diez etapas satisfactorias.
- Inventario del núcleo 70/70 y archivos protegidos sin cambios.
- Código final 0 en ambas baterías.
- Python 3.10.12 y pip check satisfactorio en el venv comunicado.

#### Evidencia manual separada

- Intento inicial del auxiliar con ruta inexistente: FileNotFoundError.
- Repetición sobre un export JSON testnet existente: autenticación,
  BIP39, seed y estructura satisfactorias, sin imprimir secretos.
- Código de salida de la repetición: 0.
- No se declara una repetición completa de los nueve casos del menú
  registrados el 4 de noviembre.

Detalle:
[test/RESULTADOS_ENDURECIMIENTO_2026-11-05.md](test/RESULTADOS_ENDURECIMIENTO_2026-11-05.md).

El núcleo, su checksum, generación, derivaciones, KDF, cifrado y escritura
se conservan. La documentación se actualiza sin reinterpretar los
resultados históricos.

SHA-256 del núcleo:

```text
b09fcc4f292283b8d5e6f4470dc3858a079b209b1c3ccb579be27cdec51b5174
```

No constituye una release formal ni una auditoría independiente.

### Inspector de reportes y finalización del menú — noviembre de 2026

#### Funcionalidad

- Incorporación de inspeccionar_reporte_cifrado.py como auxiliar distribuido.
- Sustitución del pie de dos comandos por un único comando de inspección.
- Comando construido con el intérprete de ejecución y las rutas resueltas
  del inspector y del reporte final, sin contraseñas en argv.
- Menú para verificar sin imprimir, revisar en ventana temporal
  o revelar en la terminal actual con confirmación.
- Validación del perfil GNOME BIP39-revision antes de abrir el visor.
- Escape de caracteres de control al presentar contenido.
- Selección temporizada de 360 segundos.
- Finalización del inspector después de completar la opción 2 o la 3.
- Retorno al menú tras revelación rechazada, errores de autenticación
  o revisión de ventana no completada, sin revelación automática alternativa.
- Conservación del contenedor versión 1, perfil scrypt, AES-256-GCM,
  generación, derivaciones y escritura.

#### Advertencias editoriales

- Revisión intencional de la advertencia general de uso del programa.
- Se conserva su carácter educativo y experimental y la ausencia
  de auditoría independiente para producción.
- La decisión de uso corresponde al usuario; no se presenta el proyecto
  como certificado para custodiar fondos.
- Se conservan las advertencias técnicas y el uso de datos ficticios
  en las pruebas.

#### Evidencia automática comunicada el 4 de noviembre de 2026

- Suite del inspector: 32 métodos satisfactorios; código 0.
- Batería local: nueve etapas OK, sin omisiones informadas.
- Inventario del núcleo: 70/70 entradas alcanzadas.
- Trece archivos protegidos sin cambios durante la batería.
- Ejecución posterior al parche: bateria_local_zikvxpur.
- Entorno automático: .venv-verificacion.

#### Evidencia manual comunicada por separado

- Nueve casos del menú satisfactorios.
- Cierre visual de la ventana con Enter confirmado por el mantenedor.
- Plazo de 360 segundos confirmado manualmente.
- Finalización directa después de las opciones 2 y 3 completadas.
- Errores y rechazos sin revelación automática.
- Q con código 0; timeout y Ctrl+C con código 1.
- Entorno manual observado: /usr/bin/python3 en Linux.

Detalle:
[test/RESULTADOS_INSPECTOR_2026-11-04.md](test/RESULTADOS_INSPECTOR_2026-11-04.md).

SHA-256 del núcleo correspondiente:

```text
b09fcc4f292283b8d5e6f4470dc3858a079b209b1c3ccb579be27cdec51b5174
```

El parche final de timeout modifica únicamente el inspector y su suite.
La actualización completa también incluye el pie del núcleo, su checksum,
la adaptación de la suite UX y la novena etapa de la batería.

No constituye una release formal ni una auditoría. Los resultados
históricos de otras versiones se conservan sin reinterpretarlos.

### UX compacta y batería Linux — ensayos del 31 de octubre y 2 de noviembre de 2026

- Vista compacta por defecto sin secretos, estadísticas extensas ni GAP limit.
- --show-all conserva la primera dirección de cada familia y revela
  los secretos de esa vista, sin convertirse en un volcado JSON completo.
- Verificación de lista embebida y efectiva conservada; solo se reducen
  mensajes de éxito. Errores y decisiones operativas permanecen visibles.
- Incorporación de report_notices al contexto privado normal, con avisos
  generales, de entrada y privacidad. Se mantiene el contenedor versión 1,
  su perfil scrypt y AES-256-GCM.
- TXT conserva su contenido anterior y añade avisos; JSON conserva campos.
- Pie posterior a la publicación con la ruta final y comandos escapados.
  No incluye contraseñas ni la passphrase BIP39 privada en argv.
- Suite UX de 18 métodos, suite complementaria de 28 y ejecutor local
  secuencial con inventario y control de hashes.
- Dos baterías Linux satisfactorias: ocho etapas, sin omisiones,
  70/70 entradas alcanzadas y 11 archivos protegidos sin cambios.
- Se conservan las 65 funciones anteriores y se añaden cuatro helpers.
  Generación, derivaciones, KDF, cifrado, descifrado y escritura se mantienen.
- Alcance activo Linux. Windows y macOS quedan diferidos, no aprobados
  para esta versión y sin bloquear el hito Linux.

SHA-256 del script ensayado:

```text
1f92a16c69c1566b9e228a9d7ca1d9cc3b066cad01ce0bc76be05b0fee88816f
```

El inventario alcanzado no equivale a todas las ramas o a una auditoría.
Los ensayos manuales y resultados históricos se conservan por separado.
La publicación en main no constituye una release formal.

### Captura de salida de la suite de regresión — 24 de octubre de 2026

- Corrección de test_05_mismatches_do_not_print_success:
  captura directamente stdout al ejecutar el runner.
- Eliminación de la llamada a execute() dentro de esa prueba,
  evitando que su captura interior deje sin contenido el buffer
  comprobado por la aserción exterior.
- Conservación de los tres subcasos de discrepancia:
  mnemonic, seed y round-trip.
- Incorporación de test_09_detects_success_printed_before_failure:
  comprueba que la prueba 05 detecta un runner ficticio que imprime
  éxito antes de lanzar AssertionError.
- La prueba de mutación recoge los tres fallos deliberados en un
  TestResult independiente, sin modificar el runner real.
- Ensayo local Linux con Python 3.10.12: sintaxis correcta y nueve
  métodos satisfactorios en 0,570 segundos, con código de salida 0.
- Vectores BIP39 distribuidos: 24 casos correctos y código de salida 0.
- Actualización de la descripción actual de la suite a nueve métodos.
- Conservación del registro histórico de ocho métodos del 23 de octubre.
- Sin cambios en bip39_seed_report.py, su checksum ni test/vectors.json.

La corrección fortalece una comprobación del test. No corresponde
a un cambio de lógica del script ni a una reducción de las expectativas
para aceptar un comportamiento incorrecto.

No se atribuye a este ensayo una nueva ejecución de las demás suites
ni una comprobación Windows.

### Runner BIP39 y recuperación: ensayo Linux — 23 de octubre de 2026

- Rechazo de suites vacías y de raíces o bloques de vectores con tipos
  incorrectos.
- Exigencia del bloque english cuando la raíz del archivo es un objeto;
  se conserva la aceptación de listas directas de vectores ingleses.
- Eliminación de la selección automática del primer bloque de idioma.
- Validación de toda la estructura antes de ejecutar las conversiones:
  vectores de tres o cuatro campos, textos no vacíos, entropy hexadecimal
  de longitud BIP39 y seed esperada de 64 bytes.
- Comparación de entropy y seed como bytes, admitiendo hexadecimal
  en mayúsculas o minúsculas.
- Manejo de errores de lectura, UTF-8 y JSON mediante errores controlados.
- Salida CLI por stderr y código 1 ante errores previstos de la suite
  o discrepancias en los resultados.
- Mensaje de éxito basado en los casos realmente completados.
- Aclaración en find_last_word(): los valores posibles del checksum
  no representan la cantidad de palabras candidatas.
- Conservación del algoritmo de búsqueda y del flujo de selección
  de candidatos.
- Incorporación de test/test_regresion_vectores_ultima_palabra.py:
  ocho métodos con subcasos y datos ficticios o públicos.
- Ensayo local Linux con Python 3.10.12: sintaxis correcta, 24 vectores
  BIP39, ocho métodos nuevos, 12 comprobaciones de cifrado, pruebas
  de entrada segura, 18 métodos del contenedor y 15 de escritura
  satisfactorios.
- Rechazo de una suite vacía desde la CLI con el mensaje previsto
  y código de salida 1.
- Sin cambios en generación, derivaciones, cifrado, contenedor o escritura.

SHA-256 del script correspondiente al ensayo:

```text
a0239df849b808f32ee097af7dc1052d3c899e1ceb8f27357b9c323795411538
```

El cuarto campo de los vectores se admite como texto no vacío, pero no
se verifica como clave extendida BIP32. Los resultados de esta versión
no se extrapolan a Windows ni a otros entornos.

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
