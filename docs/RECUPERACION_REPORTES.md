# Conservación y recuperación de reportes cifrados

## Alcance, versión y seguridad

Actualización documental: 12 de noviembre de 2026. Se incorpora el alcance
de la integración local entropy CLI y de la comprobación posterior de otra
copia. No se modifica el código ni el formato de cifrado.
La actualización del 6 de noviembre simplificó la selección del archivo
cifrado; sus procedimientos y resultados históricos se conservan.

La guía se preparó inicialmente el 5 de noviembre de 2026 para la referencia
c342c4ccd61b8434ed5581a70c25e9a8bc00689d. Ese hito Linux registró
42 métodos del inspector, 20 del ejecutor, diez etapas, 14 archivos
protegidos e inventario del núcleo 70/70.

La integración Linux local corregida del 10 de noviembre registró
42 métodos del inspector, 33 del ejecutor, 25 etapas, 362 métodos
unittest acumulados, inventario 73/73 y 49 entradas conservadas.
El núcleo local se identifica por SHA-256
b29675e5d91f52fd6c109a777b820945c01c12ef88e6f9926f61cc6e204e20d6.
No se atribuye un commit remoto nuevo ni se declara una release.

La comprobación posterior de otra copia Linux generó y verificó
reportes nuevos sobre runtimes base existentes del mismo equipo.
No se presenta como recuperación offline de un reporte anterior
trasladado a otro equipo. Los resultados Linux no aprueban la
integración actual en Windows/macOS.

La herramienta es educativa y experimental, no auditada para custodia o
producción. La decisión de uso corresponde al usuario. Todas las pruebas
que se describen aquí deben hacerse con material ficticio.

Python 3.10.12 fue la referencia Linux ensayada; Python 3.10.11 corresponde
al ensayo histórico Windows. No son una recomendación para instalar hoy
versiones antiguas: la rama 3.10 terminó su soporte upstream el 1 de octubre
de 2026 según Python. El soporte adicional de un distribuidor debe comprobarse
con ese proveedor. Para instalaciones nuevas, elegir un intérprete mantenido
y comprobar las dependencias y suites; no existe aquí una matriz validada
para todas las versiones nuevas. No actualizar a ciegas el entorno histórico.

Preparar dependencias con conexión antes de trabajar offline. El venv separa
paquetes, no protege contra malware, capturas, swap o un sistema comprometido.
No ejecutar el programa como administrador/root. Las instalaciones de paquetes
del sistema, si hacen falta, son una operación distinta.

Ejecutar los comandos por pasos. Si un paso falla, detenerse y revisar su
salida; un comando posterior satisfactorio no corrige un fallo anterior.
No pegar prompts como `$`, `PS>` o `>>>`.

## 1. Qué debe conservarse

| Elemento | Necesidad |
|---|---|
| Archivo cifrado íntegro | Imprescindible: contiene ciphertext, salt, nonce y metadatos |
| Contraseña de exportación | Imprescindible para derivar la clave de descifrado |
| Código compatible y versión/commit | Permite interpretar exactamente el formato |
| requirements.txt e instrucciones | Permiten preparar el entorno |
| Intérprete base compatible y forma de prepararlo, si se necesita recuperación offline | El venv y el wheelhouse no constituyen por sí solos una distribución portable de Python |
| Hashes del código y del archivo | Detectan cambios respecto de una referencia confiable |
| Dependencias offline por plataforma, si se necesitan | Evitan depender de una descarga futura |

Guardar copias verificadas del archivo cifrado y conservar la contraseña por una
vía protegida que no dependa exclusivamente de la misma copia. No publicar ninguna.
El cifrado no compensa una contraseña predecible. No hay función para recuperar
una contraseña de exportación olvidada.

El hash del reporte sirve para detectar cambios de bytes; no sustituye la autenticación
AES-GCM ni conviene publicarlo indiscriminadamente por su capacidad de correlación.
Cerrar ventanas, borrar un venv o eliminar un archivo no garantiza borrado seguro.

## 2. Contraseña de exportación y passphrase BIP39

La contraseña de exportación descifra el archivo; la passphrase BIP39 modifica la
seed BIP39. No son intercambiables.

Para abrir un reporte ya cifrado se necesita la contraseña de exportación, no la
passphrase BIP39. El inspector puede autenticar y mostrar un reporte cuyo campo
passphrase_used sea true sin solicitar la passphrase BIP39.

La opción 1 no contrasta la seed con una passphrase BIP39 no vacía. Si se desea
reconstruir directamente una wallet a partir de su mnemonic, conservar la passphrase
correspondiente y su contexto es un asunto adicional. No asumir que descifrar un
reporte valida toda esa recuperación.

## 3. Qué software conservar antes de borrar la herramienta

La opción más simple es conservar una copia completa y verificada del código de
la versión utilizada, sus avisos/licencias y documentación. No depender solo de
que el repositorio o un índice de paquetes sigan disponibles en el futuro.

Para el inspector se necesitan inspeccionar_reporte_cifrado.py,
bip39_seed_report.py y los módulos de la revisión que estos importen,
además de sus dependencias Python. En la integración local no debe
suponerse que basta con conservar únicamente los dos scripts principales.
La opción recomendada sigue siendo conservar la copia completa y
verificada del código compatible.

Preparar una recuperación no significa volver a ejecutar generación
automática. Deben distinguirse los módulos necesarios para importar
y descifrar con esa revisión de los runtimes y auxiliares utilizados
para adquirir entropy nueva. No ejecutar una nueva generación ni
recompilar proveedores como supuesto método para recuperar el cifrado.

Los metadatos de generación que contenga un reporte forman parte
del contenido cifrado existente. No es necesario reproducir aquellas
aportaciones para autenticar ese archivo; esos metadatos tampoco
certifican por sí solos el origen o la imprevisibilidad del material.

El contenedor actual utiliza scrypt y AES-256-GCM con metadatos autenticados.
Su codificación, normalización de contraseña, perfil KDF y construcción del AAD
forman parte de la compatibilidad. No es un ZIP con contraseña y no se abre con
cualquier programa que anuncie AES. No improvisar comandos OpenSSL incompatibles.

El lector histórico ENCRYPTED: se conserva por compatibilidad y avisa de su KDF
antigua. Descifrar no migra el archivo: una migración requiere exportar otra vez
en el formato actual, conservar el original y verificar el resultado por separado.

Las guías de instalación contienen descarga por commit y comprobación del núcleo:
[Linux](INSTALACION_LINUX.md), [Windows](INSTALACION_WINDOWS.md),
[macOS](INSTALACION_MACOS.md). El SHA del núcleo no cubre todo el paquete.
La release ZIP con checksum y autenticación de distribución sigue pendiente.

## 4. Preparar una recuperación realista

Antes de borrar la única instalación funcional, ensayar con un reporte ficticio:

1. Copiar el reporte original sin modificarlo; registrar su identidad localmente.
2. Abrir una carpeta limpia con el código compatible y sus documentos.
3. Reconstruir un venv; no copiar el venv del equipo original como supuesto paquete portable.
4. Instalar las dependencias con ese intérprete y ejecutar pip check.
5. Comprobar versión e integridad del código.
6. Autenticar primero sin imprimir secretos.
7. Si hace falta leerlos, usar una operación explícita en una terminal de confianza.
8. Registrar el resultado sin copiar plaintext a logs o al repositorio.

No ejecutar generación nueva para «recuperar» el archivo: crearía otro material.
Trabajar con una copia del cifrado no cambia el original ni requiere sobrescribirlo.

Para registrar un ensayo de recuperación, utilizar un reporte ficticio
preexistente y comprobar que la copia trasladada conserva sus bytes
respecto de una referencia previa confiable. Después, registrar el
resultado explícito de autenticación y el alcance de las comprobaciones.

Crear y verificar un reporte nuevo en el entorno de destino prueba
ese flujo de generación y lectura, no la recuperación del archivo
anterior. Si el objetivo es recuperación sin red o en otro equipo,
esas condiciones deben ensayarse y documentarse por separado.
No marcar la lista final como completada solo por disponer de una
batería automática satisfactoria.

## 5. Recuperación mediante el inspector en Linux

### 5.1. Situarse en la raíz y comprobar el entorno

La raíz contiene bip39_seed_report.py, inspeccionar_reporte_cifrado.py,
requirements.txt y test/. Si la terminal está dentro de output/, volver a la
raíz antes de usar los ejemplos relativos. Si se está exactamente en output/,
un nivel debajo de la raíz, basta `cd ..`; comprobar la ubicación antes de seguir.
No ejecutar ese cambio de carpeta si ya se está en la raíz.

```bash
pwd
ls -l -- bip39_seed_report.py inspeccionar_reporte_cifrado.py requirements.txt
```

Con el venv y sus dependencias ya preparados:

```bash
PY="$PWD/.venv-verificacion/bin/python"
"$PY" -c 'import sys; print(sys.executable)'
"$PY" -m pip check
```

Si falta el ejecutable o fallan dependencias, detenerse y seguir la guía Linux.
No cambiar el script para resolver una preparación incompleta.

### 5.2. Método principal: ruta relativa directa

Este ejemplo corresponde a un archivo que ya exista como
output/bip39_seed_report.json. Si la copia tiene otro nombre, un sufijo secuencial
como _001 o está en otra carpeta, sustituir la ruta real en ambos comandos.
No ejecutar el ejemplo esperando que cree o localice automáticamente otro archivo.

Primero comprobar que el archivo se encuentra desde la raíz:

```bash
ls -l -- "output/bip39_seed_report.json"
```

Solo si se encuentra, abrir el inspector:

```bash
"$PY" inspeccionar_reporte_cifrado.py "output/bip39_seed_report.json"
```

No es necesario introducir la ruta por segunda vez ni utilizar printf/read.
No se genera otra seed ni se sobrescribe el reporte existente.

### 5.3. Alternativa: asignación explícita a REPORTE

Para el mismo archivo situado bajo output/, desde la raíz:

```bash
REPORTE="$PWD/output/bip39_seed_report.json"
```

Para otro archivo, cambiar el valor de la asignación por su ruta real entre comillas.
Puede ser una ruta absoluta fuera del proyecto. No copiar una ruta ficticia sin adaptarla.
La contraseña nunca se escribe en esta variable ni en el comando.

Comprobar lo que se guardó y que el archivo existe:

```bash
printf 'Ruta guardada en REPORTE: <%s>\n' "$REPORTE"
ls -l -- "$REPORTE"
```

Solo si ls encuentra el archivo, ejecutar:

```bash
"$PY" inspeccionar_reporte_cifrado.py "$REPORTE"
```

printf imprime un mensaje o un valor; no asigna una ruta a REPORTE. La asignación
es la línea que empieza por REPORTE=. El procedimiento básico no utiliza read,
por lo que no deja una entrada adicional pendiente ni requiere pegar la ruta otra vez.

Si se usa en otro contexto `IFS= read -r REPORTE`, ese comando espera una línea
posterior de entrada. Mostrar una ruta antes con printf no la entrega automáticamente
a read. Un Enter vacío puede dejar REPORTE vacía; pegar un bloque puede proporcionar
una entrada distinta de la pretendida. No es el método básico de esta guía.

### 5.4. Autenticar antes de revelar

1. Seleccionar 1 en el menú.
2. Introducir la contraseña de exportación en la entrada oculta.
3. Revisar el resultado explícito de esa operación.
4. Elegir Q si no hace falta otra revisión.

Para el ensayo JSON con passphrase BIP39 vacía se observó:

```text
OK: reporte autenticado; no se imprime el contenido privado.
JSON: BIP39, seed con passphrase vacía y estructura comprobados; no se verifican independientemente todas las direcciones.
```

El mensaje de alcance depende del contenido: en TXT la comprobación es menor;
si la passphrase BIP39 no era vacía, no se contrasta la seed con ella.
No utilizar el texto del ejemplo para atribuir una comprobación no efectuada.

Si hace falta leer el contenido, elegir 2 (perfil GNOME requerido) o 3
(confirmación explícita). La guía Linux explica los requisitos. Nunca hay
revelación automática tras un fallo. La opción 3 puede persistir en scrollback;
la opción 2 no garantiza borrado seguro.

Un cierre con Q devuelve 0 aunque una operación anterior haya fallado. El código
final corresponde a Q. Timeout o Ctrl+C devuelven 1. Registrar los mensajes de
cada operación y no interpretar solo el código final como autenticación correcta.

### 5.5. Diagnóstico de rutas y de autenticación

| Mensaje o situación | Qué comprobar |
|---|---|
| No existe un archivo cifrado legible en la ruta indicada | Ubicación actual, valor de REPORTE, nombre/sufijo, archivo regular y ruta real |
| La variable se imprime como <> | No contiene la ruta; asignarla antes de continuar |
| ls no encuentra el archivo | Corregir la ruta antes de pedir descifrado; no generar otro reporte como arreglo |
| No se pudo autenticar o descifrar | Revisar contraseña de exportación y archivo íntegro; no confundir con passphrase BIP39 |
| Se imprimió una ruta con printf | Eso no demuestra que esté guardada en REPORTE |

Calcular SHA-256 permite registrar los bytes actuales. Para demostrar preservación
frente al original hay que comparar con un hash previo confiable; no sustituye la
autenticación del contenedor con la contraseña.

## 6. Windows/macOS: límites actuales y autenticación opcional

El CLI del inspector está restringido a Linux. Para su menú y ventana completos,
usar una instalación Linux compatible y de confianza. No cambiar sys.platform.

Si solo se necesita autenticar sin revelar, puede utilizarse el siguiente auxiliar
local opcional, que llama a las funciones existentes sin introducir otra criptografía.
Es una propuesta técnica, no una nueva función distribuida, una auditoría ni un
ensayo Windows/macOS realizado. Probar primero con un archivo ficticio. No habilita
la ventana ni el menú del inspector en esas plataformas.

### Crear el auxiliar local

Crear `local-private/` dentro de la raíz y, con un editor de texto, guardar el bloque
siguiente como `local-private/autenticar_reporte_recuperado.py`. No guardarlo como
`.py.txt`. Ese código no contiene secretos. La carpeta se excluye en el .gitignore
actual; aun así, no subir su contenido ni sus resultados por accidente.

```python
from pathlib import Path
import sys


def main():
    if len(sys.argv) != 2:
        print("Uso: python autenticar_reporte_recuperado.py ARCHIVO_CIFRADO", file=sys.stderr)
        return 1
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    import bip39_seed_report as report
    import inspeccionar_reporte_cifrado as viewer

    if not report.CRYPTO_AVAILABLE:
        raise RuntimeError("Dependencia criptografica ausente")
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise RuntimeError("Se requiere una terminal interactiva")
    path = Path(sys.argv[1]).expanduser().resolve(strict=True)
    if not path.is_file():
        raise ValueError("Se requiere un archivo regular")
    viewer.report = report
    plain = None
    try:
        plain = viewer.read_plain(path)
        viewer.parse_plain(plain, "auto")
        print("OK: contenedor autenticado y formato interno reconocido; no se imprime contenido privado.")
        print("No se verifican BIP39, seed ni derivaciones mediante este auxiliar.")
    finally:
        plain = None
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        print("Autenticacion cancelada.", file=sys.stderr)
        sys.exit(1)
    except Exception:
        print("ERROR: no se pudo autenticar o reconocer el reporte; revisar archivo, contrasena y entorno.", file=sys.stderr)
        sys.exit(1)
```

La asignación de None no garantiza borrado de memoria. La contraseña se solicita
mediante la función oculta del proyecto y no se pasa por argumentos. El auxiliar
no guarda plaintext ni imprime excepciones del backend. Un formato interno inválido
se rechaza aunque el descifrado haya completado.

### Ejecutar en Windows PowerShell

Con el venv preparado y desde la raíz:

```powershell
$PY = Join-Path $PWD.Path '.venv-verificacion\Scripts\python.exe'
$Reporte = Read-Host 'Ruta del archivo cifrado existente, sin comillas exteriores'
& $PY .\local-private\autenticar_reporte_recuperado.py $Reporte
$LASTEXITCODE
```

### Ejecutar en macOS o Linux

Con el auxiliar local creado como se indica arriba, el venv preparado y situado
en la raíz. El ejemplo supone que output/bip39_seed_report.json existe: sustituir
su ruta si el archivo está en otro lugar o tiene un nombre distinto.

```bash
PY="$PWD/.venv-verificacion/bin/python"
REPORTE="$PWD/output/bip39_seed_report.json"
printf 'Ruta guardada en REPORTE: <%s>\n' "$REPORTE"
ls -l -- "$REPORTE"
```

Solo si el archivo se encuentra:

```bash
"$PY" local-private/autenticar_reporte_recuperado.py "$REPORTE"
echo $?
```

Aquí REPORTE se asigna expresamente; printf no sustituye esa asignación.
La modificación documental no acredita nuevos ensayos reales de macOS.

Esperar código 0 solamente si aparecen los mensajes de autenticación. Código 1 indica
cancelación/error, no una razón para imprimir el contenido sin protección.
Este procedimiento conserva el mismo requisito de TTY; no usar pipes, redirecciones
o una celda de notebook para introducir la contraseña.

Para visualización completa fuera de Linux, la portabilidad del inspector sigue
pendiente. No se incluye un lector que revele automáticamente como fallback.

## 7. Recuperación sin red: preparación opcional previa

Solo preparar esto mientras se dispone de conexión y de un entorno de referencia
que funciona. Los paquetes nativos dependen de SO, arquitectura, versión/ABI de Python.
No usar un wheelhouse Linux como si fuera universal para Windows/macOS.

El wheelhouse conserva paquetes Python, no instala por sí solo el
intérprete base ni reconstruye todo el sistema. Preparar también
una vía confiable y compatible para disponer de Python en el destino.
Si se quiere reproducir generación redundante, su preparación Java/Node
es un objetivo adicional y distinto de autenticar un reporte existente.

En Linux/macOS, con PY definido y situado en la raíz:

```bash
mkdir -p local-private/wheelhouse
"$PY" -m pip freeze --all > local-private/requirements-entorno.txt
"$PY" -m pip wheel --wheel-dir local-private/wheelhouse -r local-private/requirements-entorno.txt
```

En PowerShell:

```powershell
New-Item -ItemType Directory -Force .\local-private\wheelhouse | Out-Null
& $PY -m pip freeze --all | Set-Content -Encoding UTF8 .\local-private\requirements-entorno.txt
& $PY -m pip wheel --wheel-dir .\local-private\wheelhouse -r .\local-private\requirements-entorno.txt
```

Revisar el archivo congelado: puede reflejar URLs/rutas y paquetes adicionales del
entorno. No publicarlo sin revisión. `pip wheel` puede requerir herramientas de
compilación y conexión para requisitos de construcción. Si falla, no se dispone
por ello de un kit offline completo.

Antes de utilizar el fichero congelado en el destino, revisar y resolver
las referencias directas a URLs, repositorios o rutas del equipo original,
incluidas las de requisitos adicionales. No eliminarlas ni sustituirlas
por versiones arbitrarias: preparar artefactos locales correspondientes
y comprobar que el conjunto sigue siendo compatible.

--no-index desactiva los índices de paquetes; no es un aislamiento de red
ni garantiza que cualquier referencia del fichero sea local.
El ensayo offline debe realizarse realmente sin conexión y sin depender
de rutas, cachés o recursos disponibles solo en la instalación original.

pip freeze --all describe los paquetes instalados; no calcula un lockfile
ni demuestra que el wheelhouse sea suficiente para reconstruir el entorno.
La suficiencia se comprueba instalando y autenticando un reporte ficticio
preexistente en el entorno de destino preparado para ese ensayo.

Transferir una copia verificada del código, del fichero de requisitos y del wheelhouse
al equipo compatible. Crear allí el venv antes de instalar:

Linux/macOS:

```bash
"$PY" -m pip install --no-index --find-links local-private/wheelhouse -r local-private/requirements-entorno.txt
"$PY" -m pip check
```

PowerShell:

```powershell
& $PY -m pip install --no-index --find-links .\local-private\wheelhouse -r .\local-private\requirements-entorno.txt
& $PY -m pip check
```

Esta instantánea no es un lockfile autenticado ni garantiza por sí sola
reproducibilidad futura. Verificar hashes/procedencia de todos los artefactos y
ensayar de verdad sin red en un entorno compatible antes de depender del kit.
No conservar únicamente un venv copiado o asumir que incluye un Python portable.

## 8. Lista final antes de borrar una instalación

- [ ] Tengo el cifrado íntegro y una copia verificada.
- [ ] Conservo la contraseña de exportación por una vía protegida.
- [ ] Conservo código compatible, requisitos, instrucciones e identidad de versión.
- [ ] Distingo contraseña de exportación de passphrase BIP39.
- [ ] He autenticado en el entorno de destino una copia íntegra de un reporte ficticio preexistente, no solo un reporte nuevo generado allí.
- [ ] Si necesito otro equipo o sistema operativo, probé expresamente ese destino.
- [ ] Si necesito recuperación offline, probé sin conexión el kit, el intérprete y los artefactos necesarios.
- [ ] No dependo de una ventana aún no implementada en mi SO.
- [ ] No publiqué reportes, claves o transcripciones privadas.

## 9. Comprobación del procedimiento comunicada el 6 de noviembre de 2026

En una copia local de prueba se autenticó el mismo reporte JSON mediante:

- Una ruta absoluta asignada explícitamente a REPORTE.
- La ruta relativa directa desde la raíz del proyecto.

Ambas ejecuciones de la opción 1 informaron autenticación, BIP39, seed con
passphrase vacía y estructura comprobados sin imprimir contenido privado.
Después se regresó al menú y se salió mediante Q. La transcripción no incluye
una consulta del código de salida de esas dos invocaciones.

El intento anterior falló al indicar una ruta mediante printf/read sin confirmar
el contenido de la variable. La asignación directa resolvió la selección de ruta;
no fue necesario modificar el script, cambiar contraseña o regenerar el reporte.

Son dos accesos al mismo archivo, no dos reportes independientes. Esta evidencia
no demuestra por sí sola un kit offline ni una recuperación completamente
independiente del entorno original. No se publican la ruta personal, el hash del
reporte o su contenido privado.

### Recuperación desde otra carpeta — 6 de noviembre de 2026

El mantenedor copió los archivos básicos de la herramienta y un reporte
cifrado existente a otra carpeta del mismo equipo, cuyo nombre contiene
un espacio.

Se seleccionó el intérprete de .venv-verificacion situado dentro de esa
carpeta. El inspector encontró el archivo mediante una ruta relativa y
la opción 1 terminó con autenticación, BIP39, seed con passphrase vacía
y estructura comprobados, sin imprimir contenido privado.

La captura muestra la creación del venv y pip check satisfactorio,
pero no documenta la instalación de las dependencias. Por tanto, se
registra como recuperación satisfactoria desde otra ubicación, no como
demostración completa de instalación limpia desde cero.

No se acredita mediante este ensayo recuperación sin red, en otro
equipo o en otro sistema operativo.

## 10. Alcance de la comprobación de otra copia — 10 de noviembre de 2026

El laboratorio posterior copió y verificó 64 archivos seleccionados
en otra carpeta del mismo equipo Linux. Se creó un venv nuevo,
se instalaron de nuevo los paquetes Python y se recompilaron las
dos fuentes Java sobre los runtimes base existentes.

La batería proyecto/output/bateria_local_zelv2gy3 terminó con
25 etapas, 362 métodos unittest, inventario 73/73, 49 entradas
conservadas y código 0. La ejecución individual de los 33 métodos
del ejecutor no se suma otra vez al acumulado.

Los tres casos manuales posteriores generaron reportes nuevos:
redundante de 12 palabras, current explícito de 12 e interactivo
de 24, todos en testnet. En current se conservaron mensajes
satisfactorios, pero no códigos separados de generación y verificación.

En el caso interactivo se registró verificación satisfactoria,
inspector con código 0 y confirmación visual del mantenedor:
la ventana temporal se abrió, mostró el reporte y se cerró con Enter.

No se trasladó un reporte cifrado antiguo como objeto de recuperación
de esos casos. Por tanto, el ensayo acredita preparación de una copia
y generación/verificación de reportes nuevos, no recuperación offline
de un archivo anterior en otro equipo.

La comprobación de 71 archivos registrados del origen sin cambios
se realizó antes de los manuales. No se presenta como verificación
posterior a todos los ensayos. Ese conjunto, los 64 archivos copiados
y las 49 entradas de la batería son distintos.

Este registro no sustituye la recuperación desde otra carpeta del
6 de noviembre ni amplía su alcance. Tampoco acredita una instalación
completa de runtimes desde cero, borrado seguro o recuperación Windows/macOS.

Detalle:
[Resultados de preparación de otra copia](../test/RESULTADOS_COPIA_ENTROPY_2026-11-10.md).

## Referencias

- [Resultados de integración entropy CLI](../test/RESULTADOS_ENTROPY_CLI_2026-11-10.md)
- [Resultados de preparación de otra copia](../test/RESULTADOS_COPIA_ENTROPY_2026-11-10.md)
- [Análisis de compatibilidad y resultados históricos](../ANALISIS_COMPATIBILIDAD_SO.md)
- [Instalación Linux](INSTALACION_LINUX.md)
- [Instalación Windows](INSTALACION_WINDOWS.md)
- [Instalación macOS](INSTALACION_MACOS.md)
- [Seguridad del proyecto](../SECURITY.md)
- [Pruebas](../test/README.md)
- Python venv: https://docs.python.org/3/library/venv.html
- Paquetes/entornos administrados: https://packaging.python.org/en/latest/specifications/externally-managed-environments/
- Estado de Python: https://devguide.python.org/versions/
