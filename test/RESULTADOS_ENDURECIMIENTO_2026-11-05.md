# Resultados del endurecimiento — 5 de noviembre de 2026

## Procedencia y alcance

Resultados comunicados por el mantenedor mediante salidas de terminal.

Este documento separa evidencia automática y manual. No publica
contraseñas, mnemonic, seed, WIF ni exports privados.

No constituye una auditoría independiente ni soporte universal
de plataformas.

## Identidad de la publicación revisada

Commit publicado revisado:

```text
107e527b8507e8f257ee0a093ff1a90ce02744ad
```

Esta referencia identifica la publicación consultada. No se afirma
que las salidas locales hayan registrado su HEAD Git.

SHA-256 del núcleo:

```text
b09fcc4f292283b8d5e6f4470dc3858a079b209b1c3ccb579be27cdec51b5174
```

El núcleo y su checksum no cambian durante este endurecimiento.

El hash del núcleo no identifica por sí solo el inspector, el ejecutor
o sus pruebas. La publicación fija el conjunto de fuentes; los manifiestos
locales conservan los hashes de los archivos protegidos.

## Cambios comprendidos

- Parser del JSON interno con rechazo de claves duplicadas y constantes
  no estándar.
- Validación de tipos y estructuras del reporte.
- Conservación de campos adicionales legítimos.
- Inspector ampliado de 32 a 42 métodos de prueba.
- Validación estricta de registros del worker.
- Evaluación de fallos y errores unittest aunque el proceso termine 0.
- Detección de suites vacías y resultados incompletos.
- Nueva suite del protocolo del ejecutor de 20 métodos.
- Incorporación de 10_ejecutor a la batería.

No se modifican generación, conversiones BIP39, derivaciones, perfil KDF,
AES-256-GCM ni publicación de exports.

## A. Evidencia automática

### Entorno observado

- Linux local.
- Python 3.10.12.
- pip 22.0.2.
- Ejecución de las suites y batería mediante .venv-verificacion/bin/python.
- mnemonic 0.21.
- bip-utils 2.9.3.
- cryptography 44.0.3.
- pip check: No broken requirements found.

La instalación informa Requirement already satisfied.
No se presenta como una instalación limpia desde cero.

No se trasladan automáticamente a este ensayo la distribución,
arquitectura o versión de kernel de registros históricos.

### Ejecuciones individuales

Las suites previas continúan mostrando resultados satisfactorios:
vectores BIP39, cifrado, entrada segura, contenedor, escritura,
regresión, UX y suite complementaria.

La suite del inspector muestra:

| Ejecución comunicada | Métodos | Duración interna | Resultado |
|---|---:|---:|---|
| Primera | 42 | 5,702 s | OK |
| Segunda | 42 | 6,074 s | OK |

La suite del protocolo del ejecutor contiene 20 métodos.
Su ejecución integrada figura como etapa 10_ejecutor satisfactoria.
El registro compartido no muestra una duración interna individual
separada de esa suite.

### Baterías completas

| Identificador local | Etapas | Inventario del núcleo | Archivos protegidos sin cambios | Código final |
|---|---:|---:|---|---:|
| bateria_local_l3fhi573 | 10 OK | 70/70 | True | 0 |
| bateria_local_s6olai6g | 10 OK | 70/70 | True | 0 |

La segunda ejecución incluye además echo $? con resultado 0.

El manifiesto actual define 14 rutas únicas. El ejecutor informa
su conservación durante las pruebas. No incluye el propio ejecutor
ni toda la documentación.

El inventario registra entradas a 69 funciones superiores y un método
del núcleo. No equivale a cobertura completa de líneas, ramas,
plataformas o validez criptográfica independiente.

Los vectores, comprobaciones y métodos unittest son unidades distintas;
no se suman como una cantidad homogénea de pruebas.

## B. Evidencia manual

### Intento inicial con ruta de ejemplo

El comando dirigido a output/laboratorio/reporte.json terminó con
FileNotFoundError y código 1.

Ese intento no autenticó el archivo ni demostró un fallo de contraseña
o del cifrado. Se conserva como incidencia de ruta.

### Repetición con archivo existente

Se generó un reporte JSON ficticio con:

- 12 palabras.
- Red testnet.
- Modo de entrada words.
- Passphrase BIP39 vacía.

Archivo final del ensayo: bip39_seed_report_027.json.

Se ejecutó test/verificar_export_laboratorio.py con expectativas
coincidentes de palabras, red y modo de entrada.

Resultado:

```text
OK: export autenticado; BIP39, seed y estructura de derivaciones verificados sin imprimir secretos
```

El código de salida fue 0.

La generación utilizó python3; el pie identifica /usr/bin/python3.
El auxiliar se ejecutó mediante "$PY". La captura de esta repetición
no incluye una nueva impresión de sys.executable para el auxiliar.

La prueba resuelve el intento con ruta inexistente. No verifica
independientemente todas las direcciones.

### Relación con los ensayos anteriores

Los nueve casos manuales del menú del 4 de noviembre se conservan en
[RESULTADOS_INSPECTOR_2026-11-04.md](RESULTADOS_INSPECTOR_2026-11-04.md).

No se afirma que se hayan repetido todos durante este endurecimiento.

## Separación y conservación de evidencias

El código 0 automático no aprueba los ensayos manuales.

manual_terminal_tests permanece PENDIENTES en los JSON automáticos
por diseño. Este documento registra aparte el resultado manual;
no reescribe los artefactos originales.

Los logs completos y manifiestos permanecen locales.
No se publican transcripciones con contenido privado.

## Límites

- Las pruebas con mocks no sustituyen una terminal o ventana real.
- Las pruebas del protocolo no cubren todas las rutas del coordinador.
- El esquema interno validado no certifica todas las derivaciones.
- Las pruebas no certifican el entorno ni la imprevisibilidad de entropy.
- No se declara una nueva ejecución Windows o macOS.
- El cierre de procesos no garantiza borrado de memoria o scrollback.
