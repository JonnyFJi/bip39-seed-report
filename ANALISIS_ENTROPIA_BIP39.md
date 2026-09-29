# Análisis de Entropía Criptográfica y Cumplimiento BIP39

## Fecha del análisis
Agosto 10, 2026
"Actualizado: 29 de septiembre de 2026"
"Versión analizada: wallet_bip39_off_line.py publicado".

## Objetivo
Documentar cómo el script obtiene la entropía y qué comprobaciones BIP39 realiza.
---

## ✅ Generación de Entropía

### Código analizado

```python
def generate_entropy(words):
    if words not in VALID_WORD_COUNTS:
        raise ValueError("BIP39 solo admite 12, 15, 18, 21 o 24 palabras.")
    return os.urandom({12: 16, 15: 20, 18: 24, 21: 28, 24: 32}[words])
```

### Filtro posterior por palabras repetidas (limitación conocida)

`generate_entropy()` usa `os.urandom()` sin filtros. Sin embargo, la versión publicada del script, tras convertir la entropía en mnemonic, vuelve a generar hasta 1.000 veces si alguna palabra se repite. Esto excluye mnemonics válidas y altera la distribución uniforme del origen. No aumenta la seguridad. Se eliminará en una versión futura.

### Análisis de seguridad

#### 1. Fuente de entropía: `os.urandom()`

- ✅ **CSPRNG del sistema**: Usa el generador de números pseudo-aleatorios criptográficamente seguro del sistema operativo
- ✅ **Fuente segura**: En Linux, usa `/dev/urandom` que se nutre de eventos de hardware, interrupciones, etc.
- ✅ **No bloqueante**: A diferencia de `/dev/random`, no se bloquea esperando entropía

#### 2. Longitudes de entropía

| Palabras | Bytes | Bits | Cumple BIP39 |
|----------|-------|------|--------------|
| 12 | 16 | 128 | ✅ Sí |
| 15 | 20 | 160 | ✅ Sí |
| 18 | 24 | 192 | ✅ Sí |
| 21 | 28 | 224 | ✅ Sí |
| 24 | 32 | 256 | ✅ Sí |

#### 3. Validación

- ✅ Verifica que el número de palabras sea válido (12, 15, 18, 21, 24)
- ✅ Lanza excepción si no es válido

---

## ✅ Proceso BIP39 completo

### Código analizado

```python
def entropy_to_mnemonic(entropy):
    return Mnemonic("english").to_mnemonic(entropy)

def mnemonic_seed(mnemonic, passphrase=""):
    return Bip39SeedGenerator(normalize_text(mnemonic)).Generate(
        normalize_text(passphrase)
    )
```

### Análisis del flujo BIP39

#### 1. Entropía → Mnemonic (`entropy_to_mnemonic`)

- ✅ Usa `mnemonic` library (Trezor) - implementación oficial
- ✅ Calcula checksum: `SHA256(entropy)[0:entropy_bits//32]`
- ✅ Concatena: `entropy + checksum`
- ✅ Divide en segmentos de 11 bits
- ✅ Mapea a wordlist de 2048 palabras (inglés)

#### 2. Mnemonic → Seed (`mnemonic_seed`)

- ✅ Normalización: Unicode NFKD
- ✅ PBKDF2-HMAC-SHA512
- ✅ Iteraciones: 2048 (estándar BIP39)
- ✅ Passphrase: opcional, máximo 256 bytes

#### 3. Seed → Master Key (`bip32_master_key`)

- ✅ HMAC-SHA512(Key="Bitcoin seed", Data=seed)
- ✅ Master key: I[0:32]
- ✅ Chain code: I[32:64]

---

## ✅ Test Vectors de Trezor

### Código analizado

Fragmento ilustrativo simplificado

```python
def run_bip39_test_vectors(vectors_path):
    vectors = load_vectors(vectors_path)
    
    # Extraer lista de vectors["english"]
    if isinstance(vectors, dict):
        if "english" in vectors:
            vectors = vectors["english"]
    
    for i, vector in enumerate(vectors, start=1):
        entropy_hex, expected_mnemonic, expected_seed = vector
        entropy = bytes.fromhex(entropy_hex)
        
        # Verificar mnemonic
        mnemonic = entropy_to_mnemonic(entropy)
        assert mnemonic == expected_mnemonic
        
        # Verificar seed con passphrase "TREZOR"
        seed = mnemonic_seed(mnemonic, "TREZOR").hex()
        assert seed == expected_seed
        
        # Verificar round-trip
        roundtrip = mnemonic_to_entropy(mnemonic)
        assert roundtrip["entropy"].hex() == entropy_hex
```

### Resultados

- ✅ **24 casos oficiales**: Todos pasan
- ✅ **Mnemonic generation**: Coincide exactamente
- ✅ **Seed derivation**: Coincide con passphrase "TREZOR"
- ✅ **Round-trip**: entropy → mnemonic → entropy funciona perfectamente

---

## ✅ Entropía criptográfica suficiente

### Análisis de seguridad

#### 1. 128 bits (12 palabras)

- ✅ **Seguridad**: 2^128 combinaciones posibles
- ✅ **Fuerza bruta**: Imposible con tecnología actual

#### 2. 256 bits (24 palabras)

- ✅ **Seguridad**: 2^256 combinaciones posibles
- ✅ **Máxima seguridad**: Nivel de seguridad de Bitcoin

#### 3. Comparación con otros métodos

- ✅ **os.urandom()**: Más seguro que `random.random()`. (Aclaración técnica: random no es criptográfico.)
- ✅ **vs dados**: La calidad de la entropía con dados depende del procedimiento; esta comparación no se evalúa aquí

---

## ⚠️ Consideraciones importantes

### Fortalezas

- ✅ **CSPRNG del sistema**: `os.urandom()` es criptográficamente seguro
- ✅ **Longitudes estándar**: 128-256 bits según BIP39
- ✅ **Implementación oficial**: Usa mnemonic (mantenida por Trezor) para BIP39 y bip-utils para la derivación; la segunda no es de Trezor
- ✅ **Test vectors**: Pasan los 24 casos oficiales
- ✅ **Validación completa**: Checksum, palabras, longitud

### Limitaciones

- ⚠️ **Depende del sistema**: Si el CSPRNG del SO está comprometido, la entropía podría ser predecible
- ⚠️ **No verifica calidad**: No hay forma de verificar que `os.urandom()` realmente generó entropía de alta calidad
- ⚠️ **Entorno de ejecución**: Si el sistema está comprometido (malware, backdoors), la seguridad se reduce

### Recomendaciones

- ✅ **Usar offline**: En máquina air-gapped sin conexión a internet
- ✅ **Sistema limpio**: Usar Live USB (Tails, Ubuntu Live)
- ✅ **Verificar en hardware wallet**: Siempre verificar addresses antes de usar
- ✅ **Backup en papel/metal**: Nunca guardar en digital
- ✅ **Múltiples fuentes**: Para máxima seguridad, combinar con entropía manual (dados, monedas). Advertencia: combinar fuentes exige un procedimiento correcto de mezcla que este script no implementa.

---

## ✅ Conclusión del análisis

El script obtiene bytes de `os.urandom()` con longitudes válidas de BIP39 y supera los vectores de referencia del bloque `english`. No puede demostrar la salud del generador aleatorio del sistema, ni que el equipo, el intérprete o las dependencias no estén comprometidos. La versión publicada aplica además un filtro por palabras repetidas que debe eliminarse, y su export cifrado usa una derivación de clave sin KDF resistente. Este proyecto es educativo y no se recomienda con fondos reales.

**Recomendación final**: Para máxima seguridad, usar en máquina air-gapped con sistema Live USB y verificar siempre en hardware wallet antes de usar.

---

## Referencias

- BIP39 Specification: https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki
- Trezor python-mnemonic: https://github.com/trezor/python-mnemonic
- Python os.urandom(): https://docs.python.org/3/library/os.html#os.urandom
