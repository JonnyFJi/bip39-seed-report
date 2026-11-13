# Instalación y ejecución en Windows (PowerShell)

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
conteos, con un venv nuevo y Java recompilado sobre runtimes base
existentes del mismo equipo.

Estos resultados no corresponden a una nueva ejecución Windows.
Las instrucciones para la integración local siguen siendo propuestas
pendientes de ensayo en ese sistema.

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

Este hash no se atribuye al ZIP histórico ni a una ejecución Windows.
No se afirma aquí que la integración local esté publicada en main.

Si se eligió otra revisión y el valor difiere, comparar esa revisión
antes de continuar; no regenerar el checksum para hacer desaparecer
la discrepancia.

## Estado específico de esta guía

El ensayo histórico fue Windows 10 Home x64 con Python 3.10.11; no aprueba el
parche actual ni justifica instalar esa versión hoy. Estas instrucciones para
la versión actual son un procedimiento propuesto, pendiente de ejecución Windows.

El ensayo Windows comunicado el 22 de octubre de 2026 corresponde
al núcleo con SHA-256
df80621c8a2f2adef15c370783319c88ba4593f31ed92c03c08a0d5248cc9d3f.
No es el hash del hito Linux del 5 de noviembre ni el de la integración
local del 10 de noviembre. Sus resultados y omisiones se conservan en
[ANALISIS_COMPATIBILIDAD_SO.md](../ANALISIS_COMPATIBILIDAD_SO.md).

El núcleo conserva funciones multiplataforma, pero el CLI actual
`inspeccionar_reporte_cifrado.py` rechaza Windows. No intentar saltar esa
comprobación, simular Linux o instalar GNOME como supuesto arreglo.
Para inspección completa usar el entorno Linux probado; ver recuperación.

### Generación redundante y preparación pendiente

La integración local utiliza redundant de forma predeterminada para
generación nueva. Las configuraciones ensayadas seleccionan rutas Linux
para Java y un ejecutable Node de usuario construido para Linux x64.
No copiar esas rutas o binarios a Windows como si fueran portables.

Instalar requirements.txt prepara paquetes Python, no instala Java o
Node ni compila las fuentes Java. La preparación redundante exige
revisar ejecutables, arquitectura, auxiliares y classpath de la copia.
Cambiar PATH, JAVA_HOME o $PY no sustituye automáticamente todas las
rutas fijadas en los módulos de configuración.

No se ofrece aquí una receta redundante validada en Windows.
No cambiar las fuentes, el inspector o las pruebas para aparentar
una preparación aprobada o eliminar omisiones.

Los ejemplos de generación siguientes solicitan current explícitamente,
basado en os.urandom() y sin intentar Java ni Node para esa generación.
Esto no valida el modo redundante, la batería integrada ni el inspector
en Windows. Los flags nuevos corresponden a la integración local;
no deben aplicarse sin revisión al ZIP histórico que no los incorpora.

La batería integrada incluye las suites de los proveedores redundantes
y requiere su propia preparación, aunque se utilice current en un
ensayo manual separado.

## 1. Descargar, extraer y abrir PowerShell

En el Explorador, clic derecho sobre el ZIP y `Extraer todo`. Abrir la carpeta
extraída que contiene los archivos de la raíz, no ejecutar desde «Carpetas comprimidas».
En esa carpeta abrir PowerShell desde la barra de direcciones o «Abrir en Terminal».
Estos comandos son PowerShell, no CMD ni Bash.

```powershell
Get-Location
Get-Item .\bip39_seed_report.py, .\inspeccionar_reporte_cifrado.py, .\requirements.txt, .\test\vectors.json
py -3 --version
```

Si `py` no existe, preparar Python desde un proveedor confiable, por ejemplo
https://www.python.org/downloads/windows/ , y reabrir la terminal. Verificar la
identidad de su instalador según ese proveedor. Una instalación para usuario
no requiere ejecutar el programa como administrador.

`py -3` selecciona un Python 3 instalado; registrar cuál utiliza. Si se selecciona
otra versión explícita, utilizarla para crear el venv y no mezclar entornos.

## 2. Comprobar el núcleo

Elegir el hash esperado según la revisión seleccionada, antes de calcular
el hash del archivo. No deducir automáticamente el valor esperado a partir
del archivo que se intenta comprobar.

El bloque siguiente corresponde únicamente al núcleo local de la
integración del 10 de noviembre:

```powershell
$Esperado = 'b29675e5d91f52fd6c109a777b820945c01c12ef88e6f9926f61cc6e204e20d6'
$Actual = (Get-FileHash -Algorithm SHA256 -LiteralPath '.\bip39_seed_report.py' -ErrorAction Stop).Hash.ToLowerInvariant()

if ($Actual -ne $Esperado) {
    throw 'Hash diferente: comparar la revisión elegida antes de continuar.'
}

Write-Output 'Identidad del núcleo local seleccionado: coincide'
```

Si se eligió el ZIP histórico c342c4ccd61b8434ed5581a70c25e9a8bc00689d,
el valor esperado es
b09fcc4f292283b8d5e6f4470dc3858a079b209b1c3ccb579be27cdec51b5174.
En ese caso, sustituir únicamente la asignación de $Esperado por ese valor
histórico antes de ejecutar el bloque y utilizar las instrucciones
correspondientes a esa revisión.

El hash df80621c8a2f2adef15c370783319c88ba4593f31ed92c03c08a0d5248cc9d3f
identifica otra revisión: el ensayo Windows histórico del 22 de octubre.
No intercambiar los tres valores.

Estos hashes identifican el núcleo, no el ZIP ni todos los archivos.
La coincidencia no autentica por sí sola la procedencia del archivo
ni demuestra compatibilidad Windows. No reemplazar el hash esperado
por el recibido para forzar una coincidencia.

## 3. Elegir modalidad

Se recomienda A: no necesita activar scripts ni cambiar ExecutionPolicy.

### A. Venv sin activar

Crear solo si no existe:

```powershell
py -3 -m venv .venv-verificacion
```

Seleccionar y comprobar:

```powershell
$PY = Join-Path $PWD.Path '.venv-verificacion\Scripts\python.exe'
& $PY -c 'import sys; print(sys.executable); print(sys.prefix != sys.base_prefix)'
```

Debe mostrar el ejecutable del venv y `True`. El operador `&` permite ejecutar
la ruta aunque tenga espacios. Instalar y comprobar, por pasos:

```powershell
& $PY -m pip install -r requirements.txt
```

```powershell
& $PY -m pip check
& $PY --version
& $PY -c 'import mnemonic, bip_utils, cryptography'
```

Tras un comando Python, consultar inmediatamente `$LASTEXITCODE`. No interpretar
`$?` como si fuera el código numérico de salida de Bash.
En cada terminal nueva, volver a definir `$PY` desde la raíz.

### B. Venv activado

Esta modalidad también requiere crear el entorno e instalar dependencias.
Si .venv-verificacion todavía no existe, crearlo desde la raíz:

```powershell
py -3 -m venv .venv-verificacion
```

Si ya existe, no es necesario crearlo otra vez.

Si la política existente permite activar el script:

```powershell
.\.venv-verificacion\Scripts\Activate.ps1
python -c 'import sys; print(sys.executable); print(sys.prefix != sys.base_prefix)'
$PY = (Get-Command python).Source
```

Debe mostrar `True`. Usar después los comandos con `& $PY` de esta guía.

Si todavía no se instalaron las dependencias en este entorno, ejecutar:

```powershell
& $PY -m pip install -r requirements.txt
```

Solo después de una instalación satisfactoria:

```powershell
& $PY -m pip check
& $PY -c 'import mnemonic, bip_utils, cryptography'
```

Si la activación está bloqueada, utilizar la modalidad A; no cambiar
ExecutionPolicy únicamente para continuar con esta guía.

Para salir de la activación:

```powershell
deactivate
```

`$PY` puede seguir apuntando al venv: comprobarlo antes de cambiar de modalidad.

### C. Python no virtual

En una terminal sin activación, obtener el ejecutable no virtual del launcher:

```powershell
$PY = (py -3 -c 'import sys; print(sys.executable)').Trim()
& $PY -c 'import sys; print(sys.executable); print(sys.prefix != sys.base_prefix)'
```

Debe mostrar `False` para el venv. Solo si la política del intérprete lo permite:

```powershell
& $PY -m pip install --user -r requirements.txt
```

Después ejecutar `& $PY -m pip check` e importaciones. Si el intérprete está
administrado externamente o el paquete de usuario no es visible, usar A.
No instalar en Python de otra aplicación, con privilegios elevados o saltando
la política del proveedor.

## 4. Pruebas y códigos

Con `$PY` definido y las dependencias comprobadas:

```powershell
& $PY -m py_compile .\bip39_seed_report.py .\inspeccionar_reporte_cifrado.py .\test\ejecutar_bateria_local.py .\test\test_inspeccionar_reporte_cifrado.py .\test\test_ejecutar_bateria_local.py
$LASTEXITCODE
```

```powershell
& $PY .\bip39_seed_report.py --run-tests --vectors-file .\test\vectors.json
$LASTEXITCODE
```

La suite distribuida contiene 24 casos. Registrar el resultado real, sin asumir compatibilidad.
Para comprobar suites individuales, conservar el PYTHONPATH anterior:

```powershell
$AnteriorPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = $PWD.Path
    & $PY .\test\test_inspeccionar_reporte_cifrado.py
    if ($LASTEXITCODE -ne 0) { throw 'Falló la suite del inspector; detener y revisar.' }
    & $PY .\test\test_ejecutar_bateria_local.py
    if ($LASTEXITCODE -ne 0) { throw 'Falló la suite del ejecutor; detener y revisar.' }
}
finally {
    $env:PYTHONPATH = $AnteriorPythonPath
}
```

Las suites del inspector utilizan simulaciones: pueden probar funciones
sin que el CLI del inspector esté soportado en Windows. No confundir
su éxito con una ventana Windows implementada.

Para la integración local corregida, los conteos de referencia son
42 métodos del inspector y 33 del ejecutor. El hito histórico del
5 de noviembre tenía 20 métodos del ejecutor. Son referencias del
código y de los ensayos Linux, no nuevas ejecuciones Windows acreditadas
por esta guía.

La batería de la integración local planifica 25 etapas. En Linux se
registraron 362 métodos unittest, inventario 73/73 y 49 entradas
conservadas. Esos resultados no se atribuyen a Windows; el tamaño del
manifiesto depende del árbol y no es 49 universalmente.
El hito histórico del 5 de noviembre tenía diez etapas e inventario 70/70.

No ejecutar la batería integrada como si bastara la instalación Python.
Antes deben revisarse los requisitos de todas las etapas y prepararse
los proveedores para Windows; esta guía no da esa preparación por completada.

Solo después de resolver esa preparación, el comando propuesto para
registrar el resultado de la plataforma es:

```powershell
& $PY .\test\ejecutar_bateria_local.py
$LASTEXITCODE
```

- 0: automático completo para los controles ejecutados; no certifica la plataforma.
- 1: fallo de prueba/proceso/registro o archivos protegidos modificados.
- 2: incompleto, por ejemplo métodos omitidos o inventario no alcanzado.
- 3: preparación incompleta.

Hay métodos específicos de Linux/POSIX; no se promete código global 0 en Windows.
El registro histórico de escritura tuvo 10 métodos aprobados y 5 omitidos; no
convertirlo en resultado del código actual. Una omisión no es una aprobación.
Guardar los resultados locales y no alterar la batería para eliminar esas omisiones.

## 5. Generación ficticia y verificador de laboratorio

Procedimiento propuesto para la integración local, no registrado como
ejecutado en Windows. Se solicita current explícitamente para no
depender de las rutas Linux de Java/Node durante esta generación.
No representa un respaldo automático ni valida el modo redundante.

```powershell
& $PY .\bip39_seed_report.py -w 12 -n testnet --entropy-mode current
$LASTEXITCODE
```

Introducir la contraseña de exportación en la terminal. Este ejemplo sin `-i`
utiliza passphrase BIP39 vacía. Para el modo guiado:

```powershell
& $PY .\bip39_seed_report.py -i -n testnet --entropy-mode current
$LASTEXITCODE
```

En el menú, elegir generación nueva para este ensayo.
Si se elige importar material, las opciones de entropy no lo convierten
en una adquisición nueva.

No usar argumentos de mnemonic/passphrase real ni redirigir el flujo interactivo.
La ruta puede recibir un sufijo secuencial. Tomar el nombre final mostrado,
no suponer que el primer nombre sigue correspondiendo al último reporte.

Para el primer ejemplo (12 palabras/testnet/words/passphrase vacía):

```powershell
$Reporte = Read-Host 'Ruta final mostrada al exportar, sin comillas exteriores'
if (-not (Test-Path -LiteralPath $Reporte -PathType Leaf)) { throw 'No existe ese archivo.' }
& $PY .\test\verificar_export_laboratorio.py $Reporte --words 12 --network testnet --input-mode words
$LASTEXITCODE
```

El auxiliar es de laboratorio, con alcance documentado; no calcula todas las
direcciones independientemente. Si el ensayo tuvo otra red/longitud/modo, ajustar
las expectativas. No pasar una passphrase BIP39 real por `--test-passphrase`.

El comando del pie utiliza el mismo Python que generó el reporte, pero su
inspector CLI actualmente no funciona en Windows: detenerse ante ese mensaje,
no declararlo un fallo de la generación. Consultar recuperación.

## 6. Problemas frecuentes

- Ruta con espacios: usar `& $PY` y argumentos como variables o entre comillas.
- Comandos `python -c` con varias capas de comillas: evitar pegar comandos de Bash
  en PowerShell. Los ejemplos de consulta anteriores no incluyen comillas internas.
- Paquetes nativos sin wheel: registrar Python/arquitectura y error. Algunas
  dependencias pueden necesitar compilación; no existe garantía de instalación limpia
  en cualquier Windows. No descargar wheels arbitrarios de terceros como arreglo.
- Symlinks/ACL: no elevar privilegios solo para convertir omisiones en aprobaciones.
- Enlaces duros/publicación: no añadir sobrescritura como fallback.
- Guardar contraseñas/reportes fuera de la publicación; cerrar PowerShell no borra
  necesariamente registros, memoria o copias.

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
