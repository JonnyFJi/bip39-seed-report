# Runtimes de entropy en Linux — inventario del 10 de noviembre de 2026

## Alcance del complemento

Actualización documental: 12 de noviembre de 2026.

El inventario original del 10 de noviembre registra las rutas, versiones
e identidades recibidas del entorno local existente. Complementa la guía
de instalación y el cierre de la batería, sin reescribir sus evidencias.
Ese diagnóstico no instaló runtimes, recompiló Java ni adquirió entropy.

La actualización añade por separado la comprobación posterior de otra
copia en el mismo equipo. Las tablas de versiones, comandos y hashes
que siguen conservan el contenido del inventario original; no se
sustituyen por los resultados posteriores ni se presentan como un
inventario nuevo de la copia.

- Registro local: `output/inventario_runtimes_entropy_3iinl9nb/inventario_runtimes.json`.
- El mantenedor comunicó código 0 para el bloque de diagnóstico.
- Configuración de cuatro proveedores construida: `true`.
- Consultas de versión Python, Java, Node y javac: código 0 en las cuatro.
- Fuente Java, clase compilada y auxiliares configurados: presentes.
- El JSON no contiene una marca de tiempo propia; la fecha de este documento procede de la transcripción comunicada.

## Versiones observadas, no versiones recomendadas

| Componente | Resultado de la consulta | Ruta configurada o candidata |
|---|---|---|
| Python | 3.10.12 | `.venv-regresion-entropy-cli/bin/python` |
| Java | OpenJDK 11.0.33 | `/usr/lib/jvm/java-11-openjdk-amd64/bin/java` |
| Compilador candidato | javac 11.0.33 | `/usr/lib/jvm/java-11-openjdk-amd64/bin/javac` |
| Node | v24.22.2 | `$HOME/.local/opt/bip39-node/node-v24.22.2-linux-x64/bin/node` |

Java informa Runtime Environment y VM de 64 bits, build `11.0.33+9-post-1ubuntu1-22.04.1-Ubuntu`. Estas versiones identifican el laboratorio; no se presentan como una selección universal para instalaciones nuevas.

El Python del venv es un enlace a `/usr/bin/python3.10`. El registro de proveedor sigue usando el ejecutable del venv. No sustituir su ruta por la ruta resuelta para intentar reproducir el entorno: se conservará la selección explícita del intérprete utilizado en los comandos.

El candidato javac tiene versión compatible en numeración con el Java consultado. Esta observación no demuestra qué compilador creó la clase existente.

## Comandos de proveedor registrados

Los siguientes comandos representan la configuración: no deben ejecutarse manualmente como consultas de versión ni interpretarse como un ensayo realizado al generar el inventario. El protocolo añade la solicitud correspondiente durante la generación.

| Proveedor | Configuración registrada |
|---|---|
| `python_os` | Python del venv, `-I -S`, `entropy_helpers/python_entropy_provider.py` |
| `python_secrets` | El mismo comando Python y auxiliar; selección por el protocolo |
| `java_secure_random` | Java de ruta fija, `-cp`, `build/entropy_java`, clase `JavaEntropyProvider` |
| `javascript_webcrypto` | Node aislado de ruta fija y `entropy_helpers/webcrypto_provider.cjs` |

Los dos identificadores Python no representan dos intérpretes independientes. La redundancia de interfaces tampoco certifica independencia de fuentes. Que la configuración pueda construirse no garantiza que una adquisición futura termine correctamente.

La configuración Java exige que exista `build/entropy_java/JavaEntropyProvider.class`. La configuración de los cuatro proveedores llama a esa configuración Java. Una clase ausente puede impedir la preparación antes de generar: no debe anunciarse respaldo automático para cualquier error.

## Identidades de ejecutables observadas

Los hashes siguientes identifican los archivos leídos por el diagnóstico. No autentican su procedencia ni constituyen un inventario de todas las bibliotecas, módulos, paquetes o archivos del runtime. Los lanzadores Java/javac no representan por sí solos el JDK completo.

| Archivo | Bytes | SHA-256 |
|---|---:|---|
| `python` | 5941864 | `a2f33a6e006989270f4340528eb61f8f97366e00a5d1b602ac8672ea44fc56ae` |
| `java` | 14528 | `624039b54e96af1c79c20405391cfcca7c3d82035b7930c1a50a4b635dd13ac9` |
| `node` | 126881248 | `904a6d3484241d466989f9df9ba3aab822b1496191bdb28230eb491a55c32a52` |
| `javac_candidate` | 14576 | `adcf3d0f1ecced5f682df8629bc88b9c542f6f9e583217724cc6e8394edf2c03` |

## Clase Java existente

Archivo: `build/entropy_java/JavaEntropyProvider.class`.

| Bytes | SHA-256 |
|---:|---|
| 2999 | `714288785a6afa16da5efba45594a3c7eabfb9e616fa00e3c305a4fa5410cddb` |

La clase no se compiló durante este diagnóstico. La coincidencia con un hash local no prueba que corresponda a la fuente Java ni identifica los bytes que existían durante una batería anterior que no la incluyera en su manifiesto.

No borrar ni recompilar esta clase para completar la documentación.
La comprobación de compilación se realizó posteriormente en otra copia,
separada del proyecto de referencia, como se describe más abajo.
No modifica la identidad histórica de la clase registrada en esta tabla
ni demuestra retrospectivamente su correspondencia con la fuente.

## Cruce con el manifiesto de la batería

Los seis archivos siguientes tienen el mismo hash en el inventario recibido y en el manifiesto de la batería `bateria_local_8jy797o3`:

| Archivo | SHA-256 coincidente |
|---|---|
| `entropy_helpers/python_entropy_provider.py` | `4f47c50a966bc20ce4cabc60feb10b20c2c392c69d8028d6c958b855be62061a` |
| `entropy_helpers/JavaEntropyProvider.java` | `fe71fcd3326a56136834989f475c43de5fd5038390838e7f2e51d347b8bb16c6` |
| `entropy_helpers/webcrypto_provider.cjs` | `8de44f14b4f4dffc93b58b914a7846452fe3ecb78b82b0491e849ffd154e82aa` |
| `entropy_python_config.py` | `1fe21f1a71e8f26a8331a66dea7c738ad4cbbc1cbaea5f79c518c0f83f97b3c2` |
| `entropy_java_config.py` | `e814f32e0abdc5e97e18064f106d27b3d28dce3e72c3642e01f813d50b51b9a6` |
| `entropy_all_config.py` | `1f6ceae2f9e193995e50937b7691be9f3388029ec30f5b993d20579f52a7aec6` |

Esto vincula las fuentes y configuraciones comparadas entre ambos registros; no extiende retrospectivamente el manifiesto de 49 archivos a los binarios o a la clase Java. Tampoco demuestra ausencia de cambios intermedios ni relación fuente-binario.

El atributo `executable: false` en los auxiliares Python, Java fuente, clase y JavaScript no se trató como un fallo: los comandos configurados seleccionan explícitamente sus intérpretes o runtime. No se requiere cambiar permisos de esas fuentes para cerrar este inventario.

## Comprobación posterior en otra copia — 10 de noviembre de 2026

Después del inventario se preparó el laboratorio
laboratorio_entropy_3VPhWzUX, separado del proyecto de referencia.
Se copiaron y verificaron 64 archivos seleccionados, sin trasladar
el venv, el directorio build ni los reportes cifrados anteriores.

Se creó .venv-instalacion-limpia y se instalaron de nuevo las dependencias
Python. Ese entorno registró pip 22.0.2, frente a pip 26.3 del entorno
original de la batería. Ambos registraron CPython 3.10.12,
mnemonic 0.21, bip-utils 2.9.3 y cryptography 44.0.3.
No se igualan retrospectivamente los entornos.

### Compilación y selección de proveedores

Las dos fuentes Java se compilaron en la copia con
-encoding UTF-8 --release 11 y destino build/entropy_java.
La compilación terminó con código 0.

Los comandos de proveedor seleccionaron el Python y los auxiliares
de la copia y su classpath Java. Los ejecutables base de Java y Node
fueron los existentes del equipo; no se instalaron de nuevo.

Las identidades de las clases recompiladas se registraron después
de compilar y antes de la batería. La clase Provider recompilada
no fue binariamente idéntica a la histórica de 2999 bytes.
No se atribuye una causa concreta a la diferencia ni se declara
compilación reproducible byte a byte.

Las clases no forman parte del manifiesto de 49 archivos.
No se comunicó una nueva comprobación de sus hashes después
de todos los ensayos. Los hashes de la tabla histórica anterior
no deben utilizarse como valores esperados universales de compilación.

### Batería y casos manuales

La batería proyecto/output/bateria_local_zelv2gy3 terminó con
25 etapas, 362 métodos unittest, inventario del núcleo 73/73,
49 entradas del manifiesto conservadas y código 0.
La suite individual del ejecutor terminó con 33 métodos y código 0;
no se añade otra vez al acumulado.

Antes de los casos manuales se comprobaron 71 archivos registrados
del origen sin cambios y sin ausencias. No se presenta como una
comprobación posterior a esos manuales ni de todo el sistema.
Los 64 archivos copiados, las 49 entradas protegidas y los 71 archivos
del origen corresponden a conjuntos diferentes.

Los tres casos manuales nuevos se conservaron aparte:
redundante de 12 palabras, current explícito de 12 e interactivo
de 24, todos en testnet. El caso current registró mensajes
satisfactorios, pero no códigos separados de generación y verificación.
El mantenedor confirmó visualmente la apertura, presentación y cierre
con Enter de la ventana temporal del caso interactivo.

Este ensayo acredita preparación de otra copia sobre runtimes existentes,
recompilación y los flujos registrados. No acredita instalación completa
de runtimes desde cero, recuperación offline de un reporte antiguo
en otro equipo, independencia de fuentes ni soporte nuevo Windows/macOS.

Detalle:
[Resultados de preparación de otra copia](../test/RESULTADOS_COPIA_ENTROPY_2026-11-10.md).

## Condiciones para otra preparación y pendientes de instalación completa

1. Elegir una revisión de confianza que incluya los módulos, fuentes y auxiliares de esta integración; el ZIP histórico de noviembre 5 no equivale a la integración local nueva.
2. Preparar un intérprete y dependencias adecuados, conservando una selección explícita de Python. Instalar `requirements.txt` no instala Java ni Node.
3. Preparar JDK y Node de procedencia comprobada, para la arquitectura y plataforma correspondientes. Las versiones de la tabla no sustituyen una revisión de mantenimiento ni una verificación de descargas.
4. Contrastar las rutas con `entropy_python_config.py`, `entropy_java_config.py` y `entropy_all_config.py`; `PATH` o `JAVA_HOME` no sustituyen rutas fijadas en esos módulos.
5. Compilar y verificar las fuentes Java en una copia nueva, con el classpath
   de esa copia, sin sobrescribir clases históricas. Este paso se ensayó
   posteriormente sobre los runtimes existentes; no equivale a validar
   una receta completa de descarga e instalación de JDK y Node desde cero.
6. Ejecutar configuración, suites y casos manuales sobre esa nueva preparación y conservar su propia evidencia. No adjudicarle el resultado de este laboratorio.

La preparación posterior de otra copia no ejecutó una instalación completa
desde cero de Python base, JDK, Node o sistema operativo. Ese alcance y
la reproducción en otro equipo siguen pendientes de ensayo.

El diagnóstico original no modificó /usr/bin/node, el Python del sistema
ni los proveedores para registrar el inventario. Esta revisión documental
tampoco ejecuta instalación, compilación o adquisición de entropy.
Una carpeta de usuario aislada no es un sandbox de seguridad.

## Conservación y relación con los resultados

- Conservar intacto el JSON original del inventario, que contiene rutas locales completas; este documento usa rutas relativas y `$HOME` cuando corresponde.
- No incorporar estos datos dentro del `entorno.json` o los manifiestos de una batería ya cerrada.
- El diagnóstico del inventario no generó, verificó ni certificó una muestra de entropy.
- La batería original y sus seis ensayos manuales conservan su alcance.
- La batería y los tres casos manuales posteriores de la copia se registran aparte, sin reescribir manual_terminal_tests del resumen automático.
- No incorporar las identidades de las clases recompiladas a los manifiestos históricos como si hubieran estado incluidas.
- Este complemento no declara una release, una auditoría ni soporte nuevo Windows/macOS.

[Guía Linux](INSTALACION_LINUX.md) · [Resultados de la integración](../test/RESULTADOS_ENTROPY_CLI_2026-11-10.md) · [Resultados de otra copia](../test/RESULTADOS_COPIA_ENTROPY_2026-11-10.md) · [Compatibilidad](../ANALISIS_COMPATIBILIDAD_SO.md)
