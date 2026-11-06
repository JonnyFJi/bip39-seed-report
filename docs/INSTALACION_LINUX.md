# Instalación y ejecución en Linux

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

Debe coincidir el checksum y, para el commit de referencia, el valor mostrado arriba.
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

Para la referencia actual se esperan 42 métodos y `OK`.

```bash
PYTHONPATH="$PWD" "$PY" test/test_ejecutar_bateria_local.py
```

Se esperan 20 métodos y `OK`.

```bash
"$PY" test/ejecutar_bateria_local.py
echo $?
```

El hito Linux comunicado completó diez etapas, 70/70 e integridad de archivos
con código 0. Un equipo distinto debe registrar su propio resultado:

- 0: automático completo según los controles del ejecutor.
- 1: fallo de proceso/registro/prueba o archivos protegidos modificados.
- 2: incompleto por omisiones, suites vacías, fallos esperados o inventario pendiente.
- 3: preparación incompleta.

Un `INCOMPLETO` con código de etapa 0 no es aprobación global. La batería registra
los resultados en una carpeta nueva bajo `output/`; conservarlos localmente.
Los ensayos manuales se registran aparte. No cambiar su estado dentro del JSON automático.
`py_compile` puede crear `__pycache__`; no publicarlo.

## 5. Generar un reporte ficticio y comprobarlo

```bash
"$PY" bip39_seed_report.py -w 12 -n testnet
```

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

## 6. Inspector y ventana temporal

El comando del pie es el preferido. Alternativamente, con `REPORTE` definido:

```bash
"$PY" inspeccionar_reporte_cifrado.py "$REPORTE"
```

- 1: verificar sin imprimir contenido privado; vuelve al menú.
- 2: revisar en ventana GNOME; al finalizar correctamente termina el inspector.
- 3: revelar en esta terminal tras confirmación; al completar termina.
- Q: salir con código 0.
- Selección sin respuesta en 360 segundos: finaliza con código 1.
- Ctrl+C o EOF: cancelación controlada con código 1.

Los errores o la revelación rechazada permiten volver al menú. Nunca hay
revelación automática alternativa. El plazo solo limita selección: no contraseña,
confirmación ni tiempo de lectura del visor. La opción 3 deja contenido visible
en la terminal; terminar el proceso no borra el scrollback.

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

- [README del proyecto](../README.md)
- [Guía de pruebas](../test/README.md)
- [Recuperación de reportes](RECUPERACION_REPORTES.md)
- Python venv: https://docs.python.org/3/library/venv.html
- Entornos administrados: https://packaging.python.org/en/latest/specifications/externally-managed-environments/
- Estado de Python: https://devguide.python.org/versions/
- Descargas ZIP: https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives
