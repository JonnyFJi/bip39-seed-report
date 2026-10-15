# Pruebas de BIP39 Seed Report

Las suites utilizan exclusivamente datos ficticios o vectores públicos.
No introducir mnemonics, passphrases ni claves de usuario.

## Ejecución en Linux/macOS

Ejecutar desde la raíz del proyecto, no desde la carpeta test.

Los comandos siguientes suponen que existe un entorno virtual local
en .venv-verificacion con las dependencias de requirements.txt instaladas.

```bash
PY="$PWD/.venv-verificacion/bin/python"
"$PY" --version
"$PY" -m pip check
```

Comprobar sintaxis y ejecutar las suites:

```bash
"$PY" -m py_compile bip39_seed_report.py
"$PY" -m py_compile test/test_contenedor_report.py

"$PY" bip39_seed_report.py --run-tests --vectors-file test/vectors.json

PYTHONPATH="$PWD" "$PY" test/test_cifrado_report.py
PYTHONPATH="$PWD" "$PY" test/test_entrada_segura.py
PYTHONPATH="$PWD" "$PY" test/test_contenedor_report.py
```

Ejecutar los comandos por separado. Si uno falla, revisar el error antes
de continuar; no interpretar la ejecución de las suites posteriores
como corrección del fallo anterior.

Las rutas entre comillas permiten utilizar carpetas con espacios.

Estos comandos y resultados se han comprobado en el entorno Linux
comunicado por el mantenedor. macOS y otras plataformas requieren
comprobaciones específicas.

### Suite del contenedor cifrado

test/test_contenedor_report.py contiene 18 métodos de prueba con
subcasos. Utiliza exclusivamente datos ficticios y no escribe reportes
en disco ni solicita contraseñas al usuario.

Comprueba:

- Rechazo de entradas que no sean texto y de JSON no admitido.
- Claves JSON duplicadas, incluidas claves anidadas.
- Constantes NaN e infinitos.
- Claves obligatorias ausentes y campos adicionales.
- Formato, versión, algoritmos y tipos de metadatos.
- Perfil scrypt admitido y rechazo de booleanos como parámetros.
- Base64 y longitudes de salt, nonce y ciphertext.
- Límites de tamaño y representación UTF-8.
- Rechazo de entradas inválidas antes de llamar a la KDF.
- Acceso a la KDF cuando la estructura es admisible.
- Cifrado y descifrado con scrypt real.
- Compatibilidad del formato histórico y su alias.

Algunas pruebas utilizan mocks y límites reducidos temporalmente para
comprobar las fronteras sin generar datos grandes. No modifican el
script guardado en disco. La prueba con scrypt real mantiene el perfil
configurado por el programa.

Resultado esperado:

```text
Ran 18 tests in ...
OK
```

### Resultado registrado

El 15 de octubre de 2026, el mantenedor comunicó dos ejecuciones
satisfactorias de la suite del contenedor en Linux con Python 3.10.12.
Ambas terminaron con 18 métodos correctos y código de salida 0.

SHA-256 del script correspondiente a ese ensayo:

```text
7e108699d9625054fbe2ba3750afa2b932f4b1903bda058a278c255bb23fc21a
```

Este hash identifica la versión ensayada; no certifica por sí solo
procedencia ni seguridad. Los resultados no se generalizan a otras
versiones o entornos.

## Alcance

- Vectores BIP39: casos ejecutados de conversión, seed y round-trip.
- Cifrado: recuperación, rechazo de alteraciones y compatibilidad histórica.
- Entrada: política de GetPassWarning y normalización Unicode.
- Contenedor: estructura, tipos, duplicados, límites y orden de validación
  anterior a la KDF, además de casos positivos y compatibilidad histórica.

Pasar estas suites no constituye una auditoría ni verifica todas
las derivaciones, plataformas o condiciones de escritura.

La suite del contenedor no comprueba escritura concurrente, permisos
efectivos, durabilidad del sistema de archivos ni lectura limitada
desde disco antes de cargar el contenido en memoria.

Las pruebas con mocks verifican controles concretos del programa;
no sustituyen las pruebas criptográficas reales ni los ensayos
de terminal y sistema de archivos.

## Datos de referencia

vectors.json conserva los bytes de la suite previamente probada.
La procedencia y los avisos de los datos de referencia se registran en
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

La identificación del origen histórico exacto sigue pendiente.

No reemplazarlo automáticamente desde una rama remota mutable.
