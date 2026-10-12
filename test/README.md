# Pruebas de BIP39 Seed Report

Las suites utilizan exclusivamente datos ficticios o vectores públicos.
No introducir mnemonics, passphrases ni claves de usuario.

## Ejecución en Linux/macOS

Desde la raíz del proyecto:

```bash
python3 -m py_compile bip39_seed_report.py
python3 bip39_seed_report.py --run-tests --vectors-file test/vectors.json
PYTHONPATH="$PWD" python3 test/test_cifrado_report.py
PYTHONPATH="$PWD" python3 test/test_entrada_segura.py
```

Los comandos con PYTHONPATH se han utilizado en el entorno Linux
registrado. Otras plataformas necesitan comprobación específica.

## Alcance

- Vectores BIP39: casos ejecutados de conversión, seed y round-trip.
- Cifrado: recuperación, rechazo de alteraciones y compatibilidad histórica.
- Entrada: política de GetPassWarning y normalización Unicode.

Pasar estas suites no constituye una auditoría ni verifica todas
las derivaciones, plataformas o condiciones de escritura.

## Datos de referencia

vectors.json conserva los bytes de la suite previamente probada.
La procedencia y los avisos de los datos de referencia se registran en
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

La identificación del origen histórico exacto sigue pendiente.

No reemplazarlo automáticamente desde una rama remota mutable.
