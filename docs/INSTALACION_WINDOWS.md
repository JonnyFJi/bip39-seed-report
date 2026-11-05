# Instalación y ejecución en Windows (PowerShell)

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

## Estado específico de esta guía

El ensayo histórico fue Windows 10 Home x64 con Python 3.10.11; no aprueba el
parche actual ni justifica instalar esa versión hoy. Estas instrucciones para
la versión actual son un procedimiento propuesto, pendiente de ejecución Windows.

El núcleo conserva funciones multiplataforma, pero el CLI actual
`inspeccionar_reporte_cifrado.py` rechaza Windows. No intentar saltar esa
comprobación, simular Linux o instalar GNOME como supuesto arreglo.
Para inspección completa usar el entorno Linux probado; ver recuperación.

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

```powershell
$Esperado = 'b09fcc4f292283b8d5e6f4470dc3858a079b209b1c3ccb579be27cdec51b5174'
$Actual = (Get-FileHash -Algorithm SHA256 -LiteralPath '.\bip39_seed_report.py').Hash.ToLowerInvariant()
if ($Actual -ne $Esperado) { throw 'Hash diferente: comparar la versión antes de continuar.' }
Write-Output 'Hash del núcleo de referencia: coincide'
```

Este valor es el del commit de referencia, no el hash del ZIP. No reemplazar
el hash esperado por el recibido para forzar una coincidencia.

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

Si la política existente permite activar el script:

```powershell
.\.venv-verificacion\Scripts\Activate.ps1
python -c 'import sys; print(sys.executable); print(sys.prefix != sys.base_prefix)'
$PY = (Get-Command python).Source
```

Debe mostrar `True`. Usar después los comandos con `& $PY` de esta guía.
Si la activación está bloqueada, utilizar A; no es necesario cambiar
ExecutionPolicy ni utilizar `Bypass`. Para salir de la activación:

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

Las suites del inspector utilizan simulaciones: pueden probar funciones sin que
el CLI del inspector esté soportado en Windows. No confundir su éxito con una
ventana Windows implementada. El resultado esperado por el código de referencia
es 42 y 20 métodos, pero esta guía no acredita una ejecución Windows de ellos.

Batería propuesta para registrar el resultado de esta plataforma:

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

```powershell
& $PY .\bip39_seed_report.py -w 12 -n testnet
$LASTEXITCODE
```

Introducir la contraseña de exportación en la terminal. Este ejemplo sin `-i`
utiliza passphrase BIP39 vacía. Para el modo guiado:

```powershell
& $PY .\bip39_seed_report.py -i -n testnet
```

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

- [README del proyecto](../README.md)
- [Guía de pruebas](../test/README.md)
- [Recuperación de reportes](RECUPERACION_REPORTES.md)
- Python venv: https://docs.python.org/3/library/venv.html
- Entornos administrados: https://packaging.python.org/en/latest/specifications/externally-managed-environments/
- Estado de Python: https://devguide.python.org/versions/
- Descargas ZIP: https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives
