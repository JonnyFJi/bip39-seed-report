# Compatibilidad esperada y comprobaciones por entorno

## Referencia del análisis

- Creación del documento: 10 de agosto de 2026.
- Actualización documental: 22 de octubre de 2026.
- Archivo analizado: bip39_seed_report.py.
- Repositorio: JonnyFJi/bip39-seed-report.
- Commit de referencia:
  `bbcff63daf5ca10b5a0f94218a660fc007e93b72`.
- SHA-256 del script de referencia:
  `365fafdfa71f9c0a91c088c4428335a5b96fbbce99434bff112d7152736bf55e`.

El hash identifica el script analizado, no este documento.
No certifica procedencia ni seguridad del entorno.

### Actualización posterior de referencia

Este análisis conserva como base la versión y el hash indicados arriba.

El commit 103c19637ed5b8c50c3117bf937a9c5332196059 incorpora posteriormente
el endurecimiento del contenedor cifrado y su suite de regresión.

La versión del parche de contenedor incorporada en ese commit tiene SHA-256:

7e108699d9625054fbe2ba3750afa2b932f4b1903bda058a278c255bb23fc21a

Los pendientes históricos deben interpretarse respecto de la base
analizada. El estado actual del contenedor y sus pruebas se documenta
en CHANGELOG.md y test/README.md.

### Versión del ensayo Windows y escritura sin sobrescritura

Los resultados Windows comunicados el 22 de octubre de 2026 corresponden
al script con el parche de escritura mediante enlaces duros. Su SHA-256,
comprobado en Windows y contrastado con el archivo .sha256, es:

```text
df80621c8a2f2adef15c370783319c88ba4593f31ed92c03c08a0d5248cc9d3f
```

La publicación de esa versión fue identificada en la revisión anterior
en el commit `5df71bc4573d9fbbc57f2c7be466409a30fb67eb`.
El registro Windows identifica los bytes mediante el hash anterior;
no registra directamente su HEAD Git.

Se conserva el hash `7e108699...` del ensayo anterior del contenedor y
la base histórica `365fafdf...`. No representan discrepancias: identifican
revisiones distintas. Este documento no modifica ni el script ni sus hashes.

## Objetivo y alcance

Documentar las condiciones necesarias para instalar, probar y ejecutar
el programa, separando compatibilidad esperada de resultados realmente
observados.

Este análisis no certifica todas las versiones de Python, sistemas
operativos, arquitecturas, terminales o dependencias.

## Resumen

El proyecto está pensado para ejecutarse en distintos sistemas, pero el
soporte debe comprobarse para una combinación concreta de sistema,
arquitectura, Python, dependencias y terminal.

Existen ensayos comunicados en Linux y en Windows 10 Home x64. El ensayo
Windows tiene resultados satisfactorios para las suites y flujos descritos,
con cinco métodos de escritura omitidos y tres exports adicionales sin
verificación posterior visible. No constituye soporte universal de Windows,
macOS, BSD ni de todas las distribuciones Linux.

Pasar los vectores BIP39 no prueba por sí solo la entrada de terminal,
el cifrado, los permisos ni la escritura de archivos.

---

## Componentes que condicionan la compatibilidad

| Componente | Uso en el proyecto | Qué debe verificarse |
|---|---|---|
| Python | Intérprete, biblioteca estándar, terminal y archivos | Versión concreta y ejecución de todos los flujos |
| mnemonic | Wordlist y conversiones BIP39 | Versión instalada, lista efectiva y vectores |
| bip-utils | Seed y derivaciones | Versión instalada y resultados de referencia |
| cryptography | AES-256-GCM | Importación y ensayos de cifrado/autenticación |
| hashlib.scrypt | KDF del export | Disponibilidad y ejecución del perfil configurado |
| Terminal | Lectura oculta y decisiones | TTY, ausencia de eco, cancelación y timeout |
| Sistema de archivos | Temporales, publicación sin reemplazo y permisos | Enlaces duros, colisiones y comportamiento en el destino real |

`requirements.txt` fija las tres dependencias directas del entorno
de referencia.

Todavía no existe un bloqueo completo de dependencias transitivas
ni una instalación con verificación de hashes.

El 12 de octubre de 2026, el mantenedor comunicó una instalación
satisfactoria en .venv-verificacion y resultados correctos de pip check,
compilación, 24 vectores BIP39, 12 comprobaciones de cifrado y las
pruebas de GetPassWarning y normalización Unicode.

La evidencia corresponde a ese entorno Linux. No establece soporte
universal ni una instalación reproducible con hashes.

---

## Matriz de resultados registrados

| Entorno | Python y dependencias | Evidencia | Estado |
|---|---|---|---|
| Entorno local Linux inicial | Registro completo pendiente | Ensayos anteriores comunicados, incluidos flujos manuales | Limitado a esos ensayos |
| Entorno virtual Linux .venv-verificacion | mnemonic 0.21; bip-utils 2.9.3; cryptography 44.0.3. Python exacto, distribución y arquitectura pendientes de registrar | Instalación, pip check, compilación, 24 vectores BIP39, 12 comprobaciones de cifrado y pruebas de entrada segura | Satisfactorio para las comprobaciones comunicadas |
| Windows 10 Home x64, 10.0.19045, compilación registrada 19045 | Python 3.10.11; mnemonic 0.21; bip-utils 2.9.3; cryptography 44.0.3; pip 23.0.1 | Vectores BIP39, cifrado, entrada segura, contenedor, escritura y verificación manual de exports | Satisfactorio para los casos ejecutados; escritura: 10 aprobados y 5 omitidos; ver detalle Windows |
| macOS | Sin combinación registrada | Sin ejecución comunicada | Compatibilidad por comprobar |
| BSD u otros | Sin combinación registrada | Sin ejecución comunicada | No establecido |

### Actualización del ensayo del contenedor — 15 de octubre de 2026

Para el ensayo del contenedor se registró Python 3.10.12 y el SHA-256
indicado en la sección «Actualización posterior de referencia».
La suite test/test_contenedor_report.py terminó con 18 métodos correctos
y código de salida 0 en las dos ejecuciones comunicadas.

Este resultado corresponde al ensayo del 15 de octubre de 2026.
No atribuye retrospectivamente esa versión de Python a los ensayos
anteriores registrados en la matriz.

La distribución y arquitectura exactas de ese ensayo siguen pendientes
de registrar.

La fila Linux no representa todas las distribuciones ni todas las
arquitecturas. Deben añadirse distribución, versión, arquitectura,
Python y versiones de paquetes antes de usarla como matriz reproducible.

Los tests con mocks comprueban la política programada de rechazo y
normalización; no recrean todos los comportamientos de una terminal real.

---

## Resultados Windows 10 Home x64

### Fuente, entorno e identidad

- Fecha de comunicación y revisión de la evidencia: 22 de octubre de 2026.
- Fuente: archivo `resultado-pruebas.txt` proporcionado por el mantenedor.
- Sistema: Microsoft Windows 10 Home, versión 10.0.19045.
- Compilación registrada: 19045; revisión acumulativa UBR no registrada.
- Arquitectura del sistema: x64 (64 bits).
- Intérprete: Python 3.10.11, entorno local `.venv-verificacion`.
- Terminal: Windows PowerShell; número exacto de versión no registrado.
- pip observado en el registro: 23.0.1.
- Dependencias directas: mnemonic 0.21, bip-utils 2.9.3 y cryptography 44.0.3.
- SHA-256 del script: `df80621c8a2f2adef15c370783319c88ba4593f31ed92c03c08a0d5248cc9d3f`.
- Sistema de archivos del volumen de salida: pendiente de registrar;
  una ruta C: no prueba por sí sola que sea NTFS.

El entorno se preparó para un laboratorio Windows en VM, según el contexto
comunicado. El log no certifica por sí solo la versión del hipervisor,
la arquitectura efectiva del intérprete ni todos los recursos de la VM.
La fecha de revisión no debe presentarse como fecha exacta de ejecución
de cada comando: el log no proporciona marcas temporales completas.

### Instalación y preparación

La instalación de requirements.txt terminó correctamente y `pip check`
mostró `No broken requirements found.`. La sintaxis del script y de los
archivos compilados se comprobó sin errores en las invocaciones py_compile.

Las dependencias transitivas observadas fueron:

```text
cbor2==5.9.0
cffi==2.1.1
coincurve==21.0.0
crcmod==1.7
ecdsa==0.19.2
ed25519-blake2b==1.4.1
py-sr25519-bindings==0.2.4
pycparser==3.11
pycryptodome==3.24.1
pynacl==1.6.2
six==1.17.0
```

Es un registro del entorno observado, no un lockfile ni un inventario
exhaustivo de componentes nativos. ed25519-blake2b y crcmod se instalaron
mediante setup.py install con avisos de obsolescencia y resultado done.
El log no permite determinar qué herramientas de compilación estaban
instaladas previamente. No se debe afirmar que cualquier instalación
limpia de Windows carecerá de requisitos adicionales.

### Suites automáticas

| Comprobación | Resultado observado |
|---|---|
| Ayuda CLI | Mostrada correctamente |
| Vectores con ruta predeterminada | 24 casos correctos |
| Vectores con --vectors-file | 24 casos correctos |
| Cifrado | 12 comprobaciones correctas |
| Entrada segura | GetPassWarning y normalización Unicode correctos |
| Contenedor | 18 métodos correctos; sin omisiones mostradas |
| Escritura | 15 métodos contabilizados: 10 aprobados y 5 omitidos; código 0 |

Las dos ejecuciones de vectores ejercitan la misma suite mediante rutas
resueltas de forma distinta; no representan 48 vectores independientes.

Métodos de escritura omitidos:

| Método | Motivo registrado |
|---|---|
| test_07_mode_0600 | Permisos POSIX |
| test_08_permission_failure_does_not_publish | fchmod POSIX |
| test_09_existing_symlink_not_followed | Creación de symlink no disponible |
| test_10_broken_symlink_occupied | Creación de symlink no disponible |
| test_12_process_exports_unique | Ensayo Linux con fork |

No hay fallos mostrados en esa suite. Las omisiones no son aprobaciones:
no demuestran ACL de Windows, comportamiento de enlaces simbólicos ni
concurrencia entre procesos Windows. Sí pasó la prueba concurrente con
hilos, junto con preservación de archivos, colisión forzada, límites de
intentos, fallos simulados y publicación de un temporal completo.

### Ejecución y verificación manual

Se observaron 17 exportaciones completadas y 14 verificaciones posteriores
satisfactorias. Se comprobaron los archivos de los siguientes casos:

- Generación de 12, 15, 18, 21 y 24 palabras.
- Importación de entropy hexadecimal y binaria.
- Mnemonic completa y mnemonic incompleta de 11 palabras.
- Generación interactiva con passphrase y auditoría descriptiva.
- Mainnet y testnet.
- Contenido interno JSON y texto.
- Dos exports sucesivos al mismo destino solicitado.

El caso repetido produjo repetido.json y repetido_001.json. Los hashes
antes y después del primero coincidieron y ambos exports se autenticaron
y verificaron con el auxiliar manual.

No hay verificación posterior visible de words21_001.json,
interactivo_001.json ni show_all.json. Su exportación sí consta.
El segundo interactivo mostró 24 palabras y passphrase presente.
--show-all ejercitó la revelación solicitada, no una prueba independiente
de su archivo cifrado. No dar estos tres archivos por autenticados
mediante el auxiliar sin evidencia adicional.

En JSON, el auxiliar verifica autenticación, BIP39, seed y estructura de
familias, cantidades, índices y rutas; no calcula independientemente la
validez criptográfica de cada dirección. En texto verifica autenticación,
cabecera y red, con alcance menor. La prueba sucesiva de nombres no
sustituye a una prueba multiproceso Windows, que permanece pendiente.

### Rechazos, cancelaciones e incidencias

Se observaron rechazos de número de palabras, red y formato inválidos,
mnemonic por CLI sin autorización y opciones sensibles con --run-tests.
La importación hexadecimal de longitud inválida terminó sin export;
Test-Path devolvió False para su destino.

Se registraron cancelación en la entrada de contraseña, discrepancia
de contraseñas, rechazo de contraseña corta y timeout de 360 segundos
en la decisión correspondiente. El log no demuestra cobertura de todos
los posibles puntos de cancelación ni un timeout global. Un Ctrl+C
introducido ya en el prompt de PowerShell tras terminar una exportación
no cuenta como cancelación del script.

Dos SyntaxError corresponden exclusivamente al comando Python -c para
consultar versiones: las comillas internas no llegaron como se esperaba.
No pertenecen al script ni a las suites. Para evitar esa incidencia,
utilizar en PowerShell:

```powershell
& $PY -m pip show mnemonic bip-utils cryptography
& $PY -m pip list --format=freeze
```

### Conclusión específica de Windows

No se detectó un fallo funcional pendiente del script en los casos
comprobados. La evidencia respalda esta combinación concreta de Windows,
Python, dependencias y hash; no todas las ediciones Windows ni versiones
futuras. Las cinco omisiones, los tres exports adicionales y los datos
faltantes del entorno deben conservarse en el registro.

---

## Preparación del entorno

Ejecutar desde la raíz de una copia local de confianza.

La instalación de dependencias debe prepararse antes de las pruebas
offline. Los comandos usan las versiones directas de requirements.txt.
Faltan bloqueo transitivo y hashes de artefactos para una preparación
reproducible. Hay evidencia de instalaciones Linux y Windows concretas,
no de cualquier combinación de sistema o herramientas.

### Linux/macOS: ejemplo con entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python --version
```

Estos comandos son una propuesta de preparación, no evidencia de que
todas las plataformas o versiones funcionen.

### Windows PowerShell: entorno del ensayo

Desde la raíz del proyecto, con el launcher y el intérprete instalados:

```powershell
py -3.10 -m venv .venv-verificacion
$PY = Join-Path $PWD.Path ".venv-verificacion\Scripts\python.exe"
& $PY --version
& $PY -m pip install -r requirements.txt
& $PY -m pip check
& $PY -m pip show mnemonic bip-utils cryptography
```

El ensayo utilizó Python 3.10.11. Si se elige otro intérprete, registrar
la combinación como un entorno distinto. No copiar el venv de Linux.
No es necesario activar Activate.ps1, modificar ExecutionPolicy ni
utilizar una terminal elevada para estas instrucciones.

---

## Generador del sistema y operaciones de archivo

### os.urandom()

El script solicita bytes mediante os.urandom(). La implementación
concreta depende de Python y del sistema operativo.

Este documento no atribuye una API interna únicamente a partir del
nombre o versión del sistema. Tampoco certifica la salud del generador,
la ausencia de compromisos ni un comportamiento siempre no bloqueante.

### Archivos temporales y publicación: base histórica y versión ensayada

La base histórica del análisis escribía un temporal y publicaba mediante
os.replace(). Esa descripción no representa el parche de escritura
identificado por el hash df80621c... del ensayo Windows.

En la versión ensayada, export_seed_report() serializa y cifra una vez y
_write_report_payload() crea un temporal con tempfile.mkstemp() en la
carpeta del destino. Completa la escritura, flush y fsync del archivo
antes de publicar mediante os.link(). Si el nombre está ocupado, el
exportador intenta otro nombre secuencial sin repetir el cifrado.

write_secure_file() utiliza el destino exacto y falla si existe. La función
generate_sequential_path() se conserva como propuesta de nombre, no como
reserva exclusiva; el exportador no depende de ella para publicar.

Se requieren enlaces duros y una carpeta de confianza. Si esa publicación
no está disponible, el código no recurre a os.replace() como alternativa.
No garantiza durabilidad del directorio ante pérdida de alimentación ni
protección frente a modificaciones hostiles de la ruta padre. Una
interrupción abrupta puede dejar temporales que necesitan revisión.

### Permisos

La base histórica ignoraba algunos errores de chmod. En el parche de
escritura, los sistemas POSIX ejecutan fchmod(0o600) sobre el descriptor
antes de publicar y propagan su fallo. Ese comportamiento pasó las
pruebas Linux comunicadas; los dos métodos POSIX se omiten en Windows.

La versión Windows no certifica ACL ni acceso exclusivo del propietario.
Esas propiedades requieren inspección y pruebas propias. Los permisos
no protegen frente a malware, privilegios elevados, backups o sincronización.

### Rutas

Las rutas con espacios deben escribirse entre comillas. No confundir la
raíz del proyecto con la carpeta output. El resolvedor nuevo resuelve
el padre y no sigue el enlace del nombre final, pero no protege frente
a un padre manipulado por un atacante.

La suite Linux comprueba enlaces simbólicos; los dos métodos se omitieron
en Windows porque no pudo crearlos. No generalizar el resultado de Linux
a esa condición Windows no ejecutada.

---

## Requisitos de ejecución de la versión analizada

- Python y dependencias en una combinación probada.
- hashlib.scrypt disponible y capaz de ejecutar el perfil configurado.
- Memoria suficiente para la KDF.
- Carpeta de destino accesible para crear temporales y el archivo final.
- Terminal compatible cuando se solicitan secretos.

No se declara todavía un mínimo universal de Python. py_compile,
importación y suites deben ejecutarse con el intérprete objetivo.

### Perfil scrypt

La versión analizada utiliza:

- N = 2**18.
- r = 8.
- p = 1.
- dklen = 32.
- Salt de 16 bytes.
- maxmem = 512 MiB.

maxmem es el límite configurado para la implementación; no indica que
se reserve automáticamente toda esa memoria. La disponibilidad real
debe comprobarse mediante los tests en el equipo objetivo.

Si scrypt falla, no debe sustituirse automáticamente por SHA-256 directo
ni reducirse silenciosamente el perfil.

---

## Terminal y entrada sensible

read_hidden_secret() comprueba que stdin y stdout sean TTY.
Después utiliza getpass y rechaza GetPassWarning.

El flujo que solicita secretos no debe ejecutarse con entrada o salida
redirigida. Por ejemplo, -i con stdin desde /dev/null se rechaza.

Esto es una política del programa, no una certificación de que cualquier
TTY esté libre de capturas, malware o registros.

--run-tests y los tests automáticos que no leen secretos no requieren
esa interacción y pueden registrar su salida.

### Cancelación

La contraseña de exportación se solicita dentro del manejo de
EOF y Ctrl+C. También se manejan cancelaciones durante la construcción
del contexto y la exportación.

La cobertura debe comprobarse en cada terminal objetivo.

### Timeout

La decisión sobre contraseña corta usa la capa temporizada, con
360 segundos predeterminados.

No existe un timeout global para todo el flujo ni para todas las
lecturas de secretos. La decisión puede reiniciar su espera al recibir
una opción inválida.

La implementación de decisiones temporizadas utiliza mecanismos
distintos en Unix y Windows; ambos necesitan pruebas reales por entorno.

---

## Protocolo de comprobación

### Linux/macOS

Desde la raíz, con el intérprete del entorno preparado:

```bash
python -m py_compile bip39_seed_report.py
python bip39_seed_report.py --help
python bip39_seed_report.py --run-tests --vectors-file test/vectors.json
PYTHONPATH="$PWD" python test/test_cifrado_report.py
PYTHONPATH="$PWD" python test/test_entrada_segura.py
PYTHONPATH="$PWD" python test/test_contenedor_report.py
PYTHONPATH="$PWD" python test/test_escritura_report.py
```

La invocación con PYTHONPATH está comprobada en el entorno Linux
comunicado. No debe generalizarse como prueba realizada en macOS.

### Windows PowerShell

Desde la raíz, con $PY definido como arriba, ejecutar por separado:

```powershell
& $PY -m py_compile .\bip39_seed_report.py
& $PY -m py_compile .\test\test_contenedor_report.py .\test\test_escritura_report.py .\test\verificar_export_laboratorio.py
& $PY .\bip39_seed_report.py --help
& $PY .\bip39_seed_report.py --run-tests
& $PY .\bip39_seed_report.py --run-tests --vectors-file .\test\vectors.json
```

Para las suites que importan el módulo de la raíz:

```powershell
$anterior = $env:PYTHONPATH
try {
    $env:PYTHONPATH = $PWD.Path
    & $PY .\test\test_cifrado_report.py
    & $PY .\test\test_entrada_segura.py
    & $PY .\test\test_contenedor_report.py
    & $PY .\test\test_escritura_report.py
}
finally {
    $env:PYTHONPATH = $anterior
}
```

El bloque no detiene automáticamente todos los comandos ante un código
nativo distinto de cero. Revisar cada resultado y capturar inmediatamente
$LASTEXITCODE si se desea registrar el estado de esa invocación.

Mantener la verificación manual de cada export. Ejemplo exclusivamente
con datos ficticios, ajustando ruta, número de palabras y passphrase real
del ensayo:

```powershell
& $PY .\test\verificar_export_laboratorio.py .\output\laboratorio\reporte.json --words 12 --network testnet --input-mode words
```

No imprimir plaintext ni publicar exports. Las opciones del auxiliar deben
corresponder al archivo final realmente creado, incluidos sufijos de nombre.

### Flujos manuales

Con material ficticio, comprobar:

- Contraseña vacía y confirmación diferente.
- Ctrl+C en primera contraseña y confirmación.
- Decisiones y/n/Enter/inválida/timeout.
- Rechazo sin TTY.
- Lectores de mnemonic, entropy binaria y hexadecimal.
- Passphrase vacía, discrepancia y reingreso.
- Mainnet/testnet y precedencia de -n.
- Exportación y descifrado del archivo realmente escrito.
- Permisos efectivos y fallos de escritura.

Las pruebas automáticas y manuales son complementarias.

---

## Datos que deben acompañar a cada resultado

Registrar:

- Fecha y commit o hash del script.
- Distribución y versión del sistema.
- Arquitectura.
- Python e implementación.
- Versiones de mnemonic, bip-utils y cryptography.
- Terminal utilizada.
- Suites y flujos ejecutados.
- Fallos y limitaciones observadas.

Comando para registrar Python y paquetes, usando el intérprete probado:

```bash
python -c 'import sys, platform; from importlib.metadata import version; print("Python:", sys.version); print("Implementación:", platform.python_implementation()); print("Arquitectura:", platform.machine()); print("Sistema:", platform.system(), platform.release()); print("Paquetes:", {n: version(n) for n in ("mnemonic", "bip-utils", "cryptography")})'
```

La versión del kernel no sustituye la distribución. En Linux, registrar
también los campos pertinentes de /etc/os-release.

No incluir secretos, exports privados o información innecesaria del
equipo en los logs publicados.

---

## Conclusión

Existen resultados satisfactorios en las combinaciones Linux comunicadas
y en Windows 10 Home x64, 10.0.19045, con Python 3.10.11 y las dependencias
descritas. No hay una matriz universal de soporte.

En Windows, las suites de BIP39, cifrado, entrada y contenedor terminaron
correctamente. Escritura aprobó diez métodos y omitió cinco. La batería
manual incluye catorce verificaciones satisfactorias y preservación del
primer export en un caso sucesivo de nombres repetidos.

Quedan por comprobar en Windows las ACL, los casos omitidos de enlaces
simbólicos y la concurrencia entre procesos. Faltan versión exacta de
PowerShell, sistema de archivos y otros detalles del entorno. macOS,
BSD y otras combinaciones no se dan por probados.

La publicación sin reemplazo depende del sistema de archivos y de una
carpeta de confianza. No garantiza durabilidad del directorio ni protege
un host comprometido. Los resultados no son una auditoría independiente
ni una recomendación para custodiar fondos.

---

## Referencias

- Python os.urandom(): https://docs.python.org/3/library/os.html
- Cryptography library: https://cryptography.io/
- bip-utils PyPI: https://pypi.org/project/bip-utils/
