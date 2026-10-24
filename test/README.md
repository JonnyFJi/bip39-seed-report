# Pruebas de BIP39 Seed Report

Las suites utilizan exclusivamente datos ficticios o vectores públicos.
No introducir mnemonics, passphrases ni claves de usuario.

## Ejecución en Linux/macOS

Ejecutar desde la raíz del proyecto, no desde la carpeta test.

Los comandos siguientes suponen que existe un entorno virtual local
en .venv-verificacion con las dependencias de requirements.txt instaladas.

```bash
PY="$PWD/.venv-verificacion/bin/python"
"$PY" --version
"$PY" -m pip check
```

Comprobar sintaxis y ejecutar las suites:

```bash
"$PY" -m py_compile bip39_seed_report.py
"$PY" -m py_compile test/test_contenedor_report.py
"$PY" -m py_compile test/test_escritura_report.py
"$PY" -m py_compile test/test_regresion_vectores_ultima_palabra.py

"$PY" bip39_seed_report.py --run-tests --vectors-file test/vectors.json

PYTHONPATH="$PWD" "$PY" test/test_cifrado_report.py
PYTHONPATH="$PWD" "$PY" test/test_entrada_segura.py
PYTHONPATH="$PWD" "$PY" test/test_contenedor_report.py
PYTHONPATH="$PWD" "$PY" test/test_escritura_report.py
PYTHONPATH="$PWD" "$PY" test/test_regresion_vectores_ultima_palabra.py
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

### Suite del contenedor cifrado

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

Linux:

```bash
"$PY" test/verificar_export_laboratorio.py \
  output/laboratorio/reporte.json \
  --words 12 --network testnet --input-mode words
```

Windows PowerShell:

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
