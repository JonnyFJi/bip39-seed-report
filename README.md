# BIP39 Seed Report (offline)

Proyecto educativo y experimental para generar, validar, derivar
y reportar material BIP39/BIP32.

No se recomienda usar con fondos reales. No es una wallet ni sustituye
a una hot wallet o una hardware wallet. No ha sido auditado de forma
independiente para uso en producción.

## Descripción del script

El programa permite generar o importar una mnemonic BIP39 inglesa,
obtener su seed y derivar material BIP32 y direcciones de ejemplo
en rutas BIP44, BIP49, BIP84 y BIP86, para mainnet o testnet.

No consulta la red Bitcoin, no obtiene saldos ni UTXO y no construye,
firma o transmite transacciones.

El reporte privado incluye material que puede controlar fondos.
Debe tratarse como secreto, incluso cuando esté cifrado.

## Funciones implementadas

- Generación de entropy mediante os.urandom() en longitudes BIP39 válidas.
- Conversión a mnemonics inglesas de 12, 15, 18, 21 o 24 palabras.
- Aceptación del resultado generado sin filtrar palabras repetidas.
- Importación de entropy hexadecimal, entropy binaria o mnemonic existente.
- Enumeración de candidatos para completar mnemonics de 11 o 23 palabras.
- Validación de longitud, wordlist y checksum BIP39.
- Conversión inversa de mnemonic a entropy.
- Derivación de seed con passphrase BIP39 y normalización Unicode NFKD.
- Derivación de material BIP32 y direcciones BIP44, BIP49, BIP84 y BIP86.
- Selección de mainnet o testnet.
- Indicadores descriptivos de patrón, sin score de seguridad.
- Exportación cifrada mediante scrypt y AES-256-GCM.
- Descifrado del formato histórico para compatibilidad.
- Entrada oculta centralizada con comprobación de TTY.
- Confirmación doble de passphrase y cancelación controlada.
- Bloqueo predeterminado de secretos por argumentos CLI.
- Comprobación local de la wordlist embebida y de la lista efectiva
  utilizada por mnemonic.

## Entorno de trabajo de esta etapa

El desarrollo y la verificación activa de esta etapa se realizan en Linux.
La referencia comprobada es Linux Mint 21.3 Virginia, x86_64, kernel
5.15.0-202-generic y CPython 3.10.12, con mnemonic 0.21,
bip-utils 2.9.3 y cryptography 44.0.3.

Windows y macOS quedan fuera del alcance activo y no bloquean este hito.
Su revisión queda diferida a quien ejecute el programa en esos sistemas.
Los resultados Windows históricos se conservan con su versión y sus
omisiones; no certifican el parche actual. La simulación de consola Windows
en Linux no constituye una ejecución Windows real.

## Modo interactivo recomendado

Desde la carpeta del proyecto:

```bash
python3 bip39_seed_report.py -i
```

Flujo:

1. Verifica localmente la wordlist.
2. Solicita y confirma la contraseña del reporte cifrado.
3. Permite elegir generación o importación del material de entrada.
4. En generación interactiva, permite elegir 12 o 24 palabras.
5. Solicita la red cuando no se proporcionó -n/--network.
6. Solicita y confirma la passphrase BIP39; puede quedar vacía.
7. Valida y deriva el material.
8. Muestra un resumen compacto sin secretos privados ni GAP limit.
9. Guarda el reporte privado cifrado, sin reducir el contenido.
10. Muestra la ruta final y comandos para autenticar o revelar el reporte.

La ruta predeterminada es:

```text
output/bip39_seed_report.json
```

Si el nombre solicitado está ocupado, el exportador intenta otro nombre
secuencial sin repetir el cifrado.

La publicación utiliza os.link() para crear el nombre final sin reemplazar
destinos existentes. La seguridad frente a colisiones no depende de una
comprobación previa de disponibilidad.

Requiere un sistema de archivos que admita enlaces duros y una carpeta
de salida de confianza. Las garantías quedan limitadas a las condiciones
probadas; no protegen frente a modificaciones hostiles de la ruta padre.

La entrada oculta exige una terminal interactiva en stdin y stdout.
El programa rechaza el fallback de getpass que no puede garantizar
ausencia de eco.

Esto no protege contra malware, keyloggers, capturas, registros externos
o un sistema comprometido. Los menús son visibles; no toda la entrada
del programa es oculta.

Las decisiones que utilizan la capa temporizada pueden cancelar tras
360 segundos sin respuesta. No existe un timeout global para todo el
flujo ni para todas las lecturas de secretos.

## Contraseñas diferentes

La passphrase BIP39 modifica la seed y las derivaciones.

La contraseña de exportación protege el archivo cifrado y no modifica
la seed BIP39.

Son valores distintos. No se sustituyen ni se recuperan mutuamente.

## Cifrado y protección de datos

Los exports nuevos utilizan:

- KDF: scrypt.
- Parámetros: N=2**18, r=8, p=1, dklen=32.
- Salt aleatorio de 16 bytes.
- Cifrado autenticado AES-256-GCM.
- Nonce aleatorio de 12 bytes.
- Contenedor JSON versionado con parámetros KDF.
- Metadatos definidos autenticados mediante AAD.

El parámetro maxmem de scrypt se configura en 512 MiB. Es un límite
permitido por la implementación, no una reserva automática de toda
esa memoria. El perfil debe probarse en el equipo objetivo.

El flujo normal serializa y cifra el reporte una sola vez. Después escribe
un temporal en la carpeta de destino y completa flush y fsync del archivo
antes de publicar el nombre final mediante os.link().

Si el nombre está ocupado, intenta otro nombre secuencial. No utiliza
os.replace() como alternativa y no repite la KDF por cada colisión.

En sistemas POSIX se aplica 0o600 mediante fchmod sobre el descriptor antes
de publicar. Si esa operación falla, la publicación se aborta. Esto no
equivale a verificar las ACL de Windows ni protege un sistema comprometido.

La publicación requiere enlaces duros y una carpeta de confianza.
No garantiza durabilidad del directorio ante pérdida de alimentación.
Una interrupción abrupta puede dejar un temporal que necesite revisión.

La función write_secure_file() conserva el destino exacto y falla si ya
existe. export_seed_report() utiliza reintentos secuenciales y devuelve
la ruta realmente publicada.

El formato histórico ENCRYPTED: puede descifrarse por compatibilidad
y muestra una advertencia. Los exports nuevos no utilizan el método
histórico de SHA-256 directo de contraseña.

Descifrar un archivo histórico no lo fortalece automáticamente:
para migrarlo debe volver a cifrarse con el formato actual.

La limpieza del historial del proceso Python no borra el historial
del shell, scrollback, capturas, memoria, swap ni backups.

## Pruebas

Desde la raíz del proyecto:

```bash
python3 -m py_compile bip39_seed_report.py
python3 bip39_seed_report.py --run-tests --vectors-file test/vectors.json
```

La suite distribuida está en test/vectors.json.

Sin --vectors-file, el script localiza esa suite respecto de la carpeta
del propio script. Una ruta indicada explícitamente conserva la
resolución habitual de rutas de la ejecución.

```bash
python3 bip39_seed_report.py --run-tests
```

Resultado esperado con la suite distribuida:

```text
Test vectors BIP39: OK (24 casos)
```

Las pruebas adicionales están en la carpeta test.

Desde la raíz del proyecto, en el entorno Linux preparado y con una copia
local de confianza:

```bash
PYTHONPATH="$PWD" python3 test/test_cifrado_report.py
PYTHONPATH="$PWD" python3 test/test_entrada_segura.py
PYTHONPATH="$PWD" python3 test/test_contenedor_report.py
PYTHONPATH="$PWD" python3 test/test_escritura_report.py
PYTHONPATH="$PWD" python3 test/test_regresion_vectores_ultima_palabra.py
PYTHONPATH="$PWD" python3 test/test_ux_terminal_report.py
PYTHONPATH="$PWD" python3 test/test_revision_integral_report.py
```

Ejecuta esos comandos desde la raíz y compruébalos en una descarga limpia.

Los vectores BIP39 verifican los casos ejecutados de conversión
entropy-mnemonic, derivación de seed y round-trip. No constituyen una
auditoría ni verifican todas las derivaciones o claves extendidas.

La suite de regresión del runner y última palabra comprueba rechazo
de suites vacías y entradas mal formadas, errores previstos, casos
positivos y búsqueda real de candidatos. Incluye nueve métodos con
subcasos y no verifica el cuarto campo BIP32.

La comprobación de ausencia de éxito captura directamente la salida
del runner. Una prueba de mutación confirma que detecta un runner
ficticio que imprime OK antes de fallar, sin modificar el script real.

La prueba de cifrado comprueba recuperación, rechazo de contraseña
incorrecta, alteraciones, perfil KDF y compatibilidad histórica.

La prueba de entrada segura comprueba el rechazo simulado de
GetPassWarning y la confirmación/normalización Unicode.

Las pruebas usan exclusivamente material ficticio. No introduzcas
secrets reales en los tests.

La suite del contenedor comprueba estructura, tipos, claves duplicadas,
base64 y límites. Verifica rechazos antes de ejecutar la KDF e incluye
casos positivos con scrypt real y compatibilidad histórica.

La suite de escritura comprueba preservación de destinos existentes,
colisiones, fallos simulados, publicación del contenido completo y
concurrencia con hilos. Incluye pruebas POSIX, enlaces simbólicos y
una prueba multiproceso específica de Linux.

Las omisiones dependen de la plataforma y deben registrarse: no son
casos aprobados.

El auxiliar test/verificar_export_laboratorio.py permite verificar
manualmente un export sin imprimir su contenido privado. Requiere una
terminal interactiva y no forma parte de las suites automáticas.

Para ejecutar la batería secuencial y registrar entorno, hashes e inventario:

```bash
python3 test/ejecutar_bateria_local.py
```

Consulta [test/README.md](test/README.md) para ejecución y alcance, y
[ANALISIS_COMPATIBILIDAD_SO.md](ANALISIS_COMPATIBILIDAD_SO.md) para los
entornos y resultados registrados.

## Indicadores informativos de patrón

El script calcula indicadores superficiales de patrón y los conserva
sin pérdida en el reporte privado. La terminal compacta no enumera
sus estadísticas; --show-all mantiene la presentación detallada.
No estiman entropía criptográfica ni imprevisibilidad, ni
determinan cómo se generó la mnemonic. Una mnemonic aleatoria válida puede
contener palabras repetidas o índices consecutivos. No uses estos indicadores
para aceptar o descartar una seed.

## Tipos de dirección soportados

| Estándar | Ruta de derivación | Tipo de address | Descripción |
|----------|-------------------|-----------------|-------------|
| **BIP44** | m/44'/0'/0'/0/i | P2PKH | Legacy (direcciones que empiezan con 1) |
| **BIP49** | m/49'/0'/0'/0/i | P2WPKH-P2SH | Nested SegWit (direcciones que empiezan con 3) |
| **BIP84** | m/84'/0'/0'/0/i | P2WPKH | Native SegWit (direcciones que empiezan con bc1q) |
| **BIP86** | m/86'/0'/0'/0/i | P2TR | Taproot (direcciones que empiezan con bc1p) |

Cuenta 0, cadena externa (change 0), 5 direcciones por ruta

La tabla muestra ejemplos de mainnet. En testnet se utiliza coin_type=1'
en lugar de 0' y las codificaciones correspondientes a esa red.

El programa deriva cuenta 0, cadena externa 0 y cinco direcciones por
familia, con índices 0 a 4.

El rótulo GAP limit del reporte representa actualmente la cantidad
de direcciones derivadas. No implica descubrimiento de actividad:
el programa no consulta blockchain ni busca direcciones usadas.

## Dependencias

```bash
python3 -m pip install -r requirements.txt
```

`requirements.txt` fija las dependencias directas del entorno de referencia.
Todavía no representa un bloqueo completo de dependencias transitivas
ni una instalación con verificación de hashes.

## Instalación

### 1. Verificar Python 3

```bash
python3 --version
```

Utiliza una versión de Python y dependencias que hayas probado con
este proyecto. El mínimo de compatibilidad y la matriz de plataformas
todavía no están formalmente establecidos.

Registra la versión del intérprete y de las dependencias al ejecutar
las pruebas. La instalación exitosa no certifica todos los flujos.

### 2. Instalar librerías requeridas

```bash
python3 -m pip install -r requirements.txt
```

### 3. Verificar instalación

```bash
python3 -c "from mnemonic import Mnemonic; from bip_utils import Bip44; from cryptography.hazmat.primitives.ciphers.aead import AESGCM; print('✅ Importaciones principales correctas')"
```

Esta comprobación confirma que esas importaciones funcionan con
el intérprete utilizado. No verifica por sí sola las versiones fijadas,
la consistencia de todos los requisitos ni los flujos del programa.

Consulta [test/README.md](test/README.md) para la preparación del entorno
y las pruebas.

### 4. Vectores distribuidos

El repositorio incluye la suite en test/vectors.json. Conserva la copia que corresponde
a la versión analizada; no la reemplaces automáticamente desde una rama
remota mutable.

Puedes indicar otra suite explícitamente con --vectors-file.

El runner rechaza suites vacías y valida la estructura completa antes
de ejecutar las conversiones. Si la raíz es un objeto JSON, exige
el bloque english; también admite listas directas de vectores ingleses.

Los errores previstos de lectura, UTF-8, JSON y formato, así como
las discrepancias en los resultados, terminan con un mensaje de error
y código de salida 1.

Los vectores de cuatro campos siguen sin verificar el campo de clave
extendida BIP32.

## Uso del script

### Comandos y opciones

```bash
python3 bip39_seed_report.py --help
```

Entradas disponibles:

- -w/--words: genera una mnemonic de 12, 15, 18, 21 o 24 palabras.
- --entropy-bin: importa entropy binaria.
- --entropy-hex: importa entropy hexadecimal.
- --mnemonic: importa una mnemonic completa.
- --mnemonic-incomplete: enumera candidatos para 11 o 23 palabras.

Debe resolverse una sola entrada. El modo -i ofrece un menú cuando
no se proporcionó una entrada.

Opciones generales:

- -i/--interactive: lectura interactiva de secretos sin eco en una TTY.
- -n/--network: mainnet o testnet.
- -f/--format: contenido interno JSON o texto.
- -o/--output: destino; por defecto output/bip39_seed_report.json.
- --audit-passphrase: incluye el análisis descriptivo en el reporte;
  la vista compacta indica su inclusión y --show-all muestra sus detalles.
  No estima la entropy real de la passphrase.
- --show-all: revela material privado en terminal; solo para pruebas.
- --run-tests: ejecuta la suite indicada y termina sin exportar.
- --vectors-file: ruta explícita de la suite. Si se omite, utiliza test/vectors.json respecto de la carpeta del script.
- --allow-insecure-cli-secrets: permiso explícito para argumentos
  sensibles exclusivamente en pruebas controladas.

### Política de secretos CLI

--entropy-bin, --entropy-hex, --mnemonic, --mnemonic-incomplete y
-p/--passphrase están bloqueados por defecto.

El bloqueo reconoce presencia explícita, incluso un valor vacío
como -p "". Usar -i no evita el bloqueo.

Para pruebas ficticias puede habilitarse
--allow-insecure-cli-secrets. No evita exposición en historial,
argumentos del proceso o registros.

--run-tests no admite opciones sensibles por argumentos, aunque
se proporcione el permiso.

El bloqueo no borra un valor que ya llegó al shell o al proceso.
Los mensajes estándar de errores sintácticos del parser no tienen
una política completa de redacción.

### Ejemplos de uso

#### 1. Generar mnemonic nueva (12 palabras, mainnet)

```bash
python3 bip39_seed_report.py -w 12
```

**Flujo:**
1. Pide contraseña para encriptar
2. Genera 12 palabras aleatorias
3. Realiza validación e indicadores informativos de la mnemonic
4. Usa red mainnet (default)
5. Oculta datos sensibles en terminal
6. Guarda archivo encriptado en `output/bip39_seed_report.json`

Sin -i, una passphrase BIP39 no se solicita interactivamente.
Si no se suministra, se utiliza la passphrase vacía.
Para introducirla sin eco, utiliza el modo -i.

#### 2. Generar mnemonic nueva (24 palabras, testnet)

```bash
python3 bip39_seed_report.py -w 24 -n testnet
```

**Flujo:**
1. Pide contraseña para encriptar
2. Genera 24 palabras aleatorias
3. Realiza validación e indicadores informativos
4. Usa red testnet
5. Oculta datos sensibles en terminal
6. Guarda archivo encriptado

Sin -i, una passphrase BIP39 no se solicita interactivamente.
Si no se suministra, se utiliza la passphrase vacía.
Para introducirla sin eco, utiliza el modo -i.

#### 3. Modo interactivo (menú guiado)

```bash
python3 bip39_seed_report.py -i
```

**Flujo:**
1. Pide contraseña
2. Muestra menú interactivo:
   - Seleccionar tipo de entrada (1-5)
   - Seleccionar longitud (12 o 24 palabras)
   - Seleccionar red (mainnet o testnet)
   - Ingresar passphrase (opcional)
3. Genera, importa o reconstruye el material según la opción elegida
   y valida la entrada.
4. Deriva la seed, claves y direcciones, y presenta el resumen compacto.
5. Guarda el reporte cifrado.

#### 4. Modo educativo: revelar secretos en terminal

```bash
python3 bip39_seed_report.py -w 12 --show-all
```

Flujo:

1. Solicita y confirma la contraseña de exportación.
2. Genera una mnemonic de 12 palabras.
3. Revela entropy, mnemonic, seed, clave raíz y las claves privadas
   incluidas en la vista de terminal.
4. Muestra validación e indicadores descriptivos de patrón,
   sin score de seguridad.
5. Guarda el reporte cifrado.

--show-all desactiva la ocultación de secretos en la vista de terminal,
pero no convierte esa vista en una reproducción completa del JSON privado.
Se sigue mostrando solo la primera dirección de cada familia.
GAP limit no se muestra en terminal; su valor y significado quedan
conservados en los reportes.

La salida puede revelar material suficiente para controlar fondos.
No la redirijas a logs ni la compartas.

⚠️ **ADVERTENCIA**: utiliza --show-all exclusivamente con material ficticio
en pruebas educativas. El programa no está auditado para producción
y no se recomienda usar con fondos reales.

#### 5. Verificar mnemonic existente

```bash
python3 bip39_seed_report.py \
  --allow-insecure-cli-secrets \
  --mnemonic "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about" \
  -p "TREZOR" \
  -n testnet
```

Vector público de prueba; nunca utilizar este material para fondos.
El programa todavía solicita una contraseña de exportación en una TTY.

**Flujo:**
1. Pide contraseña
2. Verifica checksum BIP39
3. Valida la mnemonic y conserva los indicadores descriptivos
   en el reporte privado.
4. Calcula seed y derivaciones
5. Guarda archivo encriptado

#### 6. Calcular última palabra (recuperación)

```bash
python3 bip39_seed_report.py \
  --allow-insecure-cli-secrets \
  --mnemonic-incomplete "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon" \
  -n testnet
```

**Flujo:**
1. Busca todas las palabras posibles
2. Muestra lista numerada
3. Pide al usuario seleccionar la correcta
4. Debes verificar manualmente la palabra elegida.
5. Genera mnemonic completa
6. Realiza Validación e indicadores

Enumera candidatos que producen una mnemonic BIP39 válida y solicita una selección explícita.

El checksum no identifica por sí solo la palabra originalmente utilizada.
Si ocurre EOF durante la selección, la operación aborta; no toma automáticamente el primer candidato.

La recuperación debe contrastarse con una referencia independiente.

#### 7. Usar entropía hexadecimal

```bash
python3 bip39_seed_report.py \
  --allow-insecure-cli-secrets \
  --entropy-hex 00000000000000000000000000000000 \
  -n testnet
```

**Requisitos y formato recomendado:**

- El contenido hexadecimal debe representar 16, 20, 24, 28 o 32 bytes:
  32, 40, 48, 56 o 64 dígitos hexadecimales, sin contar el prefijo
  opcional ni los espacios admitidos.
- Formato recomendado: dígitos 0-9 y a-f, sin espacios ni prefijo.
- El parser también admite mayúsculas, espacios ASCII y un prefijo 0x.

Los ceros son datos públicos completamente predecibles.

#### 8. Usar entropía binaria

```bash
python3 bip39_seed_report.py --allow-insecure-cli-secrets --entropy-bin 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 -n testnet
```

**Requisitos y formato recomendado:**

- Longitud válida de 128, 160, 192, 224 o 256 bits.
- Formato recomendado: una secuencia de 0 y 1 sin espacios.
- El parser elimina los espacios ASCII antes de validar los bits
  y su longitud.

Para pruebas, puedes usar una secuencia conocida; no atribuyas seguridad a una entrada manual por tener la longitud y checksum correctos.
Esta secuencia de ceros es pública y completamente predecible.
El ejemplo no debe utilizarse para proteger fondos.

#### 9. Ejecutar los vectores BIP39 distribuidos

```bash
python3 bip39_seed_report.py --run-tests --vectors-file test/vectors.json
```

**Resultado esperado:**
Test vectors BIP39: OK (24 casos)

#### 10. Auditoría de passphrase

```bash
python3 bip39_seed_report.py -i --audit-passphrase -n testnet
```

El reporte conserva los siguientes datos descriptivos. En terminal se
muestran con --show-all; en compacto se indica su inclusión:
- Número de caracteres
- Bytes UTF-8
- Caracteres distintos
- Presencia de mayúsculas, minúsculas, dígitos, símbolos, espacios
- Nota informativa; no calcula entropía real

## Flujo de trabajo de prueba recomendado

1. Ejecutar los tests desde una copia limpia.
2. Ejecutar el modo interactivo:

```bash
python3 bip39_seed_report.py -i -n testnet
```

3. Utilizar exclusivamente material ficticio.
4. Revisar el resumen del reporte.
5. Comprobar el descifrado del archivo realmente escrito.
6. Registrar versión, hashes y resultados, sin secrets.
7. Conservar el archivo original cifrado mientras se verifica la prueba.

Eliminar archivos no garantiza borrado irrecuperable. No mezclar
pruebas con material de recuperación real.

## Salida del script

La vista predeterminada es compacta: muestra entrada, red, estado BIP39,
número de palabras, presencia de passphrase, rutas, claves públicas
extendidas disponibles y la primera dirección de cada familia.
No muestra entropy, seed, claves privadas, estadísticas detalladas ni
GAP limit. Las direcciones y claves públicas extendidas son correlacionables.

--show-all revela secretos y detalles de la vista de terminal, pero mantiene
solo la primera dirección de cada familia, índice 0. No imprime todo el JSON
ni muestra GAP limit. Utilizarlo solo con material ficticio.

Los reportes privados conservan el contenido anterior. El contexto JSON
normal añade report_notices, con version, general, input y privacy.
Ese versionado informativo no cambia la versión 1 del contenedor cifrado.
El TXT mantiene su contenido y añade los avisos. GAP limit se explica en
los reportes como cantidad de direcciones generadas, no descubrimiento
de actividad: no se consulta blockchain, saldo ni UTXO.

Las verificaciones de ambas wordlists, errores, contraseñas, cancelaciones
y decisiones de seguridad siguen activas aunque se reduzcan mensajes
de éxito. Si se solicita --audit-passphrase, el cálculo y los campos se
conservan en el reporte; en compacto se indica su inclusión y los detalles
se muestran con --show-all.

### Pie de revisión

El pie usa el intérprete del entorno y la ruta final realmente publicada,
incluidos sufijos secuenciales. Los comandos deben ejecutarse desde la raíz.
La contraseña requerida es la de exportación, no la passphrase BIP39.

Sin passphrase BIP39 se ofrece el auxiliar de laboratorio con los argumentos
reales. Con passphrase no vacía se ofrece autenticación sin imprimir secretos,
y se declara que no se contrasta la seed. No se incrusta la passphrase privada.

La revelación completa se ofrece como un segundo comando con advertencia.
No se ejecuta ni se crea una copia descifrada automáticamente.

## Seguridad operacional

Trabajar sin red reduce vías de exposición, pero no prueba que el
equipo, el intérprete o las dependencias sean confiables.

Una máquina virtual, un sistema Live USB o un firewall no certifican
por sí solos ausencia de malware, capturas o persistencia de secretos.

No usar material real en estas pruebas. No copiar secrets automáticamente,
no publicar exports y no tratar limpiar pantalla o borrar archivos como
borrado seguro.

Las direcciones y extended public keys no son claves privadas,
pero pueden facilitar correlación. Trátalas con cautela.

## Revisar un reporte cifrado

La contraseña requerida es la contraseña de exportación, no la passphrase BIP39.

El archivo JSON exterior contiene metadatos y ciphertext.
Leer ese JSON no revela el contenido privado.

La función de descifrado del módulo es:

```python
decrypt_report_content(encrypted_content, password)
```

Para verificar un export JSON sin mostrar secrets, ejecuta desde la raíz del proyecto y desde una terminal interactiva:

```bash
python3 -c 'from pathlib import Path; import json; import bip39_seed_report as r; c=Path("output/bip39_seed_report.json").read_text(encoding="utf-8"); p=r.read_hidden_secret("Contraseña del reporte: "); d=json.loads(r.decrypt_report_content(c,p)); print("OK: reporte autenticado y JSON interno válido"); print("network:", d.get("network")); print("input_mode:", d.get("input_mode"))'
```

Ajusta la ruta al archivo exacto. El comando anterior corresponde a contenido interno JSON; no a un export con formato interno texto.

No publiques una copia descifrada, seed o WIF. Si utilizas el visor local revisar_reporte.py, colócalo junto a bip39_seed_report.py. No se presupone que ese visor forme parte de la distribución.

La revelación completa puede quedar en scrollback o registros.
Crear una copia descifrada en disco se reserva para material ficticio.

### Revisión en editor: solo laboratorio

Abrir el archivo cifrado en un editor muestra el contenedor y su ciphertext,
no el reporte privado. Para leer el contenido en un editor se necesita una
copia descifrada explícita, reservada a datos ficticios, fuera del repositorio
y de carpetas sincronizadas. No modificar el original cifrado.

Usar carpeta 0700 y archivo 0600 en Linux. Esos permisos no protegen un host
comprometido ni evitan backups, autosaves, archivos recientes o capturas.
Desactivar esas funciones en el editor cuando sea posible. Eliminar después
no garantiza borrado seguro. Ninguna copia descifrada debe publicarse.

Los auxiliares locales de revisión no se presuponen parte de la distribución
si no están versionados expresamente.

## Estado y trabajo pendiente

Implementado y probado en los ensayos registrados:

- Generación sin filtro de palabras repetidas.
- Indicadores sin score criptográfico.
- Verificación de wordlist embebida y efectiva.
- Entrada oculta con TTY y rechazo de GetPassWarning.
- Confirmación NFKD de passphrase y cancelación inicial.
- Exportación nueva con scrypt y AES-256-GCM.
- Compatibilidad de descifrado histórico.
- Permiso explícito para secretos CLI.
- Suite BIP39 y pruebas de cifrado y entrada segura.
- Validación estricta del contenedor versión 1: estructura, tipos, claves duplicadas, base64 y límites de tamaño.
- Suite del contenedor con rechazos anteriores a la KDF, casos positivos y compatibilidad histórica.
- Publicación mediante enlaces duros sin reemplazar destinos existentes,
  con reintentos secuenciales y cifrado único por export.
- Suite de escritura: 15 métodos aprobados en el ensayo Linux comunicado.
- Ensayo Windows 10 Home x64: 10 métodos de escritura aprobados y
  5 omitidos, con verificaciones manuales de exports.
- Auxiliar manual de laboratorio para autenticar y comprobar reportes
  sin imprimir el contenido privado.
- Runner BIP39 con validación estructural, rechazo de suites vacías
  y manejo de errores previstos desde la CLI.
- Suite de regresión del runner y última palabra: nueve métodos correctos
  en el ensayo Linux del 24 de octubre de 2026, tras corregir la captura
  de salida y añadir una prueba de mutación. El ensayo anterior,
  del 23 de octubre, registró ocho métodos.
- Mensaje de recuperación que distingue valores del checksum
  y cantidad de candidatos.
- UX compacta por defecto y revelación explícita de la vista con --show-all.
- report_notices en el contexto privado y avisos conservados en JSON/TXT.
- Pie con comandos escapados y ruta final, sin contraseña o passphrase privada en argv.
- Suites UX (18) e integral complementaria (28), y ejecutor local secuencial.
- Baterías Linux del 31 de octubre y 2 de noviembre de 2026:
  ocho etapas correctas, sin omisiones; inventario 70/70 y 11 archivos
  protegidos sin cambios. El inventario no implica cobertura completa.

Pendiente:

- Lectura limitada desde disco antes de cargar el contenedor completo en memoria.
- Durabilidad del directorio y ampliación de pruebas por plataforma
  y sistema de archivos.
- Perfiles de recuperación, auditoría y laboratorio.
- Revelación granular de secrets.
- Vectores independientes de BIP32 y todas las derivaciones.
- Bloqueo transitivo, hashes de artefactos y ampliación de la matriz de entornos y flujos probados.

Windows y macOS quedan fuera del alcance activo. La revisión se difiere
a quien los utilice; los límites y resultados históricos se conservan
en ANALISIS_COMPATIBILIDAD_SO.md y no bloquean este hito Linux.

Estos resultados no constituyen una auditoría independiente ni
una certificación para custodiar fondos.

## Advertencias finales

La validación BIP39 confirma formato y checksum, no imprevisibilidad.

Los indicadores son descriptivos y no clasifican la seguridad
criptográfica de una mnemonic.

La ejecución offline no garantiza seguridad del entorno.

El proyecto permanece educativo y no se recomienda con fondos reales.
La revisión de código y las pruebas registradas no constituyen
una auditoría independiente para producción.

## Licencia

El código original del proyecto se distribuye bajo la licencia MIT.
Consulta el archivo LICENSE.

MIT permite uso, modificación y redistribución, incluido uso comercial,
si se conservan los avisos y condiciones de la licencia.

El material de terceros conserva sus licencias y avisos correspondientes.

Consulta [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) para el inventario
de material externo, los avisos conservados y las verificaciones de
procedencia que todavía están pendientes.

La licencia no constituye una auditoría ni una garantía de seguridad.
El proyecto sigue siendo educativo y no se recomienda con fondos reales.

Consulta [LICENSE](LICENSE).

## Auditoría y contribuciones

Se aceptan revisiones de código, issues y pull requests con propuestas
de corrección y mejora.

Antes de proponer un cambio:

- Utiliza exclusivamente datos ficticios.
- No publiques mnemonic, passphrase, seed, WIF o exports privados.
- Explica el cambio y su impacto.
- Conserva las funciones existentes o justifica cualquier cambio de contrato.
- Ejecuta las pruebas del área afectada y las suites de regresión.
- Documenta el entorno y el commit de referencia.

Las propuestas se revisan antes de integrarlas.

## Contacto

**Para reportar errores o sugerencias, usa issues en el repositorio.**
No publiques mnemonics, passphrases, seeds ni exports en issues
