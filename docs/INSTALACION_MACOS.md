# Instalación y ejecución en macOS

## Alcance, versión y seguridad

Guía preparada el 5 de noviembre de 2026 para el código revisado en el commit
`c342c4ccd61b8434ed5581a70c25e9a8bc00689d`. No es una release ni declara soporte universal.
El hito Linux tiene 42 métodos del inspector, 20 del ejecutor, diez etapas
y un manifiesto de 14 archivos; el inventario 70/70 solo corresponde al núcleo.

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
2. En `Code` elegir `Download ZIP`, o descargar el snapshot del commit revisado:
   https://github.com/JonnyFJi/bip39-seed-report/archive/c342c4ccd61b8434ed5581a70c25e9a8bc00689d.zip
3. Extraer el ZIP completo; no abrir o ejecutar los scripts desde el visor del ZIP.
4. Entrar en la carpeta extraída que contiene `bip39_seed_report.py`,
   `inspeccionar_reporte_cifrado.py`, `requirements.txt` y `test/`.
   Esa carpeta es la raíz; no es `docs/` ni `test/`.

### Qué contiene el enlace ZIP fijado

El enlace al commit c342c4ccd61b8434ed5581a70c25e9a8bc00689d
descarga el código de referencia revisado. Ese commit es anterior
a la incorporación de estas guías y su ZIP no contiene la carpeta docs/.

Para conservar también las guías, guardar una copia de los cuatro
documentos publicados en docs/, o descargar el contenido actual del
repositorio mediante Code → Download ZIP.

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

Si se eligió otra revisión y el valor difiere, comparar esa revisión antes de
continuar; no regenerar el checksum para hacer desaparecer la discrepancia.

## Estado específico

Esta es una guía propuesta y pendiente de ensayo macOS para la versión actual.
No existe una ejecución macOS registrada que certifique instalación o suites.
Los comandos siguientes no convierten ese estado en soporte aprobado.

El CLI actual del inspector rechaza macOS. No hay backend de ventana temporal
para Terminal.app/iTerm2 en esta versión. No instalar GNOME ni modificar
`sys.platform` para eludir esa restricción. Ver recuperación para las alternativas.

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

Comparar con el hash de referencia de esta guía. Si `shasum` no está disponible,
calcularlo con Python, sin importar el proyecto:

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

Los conteos de referencia son 24 vectores, 42 métodos y 20 métodos, respectivamente.
Son expectativas del código, no resultados macOS observados. La suite simulada
del inspector no demuestra que su CLI o ventana estén disponibles en macOS.

```bash
"$PY" test/ejecutar_bateria_local.py
echo $?
```

La batería intenta diez etapas. Registrar códigos y omisiones: 0 completo según
los controles; 1 fallo; 2 incompleto; 3 preparación. No se promete 70/70 ni código 0
sobre macOS: hay casos específicos de Linux. No cambiar el código para ocultar
omisiones o aceptar una suite vacía. Las pruebas manuales se registran aparte.

Si faltan wheels de dependencias nativas, puede requerirse compilación y herramientas
del proveedor; esta guía no afirma que Xcode Command Line Tools resuelva cualquier
fallo. No cambiar pins o descargar binarios desconocidos para forzar la instalación.

## 5. Ensayo de generación y verificación ficticia

Procedimiento propuesto, no registrado como ejecutado aquí:

```bash
"$PY" bip39_seed_report.py -w 12 -n testnet
```

Para el flujo guiado y passphrase BIP39 opcional:

```bash
"$PY" bip39_seed_report.py -i -n testnet
```

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

- [README del proyecto](../README.md)
- [Guía de pruebas](../test/README.md)
- [Recuperación de reportes](RECUPERACION_REPORTES.md)
- Python venv: https://docs.python.org/3/library/venv.html
- Entornos administrados: https://packaging.python.org/en/latest/specifications/externally-managed-environments/
- Estado de Python: https://devguide.python.org/versions/
- Descargas ZIP: https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives
