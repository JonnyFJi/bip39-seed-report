# Compatibilidad esperada y comprobaciones por entorno

## Referencia del análisis

- Creación del documento: 10 de agosto de 2026.
- Actualización documental: 12 de octubre de 2026.
- Archivo analizado: bip39_seed_report.py.
- Repositorio: JonnyFJi/bip39-seed-report.
- Commit de referencia:
  `bbcff63daf5ca10b5a0f94218a660fc007e93b72`.
- SHA-256 del script de referencia:
  `365fafdfa71f9c0a91c088c4428335a5b96fbbce99434bff112d7152736bf55e`.

El hash identifica el script analizado, no este documento.
No certifica procedencia ni seguridad del entorno.

## Objetivo y alcance

Documentar las condiciones necesarias para instalar, probar y ejecutar
el programa, separando compatibilidad esperada de resultados realmente
observados.

Este análisis no certifica todas las versiones de Python, sistemas
operativos, arquitecturas, terminales o dependencias.

## Resumen

El proyecto está pensado para ejecutarse en distintos sistemas, pero el
soporte debe comprobarse para una combinación concreta de sistema,
arquitectura, Python, dependencias y terminal.

Los resultados comunicados hasta ahora corresponden al entorno local
del usuario. No permiten declarar soporte completo de Windows, macOS,
BSD o de todas las distribuciones Linux.

Pasar los vectores BIP39 no prueba por sí solo la entrada de terminal,
el cifrado, los permisos ni la escritura de archivos.

---

## Componentes que condicionan la compatibilidad

| Componente | Uso en el proyecto | Qué debe verificarse |
|---|---|---|
| Python | Intérprete, biblioteca estándar, terminal y archivos | Versión concreta y ejecución de todos los flujos |
| mnemonic | Wordlist y conversiones BIP39 | Versión instalada, lista efectiva y vectores |
| bip-utils | Seed y derivaciones | Versión instalada y resultados de referencia |
| cryptography | AES-256-GCM | Importación y ensayos de cifrado/autenticación |
| hashlib.scrypt | KDF del export | Disponibilidad y ejecución del perfil configurado |
| Terminal | Lectura oculta y decisiones | TTY, ausencia de eco, cancelación y timeout |
| Sistema de archivos | Temporales, reemplazo y permisos | Comportamiento y pruebas en el destino real |

`requirements.txt` fija las tres dependencias directas del entorno
de referencia.

Todavía no existe un bloqueo completo de dependencias transitivas
ni una instalación con verificación de hashes.

El 12 de octubre de 2026, el mantenedor comunicó una instalación
satisfactoria en .venv-verificacion y resultados correctos de pip check,
compilación, 24 vectores BIP39, 12 comprobaciones de cifrado y las
pruebas de GetPassWarning y normalización Unicode.

La evidencia corresponde a ese entorno Linux. No establece soporte
universal ni una instalación reproducible con hashes.

---

## Matriz de resultados registrados

| Entorno | Python y dependencias | Evidencia | Estado |
|---|---|---|---|
| Entorno local Linux inicial | Registro completo pendiente | Ensayos anteriores comunicados, incluidos flujos manuales | Limitado a esos ensayos |
| Entorno virtual Linux .venv-verificacion | mnemonic 0.21; bip-utils 2.9.3; cryptography 44.0.3. Python exacto, distribución y arquitectura pendientes de registrar | Instalación, pip check, compilación, 24 vectores BIP39, 12 comprobaciones de cifrado y pruebas de entrada segura | Satisfactorio para las comprobaciones comunicadas |
| Windows | Sin combinación registrada | Sin ejecución comunicada | Compatibilidad por comprobar |
| macOS | Sin combinación registrada | Sin ejecución comunicada | Compatibilidad por comprobar |
| BSD u otros | Sin combinación registrada | Sin ejecución comunicada | No establecido |

La fila Linux no representa todas las distribuciones ni todas las
arquitecturas. Deben añadirse distribución, versión, arquitectura,
Python y versiones de paquetes antes de usarla como matriz reproducible.

Los tests con mocks comprueban la política programada de rechazo y
normalización; no recrean todos los comportamientos de una terminal real.

---

## Preparación del entorno

Ejecutar desde la raíz de una copia local de confianza.

La instalación de dependencias debe prepararse antes de trasladar
el proyecto a un entorno offline. Los comandos usan las versiones directas de requirements.txt.
Todavía no constituyen una instalación completamente reproducible:
faltan bloqueo transitivo y hashes de artefactos. La instalación y las
suites indicadas se comprobaron en el entorno Linux comunicado; otros
entornos requieren validación específica.

### Linux/macOS: ejemplo con entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python --version
```

Estos comandos son una propuesta de preparación, no evidencia de que
todas las plataformas o versiones funcionen.

### Windows PowerShell: ejemplo con entorno virtual

Utiliza el comando de Python disponible y verificado en tu equipo.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe --version
```

No es necesario activar el entorno para utilizar su ejecutable explícito.
No desactives controles de seguridad ni eleves privilegios como paso
automático de esta guía.

---

## Generador del sistema y operaciones de archivo

### os.urandom()

El script solicita bytes mediante os.urandom(). La implementación
concreta depende de Python y del sistema operativo.

Este documento no atribuye una API interna únicamente a partir del
nombre o versión del sistema. Tampoco certifica la salud del generador,
la ausencia de compromisos ni un comportamiento siempre no bloqueante.

### Archivos temporales

write_secure_file() utiliza tempfile.mkstemp() indicando como directorio
la carpeta del destino.

Por tanto, el temporal no se crea necesariamente en /tmp o %TEMP%:
se crea junto al archivo de salida, según la ruta configurada.

En el flujo normal, el contenido se cifra antes de escribir el temporal.
Se realizan flush y fsync sobre el archivo y después os.replace().

Este mecanismo no garantiza ausencia de sobrescritura concurrente ni
todas las propiedades de durabilidad ante pérdida de alimentación.
Esas pruebas siguen pendientes.

### Permisos

El programa intenta aplicar 0o600. En sistemas que utilizan permisos
POSIX, ese modo limita los bits de lectura/escritura al propietario.

No equivale a una política completa de ACL de Windows. Tampoco elimina
riesgos de malware, procesos con privilegios, backups o sincronización.

El código actual ignora algunos errores de chmod; la interfaz puede
indicar exportación correcta sin certificar la política efectiva
de permisos.

### Rutas

Las rutas con espacios deben escribirse entre comillas.
No confundir la raíz del proyecto con la carpeta output.

La política actual de nombres secuenciales no es una reserva exclusiva
para dos procesos concurrentes.

---

## Requisitos de ejecución de la versión analizada

- Python y dependencias en una combinación probada.
- hashlib.scrypt disponible y capaz de ejecutar el perfil configurado.
- Memoria suficiente para la KDF.
- Carpeta de destino accesible para crear temporales y el archivo final.
- Terminal compatible cuando se solicitan secretos.

No se declara todavía un mínimo universal de Python. py_compile,
importación y suites deben ejecutarse con el intérprete objetivo.

### Perfil scrypt

La versión analizada utiliza:

- N = 2**18.
- r = 8.
- p = 1.
- dklen = 32.
- Salt de 16 bytes.
- maxmem = 512 MiB.

maxmem es el límite configurado para la implementación; no indica que
se reserve automáticamente toda esa memoria. La disponibilidad real
debe comprobarse mediante los tests en el equipo objetivo.

Si scrypt falla, no debe sustituirse automáticamente por SHA-256 directo
ni reducirse silenciosamente el perfil.

---

## Terminal y entrada sensible

read_hidden_secret() comprueba que stdin y stdout sean TTY.
Después utiliza getpass y rechaza GetPassWarning.

El flujo que solicita secretos no debe ejecutarse con entrada o salida
redirigida. Por ejemplo, -i con stdin desde /dev/null se rechaza.

Esto es una política del programa, no una certificación de que cualquier
TTY esté libre de capturas, malware o registros.

--run-tests y los tests automáticos que no leen secretos no requieren
esa interacción y pueden registrar su salida.

### Cancelación

La contraseña de exportación se solicita dentro del manejo de
EOF y Ctrl+C. También se manejan cancelaciones durante la construcción
del contexto y la exportación.

La cobertura debe comprobarse en cada terminal objetivo.

### Timeout

La decisión sobre contraseña corta usa la capa temporizada, con
360 segundos predeterminados.

No existe un timeout global para todo el flujo ni para todas las
lecturas de secretos. La decisión puede reiniciar su espera al recibir
una opción inválida.

La implementación de decisiones temporizadas utiliza mecanismos
distintos en Unix y Windows; ambos necesitan pruebas reales por entorno.

---

## Protocolo de comprobación

### Linux/macOS

Desde la raíz, con el intérprete del entorno preparado:

```bash
python -m py_compile bip39_seed_report.py
python bip39_seed_report.py --help
python bip39_seed_report.py --run-tests --vectors-file test/vectors.json
PYTHONPATH="$PWD" python test/test_cifrado_report.py
PYTHONPATH="$PWD" python test/test_entrada_segura.py
```

La invocación con PYTHONPATH está comprobada en el entorno Linux
comunicado. No debe generalizarse como prueba realizada en macOS.

### Windows PowerShell

Desde la raíz, con el entorno virtual del ejemplo anterior:

```powershell
.\.venv\Scripts\python.exe -m py_compile bip39_seed_report.py
.\.venv\Scripts\python.exe bip39_seed_report.py --help
.\.venv\Scripts\python.exe bip39_seed_report.py --run-tests --vectors-file test/vectors.json
```

Para los tests situados en test, puede usarse temporalmente la raíz
como ruta de importación. Esta propuesta debe probarse en Windows:

```powershell
$anterior = $env:PYTHONPATH
try {
    $env:PYTHONPATH = (Get-Location).Path
    .\.venv\Scripts\python.exe test/test_cifrado_report.py
    .\.venv\Scripts\python.exe test/test_entrada_segura.py
}
finally {
    $env:PYTHONPATH = $anterior
}
```

### Flujos manuales

Con material ficticio, comprobar:

- Contraseña vacía y confirmación diferente.
- Ctrl+C en primera contraseña y confirmación.
- Decisiones y/n/Enter/inválida/timeout.
- Rechazo sin TTY.
- Lectores de mnemonic, entropy binaria y hexadecimal.
- Passphrase vacía, discrepancia y reingreso.
- Mainnet/testnet y precedencia de -n.
- Exportación y descifrado del archivo realmente escrito.
- Permisos efectivos y fallos de escritura.

Las pruebas automáticas y manuales son complementarias.

---

## Datos que deben acompañar a cada resultado

Registrar:

- Fecha y commit o hash del script.
- Distribución y versión del sistema.
- Arquitectura.
- Python e implementación.
- Versiones de mnemonic, bip-utils y cryptography.
- Terminal utilizada.
- Suites y flujos ejecutados.
- Fallos y limitaciones observadas.

Comando para registrar Python y paquetes, usando el intérprete probado:

```bash
python -c 'import sys, platform; from importlib.metadata import version; print("Python:", sys.version); print("Implementación:", platform.python_implementation()); print("Arquitectura:", platform.machine()); print("Sistema:", platform.system(), platform.release()); print("Paquetes:", {n: version(n) for n in ("mnemonic", "bip-utils", "cryptography")})'
```

La versión del kernel no sustituye la distribución. En Linux, registrar
también los campos pertinentes de /etc/os-release.

No incluir secretos, exports privados o información innecesaria del
equipo en los logs publicados.

---

## Conclusión

La versión analizada tiene resultados satisfactorios en los ensayos
comunicados del entorno local, pero no una matriz completa de soporte.

La compatibilidad se establece para una combinación concreta de sistema,
arquitectura, intérprete, dependencias, terminal y sistema de archivos.

Pasar los vectores BIP39 no certifica todos los flujos. Windows, macOS,
BSD y otras combinaciones requieren pruebas específicas antes de
declararlas compatibles.

Ejecutar offline y sobre un entorno controlado reduce exposición, pero
no certifica seguridad. El proyecto permanece educativo y no se
recomienda con fondos reales.

---

## Referencias

- Python os.urandom(): https://docs.python.org/3/library/os.html
- Cryptography library: https://cryptography.io/
- bip-utils PyPI: https://pypi.org/project/bip-utils/
