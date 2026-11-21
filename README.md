# BIP39 Seed Report (offline)

Proyecto educativo y experimental para generar, validar, derivar
y reportar material BIP39/BIP32.

No es una wallet ni sustituye a una hot wallet o una hardware wallet.
No ha sido auditado de forma independiente para custodia o producción.

La decisión de uso corresponde al usuario. El proyecto no presenta sus
resultados ni sus pruebas como una certificación de seguridad para
custodiar fondos.

## Descripción del script

BIP39 Seed Report es una herramienta local de línea de comandos para
generar, importar, validar, derivar e inspeccionar material BIP39/BIP32.
Su propósito es hacer observable el recorrido entre las entradas,
las claves derivadas y las direcciones, y conservar el resultado en
un reporte privado cifrado.

Permite trabajar con una mnemonic BIP39 inglesa y su passphrase opcional,
o importar directamente una seed BIP32 hexadecimal sin utilizar mnemonic
ni passphrase BIP39. La entrada BIP32 directa no convierte una seed
arbitraria en una mnemonic ni certifica el origen del material importado.

Deriva direcciones para mainnet o testnet en las familias BIP44, BIP49,
BIP84 y BIP86, y en una sección legacy BIP32 basada en `m/0'`.
El reporte contiene diez direcciones de recepción y diez de cambio
por sección: cien direcciones en total. Son derivaciones locales,
no direcciones descubiertas mediante consultas de actividad.

No consulta la red Bitcoin, no obtiene saldos ni UTXO y no construye,
firma o transmite transacciones. No es una wallet ni un servicio
de recuperación de fondos.

El reporte privado incluye seeds, claves privadas y claves extendidas
que pueden permitir controlar fondos. Debe tratarse como secreto,
incluso cuando esté cifrado. La contraseña de exportación protege
el archivo; no sustituye la protección del equipo ni la conservación
responsable del material y de su contraseña.

## A quién va dirigida

- Personas que estudian BIP39, BIP32 y las rutas de derivación Bitcoin
  y quieren observar sus relaciones mediante ejemplos reproducibles.
- Docentes y estudiantes que preparan demostraciones con entradas
  ficticias, longitudes BIP39 válidas y distintas familias de direcciones.
- Desarrolladores y personas que realizan pruebas técnicas y necesitan
  generar reportes, preparar casos controlados o contrastar resultados
  con otra implementación.
- Usuarios técnicos que quieren examinar derivaciones de material
  conocido y entienden las diferencias entre mnemonic, seed, passphrase
  BIP39, contraseña del reporte y claves extendidas.

No está planteada como una solución de custodia lista para usar ni
como sustituto de una hot wallet o una hardware wallet. Requiere
preparar el entorno, revisar los requisitos del modo elegido y
comprender qué información privada se genera o se importa.

La decisión de uso corresponde al usuario. Las funciones disponibles,
el cifrado y los resultados de las pruebas no constituyen una auditoría
independiente ni una certificación de seguridad para custodiar fondos.

## Cómo aprovechar la herramienta

- Estudiar el recorrido BIP39: entropía, checksum, palabras, passphrase
  opcional y seed; observar qué cambia al modificar una entrada
  controlada y qué elementos no se pueden recuperar a partir de otros.
- Examinar la derivación BIP32: comparar la raíz, la cuenta legacy
  endurecida `m/0'` y sus claves extendidas, distinguiendo material
  privado y público.
- Comparar las familias BIP44, BIP49, BIP84 y BIP86, sus rutas de cuenta
  y las cadenas de recepción y cambio, con índices del 0 al 9.
- Trabajar con una seed BIP32 hexadecimal directa y distinguir ese
  recorrido del que comienza con una mnemonic BIP39.
- Preparar casos de prueba y contrastar direcciones, rutas o claves
  con otra implementación usando exactamente las mismas entradas,
  red, passphrase, cuenta, cadena e índice. Comparar dos llamadas
  a la misma biblioteca no equivale a una verificación independiente.
- Examinar candidatos de última palabra para una mnemonic incompleta
  de 11 o 23 palabras. La validez del checksum no identifica por sí
  sola la palabra original ni demuestra que un candidato corresponda
  a una wallet concreta.
- Conservar un reporte cifrado e inspeccionarlo después, distinguiendo
  la verificación de coherencia de la simple visualización.
- Ejecutar las suites para registrar el comportamiento de una revisión
  en un entorno concreto. Los resultados pertenecen a esa revisión
  y preparación; no certifican cualquier equipo o instalación.

Para aprendizaje, demostraciones y pruebas, utiliza material ficticio.
No compartas seeds, mnemonics, passphrases, contraseñas ni claves privadas
para pedir ayuda. Un reporte de mainnet no demuestra que existan fondos;
uno de testnet sigue pudiendo contener secretos que no deben reutilizarse
para otros fines.

## Límites de interpretación

Una mnemonic con checksum válido no demuestra que su origen fuera
aleatorio o imprevisible. Los indicadores de patrón tampoco estiman
la entropía real ni certifican la seguridad de una entrada.

La generación redundante registra el modo ejecutado y los estados
de sus proveedores. Tener varias interfaces disponibles no demuestra
que sus fuentes sean independientes. Los errores de preparación pueden
detener el proceso antes de intentar una adquisición.

GAP representa aquí la cantidad de direcciones derivadas por cadena.
No es una búsqueda de direcciones utilizadas, un escaneo de saldos
ni un mecanismo para localizar fondos o reconstruir automáticamente
las rutas de una wallet desconocida.

El inspector diferencia autenticación del archivo, comprobaciones de
coherencia y lectura del contenido. Mostrar un reporte correctamente
no verifica por sí mismo todas sus direcciones. Consultar el alcance
de cada opción en la sección de inspección.

La ejecución offline y el cifrado del reporte no protegen un equipo
comprometido ni garantizan la eliminación de secretos de memoria,
capturas, registros, archivos temporales o copias externas.
Las claves públicas extendidas también pueden facilitar correlación
entre direcciones; no deben tratarse como información sin implicaciones
de privacidad.

## Funciones implementadas

- Generación automática experimental redundante por defecto y modo
  `current` explícito mediante `os.urandom()`, en longitudes BIP39 válidas.
- Conversión a mnemonics inglesas de 12, 15, 18, 21 o 24 palabras.
- Aceptación del resultado generado sin filtrar palabras repetidas.
- Importación de entropía hexadecimal, entropía binaria o mnemonic existente.
- Enumeración de candidatos para completar mnemonics de 11 o 23 palabras.
- Validación de longitud, wordlist y checksum BIP39.
- Conversión inversa de mnemonic a entropía.
- Derivación de seed con passphrase BIP39 y normalización Unicode NFKD.
- Importación directa de una seed BIP32 hexadecimal de 16 a 64 bytes,
  sin mnemonic ni passphrase BIP39.
- Derivación de direcciones BIP44, BIP49, BIP84 y BIP86, más una sección
  legacy BIP32 P2PKH basada en `m/0'`.
- Diez direcciones por cadena de recepción y cambio, con índices del 0
  al 9 y cien direcciones en total en el reporte privado.
- Claves extendidas privadas y públicas de la raíz `m` y de la cuenta
  legacy endurecida `m/0'` en el reporte privado, etiquetadas por red,
  sin eliminar los campos hexadecimales existentes.
- Selección de mainnet o testnet.
- Resumen compacto de terminal con una dirección de recepción por sección,
  sin claves privadas ni clave pública extendida raíz.
- Indicadores descriptivos de patrón, sin score de seguridad.
- Exportación cifrada mediante scrypt y AES-256-GCM.
- Descifrado del formato histórico para compatibilidad; no implica
  compatibilidad del inspector con todas las estructuras antiguas.
- Entrada oculta centralizada con comprobación de TTY.
- Confirmación doble de passphrase BIP39 y cancelación controlada.
- Bloqueo predeterminado de secretos por argumentos CLI.
- Comprobación local de la wordlist embebida y de la lista efectiva
  utilizada por mnemonic.
- Inspector distribuido con cinco opciones y selección de menú
  limitada a 360 segundos:
  - `1`: verificar sin imprimir contenido privado.
  - `2`: revisar en una ventana temporal de GNOME Terminal.
  - `3`: revelar en la terminal actual, previa confirmación.
  - `4`: leer en el visor gráfico integrado, con búsqueda y sin edición.
  - `5`: abrir en la aplicación externa asociada a texto, tras advertir
    que se crea una copia temporal sin cifrar.
- Finalización del inspector después de completar una operación de
  lectura; la verificación de la opción `1` vuelve al menú.
- Requisitos y riesgos diferenciados para cada vía de inspección.
  El inspector actual está limitado a Linux.

Estas funciones describen la copia local en revisión. Los ensayos
históricos conservan sus propios alcances y recuentos.

La batería local del 19 de noviembre de 2026, registrada en
`output/bateria_local_lcqnkkq3`, completó las 26 etapas con código `0`.
Acumuló 411 métodos unittest, sin fallos, errores, omisiones ni fallos
esperados. Las tres etapas iniciales realizan comprobaciones que no
se contabilizan como métodos unittest.

El ejecutor registró 80 de 80 funciones o métodos del núcleo alcanzados
y conservó los 50 archivos protegidos, tanto en contenido como en el
conjunto inventariado. Estos datos no equivalen a cobertura completa
de ramas, validación de todas las plataformas ni verificación
criptográfica independiente.

El núcleo de esta corrida tiene SHA-256
`bcae133d9d57c1e6923ef13e069d308e7f1773bb384f43d439796d8cc5d01787`.
Las dos clases Java preparadas localmente conservaron sus hashes en
una comprobación adicional anterior y posterior a la batería; esa
comprobación se registra separadamente del inventario del ejecutor.

Los ensayos manuales se conservan por separado. El campo automático
`manual_terminal_tests` permanece pendiente y no se modifica para
atribuirle comprobaciones manuales. Los escenarios de ausencia de
Java o Node y la revisión final previa a publicación siguen pendientes.
Esta corrida no anuncia una release ni una auditoría independiente.

## Entorno de trabajo de esta etapa

El desarrollo y la verificación activa de esta etapa se realizan en Linux.
La integración original se ensayó en Linux Mint 21.3 Virginia, x86_64,
kernel 5.15.0-203-generic y CPython 3.10.12, con mnemonic 0.21,
bip-utils 2.9.3, cryptography 44.0.3 y pip 26.3, según
`entorno.json` de `bateria_local_8jy797o3`, registrado el
10 de noviembre de 2026 a las 19:11:17 UTC.

La comprobación posterior de otra copia utilizó el mismo sistema, kernel,
Python y versiones directas, pero un venv nuevo con pip 22.0.2.
Se instalaron de nuevo los paquetes Python y se recompilaron las fuentes
Java; los runtimes base existentes del mismo equipo se reutilizaron.
No se igualan retrospectivamente ambos entornos ni se presenta este ensayo
como instalación completa desde cero en otro equipo.

Las versiones son referencias observadas, no recomendaciones universales
ni certificados de seguridad del host. Las consultas posteriores de Java
11.0.33, javac 11.0.33 y Node v24.22.2 se registran por separado;
no se incorporan retrospectivamente a los campos del entorno.json original.
Detalle: [Inventario de runtimes Linux](docs/RUNTIMES_ENTROPY_LINUX_2026-11-10.md).

Windows y macOS quedan fuera del alcance activo y no bloquean este hito.
Su revisión queda diferida a quien ejecute el programa en esos sistemas.
Los resultados Windows históricos se conservan con su versión y sus
omisiones; no certifican el parche actual. La simulación de consola Windows
en Linux no constituye una ejecución Windows real.

## Modo interactivo recomendado

Preparar primero el entorno de la sección Instalación, incluidos los
proveedores de generación redundante cuando se utilice el modo predeterminado,
y definir PY.

Desde la raíz del proyecto:

```bash
"$PY" bip39_seed_report.py -i
```

Flujo:

1. Verifica localmente la wordlist.
2. Solicita y confirma la contraseña del reporte cifrado.
3. Permite elegir generación o importación del material de entrada,
   incluida una seed BIP32 hexadecimal directa.
4. En generación interactiva de mnemonic, permite elegir 12 o 24 palabras.
5. Solicita la red cuando no se proporcionó `-n`/`--network`.
6. En el recorrido BIP39, solicita y confirma la passphrase opcional,
   que puede quedar vacía. La entrada BIP32 directa no utiliza
   mnemonic ni passphrase BIP39.
7. Valida la entrada y deriva las cinco secciones de recepción y cambio.
8. Muestra un resumen compacto sin material privado ni el detalle GAP.
9. Guarda el reporte privado cifrado con el contenido completo.
10. Muestra la ruta final y un único comando para abrir el inspector.

La ruta predeterminada es:

```text
output/bip39_seed_report.json
```

Si el nombre solicitado está ocupado, el exportador intenta otro nombre
secuencial sin repetir el cifrado.

La publicación utiliza os.link() para crear el nombre final sin reemplazar
destinos existentes. La seguridad frente a colisiones no depende de una
comprobación previa de disponibilidad.

Requiere un sistema de archivos que admita enlaces duros y una carpeta
de salida de confianza. Las garantías quedan limitadas a las condiciones
probadas; no protegen frente a modificaciones hostiles de la ruta padre.

La entrada oculta exige una terminal interactiva en stdin y stdout.
El programa rechaza el fallback de getpass que no puede garantizar
ausencia de eco.

Esto no protege contra malware, keyloggers, capturas, registros externos
o un sistema comprometido. Los menús son visibles; no toda la entrada
del programa es oculta.

Las decisiones que utilizan la capa temporizada pueden cancelar tras
360 segundos sin respuesta. No existe un timeout global para todo el
flujo ni para todas las lecturas de secretos.

## Generación automática de entropy — revisión local del 10 de noviembre de 2026

La CLI utiliza `--entropy-mode redundant` de forma predeterminada para
generación nueva. Es una integración experimental de los proveedores
`python_os`, `java_secure_random`, `javascript_webcrypto` y `python_secrets`.
Las aportaciones seleccionadas por la política se finalizan mediante
`sha512-framed`, excepto el respaldo automático descrito a continuación.
No se certifica independencia entre interfaces que pueden compartir fuentes
del sistema operativo ni una mejora cuantificada de seguridad.

`--entropy-mode current` solicita expresamente la primitiva conservada
`generate_entropy()`, basada en `os.urandom()`. No intenta los otros tres
proveedores. No es lo mismo que un respaldo automático del modo redundante.

El reporte distingue los modos ejecutados `redundante`,
`redundante_reducido` (pareja Java + JavaScript), `actual_respaldo`
(aportación aceptada de `python_os`) y `actual_explicito`.
En `actual_respaldo` se reutiliza la aportación aceptada de `python_os`
mediante `python-os-prefix`; no se describe como una adquisición nueva.
Los fallos de preparación o una combinación no admitida pueden detener
la operación: el respaldo no es una garantía universal de continuidad.

`--entropy-timeout SEGUNDOS` debe ser positivo y finito; su valor
predeterminado es 10 segundos por proveedor. No es un plazo global del
programa, de los menús, de las contraseñas ni del visor.

Las importaciones hexadecimal, binaria o de mnemonic y la búsqueda de
última palabra no se convierten en generación automática ni mezclan
el material importado con nuevas aportaciones por estas opciones.

El campo `entropy_generation` del contenido privado registra modo solicitado,
modo ejecutado, método, versiones aplicables y estados de proveedores.
El contenido TXT incluye una descripción correspondiente. Estos metadatos
se autentican como parte del reporte cifrado; no prueban independientemente
el origen, la salud de las fuentes o la imprevisibilidad de la entrada.

La codificación del combinador y sus límites se describen en
[la especificación experimental del combinador](docs/ENTROPY_COMBINER_V1.md).

Ejemplos con material de laboratorio, desde una TTY y con `PY` preparado:

```bash
"$PY" bip39_seed_report.py -w 12 -n testnet --entropy-mode redundant
```

```bash
"$PY" bip39_seed_report.py -w 12 -n testnet --entropy-mode current
```

No habilitar `--show-all` ni pasar secretos por argumentos para estas pruebas.
Preparar los runtimes y dependencias antes de trabajar offline.


## Contraseñas diferentes

La passphrase BIP39 modifica la seed y las derivaciones.

La contraseña de exportación protege el archivo cifrado y no modifica
la seed BIP39.

Son valores distintos. No se sustituyen ni se recuperan mutuamente.

## Cifrado y protección de datos

Los exports nuevos utilizan:

- KDF: scrypt.
- Parámetros: N=2**18, r=8, p=1, dklen=32.
- Salt aleatorio de 16 bytes.
- Cifrado autenticado AES-256-GCM.
- Nonce aleatorio de 12 bytes.
- Contenedor JSON versionado con parámetros KDF.
- Metadatos definidos autenticados mediante AAD.

El parámetro maxmem de scrypt se configura en 512 MiB. Es un límite
permitido por la implementación, no una reserva automática de toda
esa memoria. El perfil debe probarse en el equipo objetivo.

El flujo normal serializa y cifra el reporte una sola vez. Después escribe
un temporal en la carpeta de destino y completa flush y fsync del archivo
antes de publicar el nombre final mediante os.link().

Si el nombre está ocupado, intenta otro nombre secuencial. No utiliza
os.replace() como alternativa y no repite la KDF por cada colisión.

En sistemas POSIX se aplica 0o600 mediante fchmod sobre el descriptor antes
de publicar. Si esa operación falla, la publicación se aborta. Esto no
equivale a verificar las ACL de Windows ni protege un sistema comprometido.

La publicación requiere enlaces duros y una carpeta de confianza.
No garantiza durabilidad del directorio ante pérdida de alimentación.
Una interrupción abrupta puede dejar un temporal que necesite revisión.

La función write_secure_file() conserva el destino exacto y falla si ya
existe. export_seed_report() utiliza reintentos secuenciales y devuelve
la ruta realmente publicada.

El formato histórico ENCRYPTED: puede descifrarse por compatibilidad
y muestra una advertencia. Los exports nuevos no utilizan el método
histórico de SHA-256 directo de contraseña.

Descifrar un archivo histórico no lo fortalece automáticamente:
para migrarlo debe volver a cifrarse con el formato actual.

La limpieza del historial del proceso Python no borra el historial
del shell, scrollback, capturas, memoria, swap ni backups.

## Pruebas

Desde la raíz del proyecto:

```bash
"$PY" -m py_compile bip39_seed_report.py
"$PY" bip39_seed_report.py --run-tests --vectors-file test/vectors.json
```

La suite distribuida está en test/vectors.json.

Sin --vectors-file, el script localiza esa suite respecto de la carpeta
del propio script. Una ruta indicada explícitamente conserva la
resolución habitual de rutas de la ejecución.

```bash
"$PY" bip39_seed_report.py --run-tests
```

Resultado esperado con la suite distribuida:

```text
Test vectors BIP39: OK (24 casos)
```

Las pruebas adicionales están en la carpeta test.

Desde la raíz del proyecto, en el entorno Linux preparado y con una copia
local de confianza:

```bash
PYTHONPATH="$PWD" "$PY" test/test_cifrado_report.py
PYTHONPATH="$PWD" "$PY" test/test_entrada_segura.py
PYTHONPATH="$PWD" "$PY" test/test_contenedor_report.py
PYTHONPATH="$PWD" "$PY" test/test_escritura_report.py
PYTHONPATH="$PWD" "$PY" test/test_regresion_vectores_ultima_palabra.py
PYTHONPATH="$PWD" "$PY" test/test_ux_terminal_report.py
PYTHONPATH="$PWD" "$PY" test/test_revision_integral_report.py
PYTHONPATH="$PWD" "$PY" test/test_inspeccionar_reporte_cifrado.py
PYTHONPATH="$PWD" "$PY" test/test_ejecutar_bateria_local.py
```

Ejecuta esos comandos desde la raíz y compruébalos en una descarga limpia.

Los vectores BIP39 verifican los casos ejecutados de conversión
entropy-mnemonic, derivación de seed y round-trip. No constituyen una
auditoría ni verifican todas las derivaciones o claves extendidas.

La suite de regresión del runner y última palabra comprueba rechazo
de suites vacías y entradas mal formadas, errores previstos, casos
positivos y búsqueda real de candidatos. Incluye nueve métodos con
subcasos y no verifica el cuarto campo BIP32.

La comprobación de ausencia de éxito captura directamente la salida
del runner. Una prueba de mutación confirma que detecta un runner
ficticio que imprime OK antes de fallar, sin modificar el script real.

La prueba de cifrado comprueba recuperación, rechazo de contraseña
incorrecta, alteraciones, perfil KDF y compatibilidad histórica.

La prueba de entrada segura comprueba el rechazo simulado de
GetPassWarning y la confirmación/normalización Unicode.

Las pruebas usan exclusivamente material ficticio. No introduzcas
secrets reales en los tests.

La suite del contenedor comprueba estructura, tipos, claves duplicadas,
base64 y límites. Verifica rechazos antes de ejecutar la KDF e incluye
casos positivos con scrypt real y compatibilidad histórica.

La suite de escritura comprueba preservación de destinos existentes,
colisiones, fallos simulados, publicación del contenido completo y
concurrencia con hilos. Incluye pruebas POSIX, enlaces simbólicos y
una prueba multiproceso específica de Linux.

Las omisiones dependen de la plataforma y deben registrarse: no son
casos aprobados.

El auxiliar test/verificar_export_laboratorio.py permite verificar
manualmente un export sin imprimir su contenido privado. Requiere una
terminal interactiva y no forma parte de las suites automáticas.

Antes de ejecutar la batería integrada en una copia nueva, preparar
los comandos y auxiliares de proveedores y compilar las fuentes Java
en el classpath configurado de esa copia, según la sección Instalación.
Instalar solo requirements.txt no completa esa preparación.

Para ejecutar la batería secuencial y registrar entorno, hashes e inventario:

```bash
"$PY" test/ejecutar_bateria_local.py
```

La batería integrada planifica 25 etapas. El ensayo local
`bateria_local_8jy797o3` registró 362 métodos unittest, incluidos
42 del inspector y 33 del ejecutor, sin fallos ni omisiones y con código 0.
Las tres primeras etapas utilizan otros procedimientos y no se cuentan
como métodos unittest. No se suma otra vez la ejecución individual del ejecutor.

El manifiesto de ese ensayo contiene 49 archivos conservados, incluidos
los dos auxiliares `.cjs` y `test/js/test_webcrypto_provider.cjs`.
La selección comprende fuentes `.py`, `.java`, `.js`, `.cjs` y `.mjs`,
además de entradas obligatorias; no todos los documentos, binarios o dependencias.
El inventario 73/73 corresponde a funciones y métodos del núcleo, no
a cobertura completa del inspector, del ejecutor ni de todas las ramas.
El total del manifiesto puede variar en otro árbol; no se impone 49 universalmente.

El ejecutor comprueba los registros de cada proceso, los códigos de
salida y los resultados unittest. Los fallos, errores y éxitos inesperados
impiden aprobar la etapa; las suites vacías, omisiones y fallos esperados
impiden una aprobación completa.

El cierre local de la integración original se documenta en
[Resultados de integración entropy CLI](test/RESULTADOS_ENTROPY_CLI_2026-11-10.md).
Sus seis ensayos manuales conservan evidencia separada. No se cambia
el estado manual del resumen automático.

### Comprobación posterior de otra copia

Se copiaron y verificaron 64 archivos seleccionados en un laboratorio
separado del proyecto de referencia. La instalación en un venv nuevo,
pip check y las importaciones principales fueron satisfactorios.
Se recompilaron las dos fuentes Java para esa copia, con código 0.
No se trasladaron el venv, el build ni los reportes cifrados anteriores.

La batería `proyecto/output/bateria_local_zelv2gy3` terminó con
25 etapas, 362 métodos unittest, inventario 73/73, 49 entradas del
manifiesto conservadas y código 0, sin fallos, errores u omisiones.
La suite individual del ejecutor terminó con 33 métodos y código 0;
no se suma otra vez al acumulado. Dos ejecuciones de la batería no
representan 724 métodos distintos.

Antes de los casos manuales, se comprobaron 71 archivos registrados
del origen sin cambios y sin ausencias. No se declara una comprobación
posterior a esos manuales ni de todo el sistema. Los 64 archivos copiados,
las 49 entradas del manifiesto y los 71 archivos del origen son conjuntos
diferentes.

Se añadieron tres casos manuales, separados de los seis originales:

| Caso | Resultado registrado | Límite del registro |
|---|---|---|
| Redundante, 12 palabras, testnet | Cuatro proveedores aceptados y utilizados; generación y verificador con código 0 | No demuestra independencia de fuentes ni imprevisibilidad |
| Current explícito, 12 palabras, testnet | Solo python_os; los otros tres no intentados; reporte creado y verificador con mensaje OK | No se capturaron códigos separados de generación y verificación |
| Interactivo, 24 palabras, testnet, passphrase BIP39 vacía | Cuatro proveedores utilizados; verificación satisfactoria e inspector con código 0 | No verifica independientemente todas las direcciones |

El mantenedor confirmó que la ventana temporal del tercer caso se abrió,
mostró el reporte y se cerró al pulsar Enter. No se declara borrado seguro
ni repetición de todos los casos de timeout, cancelación o error.
Los manuales no reescriben manual_terminal_tests del resumen automático.

Los hashes de las clases se registraron después de compilar y antes de
la batería; no se comunicó una nueva comprobación de clases después de
todos los ensayos. Las clases no forman parte del manifiesto de 49 archivos.
La clase Java recompilada no es binariamente idéntica a la histórica;
no se atribuye una causa concreta ni se declara compilación reproducible.

Esta prueba utilizó runtimes base existentes del mismo equipo y reportes
nuevos. No acredita instalación completa desde cero, recuperación offline
de un reporte antiguo trasladado a otro equipo ni soporte nuevo Windows/macOS.

Detalle:
[Resultados de preparación de otra copia](test/RESULTADOS_COPIA_ENTROPY_2026-11-10.md).

### Resultados históricos y alcance adicional

Los resultados históricos del endurecimiento del 5 de noviembre permanecen en
[test/RESULTADOS_ENDURECIMIENTO_2026-11-05.md](test/RESULTADOS_ENDURECIMIENTO_2026-11-05.md).

Los nueve ensayos manuales del menú y la batería anterior se conservan en
[test/RESULTADOS_INSPECTOR_2026-11-04.md](test/RESULTADOS_INSPECTOR_2026-11-04.md).
No se atribuyen a esas ejecuciones anteriores los conteos de esta integración.

Consulta [test/README.md](test/README.md) para ejecución y alcance, y
[ANALISIS_COMPATIBILIDAD_SO.md](ANALISIS_COMPATIBILIDAD_SO.md) para los
entornos y resultados registrados.

## Indicadores informativos de patrón

El script calcula indicadores superficiales de patrón y los conserva
sin pérdida en el reporte privado. La terminal compacta no enumera
sus estadísticas; --show-all mantiene la presentación detallada.
No estiman entropía criptográfica ni imprevisibilidad, ni
determinan cómo se generó la mnemonic. Una mnemonic aleatoria válida puede
contener palabras repetidas o índices consecutivos. No uses estos indicadores
para aceptar o descartar una seed.

## Tipos de dirección soportados

El reporte deriva las siguientes cinco secciones. En las cuatro
familias BIP44, BIP49, BIP84 y BIP86, `c` representa el coin type:
`0` para mainnet y `1` para testnet. El índice `i` recorre de 0 a 9.

| Sección | Recepción | Cambio | Tipo de dirección |
|---|---|---|---|
| BIP44 | `m/44'/c'/0'/0/i` | `m/44'/c'/0'/1/i` | P2PKH |
| BIP49 | `m/49'/c'/0'/0/i` | `m/49'/c'/0'/1/i` | P2WPKH-P2SH |
| BIP84 | `m/84'/c'/0'/0/i` | `m/84'/c'/0'/1/i` | P2WPKH |
| BIP86 | `m/86'/c'/0'/0/i` | `m/86'/c'/0'/1/i` | P2TR |
| BIP32 legacy | `m/0'/0/i` | `m/0'/1/i` | P2PKH |

Las cuatro familias BIP44 a BIP86 utilizan la cuenta endurecida `0'`.
La sección legacy utiliza el nodo endurecido `m/0'`; no añade un
coin type a esa ruta. La red seleccionada determina las codificaciones
de direcciones y claves correspondientes.

Cada sección conserva diez direcciones de recepción y diez de cambio
en el reporte privado: cien direcciones en total. La vista compacta
de terminal muestra únicamente la primera dirección de recepción
de cada sección.

GAP — Direcciones derivadas por cadena: 10.

El campo interno se conserva como `gap_limit`. En este proyecto expresa
una cantidad fija de derivaciones locales, no un descubrimiento de
actividad. El programa no consulta blockchain, saldos ni UTXO y no
busca direcciones utilizadas.

## Dependencias

Para preparar un entorno virtual y comprobar sus dependencias,
seguir la sección Instalación. Los ejemplos de ejecución posteriores
utilizan "$PY" para conservar el intérprete elegido.

`requirements.txt` fija las dependencias directas del entorno de referencia.
Todavía no representa un bloqueo completo de dependencias transitivas
ni una instalación con verificación de hashes.

## Instalación

Guías detalladas por sistema:

- [Linux](docs/INSTALACION_LINUX.md)
- [Windows PowerShell](docs/INSTALACION_WINDOWS.md)
- [macOS](docs/INSTALACION_MACOS.md)
- [Conservación y recuperación de reportes](docs/RECUPERACION_REPORTES.md)

Consultar el alcance de cada guía: las instrucciones propuestas no
equivalen a una ejecución registrada en esa plataforma.

### Dependencias adicionales de la generación redundante

Instalar `requirements.txt` no instala Java ni Node.js ni compila las
fuentes Java. Consultar
[la preparación de runtimes en Linux](docs/INSTALACION_LINUX.md#preparación-adicional-de-runtimes-para-entropy)
y el [inventario de runtimes](docs/RUNTIMES_ENTROPY_LINUX_2026-11-10.md).

Java y Node no son requisitos de todas las operaciones. Sus requisitos
dependen del modo solicitado y de las pruebas que se ejecuten:

| Operación | Preparación adicional |
|---|---|
| Generación con `--entropy-mode current` explícito | No adquiere aportaciones mediante Java ni Node. Requiere las dependencias Python del proyecto. |
| Generación redundante con los cuatro proveedores configurados | Requiere los runtimes Python, Java y Node, los auxiliares correspondientes y la clase Java compilada en el classpath configurado. |
| Batería que incluye recorridos con proveedores reales | Requiere preparar esos proveedores antes de ejecutarla. Aprobar las pruebas simuladas no acredita esa preparación. |
| Inspector de reportes existentes | No necesita Java ni Node para descifrar. Sus requisitos adicionales dependen de la opción de lectura elegida; consultar la sección de inspección. |

Para compilar las fuentes Java se necesita un JDK con `javac`; disponer
solo del ejecutable `java` no basta. Para ejecutar una clase ya compilada
se necesita un runtime Java compatible. La compilación debe realizarse
con las instrucciones de la guía Linux y en la copia de trabajo elegida.

ADVERTENCIA: con la configuración actual, si falta
`build/entropy_java/JavaEntropyProvider.class`, la construcción de los
comandos conjuntos puede detenerse con
`Falta compilar JavaEntropyProvider.java.` antes de intentar adquirir
aportaciones. Este mensaje también puede aparecer con Java instalado.
No significa que se haya intentado y rechazado una aportación Java.

No se garantiza una reducción o un respaldo automático ante cualquier
error de preparación. Si se desea el modo `current`, solicitarlo
expresamente; no cambiar de modo en silencio ni omitir pruebas para
presentar como completa una batería que no pudo ejecutarse.

Antes de generar en modo redundante o ejecutar su batería:

- Revisar las rutas efectivas de los módulos de configuración y los
  ejecutables seleccionados para Python, Java y Node.
- Disponer de los auxiliares de la misma revisión del proyecto.
- Compilar las fuentes Java en el classpath configurado de la copia.
  La configuración ensayada requiere build/entropy_java; no basta con
  tener javac instalado.
- Comprobar la configuración antes de introducir material de prueba.
  Los errores de preparación no garantizan una continuación automática.

La configuración local utiliza Node en una carpeta aislada de usuario;
esto no equivale a un sandbox. Que `node` o `java` estén en PATH no
demuestra que sean los ejecutables seleccionados.

Se comprobó un venv nuevo con paquetes reinstalados y Java recompilado
sobre los runtimes existentes. La instalación completa de esos runtimes
desde cero y su reproducción en otro equipo siguen sin acreditarse.
El modo `current` explícito no utiliza Java ni Node para generar;
no debe confundirse con un respaldo automático del modo redundante.
Las rutas Linux no se consideran portables por defecto a Windows/macOS.

### 1. Preparar el entorno virtual

Desde la raíz de una copia local de confianza:

```bash
python3 --version
python3 -m venv .venv-verificacion
PY="$PWD/.venv-verificacion/bin/python"
```

La creación del entorno solo es necesaria si todavía no existe.

### 2. Instalar y comprobar dependencias

Preparar las dependencias antes de trabajar offline:

```bash
"$PY" -m pip install -r requirements.txt
"$PY" -m pip check
```

Si una comprobación falla, revisar el entorno antes de continuar.

### 3. Confirmar el intérprete utilizado

```bash
"$PY" -c 'import sys; print(sys.executable)'
"$PY" --version
"$PY" -c 'import mnemonic, bip_utils, cryptography; print("Importaciones principales correctas")'
```

Mantener el mismo intérprete para los comandos de generación, inspección
y batería. Revisar además los comandos de adquisición definidos en los
módulos de configuración: cambiar PY no reconfigura automáticamente los
ejecutables de los proveedores.

La variable PY solo selecciona el ejecutable usado por los comandos
que contienen "$PY". Reasignarla a /usr/bin/python3 no elimina el venv,
pero cambia el intérprete y el entorno de paquetes utilizados.

En una terminal nueva, volver a definir:

```bash
PY="$PWD/.venv-verificacion/bin/python"
```

Una instalación satisfactoria no certifica todos los flujos ni todas
las plataformas. Registrar el entorno y ejecutar las pruebas.

### 4. Vectores distribuidos

El repositorio incluye la suite en test/vectors.json. Conserva la copia que corresponde
a la versión analizada; no la reemplaces automáticamente desde una rama
remota mutable.

Puedes indicar otra suite explícitamente con --vectors-file.

El runner rechaza suites vacías y valida la estructura completa antes
de ejecutar las conversiones. Si la raíz es un objeto JSON, exige
el bloque english; también admite listas directas de vectores ingleses.

Los errores previstos de lectura, UTF-8, JSON y formato, así como
las discrepancias en los resultados, terminan con un mensaje de error
y código de salida 1.

Los vectores de cuatro campos siguen sin verificar el campo de clave
extendida BIP32.

## Uso del script

### Comandos y opciones

```bash
"$PY" bip39_seed_report.py --help
```

Entradas disponibles:

- -w/--words: genera una mnemonic de 12, 15, 18, 21 o 24 palabras.
- --entropy-bin: importa entropy binaria.
- --entropy-hex: importa entropy hexadecimal.
- --mnemonic: importa una mnemonic completa.
- --mnemonic-incomplete: enumera candidatos para 11 o 23 palabras.

Debe resolverse una sola entrada. El modo -i ofrece un menú cuando
no se proporcionó una entrada.

Opciones generales:

- --entropy-mode: `redundant` por defecto o `current`; solo generación nueva.
- --entropy-timeout: segundos por proveedor del modo redundante, positivos
  y finitos; predeterminado 10. No es timeout global.
- -i/--interactive: lectura interactiva de secretos sin eco en una TTY.
- -n/--network: mainnet o testnet.
- -f/--format: contenido interno JSON o texto.
- -o/--output: destino; por defecto output/bip39_seed_report.json.
- --audit-passphrase: incluye el análisis descriptivo en el reporte;
  la vista compacta indica su inclusión y --show-all muestra sus detalles.
  No estima la entropy real de la passphrase.
- --show-all: revela material privado en terminal; solo para pruebas.
- --run-tests: ejecuta la suite indicada y termina sin exportar.
- --vectors-file: ruta explícita de la suite. Si se omite, utiliza test/vectors.json respecto de la carpeta del script.
- --allow-insecure-cli-secrets: permiso explícito para argumentos
  sensibles exclusivamente en pruebas controladas.

### Política de secretos CLI

--entropy-bin, --entropy-hex, --mnemonic, --mnemonic-incomplete y
-p/--passphrase están bloqueados por defecto.

El bloqueo reconoce presencia explícita, incluso un valor vacío
como -p "". Usar -i no evita el bloqueo.

Para pruebas ficticias puede habilitarse
--allow-insecure-cli-secrets. No evita exposición en historial,
argumentos del proceso o registros.

--run-tests no admite opciones sensibles por argumentos, aunque
se proporcione el permiso.

El bloqueo no borra un valor que ya llegó al shell o al proceso.
Los mensajes estándar de errores sintácticos del parser no tienen
una política completa de redacción.

### Ejemplos de uso

#### 1. Generar mnemonic nueva (12 palabras, mainnet)

```bash
"$PY" bip39_seed_report.py -w 12
```

**Flujo:**
1. Pide contraseña para encriptar
2. Genera 12 palabras aleatorias
3. Realiza validación e indicadores informativos de la mnemonic
4. Usa red mainnet (default)
5. Oculta datos sensibles en terminal
6. Guarda archivo encriptado en `output/bip39_seed_report.json`

Sin -i, una passphrase BIP39 no se solicita interactivamente.
Si no se suministra, se utiliza la passphrase vacía.
Para introducirla sin eco, utiliza el modo -i.

#### 2. Generar mnemonic nueva (24 palabras, testnet)

```bash
"$PY" bip39_seed_report.py -w 24 -n testnet
```

**Flujo:**
1. Pide contraseña para encriptar
2. Genera 24 palabras aleatorias
3. Realiza validación e indicadores informativos
4. Usa red testnet
5. Oculta datos sensibles en terminal
6. Guarda archivo encriptado

Sin -i, una passphrase BIP39 no se solicita interactivamente.
Si no se suministra, se utiliza la passphrase vacía.
Para introducirla sin eco, utiliza el modo -i.

#### 3. Modo interactivo (menú guiado)

```bash
"$PY" bip39_seed_report.py -i
```

**Flujo:**
1. Pide contraseña
2. Muestra menú interactivo:
   - Seleccionar tipo de entrada (1-5)
   - Seleccionar longitud (12 o 24 palabras)
   - Seleccionar red (mainnet o testnet)
   - Ingresar passphrase (opcional)
3. Genera, importa o reconstruye el material según la opción elegida
   y valida la entrada.
4. Deriva la seed, claves y direcciones, y presenta el resumen compacto.
5. Guarda el reporte cifrado.

#### 4. Modo educativo: revelar secretos en terminal

```bash
"$PY" bip39_seed_report.py -w 12 --show-all
```

Flujo:

1. Solicita y confirma la contraseña de exportación.
2. Genera una mnemonic de 12 palabras.
3. Revela entropy, mnemonic, seed, clave raíz y las claves privadas
   incluidas en la vista de terminal.
4. Muestra validación e indicadores descriptivos de patrón,
   sin score de seguridad.
5. Guarda el reporte cifrado.

--show-all desactiva la ocultación de secretos en la vista de terminal,
pero no convierte esa vista en una reproducción completa del JSON privado.
Se sigue mostrando solo la primera dirección de cada familia.
GAP limit no se muestra en terminal; su valor y significado quedan
conservados en los reportes.

La salida puede revelar material suficiente para controlar fondos.
No la redirijas a logs ni la compartas.

Advertencia: utiliza --show-all exclusivamente con material ficticio
en pruebas educativas. El proyecto permanece educativo y no ha sido auditado
de forma independiente para custodia o producción. La decisión de uso
corresponde al usuario. Los resultados y pruebas no constituyen una
certificación de seguridad para custodiar fondos.

#### 5. Verificar mnemonic existente

```bash
"$PY" bip39_seed_report.py \
  --allow-insecure-cli-secrets \
  --mnemonic "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about" \
  -p "TREZOR" \
  -n testnet
```

Vector público de prueba; nunca utilizar este material para fondos.
El programa todavía solicita una contraseña de exportación en una TTY.

**Flujo:**
1. Pide contraseña
2. Verifica checksum BIP39
3. Valida la mnemonic y conserva los indicadores descriptivos
   en el reporte privado.
4. Calcula seed y derivaciones
5. Guarda archivo encriptado

#### 6. Calcular última palabra (recuperación)

```bash
"$PY" bip39_seed_report.py \
  --allow-insecure-cli-secrets \
  --mnemonic-incomplete "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon" \
  -n testnet
```

**Flujo:**
1. Busca todas las palabras posibles
2. Muestra lista numerada
3. Pide al usuario seleccionar la correcta
4. Debes verificar manualmente la palabra elegida.
5. Genera mnemonic completa
6. Realiza Validación e indicadores

Enumera candidatos que producen una mnemonic BIP39 válida y solicita una selección explícita.

El checksum no identifica por sí solo la palabra originalmente utilizada.
Si ocurre EOF durante la selección, la operación aborta; no toma automáticamente el primer candidato.

La recuperación debe contrastarse con una referencia independiente.

#### 7. Usar entropía hexadecimal

```bash
"$PY" bip39_seed_report.py \
  --allow-insecure-cli-secrets \
  --entropy-hex 00000000000000000000000000000000 \
  -n testnet
```

**Requisitos y formato recomendado:**

- El contenido hexadecimal debe representar 16, 20, 24, 28 o 32 bytes:
  32, 40, 48, 56 o 64 dígitos hexadecimales, sin contar el prefijo
  opcional ni los espacios admitidos.
- Formato recomendado: dígitos 0-9 y a-f, sin espacios ni prefijo.
- El parser también admite mayúsculas, espacios ASCII y un prefijo 0x.

Los ceros son datos públicos completamente predecibles.

#### 8. Usar entropía binaria

```bash
"$PY" bip39_seed_report.py --allow-insecure-cli-secrets --entropy-bin 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 -n testnet
```

**Requisitos y formato recomendado:**

- Longitud válida de 128, 160, 192, 224 o 256 bits.
- Formato recomendado: una secuencia de 0 y 1 sin espacios.
- El parser elimina los espacios ASCII antes de validar los bits
  y su longitud.

Para pruebas, puedes usar una secuencia conocida; no atribuyas seguridad a una entrada manual por tener la longitud y checksum correctos.
Esta secuencia de ceros es pública y completamente predecible.
El ejemplo no debe utilizarse para proteger fondos.

#### 9. Ejecutar los vectores BIP39 distribuidos

```bash
"$PY" bip39_seed_report.py --run-tests --vectors-file test/vectors.json
```

**Resultado esperado:**
Test vectors BIP39: OK (24 casos)

#### 10. Auditoría de passphrase

```bash
"$PY" bip39_seed_report.py -i --audit-passphrase -n testnet
```

El reporte conserva los siguientes datos descriptivos. En terminal se
muestran con --show-all; en compacto se indica su inclusión:
- Número de caracteres
- Bytes UTF-8
- Caracteres distintos
- Presencia de mayúsculas, minúsculas, dígitos, símbolos, espacios
- Nota informativa; no calcula entropía real

## Flujo de trabajo de prueba recomendado

1. Ejecutar los tests desde una copia limpia.
2. Ejecutar el modo interactivo:

```bash
"$PY" bip39_seed_report.py -i -n testnet
```

3. Utilizar exclusivamente material ficticio.
4. Revisar el resumen del reporte.
5. Comprobar el descifrado del archivo realmente escrito.
6. Registrar versión, hashes y resultados, sin secrets.
7. Conservar el archivo original cifrado mientras se verifica la prueba.

Eliminar archivos no garantiza borrado irrecuperable. No mezclar
pruebas con material de recuperación real.

## Salida del script

La vista predeterminada es compacta. Muestra el modo de entrada, la red,
las rutas, las claves públicas extendidas de cuenta disponibles y
la primera dirección de recepción de cada sección. No muestra claves
privadas, seeds, entropía, la clave pública extendida raíz ni el detalle
GAP. Las direcciones y claves públicas extendidas pueden facilitar
correlación entre direcciones.

En el recorrido BIP39, también muestra el estado de validación,
el número de palabras y si se utilizó passphrase. En BIP32 directo
identifica la entrada como seed hexadecimal directa y no presenta
una mnemonic o passphrase BIP39 como si se hubieran utilizado.

`--show-all` revela secretos y detalles de la vista BIP39 en la terminal,
pero conserva una sola dirección de recepción por sección; no imprime
todo el reporte privado. En BIP32 directo, la salida de terminal mantiene
el resumen compacto incluso si se solicita `--show-all`. Utiliza
exclusivamente material ficticio para probar la revelación en terminal.

El reporte privado conserva las diez direcciones de recepción y las
diez de cambio de cada sección, las claves privadas correspondientes
y las claves extendidas privadas y públicas de `m` y `m/0'`, con sus
rutas y red identificadas. El contenido se exporta cifrado tanto
si el formato interno es JSON como si es TXT.

El contexto privado incluye `report_notices`, con `version`, `general`,
`input` y `privacy`. Ese versionado informativo no cambia la versión
del contenedor cifrado. Los avisos y el detalle GAP se conservan
en el reporte; GAP expresa cantidad de direcciones derivadas por cadena,
no descubrimiento de actividad.

Las verificaciones de wordlist, errores, contraseñas y cancelaciones
siguen activas aunque se reduzcan los mensajes de éxito. Si se solicita
`--audit-passphrase` en un recorrido BIP39, los resultados se conservan
en el reporte y el resumen indica su inclusión. La entrada BIP32 directa
no admite opciones de passphrase BIP39.

### Pie de revisión

Después de guardar el reporte cifrado, el programa muestra un único
comando para abrir `inspeccionar_reporte_cifrado.py`.

El comando utiliza el intérprete que ejecutó el programa y las rutas
resueltas del inspector y del archivo final, incluidos los sufijos
secuenciales. No requiere ejecutar el inspector desde la raíz si se
utiliza el comando completo mostrado.

Incluye las expectativas de formato, red y modo de entrada.
En reportes BIP39 incluye además el número de palabras; en BIP32
directo omite `--words`, porque no se utilizó una mnemonic.

La contraseña de exportación se solicita al elegir una operación.
No se incorpora al comando ni se sustituye por la passphrase BIP39.

El pie no ejecuta automáticamente el inspector ni revela el reporte.
El menú del inspector ofrece las opciones `1` a `5`, con requisitos
y riesgos diferenciados en la sección de inspección. Las expectativas
de red, modo y palabras se contrastan mediante la opción `1` según
su alcance; abrir el contenido con otra opción no sustituye esa
verificación.

## Seguridad operacional

Trabajar sin red reduce vías de exposición, pero no prueba que el
equipo, el intérprete o las dependencias sean confiables.

Una máquina virtual, un sistema Live USB o un firewall no certifican
por sí solos ausencia de malware, capturas o persistencia de secretos.

No usar material real en estas pruebas. No copiar secrets automáticamente,
no publicar exports y no tratar limpiar pantalla o borrar archivos como
borrado seguro.

Las direcciones y extended public keys no son claves privadas,
pero pueden facilitar correlación. Trátalas con cautela.

## Revisar un reporte cifrado

Utiliza preferentemente el comando completo que se muestra después de
generar el reporte. Cuando el inspector pida la contraseña, introduce
la de exportación, no la passphrase BIP39. No la incluyas en el comando.

También puedes abrir el inspector indicando el archivo final:

```bash
"$PY" inspeccionar_reporte_cifrado.py "output/bip39_seed_report.json"
```

Usa el mismo intérprete del proyecto y ajusta la ruta al archivo que
realmente se creó, incluidos los sufijos secuenciales. La extensión
exterior no sustituye la comprobación del formato interno.

### Requisitos

- El inspector está limitado a Linux. Requiere una terminal interactiva
  para la entrada y la salida, el archivo `inspeccionar_reporte_cifrado.py`
  junto a `bip39_seed_report.py` y las dependencias del proyecto
  disponibles en el intérprete elegido.
- Opciones `1` y `3`: no requieren GNOME Terminal, Tk ni un editor externo.
- Opción `2`: requiere una sesión gráfica, GNOME Terminal y `gsettings`.
  Debe existir un único perfil con nombre visible `BIP39-revision`,
  con `exit-action` en `close` y `use-custom-command` desactivado.
- Opción `4`: requiere una sesión gráfica y `tkinter` disponible en el
  mismo intérprete que ejecuta el inspector. Es un requisito opcional,
  exclusivo del visor integrado.
- Opción `5`: requiere una sesión gráfica, `xdg-open` y una aplicación
  local asociada a archivos de texto `.txt`. No requiere Tk ni GNOME
  Terminal. No instala ni selecciona un editor concreto.

Para comprobar si el intérprete puede abrir el visor integrado, ejecuta
lo siguiente desde una terminal de tu escritorio y cierra la ventana
de demostración. El comando no abre ningún reporte:

```bash
"$PY" -m tkinter
```

Si falta `tkinter` y usas el Python de la distribución en Linux Mint 21.3
o Ubuntu 22.04, el paquete del sistema es `python3-tk`:

```bash
sudo apt install python3-tk
```

Después de instalarlo, repite la prueba con el mismo intérprete. Si usas
un Python de otra procedencia, comprueba cómo proporciona Tk esa
instalación. Si Tk se importa pero la demostración no abre, comprueba
que estás en una sesión gráfica local antes de repetir la instalación.

Para la opción `5`, puedes consultar la asociación de texto del
escritorio sin abrir un reporte, si `xdg-mime` está disponible:

```bash
command -v xdg-open
xdg-mime query default text/plain
```

La aplicación depende de la asociación del escritorio: puede ser un
editor u otra aplicación. En el ensayo en Linux Mint se abrió Xed;
Xed no es un requisito del inspector. No uses esta opción si no confías
en la aplicación asociada o en el equipo.

### Menú y finalización

| Selección o situación | Comportamiento |
|---|---|
| `1`: verificar sin mostrar contenido privado | Muestra el resultado de la comprobación y vuelve al menú. |
| `2`: revisar en ventana temporal | Abre una ventana de GNOME Terminal. Si la revisión termina con código `0`, finaliza el inspector principal. Si la apertura o revisión no se completa, no revela el reporte automáticamente en la terminal original. |
| `3`: revelar en esta terminal | Pide confirmación antes de solicitar la contraseña. Si la revelación se completa, finaliza el inspector; si se rechaza, vuelve al menú. |
| `4`: visor gráfico de solo lectura | Pide confirmación en una ventana gráfica. Si aceptas, introduce la contraseña en la terminal. Al cerrar el visor después de una apertura correcta, finaliza el inspector. Si rechazas la confirmación, vuelve al menú sin pedir contraseña. |
| `5`: abrir en editor externo — ADVERTENCIA: crea una copia temporal sin cifrar | Advierte del riesgo y pide escribir `s` para continuar. Si se rechaza la confirmación o vence su plazo, vuelve al menú sin descifrar. Tras la revisión, cierra el documento externo y pulsa Enter cuando lo indique la terminal para retirar el temporal y finalizar. |
| Error de autenticación en el menú | Muestra el error y vuelve al menú sin revelar el reporte ni abrir una alternativa automática. |
| `Q` | Termina con código `0`. |
| Ctrl+C o fin de entrada (EOF) | Cancela la inspección con código `1`. |
| Plazo de selección agotado | Termina con código `1` sin iniciar otra operación. |

El menú ofrece hasta 360 segundos para seleccionar una opción y pulsar
Enter. Una opción inválida inicia otra solicitud. La confirmación de
la opción `5` tiene su propio plazo de 360 segundos. Estos plazos no
son un límite global y no limitan la contraseña ni el tiempo de lectura.

En la ventana de GNOME Terminal de la opción `2`, pulsa Enter para
terminar la revisión. Con el perfil requerido, la ventana se cierra
al finalizar. Un código `0` de la ventana no equivale a una verificación
independiente del reporte.

### Alcance de la opción 1

En JSON, comprueba la estructura de las cinco secciones de derivación,
incluidas las cantidades, los índices y las rutas de recepción y
cambio. Comprueba también la coherencia de las claves extendidas BIP32
con la seed declarada. El parser rechaza claves JSON duplicadas y
constantes no estándar como `NaN` e infinitos.

- En un reporte BIP39, comprueba la frase, la entropía y su checksum.
  Contrasta la seed BIP39 con la frase cuando `passphrase_used` es falso.
  Si se usó una passphrase BIP39 no vacía, no la solicita ni contrasta
  la seed con ella; indica esa limitación.
- En un JSON de BIP32 directo, comprueba la estructura correspondiente
  y la coherencia de las claves extendidas con la seed BIP32 declarada.
  `--words` no aplica a esta entrada.
- En TXT, comprueba la autenticación, la cabecera y la red. Si se pide
  expresamente `--input-mode bip32_seed_hex`, también exige que la
  etiqueta de modo del TXT coincida y rechaza `--words` para ese modo.
  No reconstruye la seed ni verifica las derivaciones del TXT.

Las expectativas de red, modo y número de palabras se aplican según
el formato y el modo de entrada. Estos controles no constituyen una
verificación criptográfica independiente de todas las direcciones o
claves. Un error de estructura posterior al descifrado no significa
que la contraseña sea incorrecta.

Las opciones `2`, `3`, `4` y `5` son vías de lectura, no sustitutos de
la opción `1`. El inspector autentica y descifra el reporte para
mostrarlo y reconoce el formato interno, pero esas vías no ejecutan
las comprobaciones de coherencia de la opción `1`. Para contrastar
`--network`, `--input-mode` o `--words` cuando corresponda, selecciona `1`.

### Exposición del contenido

Las opciones `1` a `4` no crean deliberadamente un archivo descifrado.
Esto no excluye capturas, registros externos, memoria de intercambio
ni otras formas de persistencia introducidas por el sistema.

La opción `2` muestra el reporte en otra terminal y la opción `3`
lo imprime en la terminal actual. El contenido puede quedar en el
historial visible de desplazamiento de la terminal (*scrollback*).
Cerrar la ventana no garantiza borrado seguro.

Para leer sin que el inspector escriba una copia descifrada, usa
la opción `4`. El visor integrado permite buscar y desplazarse por
el reporte, no permite editarlo y no ofrece una función de guardado.
No protege contra capturas de pantalla ni garantiza el borrado de
memoria al cerrar.

### Opción 5: editor externo y copia temporal sin cifrar

Abrir directamente el archivo cifrado en un editor solo muestra el
contenedor, no el reporte legible. La opción `5` descifra el reporte
después de una confirmación explícita, escribe una copia temporal
`reporte.txt` y la entrega a la aplicación asociada a archivos de
texto. Usa esa extensión tanto para contenido JSON como TXT sin
convertir el contenido. El original cifrado no se modifica.

El temporal se crea en un directorio privado y con permisos de archivo
`0600` en Linux. Aun así, la aplicación externa puede permitir copiar,
editar o guardar el reporte y puede conservar copias mediante el
guardado automático, las copias de respaldo o la restauración de
sesiones. También puede conservar la ruta en su lista de archivos
recientes. Usa esta vía solo con datos ficticios de laboratorio y en
una sesión local de confianza. No publiques ninguna copia descifrada.

Cuando termines, cierra el documento en la aplicación externa y pulsa
Enter en la terminal cuando se te indique. El inspector intenta
retirar su copia temporal; no elimina las copias que la aplicación
pueda haber creado. Una terminación forzada puede dejar el temporal
en el equipo. Si el inspector avisa que no pudo retirarlo, revisa la
ruta local indicada. Que una entrada reciente ya no se pueda abrir
no demuestra que se hayan eliminado otras copias ni que se haya
producido un borrado seguro.

`inspeccionar_reporte_cifrado.py` forma parte de la distribución.
Otros auxiliares locales no se consideran distribuidos salvo que
estén versionados expresamente.

## Estado y trabajo pendiente

### Estado local de la revisión de noviembre 19

La corrida `output/bateria_local_lcqnkkq3` completó 26 etapas y
411 métodos unittest, con código `0`, inventario del núcleo alcanzado
80/80 y 50 archivos protegidos conservados. Identifica el núcleo
`bcae133d9d57c1e6923ef13e069d308e7f1773bb384f43d439796d8cc5d01787`.
Las ediciones documentales posteriores no se incorporan retrospectivamente
a sus manifiestos.

La revisión incorpora recepción y cambio, diez direcciones por cadena,
la sección legacy BIP32, las claves extendidas privadas y públicas
de raíz y cuenta legacy en el reporte privado y la entrada BIP32 directa.
El inspector dispone de cinco opciones, incluido el visor integrado
y la apertura externa con advertencia de copia temporal sin cifrar.

Los ensayos manuales de lectura TXT/JSON y del editor Xed se registran
separadamente. No modifican el campo `manual_terminal_tests` del resumen
automático ni acreditan una repetición de todos los manuales históricos.

Después de esa corrida se actualizó el pie de ayuda para anunciar
las cinco opciones del inspector y advertir de la copia temporal
sin cifrar de la opción `5`. La regresión posterior
`output/bateria_local_t2c17zkm` completó 26 etapas y 412 métodos unittest,
con código `0`, inventario 80/80 y 50 archivos protegidos conservados.
Su núcleo tiene SHA-256
`b31741cc898b86394c2e103effe25db14bff4f54361f31928e19387688283fcd`.

Después se añadió una prueba con cinco subcasos de errores y cancelación
del editor externo. La suite aislada del inspector pasó de 65 a
66 métodos y terminó con `OK`, sin modificar el inspector ni el núcleo.
Ese método adicional todavía debe incorporarse a una corrida completa
posterior; no se añade retrospectivamente a los 412 métodos registrados.

Antes de publicar quedan por completar la regresión posterior al refuerzo,
la comprobación de identidades y la selección final de archivos.
La distribución se preparará para subida mediante la página web de
GitHub, sin incluir reportes, entornos, compilados ni registros privados.

### Resultados históricos conservados

La lista siguiente reúne hitos de revisiones anteriores. Sus recuentos,
menús y referencias a plataformas pertenecen a los ensayos que describen;
no sustituyen el estado local ni las instrucciones actuales.

Implementado y probado en los ensayos registrados:

- Generación sin filtro de palabras repetidas.
- Indicadores sin score criptográfico.
- Verificación de wordlist embebida y efectiva.
- Entrada oculta con TTY y rechazo de GetPassWarning.
- Confirmación NFKD de passphrase y cancelación inicial.
- Exportación nueva con scrypt y AES-256-GCM.
- Compatibilidad de descifrado histórico.
- Permiso explícito para secretos CLI.
- Suite BIP39 y pruebas de cifrado y entrada segura.
- Validación estricta del contenedor versión 1: estructura, tipos, claves duplicadas, base64 y límites de tamaño.
- Suite del contenedor con rechazos anteriores a la KDF, casos positivos y compatibilidad histórica.
- Publicación mediante enlaces duros sin reemplazar destinos existentes,
  con reintentos secuenciales y cifrado único por export.
- Suite de escritura: 15 métodos aprobados en el ensayo Linux comunicado.
- Ensayo Windows 10 Home x64: 10 métodos de escritura aprobados y
  5 omitidos, con verificaciones manuales de exports.
- Auxiliar manual de laboratorio para autenticar y comprobar reportes
  sin imprimir el contenido privado.
- Runner BIP39 con validación estructural, rechazo de suites vacías
  y manejo de errores previstos desde la CLI.
- Suite de regresión del runner y última palabra: nueve métodos correctos
  en el ensayo Linux del 24 de octubre de 2026, tras corregir la captura
  de salida y añadir una prueba de mutación. El ensayo anterior,
  del 23 de octubre, registró ocho métodos.
- Mensaje de recuperación que distingue valores del checksum
  y cantidad de candidatos.
- UX compacta por defecto y revelación explícita de la vista con --show-all.
- report_notices en el contexto privado y avisos conservados en JSON/TXT.
- Pie con comandos escapados y ruta final, sin contraseña o passphrase privada en argv.
- Suites UX (18) e integral complementaria (28), y ejecutor local secuencial.
- Baterías Linux del 31 de octubre y 2 de noviembre de 2026:
  ocho etapas correctas, sin omisiones; inventario 70/70 y 11 archivos
  protegidos sin cambios. El inventario no implica cobertura completa.
- Inspector distribuido con verificación, ventana temporal y revelación
  confirmada en terminal.
- Menú con plazo de selección de 360 segundos y salida después de
  completar las opciones 2 o 3.
- Suite del inspector de 42 métodos, incluidos rechazos de duplicados,
  constantes JSON no estándar y tipos incorrectos.
- Hito histórico del 5 de noviembre: suite del ejecutor de 20 métodos,
  décima etapa, 14 archivos protegidos e inventario del núcleo 70/70.
- Integración local del 10 de noviembre: generación redundante experimental,
  `current` explícito y metadatos de adquisición en JSON/TXT.
- Batería corregida de 25 etapas y 362 métodos, ejecutor de 33, inventario
  73/73 y 49 archivos conservados, incluidos los tres `.cjs` encontrados.
- Inventario posterior de runtimes y configuración, separado del
  entorno.json y del manifiesto originales.
- Otra copia comprobada con venv nuevo, paquetes Python reinstalados,
  Java recompilado y runtimes base reutilizados: batería de 25 etapas,
  362 métodos, 73/73 y 49 entradas conservadas.
- Tres casos manuales adicionales en testnet, incluida confirmación
  visual de la ventana temporal; límites y códigos capturados descritos
  en el informe de la copia.
- Nueve ensayos manuales del inspector comunicados el 4 de noviembre
  de 2026, separados de la evidencia automática.
- Lectura acotada de archivos cifrados en el inspector y en el verificador
  de laboratorio, con rechazo del exceso antes de solicitar contraseña.

### Pendientes y límites no resueltos

- Ensayar expresamente la ausencia de Java y de Node en los flujos
  correspondientes. Preparar todos los proveedores y superar la batería
  no acredita esos escenarios.
- Completar el cierre del lote actual y registrar una nueva regresión
  después de los cambios pendientes del núcleo o de archivos protegidos.
- Completar y comprobar la instalación de runtimes Java/Node desde cero
  en otro entorno; conservar el inventario ya realizado y registrar
  versiones e identidades nuevas para cada instalación distinta.
- Instalación completa sin reutilizar los runtimes base, auditoría del
  combinador y ampliación de pruebas de modos degradados, longitudes y flujos.
- Recuperación offline con un reporte anterior trasladado a otro equipo;
  la copia ensayada generó y verificó reportes nuevos en el mismo equipo.
- Durabilidad del directorio y ampliación de pruebas por plataforma
  y sistema de archivos.
- Perfiles de recuperación, auditoría y laboratorio.
- Revelación granular de secrets.
- Vectores independientes de BIP32 y todas las derivaciones.
- Bloqueo transitivo, hashes de artefactos y ampliación de la matriz de entornos y flujos probados.

La lectura acotada de los auxiliares distribuidos no garantiza el
comportamiento de consumidores externos que carguen el archivo por
su cuenta antes de llamar a la API de descifrado.

Windows y macOS quedan fuera del alcance activo. La revisión se difiere
a quien los utilice; los límites y resultados históricos se conservan
en ANALISIS_COMPATIBILIDAD_SO.md y no bloquean este hito Linux.

Estos resultados no constituyen una auditoría independiente ni
una certificación para custodiar fondos.

## Advertencias finales

La validación BIP39 confirma formato y checksum, no imprevisibilidad.

Los indicadores son descriptivos y no clasifican la seguridad
criptográfica de una mnemonic.

La ejecución offline no garantiza seguridad del entorno.

El proyecto permanece educativo y no ha sido auditado de forma independiente para custodia o producción.
La decisión de uso corresponde al usuario. El proyecto no presenta sus resultados ni sus pruebas como una certificación de seguridad para custodiar fondos.

## Licencia

El código original del proyecto se distribuye bajo la licencia MIT.
Consulta el archivo LICENSE.

MIT permite uso, modificación y redistribución, incluido uso comercial,
si se conservan los avisos y condiciones de la licencia.

El material de terceros conserva sus licencias y avisos correspondientes.

Consulta [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) para el inventario
de material externo, los avisos conservados y las verificaciones de
procedencia que todavía están pendientes.

La licencia no constituye una auditoría ni una garantía de seguridad.
El proyecto permanece educativo y no ha sido auditado de forma independiente
para custodia o producción. La decisión de uso corresponde al usuario;
la licencia no certifica seguridad para custodiar fondos.

Consulta [LICENSE](LICENSE).

## Auditoría y contribuciones

Se aceptan revisiones de código, issues y pull requests con propuestas
de corrección y mejora.

Antes de proponer un cambio:

- Utiliza exclusivamente datos ficticios.
- No publiques mnemonic, passphrase, seed, WIF o exports privados.
- Explica el cambio y su impacto.
- Conserva las funciones existentes o justifica cualquier cambio de contrato.
- Ejecuta las pruebas del área afectada y las suites de regresión.
- Documenta el entorno y el commit de referencia.

Las propuestas se revisan antes de integrarlas.

## Contacto

**Para reportar errores o sugerencias, usa issues en el repositorio.**
No publiques mnemonics, passphrases, seeds ni exports en issues
