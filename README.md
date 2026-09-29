# BIP39 Seed Report (offline)

PROGRAMA SOLO CON FINES EDUCATIVOS Y DE PRUEBA.
NO SE RECOMIENDA USAR CON FONDOS REALES.
No es una wallet ni sustituye a una hot wallet o a una hardware wallet.
No ha sido auditado por terceros.

## Descripción del script

Herramienta offline para generar, validar y reportar material BIP39/BIP32:
mnemonic, seed, clave raíz, extended public keys y direcciones de ejemplo en
rutas BIP44, BIP49, BIP84 y BIP86. No consulta la red, no muestra saldos y no
firma ni transmite transacciones. Su salida contiene material que puede
controlar fondos; trátalo como secreto.

## Función del script

El script realiza las siguientes funciones principales:

1. **Generación de entropía**: Usa `os.urandom()` para generar entropía criptográficamente segura
2. **Generación sin repeticiones**: Nota de estado: la versión publicada reintenta hasta 1.000 veces si hay palabras repetidas. Es una limitación conocida que sesga la distribución y se eliminará; una mnemonic válida con repeticiones no es más débil.
3. **Conversión a mnemonic**: Transforma la entropía en frases mnemotécnicas de 12, 15, 18, 21 o 24 palabras
4. **Cálculo de clave maestra BIP-32**: Usa HMAC-SHA512 con Key="Bitcoin seed" para derivar la clave maestra correctamente
5. **Derivación de seed**: Genera la seed BIP39 usando PBKDF2 con HMAC-SHA512
6. **Derivación de addresses**: Genera 5 addresses por cada ruta de derivación (GAP limit)
7. **Análisis de seguridad**: "Indicadores informativos de patrón (no estiman entropía criptográfica)".
8. **Verificación**: Valida checksums, mnemonics y round-trips
9. **Exportación segura**: "Exportación cifrada (AES-256-GCM). La clave se deriva con SHA-256 de la contraseña, sin KDF resistente: no usar como respaldo de una seed real".
10. **Verificación de wordlist**: "Compara la wordlist embebida con un hash SHA-256 esperado, sin acceso a la red".

## 🌟 Modo interactivo (-i): entrada de secretos recomendada

**El modo interactivo es la forma recomendada de introducir secretos, frente a los argumentos de línea de comandos y la más fácil de usar el script.** Ideal para usuarios que:

- ✅ No quieren memorizar comandos complejos
- ✅ Prefieren menús guiados paso a paso
- ✅ Quieren evitar errores de escritura
- ✅ Necesitan ayuda visual durante el proceso
- ✅ Desean utilizar el script sin eco en pantalla (Los secretos ingresados con getpass no quedan en el historial del shell. No protege contra malware, keyloggers ni un equipo comprometido)

### Cómo usar el modo interactivo

```bash
python3 wallet_bip39_off_line.py -i
```

**Flujo completo:**

1. **Pide contraseña para encriptar** (oculta, sin eco)
2. **Muestra menú de tipo de entrada:**
Selecciona el tipo de entrada:
- Generar nueva mnemonic aleatoria
- Ingresar entropía hexadecimal
- Ingresar entropía binaria
- Ingresar mnemonic existente
- Calcular última palabra (11 o 23 palabras)
3. **Si seleccionas [1], pregunta longitud:**
Selecciona la longitud de la mnemonic:
- 12 palabras (128 bits - estándar, recomendado)
- 24 palabras (256 bits - máxima seguridad)
4. **Pregunta red Bitcoin:**
Selecciona la red Bitcoin:
- Mainnet (Bitcoin principal - default)
- Testnet (Bitcoin de pruebas)
5. **Pide passphrase** (opcional, oculta)
6. **Genera el reporte** con análisis de seguridad automático
7. **Muestra reporte** en terminal (datos sensibles ocultos)
8. **Guarda archivo encriptado** en `output/bip39_wallet_export.json`

### Ventajas del modo interactivo

- 🎯 **Sin errores de sintaxis**: No necesitas recordar banderas ni comandos
- 🔒 **Máxima seguridad**: Todo el input es oculto (getpass)
- 📋 **Guía visual**: Menús claros en cada paso
- ⚡ **Rápido**: Flujo optimizado en 5-6 pasos
- 🛡️ **Sin historial**: Las contraseñas no quedan en el shell
- ✅ **Validación automática**: El script valida cada entrada

### Ejemplo de sesión interactiva

"Salida de ejemplo de la versión actual (puede cambiar)".

```bash
$ python3 wallet_bip39_off_line.py -i

============================================================
VERIFICACIÓN DE INTEGRIDAD BIP39
============================================================
✅ BIP39 Oficial (GitHub): VERIFICADA (2048 palabras)

🔐 SEGURIDAD ACTIVADA
- El archivo de salida será encriptado con AES-256-GCM
- Los datos sensibles se ocultarán en pantalla
- Debes recordar esta contraseña para abrir el archivo

Contraseña para encriptar: **
Confirmar contraseña: **

🔒 MODO INTERACTIVO SEGURO
Los datos ingresados no se mostrarán en pantalla.
No quedarán en el historial del shell.

Selecciona el tipo de entrada:
Generar nueva mnemonic aleatoria[1]
Ingresar entropía hexadecimal[2]
Ingresar entropía binaria[3]
Ingresar mnemonic existente[4]
Calcular última palabra (11 o 23 palabras)[5]

Opción [1-5]: 1

Selecciona la longitud de la mnemonic:
12 palabras (128 bits - estándar, recomendado)[1]
24 palabras (256 bits - máxima seguridad)[2]

Opción [1-2]: 1

Selecciona la red Bitcoin:
Mainnet (Bitcoin principal - default)[1]
Testnet (Bitcoin de pruebas)[2]

Opción [1-2]: 1

🔐 Ingresa la passphrase BIP39 (opcional, oculto):
Presiona Enter para dejarla vacía si no quieres usar una.

Passphrase: 

✅ Mnemonic sin repeticiones generada en 3 intento(s)

[Reporte completo con análisis de seguridad...]

✅ Archivo encriptado guardado: output/bip39_wallet_export_001.json
⚠️  Recuerda la contraseña para desencriptar.
⚠️  Si pierdes la contraseña, perderás acceso a los datos.
```
## Características de seguridad (Características y límites)

- ✅ **Encriptación AES-256-GCM**: Todos los archivos de salida están encriptados (clave derivada con SHA-256 de la contraseña; limitación conocida)
- ✅ **Ocultamiento de datos**: Los datos sensibles se ocultan en terminal por defecto
- ✅ **Input seguro**: Usa getpass para evitar eco en terminal; no protege un host comprometido
- ✅ **Permisos restringidos**: Archivos con permisos 0o600 (solo propietario)
- ✅ **Escritura atómica**: Usa `tempfile` + `os.replace()` para evitar corrupción
- ✅ **Limpieza de historial**: Intenta limpiar `readline.clear_history()`
- ✅ **Bitcoin-only**: Reduce superficie de ataque
- ✅ **Análisis de seguridad**: 6 tests Indicadores informativos de patrón, sin valor criptográfico
- ✅ **Verificación BIP39**: Wordlist validada contra hash SHA-256 embebido

## Test vectors

✅ **Pasaron los 24 casos oficiales de Trezor**  
✅ **Compatible con BIP39 estándar**  
✅ **Clave maestra BIP-32 calculada correctamente con HMAC-SHA512**  
✅ **Wordlist oficial verificada (2048 palabras)**

El script supera los vectores de referencia del proyecto python-mnemonic
(Trezor) del bloque `english` de `vectors.json`. Esto comprueba la conversión
entropía-mnemonic-seed; no equivale a una auditoría. El archivo incluye otros
idiomas, pero el script solo admite la wordlist inglesa.

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

## Dependencias

```bash
python3 -m pip install mnemonic bip-utils cryptography
```

## Instalación

### 1. Verificar Python 3

```bash
python3 --version
```

Deberías tener Python 3.8 o superior.

### 2. Instalar librerías requeridas

```bash
python3 -m pip install mnemonic bip-utils cryptography
```

### 3. Verificar instalación

```bash
python3 -c "from mnemonic import Mnemonic; from bip_utils import Bip44; from cryptography.hazmat.primitives.ciphers.aead import AESGCM; print('✅ Todas las dependencias instaladas')"
```

### 4. Descargar test vectors oficiales (opcional)

```bash
curl -o vectors.json https://raw.githubusercontent.com/trezor/python-mnemonic/refs/heads/master/vectors.json
```

O usa wget:

```bash
wget -O vectors.json https://raw.githubusercontent.com/trezor/python-mnemonic/refs/heads/master/vectors.json
```

## Uso del script

### Comandos y banderas

```bash
python3 wallet_bip39_off_line.py [OPCIONES]
```

#### Opciones de entrada (usar exactamente una):

Expone el valor en el historial y en la lista de procesos. Solo para pruebas con datos sin valor

- `-w, --words {12,15,18,21,24}`: Genera una mnemonic nueva con el número de palabras indicado
- `--entropy-bin`: Entropía binaria BIP39 (128, 160, 192, 224 o 256 bits)
- `--entropy-hex`: Entropía hexadecimal BIP39 (32, 40, 48, 56 o 64 caracteres hex)
- `--mnemonic`: Mnemonic BIP39 existente (completa, 12-24 palabras)
- `--mnemonic-incomplete`: Mnemonic incompleta (11 o 23 palabras) para calcular la última

#### Opciones generales:

- `-p, --passphrase`: Passphrase BIP39 opcional
- `-i, --interactive`: Modo interactivo (solicita datos de forma segura, sin historial)
- `-n, --network {mainnet,testnet}`: Red Bitcoin (default: mainnet)
- `-f, --format {txt,json}`: Formato de salida (default: json)
- `-o, --output`: Ruta del archivo de salida (default: output/bip39_wallet_export.json)
- `--show-all`: Muestra TODOS los datos en pantalla (modo educativo)
- `--audit-passphrase`: Muestra auditoría descriptiva de la passphrase
- `--run-tests`: Ejecuta los test vectors BIP39 oficiales
- `--vectors-file`: Archivo JSON de test vectors BIP39 (default: vectors.json)

### Ejemplos de uso

#### 1. Generar mnemonic nueva (12 palabras, mainnet)

```bash
python3 wallet_bip39_off_line.py -w 12
```

**Flujo:**
1. Pide contraseña para encriptar
2. Genera 12 palabras aleatorias (reintenta si hay repeticiones)
3. Realiza análisis de seguridad de la mnemonic
4. Usa red mainnet (default)
5. Oculta datos sensibles en terminal
6. Guarda archivo encriptado en `output/bip39_wallet_export.json`

#### 2. Generar mnemonic nueva (24 palabras, testnet)

```bash
python3 wallet_bip39_off_line.py -w 24 -n testnet
```

**Flujo:**
1. Pide contraseña para encriptar
2. Genera 24 palabras aleatorias (reintenta si hay repeticiones)
3. Realiza análisis de seguridad
4. Usa red testnet
5. Oculta datos sensibles en terminal
6. Guarda archivo encriptado

#### 3. Modo interactivo (menú guiado)

```bash
python3 wallet_bip39_off_line.py -i
```

**Flujo:**
1. Pide contraseña
2. Muestra menú interactivo:
   - Seleccionar tipo de entrada (1-5)
   - Seleccionar longitud (12 o 24 palabras)
   - Seleccionar red (mainnet o testnet)
   - Ingresar passphrase (opcional)
3. Genera wallet
4. Realiza análisis de seguridad
5. Guarda archivo encriptado

#### 4. Modo educativo (muestra todo en pantalla)

```bash
python3 wallet_bip39_off_line.py -w 12 --show-all
```

**Flujo:**
1. Pide contraseña
2. Genera 12 palabras
3. **Muestra TODOS los datos en pantalla** (entropy, mnemonic, seed, keys, addresses)
4. Muestra análisis de seguridad completo con score y clasificación
5. Guarda archivo encriptado

⚠️ **ADVERTENCIA**: No usar `--show-all` en producción. Solo para fines educativos.

#### 5. Verificar mnemonic existente

```bash
python3 wallet_bip39_off_line.py --mnemonic "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about" -p "TREZOR"
```

Vector de prueba público. Nunca con secretos reales

**Flujo:**
1. Pide contraseña
2. Verifica checksum BIP39
3. Realiza análisis de seguridad (6 tests)
4. Calcula seed y derivaciones
5. Guarda archivo encriptado

#### 6. Calcular última palabra (recuperación)

```bash
python3 wallet_bip39_off_line.py --mnemonic-incomplete "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon"
```

**Flujo:**
1. Busca todas las palabras posibles (16 opciones para 11 palabras)
2. Muestra lista numerada
3. Pide al usuario seleccionar la correcta
4. Debes verificar manualmente la palabra elegida. En modo no interactivo (EOF) el script elige el primer candidato; limitación conocida
5. Genera mnemonic completa
6. Realiza análisis de seguridad

#### 7. Usar entropía hexadecimal

```bash
python3 wallet_bip39_off_line.py --entropy-hex 00000000000000000000000000000000
```

**Requisitos:**
- 32, 40, 48, 56 o 64 caracteres hexadecimales
- Formato: solo 0-9, a-f (sin espacios)

#### 8. Usar entropía binaria

```bash
python3 wallet_bip39_off_line.py --entropy-bin 00000000000000000000000000000000
```

**Requisitos:**
- 128, 160, 192, 224 o 256 bits
- Formato: solo 0 y 1 (sin espacios)

#### 9. Ejecutar test vectors oficiales

```bash
python3 wallet_bip39_off_line.py --run-tests --vectors-file vectors.json
```

**Resultado esperado:**
Test vectors BIP39: OK (24 casos)

#### 10. Auditoría de passphrase

```bash
python3 wallet_bip39_off_line.py -w 12 -p "mi_passphrase" --audit-passphrase
```

**Muestra:**
- Número de caracteres
- Bytes UTF-8
- Caracteres distintos
- Presencia de mayúsculas, minúsculas, dígitos, símbolos, espacios
- Nota informativa; no calcula entropía real

## Flujo de trabajo recomendado

### Para generación mnemonic nueva:

```bash
# 1. Generar mnemonic (modo seguro)
python3 wallet_bip39_off_line.py -w 12 -i

# 2. Verificar con software o dispositivo independiente de confianza

# 3. Guardar mnemonic en papel o metal (NUNCA en digital)

# 4. Borrar archivo encriptado si no es necesario
rm output/bip39_wallet_export.json
```

### Para recuperación de mnemonic:

```bash
# 1. Calcular última palabra (si falta)
python3 wallet_bip39_off_line.py --mnemonic-incomplete "word1 word2 ... word23" -i

# 2. Verificar mnemonic completa
python3 wallet_bip39_off_line.py --mnemonic "word1 word2 ... word24" -i

# 3. Verificar análisis de seguridad

# 4. Comparar addresses generadas con las de tu mnemonic
```

### Para verificación educativa:

```bash
# 1. Generar mnemonic mostrando todo (SOLO en entorno seguro)
python3 wallet_bip39_off_line.py -w 12 --show-all

# 2. Estudiar análisis de seguridad y derivaciones

# 3. Estudiar estructura BIP32/BIP39

# 4. Borrar archivo después de estudiar
rm output/bip39_wallet_export.json
```

## Salida del script

### En terminal (por defecto):

- Coin type: Bitcoin
- Input mode: (words, entropy-bin, entropy-hex, mnemonic, mnemonic-incomplete)
- Network: mainnet/testnet
- Entropy: [OCULTO]
- Checksum: [OCULTO]
- **Análisis de seguridad**: Indicadores informativos
- Mnemonic: [OCULTO]
- BIP39 seed: [OCULTO]
- BIP32 root key: [OCULTO]
- Addresses (0): Solo primera address por ruta
- **Tipos de address**: P2PKH, P2WPKH-P2SH, P2WPKH, P2TR
- Extended public keys: xpub, ypub, zpub

### En archivo (desencriptado):

- TODOS los datos sensibles visibles
- 5 addresses por ruta (índices 0-4)
- Claves privadas en formato WIF
- Claves públicas en formato hex
- Extended public keys completas
- Análisis de seguridad completo con detalles de cada test
- Contiene mnemonic, seed, clave raíz y claves privadas WIF. Trátalo como secreto

## Seguridad operacional

### Ejecución OFF-LINE (Recomendado)

**Ventajas:**
- ✅ Sin riesgo de exposición por red
- ✅ Sin riesgo de MITM (Man-in-the-Middle)
- ✅ Sin riesgo de DNS spoofing
- ✅ Control total del entorno

**Recomendaciones:**
- Usar máquina air-gapped (nunca conectada a internet)
- Usar sistema Live USB (Tails, Ubuntu Live)
- Verificar hashes de descargas antes de transferir
- Usar hardware wallet para almacenar las keys generadas
- Imprimir o escribir en papel la mnemonic generada
- Borrar todos los archivos después de usar

### Ejecución ON-LINE (No recomendado para producción)

**Riesgos:**
- ⚠️ Posible exposición de datos por red
- ⚠️ Riesgo de malware remoto
- ⚠️ Posible keylogger
- ⚠️ Riesgo de DNS spoofing
- ⚠️ Riesgo de MITM

**Si debes ejecutar on-line:**
- Usa una máquina virtual desechable
- No uses mnemonics reales (solo pruebas)
- Usa redes seguras (evita WiFi público)
- Verifica que el firewall esté activo
- No guardes archivos sensibles permanentemente
- Borra todo después de usar

## Desencriptar archivo

Para desencriptar el archivo de salida:

```python
from wallet_bip39_off_line import decrypt_file_content

# Leer archivo encriptado
encrypted_content = open('output/bip39_wallet_export.json').read()

# Desencriptar con contraseña
decrypted = decrypt_file_content(encrypted_content, 'TU_CONTRASEÑA')

# Mostrar contenido
print(decrypted)
```

O desde la terminal:

```bash
python3 -c "import getpass; from wallet_bip39_off_line import decrypt_file_content; print(decrypt_file_content(open('output/bip39_wallet_export.json').read(), getpass.getpass('Contraseña: ')))"
```

## Estado y limitaciones conocidas

Implementado: generación con `os.urandom()`, validación de checksum BIP39,
derivación BIP32/BIP44/49/84/86 con `bip-utils`, vectores de referencia y
exportación cifrada.

Limitaciones conocidas de esta versión:
- La clave del export se deriva con SHA-256 de la contraseña, sin KDF resistente.
- La generación reintenta si hay palabras repetidas (sesgo; se eliminará).
- Los indicadores y el score son informativos, sin valor criptográfico.
- Los secretos pueden pasarse por argumentos de línea de comandos.
- El export incluye mnemonic, seed, claves raíz y WIF.
- En modo no interactivo, `--mnemonic-incomplete` elige el primer candidato.
- Las dependencias no tienen versiones fijadas.
- No está auditado y no debe usarse con fondos reales.

**Recomendación**: El script puede usarse para generación y verificación de mnemonic Bitcoin en entornos offline seguros, siempre siguiendo las mejores prácticas de seguridad operacional.

## Advertencias finales

**IMPORTANTE:**
- Este script es solo para fines educativos y de prueba
- No certifica que el sistema tiene suficiente entropía acumulada
- No certifica que una entropía manual sea imprevisible
- No certifica que el entorno no esté comprometido
- No certifica que no haya errores de usuario
- La ejecución offline en un entorno confiable es una condición necesaria, no una garantía de seguridad
- **Use el script con prudencia**
- **NUNCA uses mnemonics reales en máquinas conectadas a internet**
- **SIEMPRE verifica las addresses generadas en una wallet hardware antes de usar**
- **No auditado para producción**: Este es un proyecto educativo. No ha sido auditado por firmas de seguridad independientes. Si consideras usarlo con fondos reales (*no recomendado*), entiende los riesgos documentados y se repite la **advertencia**, verifica siempre las addresses en una hardware wallet antes de utilizar.
- **El análisis de seguridad es una guía estadística**: Un score alto no garantiza seguridad absoluta, pero un score bajo indica problemas potenciales.

## Licencia

Sin licencia declarada: todos los derechos reservados

## Contacto

**Para reportar errores o sugerencias, usa issues en el repositorio.**
No publiques mnemonics, passphrases, seeds ni exports en issues
