# Instalación y ejecución en Linux

Nota de actualización documental — 19 de noviembre de 2026:
esta guía conserva los registros y contextos históricos de noviembre 10
y 11. Las ampliaciones posteriores sobre preparación de runtimes,
BIP32 directo y opciones de inspección se distinguen de esos ensayos.
Las fechas, versiones y resultados históricos no se actualizan
retrospectivamente.

La corrida posterior `output/bateria_local_t2c17zkm`, con el pie de ayuda
ampliado, completó 26 etapas y 412 métodos unittest, inventario 80/80,
50 archivos protegidos conservados y código `0`. Corresponde al núcleo
`b31741cc898b86394c2e103effe25db14bff4f54361f31928e19387688283fcd`.
Los resultados anteriores de esta guía conservan su propia identidad.

Tras esa corrida, la suite aislada del inspector se amplió a 66 métodos
y pasó satisfactoriamente. La incorporación de ese refuerzo a una
batería completa se registrará por separado.

## Alcance, versión y seguridad

Guía actualizada el 11 de noviembre de 2026 para distinguir la integración
local entropy CLI del 10 de noviembre, su comprobación posterior en otra
copia y la referencia publicada histórica del 5 de noviembre.
No se atribuye un commit remoto nuevo ni se declara una release.

La batería corregida original y la batería posterior de la copia
registraron, cada una, 25 etapas, 362 métodos, inspector de 42,
ejecutor de 33, inventario del núcleo 73/73 y 49 entradas conservadas.
Son ejecuciones distintas, no 724 métodos diferentes.

La copia utilizó un venv nuevo, paquetes Python instalados de nuevo
y fuentes Java recompiladas sobre runtimes base existentes del mismo
equipo. La instalación completa de esos runtimes desde cero en otro
entorno sigue pendiente; no se promete preparación completa con pip.

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

## Descargar y reconocer la raíz del proyecto

1. Abrir el repositorio oficial: https://github.com/JonnyFJi/bip39-seed-report
2. Elegir la revisión que se desea verificar. `Code` → `Download ZIP`
   descarga la rama disponible, pero no demuestra que contenga la integración
   local del 10 de noviembre. El snapshot histórico anterior es:
   https://github.com/JonnyFJi/bip39-seed-report/archive/c342c4ccd61b8434ed5581a70c25e9a8bc00689d.zip
   No usar ese enlace histórico como distribución de la integración nueva.
3. Extraer el ZIP completo; no abrir o ejecutar los scripts desde el visor del ZIP.
4. Entrar en la carpeta extraída que contiene `bip39_seed_report.py`,
   `inspeccionar_reporte_cifrado.py`, `requirements.txt` y `test/`.
   Esa carpeta es la raíz; no es `docs/` ni `test/`.

### Qué contiene el enlace ZIP histórico fijado

El enlace al commit c342c4ccd61b8434ed5581a70c25e9a8bc00689d
descarga el código histórico de referencia revisado, no la integración
local entropy CLI del 10 de noviembre. Ese commit es anterior
a la incorporación de estas guías y su ZIP no contiene la carpeta docs/.

Para conservar también las guías, guardar los documentos de docs/
correspondientes a la revisión elegida, o descargar el contenido disponible
del repositorio mediante Code → Download ZIP. Registrar si las guías y
el código proceden de revisiones diferentes.

La descarga desde main incluye los archivos presentes en esa rama
en el momento de descargarla. Puede corresponder a una revisión
posterior a la referencia fija; registrar esa diferencia.

`main` puede cambiar. Registrar el commit o la versión elegida. El ZIP de GitHub
es código fuente: no incluye un Python listo para ejecutar ni sus dependencias.
Estas guías no anuncian una release del programa; esa distribución sigue pendiente.

El ZIP no impide por sí solo corrupción o sustitución. Un checksum verifica
integridad respecto de un valor confiable; si se reemplazan tanto archivo como
hash, la comparación no demuestra autenticidad. El checksum del núcleo no es
el checksum del ZIP ni del conjunto completo. No hay que inventar un hash del
ZIP automático: su compresión puede cambiar aunque conserve los archivos.

Para el núcleo del commit de referencia, el SHA-256 esperado es:

```text
b09fcc4f292283b8d5e6f4470dc3858a079b209b1c3ccb579be27cdec51b5174
```

El núcleo local de la integración del 10 de noviembre tiene otro hash:

```text
b29675e5d91f52fd6c109a777b820945c01c12ef88e6f9926f61cc6e204e20d6
```

No se atribuye este hash al ZIP histórico ni se afirma que esté publicado
en `main`. Si se eligió otra revisión y el valor difiere, comparar esa
revisión antes de continuar; no regenerar el checksum para hacer
desaparecer la discrepancia.

## 1. Abrir una terminal en la carpeta extraída

Usar «Abrir en una terminal» del administrador de archivos dentro de la raíz.
Si se usa `cd`, escribir la ruta real entre comillas; no copiar una ruta de ejemplo.
Comprobar:

```bash
pwd
ls -l bip39_seed_report.py inspeccionar_reporte_cifrado.py requirements.txt test/vectors.json
python3 --version
command -v python3
```

No hace falta dar permiso ejecutable a los `.py`: los invocaremos con Python.
Si `python3` no existe, instalar una versión mantenida desde el proveedor de la
distribución y volver a esta comprobación. No cambiar el Python del sistema
mediante enlaces o desinstalaciones.

## 2. Comprobar la identidad del núcleo

```bash
sha256sum -c bip39_seed_report.py.sha256
sha256sum bip39_seed_report.py
```

Debe coincidir el checksum y el hash de la revisión realmente elegida:
no intercambiar los valores histórico y local indicados arriba.
La coincidencia con el `.sha256` descargado no autentica por sí sola a su autor.

## 3. Elegir una de las tres modalidades

Se recomienda A. No mezclar intérpretes a mitad de una comprobación.

### A. Venv sin activar: referencia recomendada

Crear el entorno solo si no existe:

```bash
python3 -m venv .venv-verificacion
```

Seleccionarlo explícitamente desde la raíz:

```bash
PY="$PWD/.venv-verificacion/bin/python"
"$PY" -c 'import sys; print(sys.executable); print("Venv:", sys.prefix != sys.base_prefix)'
```

El resultado debe mostrar el ejecutable del venv y `Venv: True`.
Si falta el módulo `venv`, consultar la distribución. En Debian/Ubuntu/Mint,
la instalación del paquete `python3-venv` es una posible operación de preparación;
no se necesita `sudo` para ejecutar este proyecto ni para instalar dentro del venv.
No ejecutar instrucciones `apt` en distribuciones que usan otro gestor.

Instalar dependencias, con conexión y como usuario normal:

```bash
"$PY" -m pip install -r requirements.txt
```

Solo si termina correctamente:

```bash
"$PY" -m pip check
"$PY" -c 'import mnemonic, bip_utils, cryptography; print("Importaciones OK")'
```

En cada terminal nueva, volver a definir `PY` desde la raíz. Reasignarla a
`/usr/bin/python3` cambia el entorno usado; no desinstala el venv.

### B. Venv activado: alternativa

Crear el mismo venv si todavía no existe; después:

```bash
source .venv-verificacion/bin/activate
python -c 'import sys; print(sys.executable); print("Venv:", sys.prefix != sys.base_prefix)'
PY="$VIRTUAL_ENV/bin/python"
```

Utilizar las mismas instrucciones de instalación y ejecución con `"$PY"`.
La activación solo facilita seleccionar el intérprete; no añade una protección
criptográfica. Para terminar la activación:

```bash
deactivate
```

La variable `PY` puede seguir apuntando al venv después de `deactivate`.
Siempre consultar su ejecutable antes de cambiar de modalidad.

### C. Sin venv: solo si la política del intérprete lo permite

En una terminal sin venv activado, seleccionar el intérprete no virtual:

```bash
PY="$(command -v python3)"
"$PY" -c 'import sys; print(sys.executable); print("Venv:", sys.prefix != sys.base_prefix)'
```

Para esta modalidad debe mostrar `Venv: False`. Si no lo hace, elegir de manera
explícita el Python no virtual; no continuar bajo una etiqueta de entorno errónea.

```bash
"$PY" -m pip install --user -r requirements.txt
```

Después comprobar `pip check` e importaciones con ese mismo `"$PY"`.
Si aparece `externally-managed-environment`, detener esta modalidad y usar A.
No recomendar `sudo pip`, borrar `EXTERNALLY-MANAGED` o usar
`--break-system-packages` para eludir esa protección. `--user` también puede
estar restringido. `pip check` global puede detectar conflictos ajenos al proyecto.
No instalar con un Python y ejecutar con otro.

## Preparación adicional de runtimes para entropy

### Inventario posterior del entorno existente

Se registraron Python 3.10.12, OpenJDK 11.0.33, javac 11.0.33
y Node v24.22.2, con las cuatro consultas de versión satisfactorias.
La configuración completa pudo construirse y la clase Java estaba presente.

Rutas, hashes, comandos registrados y límites:
[Runtimes de entropy en Linux — 10 de noviembre de 2026](RUNTIMES_ENTROPY_LINUX_2026-11-10.md).

Ese diagnóstico no instaló runtimes ni recompiló la clase existente.
La recompilación posterior pertenece al ensayo de otra copia.
No se mezclan los hashes de la clase histórica con los de las clases
generadas después.

### Preparación y límites

El modo CLI predeterminado redundant utiliza módulos locales y proveedores
Python, Java y JavaScript. Instalar requirements.txt no instala Java
ni Node, ni compila las fuentes Java.

Antes de trabajar offline, preparar los componentes de la revisión
seleccionada y revisar entropy_python_config.py, entropy_java_config.py
y entropy_all_config.py. Cambiar PY selecciona el intérprete de los
comandos que contienen "$PY"; no modifica automáticamente todas las
rutas de proveedores definidas en esos módulos.

Los ejemplos siguientes corresponden a las rutas de la configuración
Linux ensayada. No constituyen una receta universal de instalación
de runtimes. Si no corresponden al equipo o a la revisión elegida,
detenerse y revisar la configuración; no crear enlaces o sustituir
ejecutables del sistema para aparentar coincidencia.

La preparación debe hacerse en una copia de trabajo nueva. No ejecutar
esta compilación sobre el proyecto de referencia o el laboratorio
histórico si se desea conservar sus clases y registros originales.

### Si faltan Java, el compilador, Node o la clase compilada

Las instrucciones siguientes comprueban y preparan componentes de la
configuración Linux ensayada; no instalan automáticamente los runtimes.

- Si falta `java`, preparar un runtime Java compatible y de procedencia
  comprobada para el equipo.
- Si falta `javac`, preparar un JDK compatible para compilar las fuentes.
  Tener `java` instalado no demuestra que exista un compilador.
- Si falta Node en la ruta configurada, preparar un runtime Node adecuado
  y revisar su procedencia, arquitectura y mantenimiento. Un `node`
  distinto disponible en `PATH` no sustituye esa ruta.
- Si falta `JavaEntropyProvider.class`, seguir el paso de compilación
  aunque las consultas de versión de Java y `javac` funcionen.
- Si ya existe `build/entropy_java`, revisar su contenido antes de
  recompilar. No borrarlo automáticamente ni sobrescribir compilados
  históricos para superar una comprobación.

El mensaje `Falta compilar JavaEntropyProvider.java.` indica que no
se encontró el archivo de clase exigido por la configuración. Puede
deberse a una compilación pendiente o a una copia o ruta de salida
incorrecta; por sí solo no demuestra que Java esté desinstalado.

Antes de iniciar la batería completa, realizar los pasos 1 a 4 de esta
preparación. El paso 3 compila las fuentes; el paso 4 construye los
comandos y comprueba los ejecutables seleccionados sin generar un
reporte. Esa comprobación previa no sustituye las pruebas funcionales.

La configuración conjunta prepara los comandos Java antes de que
algunas pruebas deshabiliten proveedores para simular modos reducidos
o de respaldo. Por ello, una clase ausente puede detener también una
prueba cuyo resultado final solo utilizaría el proveedor del sistema
operativo.

No convertir este error en una omisión de pruebas ni dar por validado
un respaldo automático. Los ensayos de ausencia de Java o Node deben
registrarse por separado. El modo `current` explícito sigue siendo una
elección distinta, no una reparación de la preparación redundante.

### 1. Comprobar fuentes y auxiliares de la revisión

Desde la raíz de la copia nueva, con PY definido:

```bash
ls -l \
  entropy_python_config.py \
  entropy_java_config.py \
  entropy_all_config.py \
  entropy_helpers/python_entropy_provider.py \
  entropy_helpers/JavaEntropyProbe.java \
  entropy_helpers/JavaEntropyProvider.java \
  entropy_helpers/node_entropy_probe.cjs \
  entropy_helpers/webcrypto_provider.cjs
```

Si falta alguno, revisar la copia o la revisión seleccionada antes
de continuar. No descargar un auxiliar aislado desde una rama mutable
para completar silenciosamente una versión distinta.

### 2. Identificar Java, javac y Node

Para las rutas ensayadas:

```bash
JAVA="/usr/lib/jvm/java-11-openjdk-amd64/bin/java"
JAVAC="/usr/lib/jvm/java-11-openjdk-amd64/bin/javac"
NODE="$HOME/.local/opt/bip39-node/node-v24.22.2-linux-x64/bin/node"

ls -l "$JAVA" "$JAVAC" "$NODE"
```

Después de revisar su procedencia y decidir que son confiables,
consultar por separado:

```bash
"$JAVA" -version
```

```bash
"$JAVAC" -version
```

```bash
"$NODE" --version
```

Para registrar su identidad local:

```bash
sha256sum "$JAVA" "$JAVAC" "$NODE"
```

Estos comandos no instalan runtimes ni contrastan sus hashes con
una firma o referencia externa confiable. El nombre de una carpeta
no prueba la versión ni el mantenimiento de su contenido.
No copiar binarios sin revisar origen, integridad y arquitectura.

La carpeta de usuario de Node no es un sandbox. Cambiar PATH o JAVA_HOME
no sustituye una ruta fijada en un módulo de configuración.
No cambiar el Python del sistema ni sustituir /usr/bin/node.

### 3. Compilar Java antes de construir la configuración completa

La configuración ensayada utiliza build/entropy_java y exige
JavaEntropyProvider.class. En la copia nueva, compilar las dos fuentes
con el compilador seleccionado:

```bash
(
    if [ -e build/entropy_java ]; then
        printf '%s\n' \
          'Detener: build/entropy_java ya existe. Revisar antes de recompilar.' >&2
        exit 1
    fi

    mkdir -p build/entropy_java || exit 1

    "$JAVAC" \
      -encoding UTF-8 \
      --release 11 \
      -d build/entropy_java \
      entropy_helpers/JavaEntropyProbe.java \
      entropy_helpers/JavaEntropyProvider.java
)
printf 'Codigo de compilacion Java: %s\n' "$?"
```

Continuar únicamente si la compilación termina con código 0.
Si falla, detenerse: la existencia del directorio de salida no
demuestra que la compilación haya finalizado correctamente.
No borrar automáticamente un build existente para repetir el paso.

Comprobar los resultados y registrar sus hashes:

```bash
ls -l \
  build/entropy_java/JavaEntropyProbe.class \
  build/entropy_java/JavaEntropyProvider.class

sha256sum \
  build/entropy_java/JavaEntropyProbe.class \
  build/entropy_java/JavaEntropyProvider.class
```

La copia ensayada compiló con código 0 y registró los hashes antes
de la batería. La clase Provider recompilada no fue binariamente
idéntica a la histórica. No se exige igualar aquel hash mediante
cambios de fuentes o compilador ni se declara compilación reproducible.

Las clases no forman parte del manifiesto de 49 archivos de esas
baterías. Para comprobar su conservación después de otras pruebas,
se necesita una comparación específica adicional.

### 4. Construir y revisar los comandos efectivos

Solo sobre una copia local de confianza, después de compilar:

```bash
"$PY" -B - <<'PY'
from pathlib import Path
import os
import sys

from entropy_all_config import build_all_provider_commands

commands = build_all_provider_commands()

for provider, command in commands.items():
    if not command:
        raise SystemExit("Proveedor sin comando: " + provider)

    executable_name, *arguments = command
    executable = Path(executable_name)

    if not executable.is_absolute():
        raise SystemExit("Ejecutable sin ruta absoluta: " + provider)

    if not executable.is_file() or not os.access(executable, os.X_OK):
        raise SystemExit("Ejecutable ausente o no ejecutable: " + provider)

print("Intérprete de esta comprobación:", sys.executable)

for provider, command in commands.items():
    print(provider, "=>", repr(command))

print("Configuración construida y ejecutables presentes.")
print("No se han adquirido aportaciones ni generado un reporte.")
PY
```

Revisar que los auxiliares y el classpath pertenecen a la copia nueva,
y que los ejecutables corresponden a los seleccionados.
La salida puede contener rutas personales: no publicarla sin revisar.

Construir estos comandos y comprobar que existen los ejecutables no
valida por sí solo el protocolo, la salud de las fuentes ni su
independencia. Las suites y pruebas funcionales se ejecutan después.
Una preparación inválida puede detener la operación; no se promete
respaldo automático para cualquier error.

### Current explícito y plazos

current explícito genera mediante os.urandom() sin intentar Java ni Node:

```bash
"$PY" bip39_seed_report.py -w 12 -n testnet --entropy-mode current
```

Es otro modo solicitado, no una aprobación de la preparación redundante.
El ejemplo genera un reporte ficticio y requiere una TTY y las
dependencias Python preparadas; no es una consulta de configuración.

El timeout predeterminado de entropy es de 10 segundos por proveedor,
positivo y finito; no es un plazo global ni limita contraseñas o visor.

## 4. Comprobar el programa y ejecutar las pruebas

Con la modalidad elegida y `PY` definido:

```bash
"$PY" --version
"$PY" -m pip check
"$PY" -m py_compile bip39_seed_report.py inspeccionar_reporte_cifrado.py test/ejecutar_bateria_local.py test/test_inspeccionar_reporte_cifrado.py test/test_ejecutar_bateria_local.py
```

Los siguientes comandos se ejecutan por separado:

```bash
"$PY" bip39_seed_report.py --run-tests --vectors-file test/vectors.json
```

La suite distribuida espera 24 casos BIP39. No es una auditoría de todas las derivaciones.

```bash
PYTHONPATH="$PWD" "$PY" test/test_inspeccionar_reporte_cifrado.py
```

En la copia local comprobada el 19 de noviembre de 2026, la suite del
inspector ejecutó 65 métodos y terminó con `OK`. Los 42 métodos de
la revisión anterior se conservan como referencia histórica, no
como expectativa de la suite ampliada. Si se utiliza otra revisión,
consultar sus fuentes y registrar el recuento realmente ejecutado.

```bash
PYTHONPATH="$PWD" "$PY" test/test_ejecutar_bateria_local.py
```

Para la integración local corregida se esperan 33 métodos y `OK`.
La revisión histórica del 5 de noviembre tenía 20; no mezclar expectativas.

```bash
"$PY" test/ejecutar_bateria_local.py
echo $?
```

La corrida local del 19 de noviembre de 2026, registrada en
`output/bateria_local_lcqnkkq3`, completó 26 etapas y acumuló
411 métodos unittest, con código `0`. El ejecutor registró 80/80
funciones o métodos del núcleo alcanzados y 50 archivos protegidos,
sin cambios de contenido ni del conjunto inventariado.

El núcleo de esa corrida tiene SHA-256
`bcae133d9d57c1e6923ef13e069d308e7f1773bb384f43d439796d8cc5d01787`.
Las clases Java se comprobaron por separado antes y después de
la batería y conservaron sus hashes. Estos controles no constituyen
cobertura completa de ramas ni verificación criptográfica independiente.

Como referencia histórica, la integración del 10 de noviembre completó
25 etapas, 362 métodos unittest, 73/73 y 49 archivos conservados.
El hito del 5 de noviembre tenía diez etapas y 70/70. Esos resultados
conservan su revisión y no se atribuyen al código posterior.

El número de archivos protegidos depende del árbol seleccionado;
no es un valor universal. Un equipo o revisión distintos deben
registrar su propio resultado:

- 0: automático completo según los controles del ejecutor.
- 1: fallo de proceso/registro/prueba o archivos protegidos modificados.
- 2: incompleto por omisiones, suites vacías, fallos esperados o inventario pendiente.
- 3: preparación incompleta.

Un `INCOMPLETO` con código de etapa 0 no es aprobación global. La batería registra
los resultados en una carpeta nueva bajo `output/`; conservarlos localmente.
Los ensayos manuales se registran aparte. No cambiar su estado dentro del JSON automático.
`py_compile` puede crear `__pycache__`; no publicarlo.

### Registro de la comprobación posterior en otra copia

La preparación del laboratorio del 10 de noviembre utilizó
.venv-instalacion-limpia, con pip 22.0.2. La batería original utilizó
.venv-regresion-entropy-cli, con pip 26.3. Los nombres de entorno
identifican esos ensayos; los ejemplos generales de esta guía utilizan
.venv-verificacion. No se presentan como el mismo venv.

En la copia se instalaron de nuevo las dependencias Python, se comprobó
pip check y se recompilaron las dos fuentes Java. Los runtimes base
existentes del mismo equipo se reutilizaron.

La batería proyecto/output/bateria_local_zelv2gy3 terminó con
25 etapas, 362 métodos unittest, inventario 73/73, 49 entradas
conservadas y código 0. La ejecución individual de los 33 métodos
del ejecutor no se añade otra vez al acumulado.

Los tres casos manuales posteriores se registran aparte:
redundante de 12 palabras, current explícito de 12 e interactivo
de 24, todos en testnet. En current se conservaron mensajes
satisfactorios, pero no códigos separados de generación y verificación.
El mantenedor confirmó visualmente la apertura, presentación y cierre
con Enter de la ventana temporal del caso interactivo.

Estos casos no sustituyen los seis manuales de la integración original
ni acreditan repetición de todos los timeouts, cancelaciones o errores.
La copia generó reportes nuevos: no demuestra recuperación offline
de un reporte anterior trasladado a otro equipo.

Detalle:
[Resultados de preparación de otra copia](../test/RESULTADOS_COPIA_ENTROPY_2026-11-10.md).

## 5. Generar un reporte ficticio y comprobarlo

En la integración local, el ejemplo siguiente solicita generación redundante
experimental por defecto; requiere la preparación adicional anterior.
Para elegir la primitiva conservada, añadir `--entropy-mode current`.
Las importaciones no adquieren aportaciones nuevas por estas opciones.

```bash
"$PY" bip39_seed_report.py -w 12 -n testnet
```

El reporte registra el modo realmente ejecutado y los estados de proveedores;
no interpretar una reducción o respaldo como cuatro aportaciones disponibles.

Introducir y confirmar la contraseña de exportación sin eco. No es la passphrase
BIP39. El uso sin `-i` de este ejemplo no solicita una passphrase BIP39: utiliza la vacía.
Para entrada guiada y passphrase BIP39 opcional:

```bash
"$PY" bip39_seed_report.py -i -n testnet
```

No proporcionar secretos por argumentos para eludir la lectura oculta.
No redirigir el flujo interactivo a archivos ni usar `tee` con contenido privado.

El exportador no reemplaza un destino existente: puede crear `_001`, `_002`, etc.
Copiar el comando completo del pie para inspeccionar el archivo realmente creado.
No ejecutar automáticamente una ruta de un ejemplo si el export tiene otro nombre.

Para la verificación de laboratorio del primer ejemplo (12 palabras/testnet/words,
passphrase BIP39 vacía), solicitar la ruta final sin comillas exteriores:

```bash
printf 'Ruta final del reporte cifrado que acaba de crear: '
IFS= read -r REPORTE
"$PY" test/verificar_export_laboratorio.py "$REPORTE" --words 12 --network testnet --input-mode words
```

Ajustar expectativas si se hizo otro ensayo. El ejemplo no crea el archivo
antes de verificarlo. Una ruta inexistente produce FileNotFoundError, no un error de cifrado.

## 6. Inspector y opciones de lectura

El inspector actual está limitado a Linux y requiere una terminal
interactiva. El comando completo del pie de exportación es el preferido.
Alternativamente, con `REPORTE` apuntando al archivo cifrado existente:

```bash
"$PY" inspeccionar_reporte_cifrado.py "$REPORTE"
```

El menú conserva las siguientes opciones:

- `1`: verificar sin imprimir contenido privado. Muestra el alcance
  de la comprobación realizada y vuelve al menú.
- `2`: revisar en una ventana de GNOME Terminal. Al finalizar
  correctamente la revisión, termina el inspector principal.
- `3`: revelar en la terminal actual después de una confirmación.
  Si se completa la revelación, termina el inspector.
- `4`: abrir el visor gráfico integrado de solo lectura, con búsqueda.
  Requiere una sesión gráfica y `tkinter` en el intérprete elegido.
  Pide confirmación antes de solicitar la contraseña en la terminal.
- `5`: abrir en la aplicación externa asociada a texto.
  ADVERTENCIA: crea una copia temporal sin cifrar. Requiere una sesión
  gráfica, `xdg-open` y una aplicación asociada a archivos `.txt`;
  no requiere Tk ni GNOME Terminal.
- `Q`: salir con código `0`.

El menú ofrece 360 segundos para seleccionar y pulsar Enter.
La confirmación de la opción `5` tiene su propio plazo de 360 segundos
y requiere escribir `s` para continuar; Enter por sí solo cancela
sin solicitar contraseña. Estos plazos no limitan la contraseña
ni el tiempo de lectura. Ctrl+C o EOF cancelan con código `1`.

Rechazar la confirmación de una operación devuelve el control al menú
sin solicitar contraseña. Los errores de autenticación en el menú no
activan una revelación alternativa. Al completar correctamente la
lectura en las opciones `2`, `3`, `4` o `5`, termina la inspección.

Las opciones de lectura autentican, descifran y reconocen el formato,
pero no sustituyen las comprobaciones de coherencia de la opción `1`.
Las expectativas de red, modo y palabras se contrastan mediante `1`
según su alcance. La entrada BIP32 directa no utiliza `--words`.

### Preparar el visor integrado para la opción 4

Desde una terminal de tu escritorio, con el mismo `PY` del inspector:

```bash
"$PY" -m tkinter
```

Cierra la demostración antes de abrir un reporte. Si falta `tkinter`
y se utiliza el Python de la distribución en Linux Mint 21.3 o
Ubuntu 22.04, puede prepararse mediante el paquete del sistema:

```bash
sudo apt install python3-tk
```

Esta instalación es una operación de preparación del equipo; no ejecutes
el inspector como root. Para un Python de otra procedencia, comprobar
cómo proporciona Tk esa instalación. No es necesario instalar Tk
para utilizar las demás opciones del inspector.

El visor no permite editar el reporte ni ofrece una función de guardado.
No crea deliberadamente un archivo descifrado, pero no protege contra
capturas de pantalla ni garantiza el borrado de memoria al cerrar.

### Preparar y usar la opción 5 con advertencia

Consultar el abridor y, si está disponible `xdg-mime`, la asociación
de archivos de texto:

```bash
command -v xdg-open
xdg-mime query default text/plain
```

La aplicación depende de la configuración del escritorio; no se impone
un editor concreto. En el ensayo local se abrió Xed. No continúes
si no confías en la aplicación asociada o en el equipo.

Después de aceptar la advertencia y autenticar el reporte, el inspector
escribe `reporte.txt` en un directorio temporal privado, con permisos
de archivo `0600`, y entrega su ruta a la aplicación externa. Utiliza
esa extensión tanto para contenido JSON como TXT, sin convertirlo.
El original cifrado no se modifica.

Cierra el documento externo y pulsa Enter en la terminal cuando se
indique para retirar la copia temporal. El retorno del abridor no
garantiza que el documento esté cerrado; puede regresar antes o
permanecer activo mientras la aplicación sigue abierta.

La aplicación puede permitir copiar, editar o guardar, y puede conservar
copias mediante respaldos, guardado automático o restauración de sesión.
El inspector intenta retirar su temporal, no esas copias externas.
Una terminación forzada puede dejar el temporal en el equipo.
Si se informa un fallo de limpieza, revisar la ruta local indicada.

Usa esta vía con datos ficticios de laboratorio. Que el editor muestre
«archivo no encontrado» al abrir una entrada reciente confirma únicamente
que esa ruta ya no está disponible, no un borrado seguro ni la ausencia
de otras copias.

La opción `3` y la ventana de la opción `2` también pueden dejar
contenido en el scrollback. Cerrar el proceso o la ventana no garantiza
borrado seguro.

Para el alcance completo y los riesgos de cada vía, consultar
[Revisar un reporte cifrado](../README.md#revisar-un-reporte-cifrado).

### Preparar GNOME Terminal para la opción 2

Solo si se desea esta opción y existe una sesión gráfica:

```bash
command -v gnome-terminal
command -v gsettings
```

En las preferencias de GNOME Terminal, crear un único perfil con nombre visible
`BIP39-revision`. En sus opciones de comando:

1. Al finalizar el comando, seleccionar cerrar/salir de la terminal
   (`exit-action` debe ser `close`, no `hold` ni `restart`).
2. Desactivar el comando personalizado (`use-custom-command` debe ser `false`).
3. No configurar contraseñas ni secretos en el perfil.

Los nombres visuales cambian con idioma/versión. El inspector comprueba esas
propiedades antes de abrir. Se requiere `DISPLAY` o `WAYLAND_DISPLAY` real;
no inventar sus valores para eludir una sesión gráfica ausente.
La revisión permanece abierta hasta Enter; cerrarla no garantiza borrado seguro.
Las opciones 1 y 3 no requieren GNOME Terminal.

## 7. Diagnóstico y conservación

- Fallo de instalación nativa: registrar Python/arquitectura y el error; no reducir
  versiones o parámetros criptográficos a ciegas. Puede requerir herramientas de
  compilación específicas del paquete; no se promete una instalación solo con wheels.
- Error TTY/GetPassWarning: ejecutar en una terminal local interactiva sin redirección.
- Fallo scrypt/memoria: revisar el equipo; no sustituir scrypt por SHA-256.
  `maxmem=512 MiB` es un límite configurado, no una reserva automática de 512 MiB.
- Error de enlaces duros o permisos: usar una carpeta y sistema de archivos compatibles
  y de confianza; no sustituir la publicación sin reemplazo por sobrescritura.
- Si una actualización cambia el hash del núcleo, comparar versión antes de usar
  una batería fijada a otro hash.

Conservar reportes y contraseñas según la guía de recuperación. No borrar un venv
que sea la única forma probada de recuperar un reporte hasta probar la recuperación
por otra vía. No publicar `output/`, backups, venv ni logs privados.

## Referencias y documentos relacionados

- [Resultados locales entropy CLI](../test/RESULTADOS_ENTROPY_CLI_2026-11-10.md)
- [README del proyecto](../README.md)
- [Guía de pruebas](../test/README.md)
- [Recuperación de reportes](RECUPERACION_REPORTES.md)
- Python venv: https://docs.python.org/3/library/venv.html
- Entornos administrados: https://packaging.python.org/en/latest/specifications/externally-managed-environments/
- Estado de Python: https://devguide.python.org/versions/
- Descargas ZIP: https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives
- [Resultados de preparación de otra copia](../test/RESULTADOS_COPIA_ENTROPY_2026-11-10.md)
- [Inventario de runtimes Linux](RUNTIMES_ENTROPY_LINUX_2026-11-10.md)
