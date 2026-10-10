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
8. Muestra un reporte con secretos privados ocultos por defecto.
9. Guarda un reporte cifrado.

La ruta predeterminada es:

```text
output/bip39_seed_report.json
```

Si ya existe, el programa busca un nombre secuencial. Este mecanismo
todavía no garantiza ausencia de sobrescritura entre procesos concurrentes.

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

El flujo normal cifra el contenido antes de escribirlo en un temporal,
sincroniza el archivo y lo coloca en el destino mediante os.replace().

Se intenta aplicar el modo 0o600. Esta medida no certifica las ACL de
Windows ni protege contra un sistema comprometido.

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
python3 bip39_seed_report.py --run-tests --vectors-file vectors.json
```

Resultado esperado con la suite distribuida:

```text
Test vectors BIP39: OK (24 casos)
```

Las pruebas adicionales están en la carpeta test.

Desde la raíz del proyecto, en Linux/macOS y utilizando una copia local de confianza:

```bash
PYTHONPATH="$PWD" python3 test/test_cifrado_report.py
PYTHONPATH="$PWD" python3 test/test_entrada_segura.py
```

Ejecuta esos comandos desde la raíz y compruébalos en una descarga limpia.

Los vectores BIP39 verifican los casos ejecutados de conversión
entropy-mnemonic, derivación de seed y round-trip. No constituyen una
auditoría ni verifican todas las derivaciones o claves extendidas.

La prueba de cifrado comprueba recuperación, rechazo de contraseña
incorrecta, alteraciones, perfil KDF y compatibilidad histórica.

La prueba de entrada segura comprueba el rechazo simulado de
GetPassWarning y la confirmación/normalización Unicode.

Las pruebas usan exclusivamente material ficticio. No introduzcas
secrets reales en los tests.

## Indicadores informativos de patrón

El script muestra indicadores superficiales (unicidad, repeticiones, índices
consecutivos). No estiman entropía criptográfica ni imprevisibilidad, ni
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
python3 -m pip install mnemonic bip-utils cryptography
```

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
python3 -m pip install mnemonic bip-utils cryptography
```

### 3. Verificar instalación

```bash
python3 -c "from mnemonic import Mnemonic; from bip_utils import Bip44; from cryptography.hazmat.primitives.ciphers.aead import AESGCM; print('✅ Todas las dependencias instaladas')"
```

### 4. Vectores distribuidos

El repositorio incluye vectors.json. Conserva la copia que corresponde
a la versión analizada; no la reemplaces automáticamente desde una rama
remota mutable.

Puedes indicar otra suite explícitamente con --vectors-file.
Actualmente sigue pendiente endurecer el manejo de archivos ausentes,
JSON inválido y suites vacías.

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
- --audit-passphrase: descripción de la passphrase, sin estimar
  su entropy real.
- --show-all: revela material privado en terminal; solo para pruebas.
- --run-tests: ejecuta la suite indicada y termina sin exportar.
- --vectors-file: ruta de la suite; por defecto vectors.json.
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
3. Genera mnemonic
4. Realiza Validación e indicadores
5. Guarda archivo encriptado

#### 4. Modo educativo (muestra todo en pantalla)

```bash
python3 bip39_seed_report.py -w 12 --show-all
```

**Flujo:**
1. Pide contraseña
2. Genera 12 palabras
3. **Muestra TODOS los datos en pantalla** (entropy, mnemonic, seed, keys, addresses)
4. Muestra validación e indicadores descriptivos de patrón, sin score de seguridad
5. Guarda archivo encriptado

La salida de terminal no necesariamente reproduce todos los campos
del JSON privado. Puede revelar mnemonic, seed y claves privadas.
No la redirijas a logs ni la compartas.

⚠️ **ADVERTENCIA**: No usar `--show-all` en producción. Solo para fines educativos.

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
3. Valida la mnemonic y muestra indicadores descriptivos.
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

**Requisitos:**
- 32, 40, 48, 56 o 64 caracteres hexadecimales
- Formato: solo 0-9, a-f (sin espacios)

Los ceros son datos públicos completamente predecibles.

#### 8. Usar entropía binaria

```bash
python3 bip39_seed_report.py --allow-insecure-cli-secrets --entropy-bin 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 -n testnet
```

**Requisitos:**
- 128, 160, 192, 224 o 256 bits
- Formato: solo 0 y 1 (sin espacios)

Para pruebas, puedes usar una secuencia conocida; no atribuyas seguridad a una entrada manual por tener la longitud y checksum correctos.
Esta secuencia de ceros es pública y completamente predecible.
El ejemplo no debe utilizarse para proteger fondos.

#### 9. Ejecutar test vectors oficiales

```bash
python3 bip39_seed_report.py --run-tests --vectors-file vectors.json
```

**Resultado esperado:**
Test vectors BIP39: OK (24 casos)

#### 10. Auditoría de passphrase

```bash
python3 bip39_seed_report.py -i --audit-passphrase -n testnet
```

**Muestra:**
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

### En terminal (por defecto):

- Coin type: Bitcoin
- Input mode: (words, entropy_bin, entropy_hex, mnemonic, mnemonic_incomplete)
- Network: mainnet/testnet
- Entropy: [OCULTO]
- Checksum: [OCULTO]
- **Validación e indicadores**: Indicadores informativos
- Mnemonic: [OCULTO]
- BIP39 seed: [OCULTO]
- BIP32 root key: [OCULTO]
- Addresses (0): Solo primera address por ruta
- **Tipos de address**: P2PKH, P2WPKH-P2SH, P2WPKH, P2TR
- Extended public keys: xpub, ypub, zpub

### En archivo (desencriptado):

- Material privado del reporte visible al descifrarlo.
- 5 addresses por ruta (índices 0-4)
- Claves privadas en formato WIF
- Claves públicas en formato hex
- Extended public keys completas
- Resultado de validación e indicadores descriptivos.
- Contiene mnemonic, seed, clave raíz y claves privadas WIF. Trátalo como secreto
- passphrase_used indica si se utilizó una passphrase BIP39. La passphrase no se guarda en claro como campo del contexto actual.
- bip32_root_key contiene la concatenación hexadecimal de la clave privada maestra y el chain code; no es una clave extendida serializada xprv/tprv.

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

Pendiente:

- Validación estricta del contenedor, límites de tamaño y claves JSON duplicadas.
- Protección y pruebas de escritura concurrente.
- Perfiles de recuperación, auditoría y laboratorio.
- Revelación granular de secrets.
- Vectores independientes de BIP32 y todas las derivaciones.
- Manejo robusto de archivos de vectores y suites vacías.
- Dependencias fijadas, matriz de plataformas e identidad de release.

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

Sin licencia declarada: todos los derechos reservados

## Contacto

**Para reportar errores o sugerencias, usa issues en el repositorio.**
No publiques mnemonics, passphrases, seeds ni exports en issues
