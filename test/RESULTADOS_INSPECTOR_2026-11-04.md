# Resultados del inspector — 4 de noviembre de 2026

## Procedencia y alcance

Resultados comunicados por el mantenedor mediante salidas de terminal
y confirmaciones manuales.

Este documento resume la evidencia sin publicar contraseñas, mnemonic,
seed, WIF ni exports privados.

Fecha de comunicación y cierre de la revisión: 4 de noviembre de 2026.
No se atribuyen marcas temporales exactas a cada ejecución.

Los resultados respaldan los casos descritos en los entornos utilizados.
No constituyen una auditoría independiente ni soporte universal.

## Identidad del núcleo

Archivo: bip39_seed_report.py.

SHA-256:

```text
b09fcc4f292283b8d5e6f4470dc3858a079b209b1c3ccb579be27cdec51b5174
```

La comprobación con bip39_seed_report.py.sha256 coincidió antes y
después de la suite individual.

El ajuste de timeout y finalización modifica el inspector y su suite,
no el núcleo. El hash del núcleo no identifica por sí solo los bytes
del inspector ni de sus pruebas.

Los manifiestos locales de la batería conservan los hashes de los
13 archivos protegidos.

## A. Evidencia automática

### Entorno

- Linux local.
- Intérprete observado: .venv-verificacion/bin/python.
- No se atribuye al ensayo manual el entorno de paquetes del venv.
- Los detalles adicionales del entorno se conservan en entorno.json local.

### Suite individual del inspector

- Sintaxis del inspector y de su suite: correcta.
- Métodos ejecutados: 32.
- Duración interna comunicada: 7,140 segundos.
- Resultado: OK.
- Código de salida: 0.

Las pruebas incluyen mocks y un round-trip con cifrado real.
Las simulaciones del menú no esperan 360 segundos y las del lanzador
no constituyen apertura real de GNOME Terminal.

### Batería completa posterior al parche

Identificador local: bateria_local_zikvxpur.

| Etapa | Duración externa | Código | Estado |
|---|---:|---:|---|
| 01_vectores | 1,714 s | 0 | OK |
| 02_cifrado | 19,712 s | 0 | OK |
| 03_entrada | 1,634 s | 0 | OK |
| 04_contenedor | 7,010 s | 0 | OK |
| 05_escritura | 2,446 s | 0 | OK |
| 06_regresion | 2,977 s | 0 | OK |
| 07_ux | 12,707 s | 0 | OK |
| 08_integral | 4,028 s | 0 | OK |
| 09_inspector | 7,260 s | 0 | OK |

Resultado global:

- Nueve etapas satisfactorias.
- Sin omisiones informadas.
- Inventario del núcleo: 70/70 entradas alcanzadas.
- Archivos protegidos sin cambios: True.
- Código final: 0.

El inventario registra entradas a 69 funciones superiores y un método
del núcleo. No representa cobertura completa de líneas o ramas ni
incorpora las funciones del inspector.

El manifiesto protege 13 archivos únicos. El propio ejecutor y la
documentación no forman parte de ese conjunto.

Las duraciones externas de las etapas y los tiempos internos de unittest
miden cosas diferentes. No se presentan como benchmark.

## B. Evidencia manual

### Entorno y método

- Linux local.
- Intérprete observado en los comandos: /usr/bin/python3.
- Ventana temporal de GNOME Terminal.
- Reportes JSON de laboratorio, sin passphrase BIP39.
- Los resultados no se extrapolan a TXT, passphrase no vacía, Windows
  o macOS como ensayos manuales de esta actualización.
- No se atribuye a /usr/bin/python3 un pip check satisfactorio a partir
  de estas pruebas de interacción.

### Casos ejecutados

| N.º | Caso | Resultado observado |
|---:|---|---|
| 1 | Opción 1 correcta | Autentica sin imprimir contenido privado y vuelve al menú temporizado |
| 2 | Opción 2 correcta | Muestra el reporte en el visor; Enter cierra la ventana y el inspector principal termina con código 0 |
| 3 | Opción 2 con contraseña incorrecta | Rechazo en el visor y retorno al menú, sin revelación alternativa; salida posterior con Q y código 0 |
| 4 | Opción 3, responder n | Cancela sin solicitar contraseña y vuelve al menú; salida posterior con Q y código 0 |
| 5 | Opción 3 confirmada y contraseña correcta | Muestra el reporte y termina directamente con código 0 |
| 6 | Opción 3 con contraseña incorrecta | Error controlado y retorno al menú; salida posterior con Q y código 0 |
| 7 | Menú sin responder | Cancela automáticamente al cumplirse el plazo; código 1 |
| 8 | Q | Termina directamente con código 0 |
| 9 | Ctrl+C | Cancelación controlada, sin revelación alternativa; código 1 |

El mantenedor confirmó expresamente el cierre visual de la ventana
en la prueba 2 y una espera de 360 segundos en la prueba 7.

La duración del timeout se registra como confirmación manual del
mantenedor, no como medición independiente mediante un log temporizado.

En las pruebas negativas seguidas de Q, el código final 0 corresponde
a Q y no convierte el intento de descifrado en satisfactorio.

Resultado manual: nueve casos satisfactorios para el alcance descrito.

## Separación de evidencias

El código 0 de la batería no aprueba automáticamente los ensayos manuales.

manual_terminal_tests permanece PENDIENTES en el resumen automático
por diseño. Este documento registra aparte los resultados manuales;
no reescribe los artefactos originales.

Los registros completos permanecen locales. No se adjuntan transcripciones
que contienen material privado.

## Límites

- No se verifican independientemente todas las derivaciones.
- Una TTY y las pruebas satisfactorias no certifican el entorno.
- La ventana dedicada no garantiza borrado de memoria, swap o registros.
- Terminar la opción 3 no elimina el scrollback de la terminal.
- El plazo de 360 segundos corresponde a selección de menú, no a todas
  las lecturas ni a la duración del visor.
- No se registró una nueva certificación de compatibilidad Windows/macOS.
