# Política de seguridad

## Alcance del proyecto

BIP39 Seed Report es una herramienta educativa y experimental.
No está auditada de forma independiente para custodia o producción.

La decisión de uso corresponde al usuario. Las pruebas y controles
documentados no constituyen una certificación de seguridad para
custodiar fondos.

No consulta la red Bitcoin ni construye, firma o transmite transacciones.

La verificación activa de esta etapa se realiza en Linux. Windows y macOS
quedan fuera del alcance activo; requieren revisión por quien los utilice.
Eso no implica compatibilidad aprobada ni retiro de las funciones existentes.

## Material sensible

El programa procesa entropy, mnemonic, passphrase, seed y claves privadas.
El reporte privado debe tratarse como secreto, incluso cifrado.

No publicar esos datos en issues, pull requests, capturas o logs.
No adjuntar exports privados para comunicar un fallo.

## Generación automática y proveedores experimentales

La CLI utiliza generación redundante experimental por defecto. Selecciona
aportaciones de `python_os`, `java_secure_random`, `javascript_webcrypto`
y `python_secrets` según la política implementada. `current` solicita
expresamente `os.urandom()` sin intentar los otros proveedores.

La redundancia de interfaces no prueba independencia: pueden compartir
fuentes del sistema operativo. El combinador `sha512-framed` no cuenta
con auditoría criptográfica independiente ni acredita un incremento
cuantificado de seguridad. No corrige un sistema comprometido.

El modo ejecutado puede diferir del solicitado. El reporte registra
redundancia, reducción o respaldo según corresponda. El respaldo automático
reutiliza una aportación aceptada de `python_os`; no debe confundirse con
`current` ni anunciarse como una nueva adquisición independiente.
Una preparación inválida o una combinación inadmisible puede detener la operación.

`entropy_generation` está dentro del contenido privado cifrado. Su
autenticación protege contra alteración no autorizada del reporte bajo
las condiciones del contenedor; no verifica de forma externa el origen,
la salud ni la imprevisibilidad de los bytes declarados.

Los subprocesos y runtimes amplían los componentes que deben protegerse.
El manifiesto de fuentes no certifica los binarios de Python, Java o Node,
sus bibliotecas ni toda la cadena de suministro. Un runtime aislado en
una carpeta de usuario no es un sandbox de seguridad.

El inventario de versiones, rutas y hashes identifica componentes observados;
no certifica su procedencia ni que estén libres de modificaciones maliciosas.
Instalar paquetes en un venv nuevo no reinstala ni verifica por sí solo
el intérprete base, Java, Node o el sistema operativo.

La recompilación Java de la copia ensayada es un registro distinto del
inventario de la clase histórica. No demuestra identidad binaria ni
compilación reproducible. Las clases compiladas no forman parte del
manifiesto de 49 archivos de esas baterías; sus hashes registrados
antes de la batería no se presentan como una comprobación posterior
a todos los ensayos.

El timeout de entropy es por proveedor, no un timeout global. No limita
las lecturas de contraseñas ni el tiempo de revisión en el visor.


## Controles del contenedor

El formato versión 1 comprueba estructura, tipos, claves JSON duplicadas,
algoritmos admitidos, perfil scrypt, base64 y longitudes antes de ejecutar
la KDF cuando la entrada no cumple esas condiciones.

Estos controles no sustituyen la autenticación AES-GCM ni certifican
seguridad del entorno.

## Controles del contenido JSON interno

Después del descifrado, el inspector rechaza claves duplicadas y
constantes JSON no estándar.

La opción de verificación comprueba tipos y estructura de los campos
utilizados: bits, índices, familias, listas de direcciones, rutas y
direcciones como texto no vacío. Se conservan extensiones legítimas.

Estos controles son distintos de la autenticación del contenedor exterior.
No certifican el origen de entropy ni verifican independientemente
todas las direcciones, claves o derivaciones.

## Controles de escritura

El flujo normal cifra el reporte antes de escribirlo en un temporal
situado en la carpeta de destino.

Después de completar la escritura, flush y fsync del archivo, publica
mediante os.link() sin reemplazar destinos existentes. Las colisiones
provocan reintentos de nombre sin repetir el cifrado.

Si el sistema de archivos no permite esa publicación, el programa falla
sin recurrir a os.replace() como alternativa.

En POSIX se aplica 0o600 sobre el descriptor antes de publicar y se
propagan los errores de esa operación. En Windows no se certifican ACL.

Estos controles requieren una carpeta de salida de confianza. No
garantizan durabilidad del directorio ni protección frente a cambios
hostiles de la ruta padre.

## Exposición y presentación de reportes

La terminal compacta reduce información visible, pero no proporciona
anonimato: direcciones y claves públicas extendidas permanecen visibles.
--show-all revela material privado y solo debe utilizarse con datos ficticios.
Reducir mensajes no desactiva validaciones, errores ni decisiones.

report_notices conserva advertencias dentro del contenido privado cifrado.
No certifica la imprevisibilidad de una entrada o la seguridad del equipo.

El comando del pie no se ejecuta automáticamente. Abre un inspector
distribuido que solicita la contraseña de exportación al elegir
una operación, sin incorporarla a argv.

La opción 1 no imprime el contenido privado. Su verificación JSON
no contrasta la seed cuando se utilizó una passphrase BIP39 no vacía.
No verifica independientemente todas las derivaciones.

Las opciones 2 y 3 muestran contenido privado. La segunda utiliza
una ventana dedicada; la tercera exige confirmación y utiliza la
terminal actual. Un fallo de ventana no activa una revelación alternativa.

Cada selección del menú tiene un plazo de 360 segundos. No es un
timeout de contraseñas ni un límite de lectura del visor.

Después de completar las opciones 2 o 3, el inspector termina.
Ese cierre no garantiza eliminación de scrollback, memoria, swap,
capturas o registros externos.

El inspector no crea expresamente una copia descifrada en disco.
La ventana dedicada reduce la exposición directa en la terminal
lanzadora, sin garantizar privacidad total ni borrado seguro.

Una copia descifrada para un editor es un nuevo archivo sin protección
criptográfica. Reservarla a laboratorio ficticio, fuera del repositorio
y de sincronización, con carpeta 0700 y archivo 0600 en Linux.
El editor puede dejar backups, autosaves, archivos recientes o copias
recuperables. Cerrar o eliminar no garantiza borrado seguro.

Un sistema operativo comprometido puede afectar la confidencialidad
antes o después del cifrado aunque las suites terminen con OK. Un kernel
registrado en un ensayo no equivale a un kernel certificado seguro.

## Límites conocidos

- El entorno, Python, dependencias y hardware no quedan certificados.
- El cifrado no compensa una contraseña predecible.
- La lectura oculta no protege un host comprometido.
- Limpiar pantalla o borrar archivos no garantiza eliminación segura.
- El inspector y el verificador de laboratorio limitan la lectura desde
  disco y rechazan el exceso antes de solicitar contraseña. Esto no
  garantiza el comportamiento de consumidores externos que carguen
  el archivo por su cuenta antes de llamar a la API de descifrado.
- La publicación sin reemplazo requiere enlaces duros y una carpeta
  de salida de confianza.
- No se garantiza durabilidad del directorio ante pérdida de alimentación
  ni protección frente a modificaciones hostiles de la ruta padre.
- Una interrupción abrupta puede dejar temporales.
- La revisión de ACL, procesos y casos omitidos Windows queda diferida
  fuera del alcance activo; no se dan por certificados.
- La separación de perfiles de reporte sigue pendiente.
- Las suites no cubren todas las derivaciones, plataformas o condiciones
  de ejecución.

## Alcance de la evidencia automática

La batería valida registros del worker y resultados unittest, además
de códigos de proceso, inventario y conservación de archivos protegidos.

Un código 0 no certifica el equipo ni todas las rutas de ejecución.
El inventario de funciones no es cobertura completa de ramas.

La batería corregida de la integración original,
output/bateria_local_8jy797o3, registró 25 etapas, 362 métodos unittest,
inventario 73/73 y 49 archivos conservados, con código 0.
La comprobación posterior de otra copia,
proyecto/output/bateria_local_zelv2gy3, registró los mismos conteos
y código 0. Son resultados de dos ejecuciones locales, no garantías
para otros equipos ni 724 métodos distintos.

Los 33 métodos de la suite individual del ejecutor ya están incluidos
en el acumulado de 362 de la batería; no se suman otra vez.

La copia posterior utilizó un venv nuevo, paquetes Python instalados
de nuevo y fuentes Java recompiladas sobre runtimes base existentes
del mismo equipo. No acredita instalación completa desde cero,
recuperación offline de un reporte antiguo trasladado a otro equipo
ni soporte nuevo Windows/macOS.

El ejecutor conserva un timeout por etapa, no global,
y su captura stdout mediante PIPE no tiene un límite previo equivalente
al límite del registro JSON del worker.

El manifiesto selecciona fuentes y archivos obligatorios, no todo el árbol.
La comparación antes/después no demuestra ausencia de cambios transitorios
ni valida por sí sola la procedencia de los bytes.

La comprobación de archivos del origen del laboratorio se realizó antes
de los casos manuales. No se presenta como una verificación posterior
a esos casos ni de todos los archivos del sistema.

La evidencia manual se registra por separado. Los tres casos posteriores
de la copia no sustituyen los seis manuales originales ni las pruebas
históricas del inspector. La confirmación visual de apertura, presentación
y cierre de una ventana no demuestra borrado seguro ni verificación
independiente de todas las derivaciones.

No se cambia el estado manual de un resumen automático para aparentar
una aprobación integrada.

Detalle de resultados y límites:

- [Integración entropy CLI](test/RESULTADOS_ENTROPY_CLI_2026-11-10.md).
- [Preparación de otra copia](test/RESULTADOS_COPIA_ENTROPY_2026-11-10.md).
- [Inventario de runtimes Linux](docs/RUNTIMES_ENTROPY_LINUX_2026-11-10.md).

## Comunicación de problemas

### Reporte privado de posibles vulnerabilidades

Para comunicar una posible vulnerabilidad de seguridad, escribe a:

jonnyfji.jt7rg@aleeas.com

Utiliza como asunto: [Seguridad] BIP39 Seed Report — descripción breve.

Incluye, cuando sea posible:

- Una descripción del problema y su posible impacto.
- La versión o el commit afectado.
- El sistema operativo, la versión de Python y las dependencias relevantes.
- Pasos para reproducirlo utilizando exclusivamente datos ficticios.
- El resultado esperado y el observado.

No envíes mnemonics, passphrases BIP39, contraseñas de exportación,
seeds, claves privadas, WIF ni reportes privados, aunque estén cifrados.

Revisa también las capturas, logs y archivos adjuntos para evitar
incluir información sensible.

Si necesitas compartir material adicional que no pueda publicarse,
descríbelo primero sin adjuntarlo y solicita un procedimiento adecuado
para su intercambio.

Mientras se evalúa una posible vulnerabilidad, utiliza este canal
privado en lugar de publicar sus detalles en un issue o pull request.

### Errores no sensibles y consultas generales

Los errores funcionales que no expongan una vulnerabilidad o información
privada pueden comunicarse mediante un issue en el repositorio.

Incluye pasos de reproducción y datos ficticios. No publiques secretos
ni exports privados.

### Disponibilidad y alcance

El proyecto es educativo y experimental y no cuenta con una auditoría
independiente para custodia o producción.

Los reportes se revisarán según la disponibilidad del mantenedor.
No se garantiza un plazo de respuesta o corrección ni soporte de
versiones antiguas.
