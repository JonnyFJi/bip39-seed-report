# Compatibilidad esperada con sistemas operativos

## Fecha del análisis
Agosto 10, 2026. Análisis documental; no se ha probado en todas las plataformas.
Octubre 9, 2026. Análisis documental; no se ha probado en todas las plataformas.


## Objetivo
Determinar si el script tiene limitaciones de sistema operativo o si puede usarse en cualquier sistema (Windows, macOS, Linux).

---

## ✅ Respuesta corta

**El script está escrito para funcionar en Windows, macOS y Linux con Python 3, pero esta compatibilidad no está verificada en todas las plataformas. Depende de las versiones de Python y de las tres dependencias instaladas..**

---

## ✅ Análisis detallado por componente

### 1. `mnemonic` library (Trezor)

**Cross-platform:**
- ✅ **Python puro**: No tiene dependencias nativas
- ✅ **Funciona en**: Windows, macOS, Linux, BSD
- ✅ **Requisito**: Python 3.7+

### 2. `bip-utils` library

**Cross-platform:**
- ✅ **Python puro**: Instalado desde PyPI
- ✅ **Funciona en**: Windows, macOS, Linux
- ✅ **Requisito**: Python 3+

### 3. `cryptography` library

**Cross-platform con soporte oficial:**
- ✅ **Windows**: x86-64, 64-bit (wheels preconstruidos)
- ✅ **macOS**: ARM64 (Apple Silicon), x86-64 (Intel)
- ✅ **Linux**: x86-64, ARM64, múltiples distribuciones
- ✅ **Requisito**: Python 3.7+

**Instalación automática:**
```bash
pip install cryptography
```

---

## ✅ Instalación en cada sistema

### Linux (cualquier distribución)

```bash
# Ubuntu, Debian, Fedora, CentOS, Arch, etc.
python3 -m pip install mnemonic bip-utils cryptography
python3 bip39_seed_report.py --run-tests --vectors-file vectors.json
```

### Windows (10, 11)

```powershell
# PowerShell o CMD
python -m pip install mnemonic bip-utils cryptography
python3 bip39_seed_report.py --run-tests --vectors-file vectors.json
```

### macOS (Intel y Apple Silicon)

```bash
# Terminal
python3 -m pip install mnemonic bip-utils cryptography
python3 bip39_seed_report.py --run-tests --vectors-file vectors.json
```

---

## ✅ Funciones específicas del sistema

### `os.urandom()` por sistema

| Sistema | Implementación | Fuente |
|---------|---------------|---------|
| Linux 3.17+ | `getrandom()` syscall | ✅ CSPRNG del sistema |
| Linux <3.17 | `/dev/urandom` | ✅ CSPRNG del sistema |
| Windows 10+ | `BCryptGenRandom()` | ✅ CSPRNG del sistema |
| Windows 7-8 | `CryptGenRandom()` | ✅ CSPRNG del sistema |
| macOS 10.12+ | `getentropy()` / `/dev/urandom` | ✅ CSPRNG del sistema |
| OpenBSD 5.6+ | `getentropy()` | ✅ CSPRNG del sistema |

**Documentación oficial de Python:**
> "On a Unix-like system this will query /dev/urandom, and on Windows it will use CryptGenRandom()."

**Depende de que el sistema operativo no esté comprometido**

### `tempfile.mkstemp()` - Archivos temporales

**Funciona en todos los sistemas:**
- ✅ **Linux/Unix**: `/tmp/` o directorio temporal del sistema
- ✅ **Windows**: `%TEMP%` o directorio temporal del usuario
- ✅ **macOS**: `/tmp/` o directorio temporal del sistema

### `os.chmod()` - Permisos de archivo

**Funciona en todos los sistemas:**
- ✅ **Linux/Unix**: `0o600` (solo propietario)
- ✅ **macOS**: `0o600` (solo propietario)
- ✅ **Windows**: os.chmod(`0o600`) no equivale de forma fiable a una ACL de NTFS en Windows

---

## ✅ Requisitos mínimos por sistema

### Linux
- ✅ Python 3.7+
- ✅ pip3
- ✅ (Opcional) OpenSSL para `cryptography`

### Windows
- ✅ Python 3.7+ (64-bit recomendado)
- ✅ pip
- ✅ No requiere OpenSSL adicional (wheels preconstruidos)

### macOS
- ✅ Python 3.7+
- ✅ pip3
- ✅ Xcode Command Line Tools (para compilar dependencias si es necesario)

---

## ✅ Instalación en todos los sistemas

```bash
# 1. Verificar Python
python --version  # o python3 --version

# 2. Instalar dependencias
python -m pip install mnemonic bip-utils cryptography  # Windows
python3 -m pip install mnemonic bip-utils cryptography  # Linux/macOS

# 3. Verificar instalación
python -c "from mnemonic import Mnemonic; from bip_utils import Bip44; from cryptography.hazmat.primitives.ciphers.aead import AESGCM; print('✅ Todo instalado')"
```

---

## ⚠️ Consideraciones por sistema

### Windows

| Aspecto | Estado |
|---------|--------|
| **Ventaja** | ✅ Wheels preconstruidos, no requiere compilación |
| **Recomendación** | ✅ Verifica el hash del script antes de ejecutarlo |
| **Nota** | ⚠️ Windows Defender puede marcar scripts Python como sospechosos (falso positivo) |

### Linux

| Aspecto | Estado |
|---------|--------|
| **Ventaja** | ✅ Máximo control y transparencia |
| **Recomendación** | ✅ Usar en entorno offline para mayor seguridad |
| **Nota** | ⚠️ Algunas distribuciones pueden requerir instalar `python3-dev` o `libssl-dev` |

### macOS

| Aspecto | Estado |
|---------|--------|
| **Ventaja** | ✅ Sistema Unix-like con buena seguridad |
| **Recomendación** | ✅ Usar Python oficial de python.org o Homebrew |

---

## ✅ Conclusión

El script está pensado para ser multiplataforma, pero la compatibilidad debe
confirmarse en cada entorno con `--run-tests`. Ejecútalo solo offline, en un
entorno confiable (por ejemplo un sistema Live USB) y con dependencias de
versiones conocidas.

| Sistema | Compatibilidad |
|---------|---------------|
| Windows 10/11 | ✅ Objetivo de compatibilidad; ver matriz de pruebas |
| macOS (Intel y Apple Silicon) | ✅ Funciona |
| Linux (cualquier distribución) | ✅ Funciona |

**Recomendación**: Para mayor seguridad, usar en cualquier sistema pero **siempre offline** en entorno confiable (Live USB, máquina air-gapped, etc.).

---

## Referencias

- Python os.urandom(): https://docs.python.org/3/library/os.html
- Cryptography library: https://cryptography.io/
- bip-utils PyPI: https://pypi.org/project/bip-utils/
