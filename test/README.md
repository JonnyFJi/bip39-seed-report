# Pruebas de BIP39 Seed Report

## Resultado comprobado — integración entropy CLI, 10 de noviembre de 2026

La batería local `bateria_local_8jy797o3` terminó satisfactoriamente
en el entorno Linux comunicado:

- 25 etapas planificadas y completadas.
- 362 métodos unittest registrados.
- Suite del ejecutor de 33 métodos.
- Sin fallos, errores, omisiones, fallos esperados ni éxitos inesperados.
- Inventario del núcleo alcanzado: 73/73.
- 49 archivos protegidos, con hashes y conjunto conservados.
- Código final 0.

El manifiesto incluye los auxiliares
`entropy_helpers/node_entropy_probe.cjs`,
`entropy_helpers/webcrypto_provider.cjs`
y la prueba `test/js/test_webcrypto_provider.cjs`.

SHA-256 del núcleo ensayado:

```text
b29675e5d91f52fd6c109a777b820945c01c12ef88e6f9926f61cc6e204e20d6
```

El desglose, identidades, incidencias y límites se conservan en
[RESULTADOS_ENTROPY_CLI_2026-11-10.md](RESULTADOS_ENTROPY_CLI_2026-11-10.md).

Los seis ensayos manuales se registran por separado.
`manual_terminal_tests` permanece pendiente en el resumen automático
por diseño; no se reescriben los artefactos de la batería.

La batería anterior `bateria_local_082q7ze7` conserva su resultado
de 360 métodos y 46 archivos. No se le atribuye retrospectivamente
la protección de los archivos `.cjs`.

Las secciones de preparación y los registros históricos siguientes
conservan su contexto. Este resultado no demuestra cobertura completa
de ramas, independencia entre proveedores, instalación desde cero
ni verificación independiente de todas las derivaciones.

## Resultado comprobado — otra copia Linux, 10 de noviembre de 2026

La batería proyecto/output/bateria_local_zelv2gy3 terminó con
25 etapas, 362 métodos unittest, inventario del núcleo 73/73,
49 entradas del manifiesto conservadas y código final 0.
No hubo fallos, errores, omisiones, fallos esperados, éxitos inesperados
o errores de registro; ninguna etapa quedó incompleta.

La suite individual del ejecutor terminó con 33 métodos y código 0.
Esos métodos ya están incluidos en el acumulado de la batería.
Las dos baterías de 362 métodos son ejecuciones distintas, no
724 métodos diferentes.

### Preparación y alcance

- Se copiaron y verificaron 64 archivos seleccionados en un laboratorio
  separado del proyecto de referencia.
- Se creó un venv nuevo y se instalaron de nuevo las dependencias Python.
- La copia registró pip 22.0.2; el entorno original registró pip 26.3.
  No se igualan retrospectivamente.
- Se recompilaron las dos fuentes Java con código 0, utilizando los
  runtimes base existentes del mismo equipo.
- Los hashes de las clases se registraron antes de la batería.
  Las clases no forman parte del manifiesto de 49 archivos y no se
  comunicó una nueva comprobación de sus hashes después de todos los ensayos.
- Antes de los manuales se comprobaron 71 archivos registrados del origen
  sin cambios y sin ausencias. No se presenta como una comprobación
  posterior a esos manuales ni de todo el sistema.

Los 64 archivos copiados, las 49 entradas protegidas y los 71 archivos
comprobados del origen son conjuntos distintos.

### Tres casos manuales posteriores

| Caso | Resultado registrado | Límite |
|---|---|---|
| Redundante, 12 palabras, testnet | Cuatro proveedores aceptados y utilizados; generación y verificador con código 0 | No demuestra independencia ni imprevisibilidad |
| Current explícito, 12 palabras, testnet | Solo python_os; otros tres no intentados; reporte creado y verificador con mensaje OK | No se capturaron códigos separados de generación y verificación |
| Interactivo, 24 palabras, testnet, passphrase BIP39 vacía | Cuatro proveedores utilizados; verificación satisfactoria e inspector con código 0 | No verifica independientemente todas las direcciones |

El mantenedor confirmó visualmente que la ventana temporal del tercer
caso se abrió, mostró el reporte y se cerró al pulsar Enter.
No se declara borrado seguro ni repetición de todos los timeouts,
cancelaciones o errores del menú.

Los tres casos nuevos no sustituyen los seis manuales originales.
manual_terminal_tests conserva su estado original en los resúmenes;
no se reescriben los artefactos para incorporar aprobaciones manuales.

Esta comprobación utilizó reportes nuevos y runtimes existentes
del mismo equipo. No acredita instalación completa desde cero,
recuperación offline de un reporte antiguo trasladado a otro equipo
ni soporte nuevo Windows/macOS.

Detalle:
[RESULTADOS_COPIA_ENTROPY_2026-11-10.md](RESULTADOS_COPIA_ENTROPY_2026-11-10.md).

Las ediciones documentales posteriores cambian la identidad de los
documentos editados, incluido este README protegido por el ejecutor.
No se actualizan por ello los manifiestos históricos ni se presenta
la conservación registrada durante una batería como una comprobación
del árbol actual después de esas ediciones.

## Batería integrada de entropy CLI — configuración e instrucciones

Esta sección describe la configuración de la integración ensayada y
las instrucciones para una nueva ejecución. Los resultados originales
y de la copia posterior están registrados arriba; no se atribuyen
automáticamente a otro árbol, equipo o entorno.

### Preparación antes de ejecutar

Utilizar una copia local de confianza, con dependencias Python,
configuración de proveedores, auxiliares y runtimes preparados.
Instalar requirements.txt no instala Java o Node ni compila Java.

Antes de la batería, comprobar las rutas efectivas y compilar las
fuentes Java en el classpath de esa copia. La configuración ensayada
exige build/entropy_java/JavaEntropyProvider.class. No recompilar clases
históricas ni modificar proveedores para cerrar esta revisión documental.

El proveedor Web Crypto ensayado exige Node v24.22.2, OpenSSL 3.5.9,
Linux x64, execArgv vacío y getFips() igual a 0, además de su protocolo
de pipes. Son condiciones de esa implementación, no una recomendación
universal de versiones ni una certificación. Otro runtime puede ser
rechazado aunque disponga de Web Crypto.

La preparación completa se describe en la
[guía Linux](../docs/INSTALACION_LINUX.md#preparación-adicional-de-runtimes-para-entropy)
y sus identidades observadas en el
[inventario de runtimes](../docs/RUNTIMES_ENTROPY_LINUX_2026-11-10.md).
Las rutas Linux no constituyen una preparación Windows/macOS.

Desde la raíz del proyecto, ejecutar las líneas siguientes por separado.
Detenerse si una falla; la ejecución posterior no corrige un fallo previo:

```bash
PY="$PWD/.venv-regresion-entropy-cli/bin/python"
"$PY" --version
"$PY" -m pip check
PYTHONPATH="$PWD" "$PY" -B test/test_ejecutar_bateria_local.py
"$PY" -B test/ejecutar_bateria_local.py
```

El nombre del venv del ejemplo corresponde al entorno original.
En otra copia, definir PY con el intérprete realmente preparado y
mantenerlo durante la comprobación; no mezclar resultados de entornos.

La suite del ejecutor conserva los 20 métodos anteriores y agrega 13:
total 33. Son pruebas del protocolo y configuración, con fixtures;
no una ejecución completa de todos los proveedores reales.

### Etapas

Se conservan las diez etapas anteriores y se agregan quince etapas, una
por cada archivo test_entropy_*.py registrado: total 25. Cada etapa nueva
exige un registro unittest no vacio. El inventario de nombres se contrasta
antes de iniciar: un archivo esperado ausente o una suite entropy nueva
no registrada detienen la preparacion con codigo 3. No hay descubrimiento
silencioso de suites ni se fija un contador global de metodos.

### Identidad e inventario

El nucleo esperado conserva SHA-256:

```text
b29675e5d91f52fd6c109a777b820945c01c12ef88e6f9926f61cc6e204e20d6
```

El checksum local debe identificar esa misma version. Esta actualizacion
no modifica bip39_seed_report.py ni sus proveedores.
El inventario AST del núcleo revisado contiene 72 funciones superiores
y un método: 73 entradas. Las baterías original corregida y posterior
de la copia registraron 73/73. Una nueva ejecución debe conservar
su propio resultado; no hereda ese alcance por usar el mismo código.
No es cobertura de líneas o ramas ni inventario de funciones de
todos los módulos de entropy.

### Manifiesto

PROTECTED_FILES define entradas obligatorias, entre ellas el ejecutor,
su suite, este README, entropy_cli_support.py y los auxiliares
entropy_helpers/node_entropy_probe.cjs y
entropy_helpers/webcrypto_provider.cjs.

Se agregan los objetivos de todas las etapas y los archivos .py, .java,
.js, .cjs y .mjs encontrados en el arbol visible del proyecto. Se excluyen directorios ocultos y los llamados
output, backups, node_modules, __pycache__, venv y env.
Los enlaces simbolicos encontrados dentro del arbol seleccionado se
rechazan. El conteo es dinamico y se registra en protected_files_total.
Se comprueban hashes y conservacion del conjunto de archivos seleccionado.

Este manifiesto identifica fuentes seleccionadas durante una ejecucion;
no verifica su procedencia. No incluye automaticamente binarios de Java,
Node o Python, .class, dependencias de entornos, fuentes ocultas ni todos
los archivos documentales. Los ejecutables y artefactos de runtimes siguen
fuera de esta politica. Revisar hashes_antes.json para conocer el alcance
real. No confundir este manifiesto con el cierre de toda la cadena de suministro.

### Resultados y limites

Los codigos finales conservan su significado: 0 automatico completo,
1 fallo, 2 incompleto y 3 preparacion. Las omisiones o fallos esperados
no equivalen a una aprobacion completa. El resumen agrega stages_planned,
protected_files_total y protected_file_set_unchanged.

La lectura del registro del worker esta limitada; la captura de stdout
y stderr no tiene un limite de volumen incorporado. El timeout de 900
segundos es por etapa, no un plazo global ni una garantia de limpieza
de todos los descendientes.

manual_terminal_tests permanece pendiente en el resumen automatico por
diseno. Los seis casos manuales comunicados el 10 de noviembre se registran
por separado: redundante JSON, current JSON, importaciones hexadecimal,
binaria y mnemonic completa JSON, y redundante TXT.
En TXT hubo un error del verificador auxiliar de cabecera/espaciado,
corregido sobre el mismo reporte. El inspector TXT verifica autenticacion,
cabecera y red; la comprobacion adicional revisa texto registrado, sin
recalcular BIP39, seed o derivaciones.

La ejecucion previa de 349 metodos se conserva como evidencia anterior;
no se atribuye automaticamente a este ejecutor modificado. La nueva suite
cambia el numero de metodos: registrar el resultado real, no reutilizar 349.
No se certifica independencia entre interfaces de proveedores, imprevisibilidad
de muestras, seguridad del host ni todas las derivaciones. Linux es el
alcance activo; Windows/macOS no se validan mediante esta actualizacion.

### Correccion del manifiesto JavaScript — 10 de noviembre de 2026

La bateria bateria_local_082q7ze7 termino con 25 etapas satisfactorias,
360 metodos unittest, inventario del nucleo 73/73, 46 archivos protegidos
sin cambios y codigo final 0.

La revision posterior del manifiesto identifico que no incluia los
auxiliares node_entropy_probe.cjs y webcrypto_provider.cjs, porque la
seleccion de fuentes JavaScript solo contemplaba .js.

Se incorporan ambos auxiliares como archivos obligatorios y se amplian
las extensiones seleccionadas a .js, .cjs y .mjs. Se agregan dos pruebas
de regresion; la suite del ejecutor pasa de 31 a 33 metodos.

La batería anterior conserva su alcance original. La corrección requirió
una nueva ejecución, realizada después como bateria_local_8jy797o3:
25 etapas, 362 métodos, inventario 73/73, 49 archivos conservados
y código final 0.

No se modifican los manifiestos de bateria_local_082q7ze7 ni se le
atribuye retrospectivamente la protección de los auxiliares omitidos.
El resultado posterior tampoco convierte los 46 archivos anteriores
en un manifiesto de 49.

## Documentacion y registros anteriores — conservar como referencia historica

Los apartados siguientes conservan sus conteos y contexto históricos.
Las menciones a diez etapas, catorce archivos, veinte métodos del ejecutor
y 70/70 corresponden a configuraciones anteriores, no a la integración
de 25 etapas descrita arriba.

Las expresiones «actual» o «nueva» dentro de esos registros se refieren
al hito que describían, no al estado más reciente de esta actualización.
Para ejecutar la batería integrada, utilizar la preparación y las
instrucciones superiores; no interpretar los conteos históricos como
expectativas de la revisión nueva.


Las suites utilizan exclusivamente datos ficticios o vectores públicos.
No introducir mnemonics, passphrases ni claves de usuario.

La verificación de esta etapa se realiza en Linux. Windows/macOS quedan
diferidos a quien ejecute el proyecto allí, sin bloquear este hito.
Los registros históricos se conservan y no prueban la versión actual.

## Ejecución en Linux

Ejecutar desde la raíz del proyecto, no desde la carpeta test.

Los comandos siguientes suponen que existe un entorno virtual local
en .venv-verificacion con las dependencias de requirements.txt instaladas.

```bash
PY="$PWD/.venv-verificacion/bin/python"
"$PY" --version
"$PY" -m pip check
```

No reasignar PY al Python del sistema durante la misma verificación.
Si se cambia el intérprete, registrar sus resultados como otro entorno.

La batería utiliza sys.executable para sus procesos hijos.

Comprobar sintaxis y ejecutar las suites:

```bash
"$PY" -m py_compile bip39_seed_report.py
"$PY" -m py_compile test/test_contenedor_report.py
"$PY" -m py_compile test/test_escritura_report.py
"$PY" -m py_compile test/test_regresion_vectores_ultima_palabra.py
"$PY" -m py_compile test/test_ux_terminal_report.py
"$PY" -m py_compile test/test_revision_integral_report.py
"$PY" -m py_compile test/ejecutar_bateria_local.py
"$PY" -m py_compile inspeccionar_reporte_cifrado.py
"$PY" -m py_compile test/test_inspeccionar_reporte_cifrado.py
"$PY" -m py_compile test/test_ejecutar_bateria_local.py

"$PY" bip39_seed_report.py --run-tests --vectors-file test/vectors.json

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

Ejecutar los comandos por separado. Si uno falla, revisar el error antes
de continuar; no interpretar la ejecución de las suites posteriores
como corrección del fallo anterior.

Las rutas entre comillas permiten utilizar carpetas con espacios.

Estos comandos se han utilizado en el entorno Linux comunicado.
También existen ensayos Windows, descritos en
[ANALISIS_COMPATIBILIDAD_SO.md](../ANALISIS_COMPATIBILIDAD_SO.md).

Los resultados no se generalizan a otras versiones o plataformas.
macOS permanece pendiente.

## Batería local secuencial

Con el entorno preparado:

```bash
"$PY" test/ejecutar_bateria_local.py
echo $?
```

El ejecutor comprueba la identidad de la versión, sintaxis,
importaciones, pip check y diez etapas. Se detiene en el primer fallo
y guarda nuevos registros dentro de output/.

La novena etapa ejecuta test/test_inspeccionar_reporte_cifrado.py.
La décima ejecuta test/test_ejecutar_bateria_local.py.

El manifiesto actual protege 14 archivos únicos, incluidos el inspector,
su suite y la nueva suite del protocolo del ejecutor. No incluye el propio
test/ejecutar_bateria_local.py ni toda la documentación.

Los registros del worker son obligatorios y tienen límite de tamaño.
Se validan JSON, estructura, tipos, código registrado, inventario
y contadores unittest.

Un proceso que termina con código 0 no se aprueba si su registro
contiene fallos, errores o éxitos inesperados. Las suites vacías,
omisiones y fallos esperados producen un resultado incompleto.

Las etapas de vectores, cifrado y entrada segura se distinguen de las
etapas que deben registrar ejecuciones unittest.

El inventario se calcula sobre bip39_seed_report.py:
69 funciones superiores y un método de clase. Las funciones del inspector
y del ejecutor no forman parte del conteo 70/70.

Códigos finales:

- 0: etapas automáticas completas, sin fallos ni resultados incompletos,
  inventario alcanzado y hashes protegidos conservados.
- 1: fallo de proceso, registro rechazado, fallo/error/éxito inesperado
  unittest o modificación de archivos protegidos.
- 2: resultado incompleto por suites vacías, omisiones, fallos esperados,
  funciones no alcanzadas o etapas no completadas sin otro fallo prioritario.
- 3: problema de preparación.

El código 0 no aprueba automáticamente los ensayos manuales.
funciones.csv registra entradas a funciones, no cobertura completa
de líneas o ramas. Las simulaciones de Windows no son ensayos
en una consola Windows real.

## Suite del contenedor cifrado

test/test_contenedor_report.py contiene 18 métodos de prueba con
subcasos. Utiliza exclusivamente datos ficticios y no escribe reportes
en disco ni solicita contraseñas al usuario.

Comprueba:

- Rechazo de entradas que no sean texto y de JSON no admitido.
- Claves JSON duplicadas, incluidas claves anidadas.
- Constantes NaN e infinitos.
- Claves obligatorias ausentes y campos adicionales.
- Formato, versión, algoritmos y tipos de metadatos.
- Perfil scrypt admitido y rechazo de booleanos como parámetros.
- Base64 y longitudes de salt, nonce y ciphertext.
- Límites de tamaño y representación UTF-8.
- Rechazo de entradas inválidas antes de llamar a la KDF.
- Acceso a la KDF cuando la estructura es admisible.
- Cifrado y descifrado con scrypt real.
- Compatibilidad del formato histórico y su alias.

Algunas pruebas utilizan mocks y límites reducidos temporalmente para
comprobar las fronteras sin generar datos grandes. No modifican el
script guardado en disco. La prueba con scrypt real mantiene el perfil
configurado por el programa.

Resultado esperado:

```text
Ran 18 tests in ...
OK
```

### Resultado registrado

El 15 de octubre de 2026, el mantenedor comunicó dos ejecuciones
satisfactorias de la suite del contenedor en Linux con Python 3.10.12.
Ambas terminaron con 18 métodos correctos y código de salida 0.

SHA-256 del script correspondiente a ese ensayo:

```text
7e108699d9625054fbe2ba3750afa2b932f4b1903bda058a278c255bb23fc21a
```

Este hash identifica la versión ensayada; no certifica por sí solo
procedencia ni seguridad. Los resultados no se generalizan a otras
versiones o entornos.

## Regresión del runner BIP39 y última palabra

test/test_regresion_vectores_ultima_palabra.py contiene nueve métodos
de prueba con subcasos. Utiliza exclusivamente datos ficticios o públicos.

Comprueba:

- Rechazo de suites vacías, estructuras incorrectas y objetos
  sin el bloque english.
- Aceptación de vectores de tres y cuatro campos.
- Rechazo de campos, entropy hexadecimal y seed mal formados.
- Validación de toda la estructura antes de iniciar las conversiones.
- Rechazo de discrepancias en mnemonic, seed y round-trip,
  sin anunciar éxito.
- Detección, mediante una prueba de mutación controlada, de un runner
  ficticio que imprime éxito antes de lanzar una excepción.
- Errores de archivo inexistente, JSON inválido y UTF-8 inválido,
  además de un fallo de permisos simulado.
- Búsqueda real de candidatos para prefijos de 11 y 23 palabras,
  con comprobación de cantidad, ausencia de duplicados y validez.
- Mensajes que distinguen valores del checksum y cantidad de candidatos.
- Rechazo de cantidades de palabras no admitidas.

Los controles de estructura y fallos incluyen mocks. Los casos positivos
de vectores y la búsqueda de última palabra utilizan las dependencias
instaladas en el entorno.

El caso positivo de cuatro campos no verifica BIP32: deja explícito
que el cuarto campo no se comprueba como clave extendida.

La prueba 05 captura directamente la salida del runner. No utiliza
el auxiliar execute(), para evitar que una captura interior impida
comprobar el contenido del buffer exterior.

La prueba 09 ejecuta esa comprobación contra un runner ficticio que
imprime OK y después lanza AssertionError. Debe detectar tres fallos
internos, uno por cada subcaso de discrepancia de la prueba 05.

Esos fallos deliberados se recogen en un TestResult independiente.
El resultado correcto de la prueba 09 es confirmar su detección,
no aceptar ese comportamiento en el runner real.

La simulación no modifica el script guardado en disco.

### Resultado registrado — 23 de octubre de 2026

El mantenedor comunicó una ejecución local Linux con Python 3.10.12
y las dependencias directas mnemonic 0.21, bip-utils 2.9.3
y cryptography 44.0.3.

La suite terminó con ocho métodos correctos, sin omisiones,
y código de salida 0:

```text
Ran 8 tests in 0.381s

OK
```

SHA-256 del script correspondiente a ese ensayo:

```text
a0239df849b808f32ee097af7dc1052d3c899e1ceb8f27357b9c323795411538
```

También se comprobó por separado la CLI con una suite vacía.
El programa mostró el error controlado y terminó con código 1,
sin anunciar éxito con cero casos.

Ese código 1 es el resultado esperado de la prueba negativa.
No representa un fallo del ensayo.

Esta versión no cuenta aquí con una ejecución Windows registrada.

### Resultado registrado — 24 de octubre de 2026

El mantenedor comunicó una ejecución local Linux con Python 3.10.12,
utilizando el entorno .venv-verificacion.

La sintaxis del archivo de pruebas se comprobó correctamente.
La suite corregida terminó con nueve métodos correctos, sin omisiones
mostradas, y código de salida 0:

```text
Ran 9 tests in 0.570s

OK
```

Pasaron tanto test_05_mismatches_do_not_print_success como
test_09_detects_success_printed_before_failure.

La ejecución separada de los vectores distribuidos también terminó
correctamente:

```text
Test vectors BIP39: OK (24 casos)
```

Su código de salida fue 0.

La corrección afecta a la captura de salida de la prueba 05 y añade
la prueba 09. No modifica bip39_seed_report.py, su checksum
ni test/vectors.json.

SHA-256 del archivo de pruebas corregido revisado:

```text
d98f58e0d627e63d606eec9ebbe8d7fa1e5d5effbbc30b84cd7e2665274826dc
```

Este hash identifica el archivo de pruebas, no el script principal.

El resultado histórico de ocho métodos del 23 de octubre se conserva
como registro de ejecución. No demuestra por sí solo la eficacia
de la antigua aserción de captura, corregida en esta actualización.

En este ensayo no se comunicó una nueva ejecución de las suites
de cifrado, entrada segura, contenedor o escritura, ni un ensayo Windows
de la suite corregida.

## Suite de escritura

test/test_escritura_report.py contiene 15 métodos de prueba con datos
ficticios y carpetas temporales.

Comprueba:

- Escritura exacta y preservación de destinos existentes.
- Selección secuencial y cifrado único por export.
- Colisiones forzadas durante la publicación.
- Fallo sin alternativa insegura si no se admiten enlaces duros.
- Fallos de fsync y permisos POSIX.
- Enlaces simbólicos existentes y rotos.
- Concurrencia con hilos.
- Exportaciones multiproceso mediante fork en Linux.
- Límite de intentos, rutas con espacios y temporal completo
  antes de publicar.

Las pruebas de exportación simulan el cifrado para aislar la escritura.
No sustituyen las suites criptográficas ni la verificación manual de
exports reales.

### Ejecución

Linux, desde la raíz y con el intérprete preparado:

```bash
PYTHONPATH="$PWD" "$PY" test/test_escritura_report.py
```

Windows PowerShell, con $PY apuntando al intérprete local:

```powershell
$anterior = $env:PYTHONPATH
try {
    $env:PYTHONPATH = $PWD.Path
    & $PY .\test\test_escritura_report.py
}
finally {
    $env:PYTHONPATH = $anterior
}
```

Referencia histórica; revisión actual diferida y no bloqueante

### Resultados registrados

- Linux, Python 3.10.12: 15 métodos correctos, sin omisiones;
  código de salida 0.
- Windows 10 Home x64, 10.0.19045, Python 3.10.11:
  10 métodos aprobados y 5 omitidos; código de salida 0.

En Windows se omitieron:

- test_07_mode_0600: exclusivo POSIX.
- test_08_permission_failure_does_not_publish: exclusivo POSIX.
- test_09_existing_symlink_not_followed: no se pudo crear el symlink.
- test_10_broken_symlink_occupied: no se pudo crear el symlink.
- test_12_process_exports_unique: específico de Linux con fork.

Las omisiones no demuestran el comportamiento de esos casos en Windows.

SHA-256 de la versión de escritura ensayada:

```text
df80621c8a2f2adef15c370783319c88ba4593f31ed92c03c08a0d5248cc9d3f
```

## Suite UX

test/test_ux_terminal_report.py contiene 18 métodos con subcasos.
Comprueba privacidad de vistas, índice 0, GAP solo en reportes, conservación
de contexto y exports, avisos, comandos, orden de main, fallos de wordlist,
errores de publicación y round-trip cifrado JSON/TXT.

Usa fixtures ficticias y mocks de coordinación; no es verificación
independiente de todas las derivaciones. La prueba PowerShell construye
una cadena, no ejecuta una consola Windows real.

## Suite del inspector

test/test_inspeccionar_reporte_cifrado.py contiene 42 métodos.

Comprueba lectura limitada antes de solicitar contraseña, errores
controlados, alcance de verificación JSON/TXT, confirmación de revelación,
escape de caracteres de control, construcción del comando del visor,
validación del perfil GNOME y ausencia de revelación automática.

Incluye los estados de finalización del menú, timeout simulado,
retorno tras errores, rechazo de una lectura sin límite como fallback
y un round-trip con cifrado real sin crear un archivo descifrado.

Las pruebas 33 a 42 añaden rechazo de claves duplicadas en raíz y
objetos anidados, constantes JSON no estándar, tipos incorrectos,
direcciones que no sean texto no vacío y estructuras de familias
o direcciones no admitidas.

También comprueban que se acepten extensiones legítimas y que la
revelación rechace JSON duplicado antes de imprimir contenido privado.

Las pruebas del menú y del lanzador utilizan simulaciones. No abren
una ventana GNOME real ni esperan 360 segundos.

Resultado esperado:

```text
Ran 42 tests in ...
OK
```

Los ensayos reales de terminal y ventana se registran por separado en
[RESULTADOS_INSPECTOR_2026-11-04.md](RESULTADOS_INSPECTOR_2026-11-04.md).

El endurecimiento posterior y sus nuevas ejecuciones se registran en
[RESULTADOS_ENDURECIMIENTO_2026-11-05.md](RESULTADOS_ENDURECIMIENTO_2026-11-05.md).

## Suite del protocolo del ejecutor

test/test_ejecutar_bateria_local.py contiene 20 métodos.

Comprueba:

- Estructura y tipos de los registros del worker.
- Correspondencia entre código registrado y código del proceso.
- Inventario y contadores admitidos.
- Registros ausentes, ilegibles, demasiado grandes o JSON no válido.
- Claves duplicadas y constantes no estándar.
- Fallos y errores aunque el proceso termine con código 0.
- Éxitos inesperados.
- Suites vacías, omisiones y fallos esperados.
- Etapas que no utilizan unittest.
- Normalización de salidas booleanas a enteros.

Incluye programas ficticios ejecutados mediante el worker: fallo
capturado con salida 0, suite vacía, salidas booleanas y ejecución correcta.

Resultado esperado en una ejecución individual:

```text
Ran 20 tests in ...
OK
```

Su integración en la batería corresponde a 10_ejecutor.

La suite comprueba el protocolo y casos reales del worker; no equivale
a una prueba end-to-end de todas las rutas de main del coordinador.

## Suite complementaria

test/test_revision_integral_report.py contiene 28 métodos con subcasos.
Incluye entropy y BIP39, NFKD, primitivas maestras, estructura de familias,
entradas, recuperación, menús, utilidades de terminal, bloqueo CLI,
abortos, contexto, print_report y rutas de vectores.

No todos sus ensayos son de integración: algunos simulan TTY, decisiones
y msvcrt. No introduce red ni material real y no reemplaza las otras suites.

## Evidencia actual del endurecimiento — 5 de noviembre de 2026

La suite del inspector terminó con 42 métodos satisfactorios en las
dos ejecuciones individuales comunicadas.

La suite del protocolo del ejecutor contiene 20 métodos y se incorpora
como décima etapa. Las dos baterías comunicadas terminaron con diez
etapas OK, inventario del núcleo 70/70, archivos protegidos sin cambios
y código final 0.

El manifiesto actual define 14 archivos protegidos.

Los resultados automáticos y la verificación manual posterior de un
export testnet se registran por separado en
[RESULTADOS_ENDURECIMIENTO_2026-11-05.md](RESULTADOS_ENDURECIMIENTO_2026-11-05.md).

Los nueve ensayos manuales del menú del 4 de noviembre siguen siendo
evidencia histórica separada. No se declara una repetición completa
de esos nueve casos durante este nuevo hito.

manual_terminal_tests permanece PENDIENTES en el resumen automático
por diseño; los resultados manuales no se incorporan reescribiendo
los artefactos originales.

## Evidencia histórica del inspector — 4 de noviembre de 2026

La ejecución posterior al ajuste del menú terminó con nueve etapas
satisfactorias, inventario del núcleo 70/70, 13 archivos protegidos
sin cambios y código final 0.

La suite individual del inspector terminó con 32 métodos satisfactorios.

La evidencia automática y los nueve ensayos manuales se documentan
por separado en
[RESULTADOS_INSPECTOR_2026-11-04.md](RESULTADOS_INSPECTOR_2026-11-04.md).

El campo manual_terminal_tests del resumen automático permanece
PENDIENTES por diseño. No se modifica para incorporar aprobaciones manuales.

## Batería histórica Linux — 31 de octubre y 2 de noviembre de 2026

Versión del script ensayado: 97.076 bytes.

SHA-256:

```text
1f92a16c69c1566b9e228a9d7ca1d9cc3b066cad01ce0bc76be05b0fee88816f
```

Etapas satisfactorias: 24 vectores BIP39, cifrado, entrada segura,
18 métodos del contenedor, 15 de escritura, nueve de regresión,
18 de UX y 28 de la suite complementaria. Las cinco suites unittest
contabilizan 88 métodos; no sumar esos métodos a vectores y comprobaciones
como si fueran unidades homogéneas.

Se conservaron los hashes de los 11 archivos protegidos. El inventario
registró 70/70 entradas alcanzadas: 69 funciones superiores y un método
de clase. Esto no significa cobertura completa de líneas, ramas,
plataformas ni validez criptográfica independiente.

| Fecha del registro | Hora UTC de entorno.json | Suma de etapas externas | Resultado |
|---|---|---:|---|
| 31 de octubre de 2026 | 22:05:40 | 54,159 s | Ocho etapas, código 0, sin omisiones |
| 2 de noviembre de 2026 | 19:10:19 | 53,092 s | Ocho etapas, código 0, sin omisiones |

Son dos ejecuciones distintas sobre el mismo hash. La suma de etapas no
incluye toda la preparación; los tiempos internos de unittest no son
los mismos que la duración externa del proceso.

Los ensayos manuales comunicados el 31 de octubre incluyen compacto,
--show-all, TXT, passphrase no vacía y comandos de autenticación/revelación.
Se observaron autenticación del JSON visible y del TXT con el auxiliar,
y autenticación del JSON con passphrase no vacía mediante el comando
que no contrasta independientemente la seed. Los resultados no validan
retrospectivamente otros exports no comprobados.

manual_terminal_tests permanece PENDIENTES en el resumen automático
por diseño. Los casos manuales se registran aparte; no se inventan
pruebas de timeout real o de otras plataformas.

## Verificador manual de exports de laboratorio

test/verificar_export_laboratorio.py comprueba un archivo cifrado
generado por el programa sin imprimir el contenido privado.

Requiere una terminal interactiva y la contraseña del export. No forma
parte de las suites automáticas ni ejecuta por sí mismo las opciones
del programa principal.

En JSON comprueba autenticación, red, número de palabras, BIP39, entropy,
seed y estructura de familias, cantidades, índices y rutas. No verifica
criptográficamente todas las direcciones.

En texto comprueba autenticación, cabecera y red, con alcance menor.

La contraseña de exportación se solicita sin eco. --test-passphrase
representa exclusivamente una passphrase BIP39 ficticia para contrastar
la seed; no es la contraseña del archivo.

### Ejemplos

Los ejemplos no crean el archivo indicado. Antes de ejecutarlos,
seleccionar un export ficticio existente y ajustar todas las expectativas.

No copiar literalmente output/laboratorio/reporte.json si ese archivo
no existe. Un FileNotFoundError no comprueba autenticación ni descifrado.

Linux:

```bash
"$PY" test/verificar_export_laboratorio.py \
  output/laboratorio/reporte.json \
  --words 12 --network testnet --input-mode words
```

Ejemplo registrado el 5 de noviembre de 2026:

```bash
"$PY" test/verificar_export_laboratorio.py \
  output/bip39_seed_report_027.json \
  --words 12 --network testnet --input-mode words
```

Ese nombre corresponde únicamente al archivo del ensayo comunicado.
En otra copia local debe sustituirse por el archivo realmente existente.

Windows PowerShell — referencia histórica; revisión actual diferida
y no bloqueante:

```powershell
& $PY .\test\verificar_export_laboratorio.py .\output\laboratorio\reporte.json --words 12 --network testnet --input-mode words
```

Ajustar siempre la ruta al archivo final realmente creado, incluidos
los sufijos secuenciales. Las expectativas deben corresponder al archivo.

Si el ensayo utilizó la passphrase ficticia TREZOR, añadir:

```text
--test-passphrase TREZOR
```

No utilizar material real, publicar exports ni imprimir el plaintext.
Un resultado correcto no certifica la imprevisibilidad de la fuente,
la seguridad del equipo ni todas las derivaciones.

## Alcance

- Vectores BIP39: casos ejecutados de conversión, seed y round-trip.
- Runner BIP39 y última palabra: validación de suites y campos,
  errores previstos, casos positivos, búsqueda real de candidatos
  y comprobación de la captura de salida mediante mutación controlada.
- Cifrado: recuperación, rechazo de alteraciones y compatibilidad histórica.
- Entrada: política de GetPassWarning y normalización Unicode.
- Contenedor: estructura, tipos, duplicados, límites y orden de validación
  anterior a la KDF, además de casos positivos y compatibilidad histórica.
- Escritura: publicación sin reemplazo, colisiones, fallos y concurrencia
  según los métodos ejecutados en cada plataforma.
- Auxiliar manual: autenticación y comprobaciones del export elegido,
  con alcance diferente para JSON y texto.
- UX: separación entre presentación compacta y reporte privado completo.
- Integral: casos funcionales, negativos y UI simulada.
- Ejecutor: entorno, estados, omisiones, inventario y conservación de hashes.

Pasar estas suites no constituye una auditoría ni verifica todas
las derivaciones, plataformas o condiciones de escritura.

La suite nueva no verifica el cuarto campo BIP32 de los vectores
ni sustituye las pruebas completas del flujo interactivo de recuperación.
La comprobación CLI de suite vacía se registró por separado.

La suite del contenedor no comprueba escritura concurrente, permisos
efectivos, durabilidad del sistema de archivos ni lectura limitada
desde disco antes de cargar el contenido en memoria.

Las pruebas con mocks verifican controles concretos del programa;
no sustituyen las pruebas criptográficas reales ni los ensayos
de terminal y sistema de archivos.

La suite de escritura no garantiza durabilidad del directorio ni defensa
frente a un padre manipulado por un atacante. Los ensayos Windows no
certifican ACL, enlaces simbólicos omitidos ni concurrencia entre procesos.

Los resultados y límites completos por entorno se registran en
[ANALISIS_COMPATIBILIDAD_SO.md](../ANALISIS_COMPATIBILIDAD_SO.md).

## Datos de referencia

vectors.json conserva los bytes de la suite previamente probada.
La procedencia y los avisos de los datos de referencia se registran en
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

La identificación del origen histórico exacto sigue pendiente.

No reemplazarlo automáticamente desde una rama remota mutable.
