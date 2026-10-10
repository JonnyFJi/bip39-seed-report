# Análisis de generación de entropy y verificaciones BIP39

## Referencia del análisis

- Creación del documento: 10 de agosto de 2026.
- Actualización documental: 10 de octubre de 2026.
- Archivo analizado: bip39_seed_report.py.
- Repositorio de referencia: JonnyFJi/bip39-seed-report.
- Commit consultado:
  `73d5a64dcf01d773439c0f7364b481c787d45ce1`.
- El SHA-256 siguiente identifica el script analizado, no este documento.
- SHA-256 del script de referencia:
  cd58e2cc0c32a00f2087e8cb43a39e54b4a14380b4a46e41b402a99b771c6184

Los números de línea y las conclusiones deben revisarse cuando cambie el código de referencia. El hash identifica los bytes del archivo; no certifica su procedencia ni la seguridad del entorno.

## Objetivo y alcance

Documentar cómo el script obtiene entropy, la transforma en una mnemonic y deriva una seed, y distinguir las comprobaciones implementadas de las propiedades que el programa no puede certificar.

Este documento no es una auditoría independiente, no certifica la imprevisibilidad de una entrada y no recomienda uso con fondos reales.

## ✅ Generación de Entropía

### Código analizado

```python
def generate_entropy(words):
    if words not in VALID_WORD_COUNTS:
        raise ValueError("BIP39 solo admite 12, 15, 18, 21 o 24 palabras.")
    return os.urandom({12: 16, 15: 20, 18: 24, 21: 28, 24: 32}[words])
```

### Generación sin filtro por repeticiones

La versión actual genera entropy y acepta la mnemonic resultante sin regenerarla para evitar palabras repetidas.

Las repeticiones, palabras cercanas en la wordlist o secuencias simples no invalidan por sí solas una mnemonic generada desde una fuente adecuada.

El programa puede describir esos patrones, pero no los utiliza para asignar un score de seguridad ni para certificar imprevisibilidad.

### Fuente y tamaños de entrada

generate_entropy() solicita bytes a os.urandom(), la interfaz del generador criptográfico del sistema operativo.

El programa depende del funcionamiento del sistema, Python y sus dependencias. No comprueba retrospectivamente la imprevisibilidad de los bytes recibidos ni la ausencia de compromisos del entorno.

No se afirma que la llamada sea siempre no bloqueante: su comportamiento depende de la plataforma, la versión de Python y la inicialización del generador del sistema.

| Palabras | Bytes de entrada | Bits de entrada |
|---:|---:|---:|
| 12 | 16 | 128 |
| 15 | 20 | 160 |
| 18 | 24 | 192 |
| 21 | 28 | 224 |
| 24 | 32 | 256 |

Estos tamaños corresponden al formato BIP39. Tener esa longitud no demuestra que una entrada manual sea aleatoria o imprevisible.

La función rechaza números de palabras fuera de los tamaños admitidos.
Las entradas hexadecimal y binaria se validan por formato y longitud.
La importación de mnemonic se valida por número de palabras, wordlist y checksum.

## Transformación BIP39 y material maestro BIP32

### Código analizado

```python
def entropy_to_mnemonic(entropy):
    return Mnemonic("english").to_mnemonic(entropy)

def mnemonic_seed(mnemonic, passphrase=""):
    return Bip39SeedGenerator(normalize_text(mnemonic)).Generate(
        normalize_text(passphrase)
    )
```

### Flujo de transformación

#### 1. Entropy a mnemonic

El script utiliza Mnemonic("english").to_mnemonic(entropy).

BIP39 combina los bits de entrada con los primeros ENT/32 bits de SHA-256 de la entrada. La secuencia resultante se divide en grupos de 11 bits que corresponden a índices de la wordlist.

La versión actual comprueba localmente la lista inglesa embebida y su igualdad de contenido y orden con la lista efectiva de mnemonic.
La comprobación no certifica toda la implementación de las dependencias.

#### 2. Mnemonic a seed

mnemonic_seed() utiliza Bip39SeedGenerator y normaliza la mnemonic y la passphrase mediante Unicode NFKD.

La derivación BIP39 utiliza PBKDF2-HMAC-SHA512 con 2048 iteraciones y produce una seed de 64 bytes.

La passphrase es opcional. En modo interactivo se solicita dos veces y se compara en su forma normalizada. Dos entradas vacías representan la passphrase vacía.

Este documento no atribuye un máximo de 256 bytes a la passphrase: el script no define expresamente ese límite.

#### 3. Seed a material maestro BIP32

bip32_master_key() calcula HMAC-SHA512 con la clave "Bitcoin seed".

Las dos mitades de 32 bytes se presentan como clave privada maestra y chain code. El campo bip32_root_key concatena esas mitades en hexadecimal; no es una clave extendida serializada xprv/tprv.

La validación explícita del caso excepcional de escalar maestro inválido y los vectores independientes BIP32 siguen pendientes en esta revisión.
Las derivaciones de direcciones utilizan bip-utils.

## Vectores de referencia y alcance de las pruebas

El repositorio distribuye vectors.json. El script utiliza el bloque english cuando está presente.

Desde la raíz del proyecto:

```bash
python3 bip39_seed_report.py --run-tests --vectors-file vectors.json
```

Resultado registrado con la suite distribuida:

```text
Test vectors BIP39: OK (24 casos)
```

El runner comprueba, para cada caso ejecutado:

- Conversión de entropy a mnemonic esperada.
- Seed esperada con la passphrase pública TREZOR.
- Conversión inversa de mnemonic a entropy.

El runner admite vectores de tres o cuatro elementos, pero no verifica el cuarto campo de clave extendida. Por tanto, estos resultados no certifican todas las operaciones BIP32 ni las derivaciones BIP44, BIP49, BIP84 y BIP86.

También siguen pendientes:

- Rechazar suites vacías.
- Exigir de forma explícita el bloque de idioma esperado.
- Manejar errores de archivo, permisos, JSON y formato con mensajes claros.
- Añadir vectores independientes de clave maestra y derivaciones.

El modo --run-tests no solicita secretos ni genera un export.
Las opciones sensibles por CLI no pueden combinarse con ese modo.

## Tamaño del espacio y límites de interpretación

Una entrada de 128 bits tiene 2^128 valores posibles; una de 256 bits tiene 2^256 valores posibles.

Esas cifras describen el espacio de entradas. Interpretarlas como incertidumbre efectiva requiere que el proceso de selección sea adecuado y no predecible para un adversario.

El checksum agrega estructura de validación, no nuevos bits independientes de imprevisibilidad.

Una entrada formada por ceros puede tener longitud válida y convertirse en una mnemonic válida, pero es completamente predecible.

La seed derivada tiene 512 bits de longitud, pero esa longitud no convierte una entrada débil en una fuente de 512 bits de incertidumbre.

El módulo random no debe confundirse con una fuente criptográfica.
El script utiliza os.urandom() para generación nueva.

La recolección mediante dados, monedas u otros procedimientos físicos no se evalúa en este documento y no está implementada como ceremonia en la versión analizada.

## Controles y limitaciones

### Controles actuales

- Generación de entropy nueva mediante os.urandom().
- Aceptación sin filtros por palabras repetidas.
- Validación BIP39 de formato y checksum.
- Comprobación de wordlist embebida y efectiva.
- Indicadores de patrón sin score criptográfico.
- Entrada interactiva sin eco, con comprobación de TTY.
- Confirmación de passphrase normalizada.
- Bloqueo predeterminado de secretos por argumentos CLI.

### Límites de generación e importación

El script no puede certificar:

- La salud del generador del sistema.
- La ausencia de malware o modificaciones en las dependencias.
- La imprevisibilidad de una entrada manual.
- El origen histórico de una mnemonic importada.
- La ausencia de errores de copia o respaldo.

No se implementa mezcla de entropy física. No debe recomendarse combinar fuentes sin un procedimiento diseñado, revisado y probado.

### Cifrado del reporte: control distinto de la entropy

La exportación nueva utiliza scrypt con salt aleatorio y AES-256-GCM en un contenedor versionado.

SHA-256 directo permanece exclusivamente en el descifrado histórico para compatibilidad. Los exports nuevos no utilizan ese método.

Los ensayos registrados de cifrado y compatibilidad pasaron, pero no certifican la imprevisibilidad del material BIP39 ni la fuerza de cualquier contraseña elegida por el usuario.

Siguen pendientes la validación estricta del contenedor, límites de tamaño, escritura concurrente y separación de perfiles de reporte.

### Uso de prueba

Utilizar exclusivamente material ficticio, preferentemente offline y en un entorno controlado. La ejecución offline no garantiza seguridad.
No publicar mnemonic, passphrase, seed, WIF o exports privados.

## Conclusión

La versión analizada obtiene bytes del generador del sistema en tamaños admitidos por BIP39, acepta mnemonics generadas sin filtrar repeticiones y valida formato, wordlist y checksum.

Los 24 vectores de referencia ejecutados respaldan las conversiones y la derivación de seed comprobadas, no una certificación completa del programa ni de todas las derivaciones.

El export nuevo utiliza scrypt y AES-256-GCM. El método histórico se conserva únicamente para descifrado compatible.

El programa no certifica la imprevisibilidad de una entrada ni la seguridad del entorno. El proyecto permanece educativo y no se recomienda con fondos reales.

## Referencias

- BIP39 Specification: https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki
- Trezor python-mnemonic: https://github.com/trezor/python-mnemonic
- Python os.urandom(): https://docs.python.org/3/library/os.html#os.urandom
