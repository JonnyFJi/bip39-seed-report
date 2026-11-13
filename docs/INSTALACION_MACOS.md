# Instalación y ejecución en macOS

## Alcance, versión y seguridad

Guía preparada inicialmente el 5 de noviembre de 2026 para la referencia
histórica c342c4ccd61b8434ed5581a70c25e9a8bc00689d y actualizada
documentalmente el 11 de noviembre para distinguirla de la integración
local entropy CLI del 10 de noviembre. No se atribuye un commit remoto
nuevo ni se declara una release.

El hito histórico Linux del 5 de noviembre registró 42 métodos del
inspector, 20 del ejecutor, diez etapas, 14 archivos protegidos
e inventario del núcleo 70/70.

La integración Linux local corregida del 10 de noviembre registró
42 métodos del inspector, 33 del ejecutor, 25 etapas, 362 métodos
unittest acumulados, inventario 73/73 y 49 entradas conservadas.
La comprobación posterior de otra copia Linux registró esos mismos
conteos, utilizando un venv nuevo y Java recompilado sobre runtimes
base existentes del mismo equipo.

Ninguno de esos resultados corresponde a macOS. Esta guía sigue
siendo una propuesta pendiente de ensayo para ese sistema.

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
2. Elegir y registrar la revisión que se desea comprobar. `Code` →
   `Download ZIP` descarga la rama disponible, pero no demuestra que
   contenga la integración local entropy CLI. El snapshot histórico es:
   [https://github.com/JonnyFJi/bip39-seed-report/archive/c342c4ccd61b8434ed5581a70c25e9a8bc00689d.zip](https://github.com/JonnyFJi/bip39-seed-report/archive/c342c4ccd61b8434ed5581a70c25e9a8bc00689d.zip)
   No utilizar ese enlace histórico como distribución de la integración nueva.
3. Extraer el ZIP completo; no abrir o ejecutar los scripts desde el visor del ZIP.
4. Entrar en la carpeta extraída que contiene `bip39_seed_report.py`,
   `inspeccionar_reporte_cifrado.py`, `requirements.txt` y `test/`.
   Esa carpeta es la raíz; no es `docs/` ni `test/`.

### Qué contiene el enlace ZIP histórico fijado

El enlace al commit c342c4ccd61b8434ed5581a70c25e9a8bc00689d
descarga el código histórico de referencia, no la integración local
entropy CLI del 10 de noviembre. Ese commit es anterior a la
incorporación de estas guías y su ZIP no contiene la carpeta docs/.

Para conservar también las guías, guardar los documentos de docs/
correspondientes a la revisión elegida, o descargar el contenido disponible
del repositorio mediante Code → Download ZIP. Registrar si las guías
y el código proceden de revisiones diferentes.

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

Este hash no se atribuye al ZIP histórico ni a una ejecución macOS.
No se afirma aquí que la integración local esté publicada en main.

Si se eligió otra revisión y el valor difiere, comparar esa revisión
antes de continuar; no regenerar el checksum para hacer desaparecer
la discrepancia.

## Estado específico

Esta es una guía propuesta y pendiente de ensayo macOS para la versión actual.
No existe una ejecución macOS registrada que certifique instalación o suites.
Los comandos siguientes no convierten ese estado en soporte aprobado.

El CLI actual del inspector rechaza macOS. No hay backend de ventana temporal
para Terminal.app/iTerm2 en esta versión. No instalar GNOME ni modificar
`sys.platform` para eludir esa restricción. Ver recuperación para las alternativas.

### Generación redundante y preparación pendiente

La integración local utiliza redundant de forma predeterminada para
generación nueva. Sus configuraciones ensayadas seleccionan rutas Linux
para Java y un ejecutable Node de usuario construido para Linux x64.
Esas rutas y binarios no deben copiarse a macOS como si fueran portables.

Instalar requirements.txt prepara paquetes Python, no instala Java o
Node ni compila las fuentes Java. La preparación redundante exige
revisar ejecutables, arquitectura, auxiliares y classpath de la copia.
Cambiar PATH, JAVA_HOME o PY no sustituye automáticamente todas las
rutas fijadas en los módulos de configuración.

No se ofrece aquí una receta de proveedores redundantes validada en
macOS. La compilación y comprobación realizadas en Linux no acreditan
el mismo resultado en Intel o Apple Silicon. No modificar el proyecto
de referencia para aparentar una preparación aprobada.

Los ejemplos de generación de esta guía solicitan current explícitamente,
basado en os.urandom() y sin intentar Java ni Node para esa generación.
Esto reduce los requisitos de adquisición del ejemplo, pero no acredita
compatibilidad macOS del conjunto ni hace utilizable el inspector Linux.
La batería integrada también incluye las suites de los proveedores
redundantes y necesita su propia preparación.

## 1. Preparar Python y abrir Terminal en la raíz

Preparar un Python mantenido de procedencia confiable; por ejemplo, el instalador
oficial de https://www.python.org/downloads/macos/ , o un gestor ya administrado
por el usuario. Verificar el instalador según su proveedor. No reemplazar componentes
de Apple ni cambiar enlaces del sistema.

Finder permite extraer el ZIP con doble clic. Entrar en la carpeta real que contiene
los scripts. En Terminal, escribir `cd ` (con espacio), arrastrar esa carpeta desde
Finder a la ventana y pulsar Enter; así se evitan rutas de ejemplo inexistentes.

```bash
pwd
ls -l bip39_seed_report.py inspeccionar_reporte_cifrado.py requirements.txt test/vectors.json
python3 --version
command -v python3
uname -m
```

Registrar si el entorno es Intel o Apple Silicon y la arquitectura efectiva de Python:

```bash
python3 -c 'import sys, platform; print(sys.executable); print(platform.machine())'
```

No mezclar wheels/venv de Intel, Apple Silicon, Linux o Windows.

## 2. Comprobar el núcleo

```bash
shasum -a 256 bip39_seed_report.py
shasum -a 256 -c bip39_seed_report.py.sha256
```

Comparar con el hash de la revisión realmente elegida: no intercambiar
la referencia histórica y la integración local indicadas arriba.
Si shasum no está disponible, calcularlo con Python, sin importar el proyecto:

```bash
python3 -c 'from pathlib import Path; import hashlib; print(hashlib.sha256(Path("bip39_seed_report.py").read_bytes()).hexdigest())'
```

Un hash diferente requiere comparar la revisión, no actualizar el valor esperado
para aceptar automáticamente el archivo.

## 3. Tres modalidades

### A. Venv sin activar: preferida

Crear solo si no existe:

```bash
python3 -m venv .venv-verificacion
```

Desde la raíz:

```bash
PY="$PWD/.venv-verificacion/bin/python"
"$PY" -c 'import sys; print(sys.executable); print("Venv:", sys.prefix != sys.base_prefix)'
```

Instalar por separado y detenerse si falla:

```bash
"$PY" -m pip install -r requirements.txt
```

```bash
"$PY" -m pip check
"$PY" --version
"$PY" -c 'import mnemonic, bip_utils, cryptography; print("Importaciones OK")'
```

En cada terminal nueva definir otra vez `PY` desde la raíz. No se requiere activar
el venv ni cambiar permisos de ejecución de los `.py`.

### B. Venv activado: alternativa para zsh/Bash

Esta modalidad requiere el mismo entorno que la modalidad A.
Si todavía no existe, crearlo desde la raíz:

```bash
python3 -m venv .venv-verificacion
```

No repetir la creación si ya existe.

```bash
source .venv-verificacion/bin/activate
python -c 'import sys; print(sys.executable); print(sys.prefix != sys.base_prefix)'
PY="$VIRTUAL_ENV/bin/python"
```

Si las dependencias todavía no están instaladas en este entorno:

```bash
"$PY" -m pip install -r requirements.txt
```

Solo después de una instalación satisfactoria:

```bash
"$PY" -m pip check
"$PY" -c 'import mnemonic, bip_utils, cryptography'
```

Usar el mismo `"$PY"` en las instrucciones posteriores. `deactivate` termina la
activación, pero no necesariamente borra la variable `PY` elegida antes.

### C. Intérprete no virtual

En una terminal sin activación:

```bash
PY="$(command -v python3)"
"$PY" -c 'import sys; print(sys.executable); print("Venv:", sys.prefix != sys.base_prefix)'
```

Debe indicar `Venv: False`. Solo si la política de ese Python lo permite:

```bash
"$PY" -m pip install --user -r requirements.txt
```

Comprobar luego dependencias e importaciones con ese mismo Python.
Homebrew u otros proveedores pueden marcarlo como administrado externamente.
Si pip lo rechaza, usar A: no `sudo pip`, no quitar el marcador y no recurrir
por defecto a `--break-system-packages`.

## 4. Pruebas propuestas

Con el intérprete preparado:

```bash
"$PY" -m pip check
"$PY" -m py_compile bip39_seed_report.py inspeccionar_reporte_cifrado.py test/ejecutar_bateria_local.py test/test_inspeccionar_reporte_cifrado.py test/test_ejecutar_bateria_local.py
```

Ejecutar por separado:

```bash
"$PY" bip39_seed_report.py --run-tests --vectors-file test/vectors.json
```

```bash
PYTHONPATH="$PWD" "$PY" test/test_inspeccionar_reporte_cifrado.py
```

```bash
PYTHONPATH="$PWD" "$PY" test/test_ejecutar_bateria_local.py
```

Para la integración local corregida del 10 de noviembre, los conteos
de referencia son 24 vectores, 42 métodos del inspector y 33 métodos
del ejecutor. El hito histórico del 5 de noviembre tenía 20 métodos
del ejecutor; no mezclar expectativas entre revisiones.

Son referencias del código y de los ensayos Linux, no resultados macOS
observados. La suite con simulaciones del inspector no demuestra que
su CLI o ventana estén disponibles en macOS.

No ejecutar la batería integrada como si bastara la instalación Python:
antes deben revisarse los requisitos de todas sus etapas y prepararse
los proveedores para la plataforma. Esta guía no da esa preparación
macOS por completada.

```bash
"$PY" test/ejecutar_bateria_local.py
echo $?
```

La batería de la integración local planifica 25 etapas. En Linux se
registraron 362 métodos unittest, inventario 73/73 y 49 entradas
conservadas; no son resultados ni garantías para macOS. El total
del manifiesto depende del árbol seleccionado, no es 49 universalmente.
El hito histórico del 5 de noviembre tenía diez etapas e inventario 70/70.

Registrar códigos y omisiones: 0 completo según los controles del
ejecutor; 1 fallo; 2 incompleto; 3 preparación. No se promete inventario
completo ni código 0 en macOS: existen casos específicos de Linux
y requisitos de proveedores que deben revisarse.

No cambiar el código para ocultar omisiones o aceptar una suite vacía.
Las pruebas manuales se registran aparte y no se convierten en una
aprobación dentro del resumen automático.

Si faltan wheels de dependencias nativas, puede requerirse compilación y herramientas
del proveedor; esta guía no afirma que Xcode Command Line Tools resuelva cualquier
fallo. No cambiar pins o descargar binarios desconocidos para forzar la instalación.

## 5. Ensayo de generación y verificación ficticia

Procedimiento propuesto para la integración local, no registrado como
ejecutado en macOS. Se solicita current explícitamente para no depender
de las rutas Linux de Java/Node durante esta generación.
No representa un respaldo automático ni valida el modo redundante:

```bash
"$PY" bip39_seed_report.py -w 12 -n testnet --entropy-mode current
```

Para el flujo guiado y passphrase BIP39 opcional:

```bash
"$PY" bip39_seed_report.py -i -n testnet --entropy-mode current
```

En el menú interactivo, elegir generación nueva para este ensayo.
Si se elige importar material, las opciones de entropy no lo convierten
en una adquisición nueva.

La contraseña de exportación no es la passphrase BIP39. En el primer ejemplo sin
`-i` se utiliza passphrase BIP39 vacía. No introducir secretos por argumentos.

Obtener la ruta final real, incluidos sufijos, y verificar el primer ejemplo:

```bash
printf 'Ruta final mostrada al exportar, sin comillas exteriores: '
IFS= read -r REPORTE
"$PY" test/verificar_export_laboratorio.py "$REPORTE" --words 12 --network testnet --input-mode words
```

Ese auxiliar tiene alcance de laboratorio. Ajustar expectativas para otros ensayos;
no usar `--test-passphrase` con secretos reales. La primera línea de contraseña es
interactiva; no redirigir stdin ni stdout.

No ejecutar el comando del inspector del pie como si ya estuviera portado: actualmente
se rechazará por plataforma. Para inspección completa, utilizar el entorno Linux
probado y seguir [RECUPERACION_REPORTES.md](RECUPERACION_REPORTES.md).

## 6. Conservación y diagnóstico

- No copiar el venv a otra máquina/arquitectura: reconstruirlo.
- Registrar versión de macOS, Python, arquitectura, dependencias, errores y omisiones.
- No atribuir al macOS actual el resultado histórico de Windows o Linux.
- La KDF requiere recursos: no reducirla ni sustituirla para ocultar errores.
- Los exports necesitan sistema de archivos compatible con enlaces duros y carpeta
  de confianza; no implementar sobrescritura para sortear una limitación.
- No publicar `output/`, claves, reportes, capturas privadas o el entorno completo.

## Referencias y documentos relacionados

- [Resultados de integración entropy CLI en Linux](../test/RESULTADOS_ENTROPY_CLI_2026-11-10.md)
- [Resultados de preparación de otra copia Linux](../test/RESULTADOS_COPIA_ENTROPY_2026-11-10.md)
- [Inventario de runtimes Linux](RUNTIMES_ENTROPY_LINUX_2026-11-10.md)
- [README del proyecto](../README.md)
- [Guía de pruebas](../test/README.md)
- [Recuperación de reportes](RECUPERACION_REPORTES.md)
- Python venv: https://docs.python.org/3/library/venv.html
- Entornos administrados: https://packaging.python.org/en/latest/specifications/externally-managed-environments/
- Estado de Python: https://devguide.python.org/versions/
- Descargas ZIP: https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives
