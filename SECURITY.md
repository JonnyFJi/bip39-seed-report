# Política de seguridad

## Alcance del proyecto

BIP39 Seed Report es una herramienta educativa y experimental.
No está auditada de forma independiente para custodia o producción
y no se recomienda usar con fondos reales.

No consulta la red Bitcoin ni construye, firma o transmite transacciones.

## Material sensible

El programa procesa entropy, mnemonic, passphrase, seed y claves privadas.
El reporte privado debe tratarse como secreto, incluso cifrado.

No publicar esos datos en issues, pull requests, capturas o logs.
No adjuntar exports privados para comunicar un fallo.

## Límites conocidos

- El entorno, Python, dependencias y hardware no quedan certificados.
- El cifrado no compensa una contraseña predecible.
- La lectura oculta no protege un host comprometido.
- Limpiar pantalla o borrar archivos no garantiza eliminación segura.
- La validación estricta del contenedor sigue pendiente.
- La protección frente a sobrescritura concurrente sigue pendiente.
- La separación de perfiles de reporte sigue pendiente.
- Las suites no cubren todas las derivaciones o plataformas.

## Comunicación de problemas

No se ha establecido todavía un canal privado específico.

Para errores no sensibles, abrir un issue con datos ficticios,
pasos de reproducción, versión del entorno y hash del script.

Si el informe requiere información sensible, no publicarla.
Solicitar primero al mantenedor un canal privado adecuado.

No se promete un plazo de respuesta ni soporte de versiones antiguas.
