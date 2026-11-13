# Resultados de preparación de otra copia — entropy CLI

Fecha de cierre: 10 de noviembre de 2026.
Estado: satisfactorio para el entorno y los casos registrados por el mantenedor.

## Alcance y procedencia

Este registro se basa en la transcripción de terminal y en los contenidos de
entorno.json, resumen.json, hashes_antes.json, hashes_despues.json y
07_clases_java.sha256 pegados por el mantenedor. El revisor no ejecutó estas
pruebas en el equipo del mantenedor. La inspección de la ventana incorpora
su confirmación visual explícita.

Se preparó otra copia del proyecto, un venv nuevo y clases Java recompiladas,
sobre el mismo equipo y los runtimes existentes. No se presenta como instalación
completa desde cero en otro equipo ni como kit offline probado.

Referencias locales, sin rutas personales:
- Laboratorio: laboratorio_entropy_3VPhWzUX.
- Proyecto: proyecto/.
- Evidencia de preparación: evidencia/, al mismo nivel que proyecto/.
- Batería: proyecto/output/bateria_local_zelv2gy3.

## Identidad del núcleo

SHA-256 de bip39_seed_report.py:

```text
b29675e5d91f52fd6c109a777b820945c01c12ef88e6f9926f61cc6e204e20d6
```

## Preparación

- Auxiliar preparar_copia_entropy.py con hash esperado.
- 64 archivos seleccionados copiados y verificados; código 0.
- No se copiaron venv, build ni reportes cifrados anteriores.
- Venv nuevo .venv-instalacion-limpia, creación con código 0 y Venv: True.
- Dependencias instaladas desde requirements.txt con código 0.
- pip check: No broken requirements found.
- Importaciones de mnemonic, bip_utils y cryptography correctas.
- crcmod y ed25519-blake2b usaron setup.py install según el log; ambas
  operaciones terminaron correctamente. No fue una instalación solo de wheels.

## Entorno registrado

| Campo | Valor |
|---|---|
| Fecha UTC del entorno.json | 2026-11-10T21:18:44.892700+00:00 |
| Sistema | Linux Mint 21.3 Virginia, x86_64 |
| Kernel | 5.15.0-203-generic |
| Python | CPython 3.10.12, GCC 11.4.0 |
| mnemonic | 0.21 |
| bip-utils | 2.9.3 |
| cryptography | 44.0.3 |
| pip | 22.0.2 |
| Java y javac consultados | OpenJDK 11.0.33 y javac 11.0.33 |
| Node consultado | v24.22.2 |

Java, javac y Node proceden de consultas de terminal, no de campos del entorno.json.
La referencia automática original usó pip 26.3; se conserva la diferencia.
Las versiones describen el ensayo y no constituyen recomendaciones universales.

## Compilación Java nueva

Comando comunicado desde la copia:

```bash
"$JAVAC" -encoding UTF-8 --release 11 -d build/entropy_java \
  entropy_helpers/JavaEntropyProbe.java \
  entropy_helpers/JavaEntropyProvider.java
```

Código 0; sin mensajes de error en el log mostrado.

| Clase | Bytes comunicados | SHA-256 posterior a compilación |
|---|---:|---|
| JavaEntropyProbe.class | 3317 | 46f002e8228d7cd3865f9b405a1ad1ba94a4b84ddadddc83d0f480d8cc88bc0f |
| JavaEntropyProvider.class | 3357 | ac5f2d5e227886c7b09aa262beada337f9cda2b581d64e8166276cbd60abe27e |

La clase histórica JavaEntropyProvider.class tenía 2999 bytes y SHA-256
714288785a6afa16da5efba45594a3c7eabfb9e616fa00e3c305a4fa5410cddb.
No existe identidad binaria entre ambas. No se atribuye una causa exacta a la
diferencia ni se declara compilación reproducible byte a byte. Los hashes
se registraron tras compilar, antes de la batería; no se comunicó un segundo
hash de clases después de todos los ensayos. El manifiesto de 49 entradas
no incluye las clases.

Los comandos de proveedor apuntaron al Python y los auxiliares de la copia,
y al classpath build/entropy_java de esa copia. Java y Node fueron externos.

## Resultado automático

| Comprobación | Resultado |
|---|---|
| Suite individual del ejecutor | 33 métodos, OK, código 0 |
| Etapas de la batería | 25 de 25, todas OK |
| Métodos unittest acumulados | 362 |
| Fallos, errores, omisiones, fallos esperados, éxitos inesperados | 0 |
| Errores de registro y etapas incompletas | Ninguno |
| Inventario del núcleo | 73/73 |
| Manifiesto | 49 nombres y hashes idénticos antes y después |
| Código final | 0 |

Los 33 métodos individuales no se suman otra vez a 362. Las primeras tres
etapas no se cuentan como métodos unittest. Los 64 archivos copiados, las 49
entradas del manifiesto y los 71 archivos de la comprobación del origen son
conjuntos y comprobaciones diferentes.

## Conservación del origen

El auxiliar informó unchanged: true, changed_or_missing: [] y checked: 71,
con código 0. La comprobación ocurrió antes de los casos manuales siguientes.
No se afirma una comprobación posterior ni conservación de todo el sistema.

## Casos manuales nuevos

| Caso | Evidencia comunicada | Límite |
|---|---|---|
| Redundante, 12 palabras, testnet | Cuatro proveedores aceptados y utilizados; SHA-512 framed; generación y verificador código 0 | No prueba independencia de fuentes |
| Current explícito, 12 palabras, testnet | Solo python_os; otros tres no intentados; reporte creado y verificador con mensaje OK | Sin códigos separados capturados para esos dos procesos |
| Interactivo, 24 palabras, testnet, passphrase BIP39 vacía | Cuatro proveedores utilizados; opción 1 autentica y comprueba BIP39, seed y estructura; opción 2 finalizada; inspector código 0 | No verifica independientemente todas las direcciones |
| Ventana del tercer caso | Apertura, visualización y cierre con Enter confirmados explícitamente por el mantenedor | No demuestra borrado seguro |

Los reportes quedaron en el output de la copia y no se adjuntan ni publican.
No se reproducen direcciones, claves públicas extendidas ni material privado.
Los tres casos nuevos no sustituyen ni convierten en repetidos los seis
casos manuales históricos. manual_terminal_tests permanece intacto en el resumen.

## Conclusión y límites

Preparación y comprobación satisfactorias de otra copia para el alcance
registrado. No fue reinstalación de Python base, Java, Node ni del sistema.
No se certifican equipo, independencia de proveedores, imprevisibilidad,
todas las derivaciones ni recuperación offline. No es publicación o release.

Conservar evidencia original sin reescribirla. Los cambios documentales
posteriores no adquieren retrospectivamente los hashes de la batería.

## Documentos relacionados

- [Integración y batería original](RESULTADOS_ENTROPY_CLI_2026-11-10.md)
- [Guía de pruebas](README.md)
- [Runtimes Linux](../docs/RUNTIMES_ENTROPY_LINUX_2026-11-10.md)
- [Instalación Linux](../docs/INSTALACION_LINUX.md)
