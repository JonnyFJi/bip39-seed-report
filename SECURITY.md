# Política de seguridad

## Alcance del proyecto

BIP39 Seed Report es una herramienta educativa y experimental.
No está auditada de forma independiente para custodia o producción
y no se recomienda usar con fondos reales.

No consulta la red Bitcoin ni construye, firma o transmite transacciones.

La verificación activa de esta etapa se realiza en Linux. Windows y macOS
quedan fuera del alcance activo; requieren revisión por quien los utilice.
Eso no implica compatibilidad aprobada ni retiro de las funciones existentes.

## Material sensible

El programa procesa entropy, mnemonic, passphrase, seed y claves privadas.
El reporte privado debe tratarse como secreto, incluso cifrado.

No publicar esos datos en issues, pull requests, capturas o logs.
No adjuntar exports privados para comunicar un fallo.

## Controles del contenedor

El formato versión 1 comprueba estructura, tipos, claves JSON duplicadas,
algoritmos admitidos, perfil scrypt, base64 y longitudes antes de ejecutar
la KDF cuando la entrada no cumple esas condiciones.

Estos controles no sustituyen la autenticación AES-GCM ni certifican
seguridad del entorno.

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

Los comandos del pie no se ejecutan automáticamente. Solicitan la contraseña
de exportación sin incorporarla a argv. La rama de autenticación para
passphrase BIP39 no vacía no contrasta la seed con esa passphrase.
Los comandos de revelación muestran plaintext de forma explícita.

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
- El contenedor aplica validación estructural y límites, pero la lectura
  limitada desde disco no queda garantizada para todos sus consumidores.
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

## Comunicación de problemas

No se ha establecido todavía un canal privado específico.

Para errores no sensibles, abrir un issue con datos ficticios,
pasos de reproducción, versión del entorno y hash del script.

Si el informe requiere información sensible, no publicarla.
Solicitar primero al mantenedor un canal privado adecuado.

No se promete un plazo de respuesta ni soporte de versiones antiguas.
