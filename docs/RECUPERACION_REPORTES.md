# Conservación y recuperación de reportes cifrados

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

## 1. Qué debe conservarse

| Elemento | Necesidad |
|---|---|
| Archivo cifrado íntegro | Imprescindible: contiene ciphertext, salt, nonce y metadatos |
| Contraseña de exportación | Imprescindible para derivar la clave de descifrado |
| Código compatible y versión/commit | Permite interpretar exactamente el formato |
| requirements.txt e instrucciones | Permiten preparar el entorno |
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

Para el inspector actual se necesitan tanto `inspeccionar_reporte_cifrado.py` como
`bip39_seed_report.py`. Este último importa mnemonic, bip-utils y cryptography:
conservar solamente el inspector no basta.

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

## 5. Recuperación mediante el inspector en Linux

Desde la raíz de la copia compatible, con las dependencias ya preparadas:

```bash
PY="$PWD/.venv-verificacion/bin/python"
"$PY" -c 'import sys; print(sys.executable)'
"$PY" -m pip check
```

Solicitar la ruta de la copia cifrada existente:

```bash
printf 'Ruta del reporte cifrado existente, sin comillas exteriores: '
IFS= read -r REPORTE
"$PY" inspeccionar_reporte_cifrado.py "$REPORTE"
```

Seleccionar 1 para comprobar sin mostrar. Con formato auto se reconoce JSON o TXT.
La comprobación TXT es menor; una JSON con passphrase no vacía no contrasta la seed
con ella. Un OK no verifica independientemente todas las direcciones.

Si es necesario leer el contenido, elegir 2 (perfil GNOME requerido) o 3 (confirmación
explícita). La guía Linux explica esos requisitos. No hay revelación automática tras
un fallo. La opción 3 puede persistir en scrollback. La opción 2 no garantiza borrado.

Un cierre con Q devuelve 0 aunque se haya producido un error previo en una operación:
el código final corresponde a Q. Timeout o Ctrl+C devuelven 1. Registrar lo que pasó,
no interpretar únicamente el código final como autenticación correcta.

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

```bash
PY="$PWD/.venv-verificacion/bin/python"
printf 'Ruta del archivo cifrado existente, sin comillas exteriores: '
IFS= read -r REPORTE
"$PY" local-private/autenticar_reporte_recuperado.py "$REPORTE"
echo $?
```

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
- [ ] He probado la recuperación de un archivo ficticio en otra carpeta/entorno.
- [ ] Si necesito recuperación offline, probé el kit sin conexión.
- [ ] No dependo de una ventana aún no implementada en mi SO.
- [ ] No publiqué reportes, claves o transcripciones privadas.

## Referencias

- [Instalación Linux](INSTALACION_LINUX.md)
- [Instalación Windows](INSTALACION_WINDOWS.md)
- [Instalación macOS](INSTALACION_MACOS.md)
- [Seguridad del proyecto](../SECURITY.md)
- [Pruebas](../test/README.md)
- Python venv: https://docs.python.org/3/library/venv.html
- Paquetes/entornos administrados: https://packaging.python.org/en/latest/specifications/externally-managed-environments/
- Estado de Python: https://devguide.python.org/versions/
