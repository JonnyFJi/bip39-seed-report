# Combinador de entropy — especificación experimental v1

Estado: experimental. Utilizado por la integración local de generación
automática BIP39 del programa principal.
Esta descripción se ha contrastado mediante revisión estática del
combinador, la política, la adaptación CLI y la suite proporcionados.
No constituye una auditoría criptográfica independiente ni una nueva
ejecución de pruebas.

No utilizar los vectores públicos de prueba como material de wallet.

## Identificadores

- Version: sha512-framed-v1
- Proposito: bip39-initial-entropy
- Politica: redundant-with-os-backup-and-java-pair-v1
- Cabecera binaria: BSR-ENTROPY seguida de un byte NUL.
- Cabecera hexadecimal: 4253522d454e54524f505900

## Entradas

Se recibe un AcquisitionResult del coordinador.

Antes de finalizar:
1. Se recalcula el plan desde los cuatro estados.
2. Se exige coincidencia con el plan recibido.
3. Se exige que las aportaciones coincidan exactamente con los
   identificadores seleccionados.
4. Cada aportacion debe ser bytes de longitud 32.
5. Se toma una copia del contenedor de aportaciones.

No se evalua la apariencia de los bytes ni se estima su entropy.

## Selección de modo

La política se aplica antes de combinar las aportaciones:

- Con tres o cuatro proveedores aceptados, selecciona `redundante`
  y utiliza todos los aceptados, incluso si `python_os` no está entre ellos.
- Con menos de tres aceptados y `python_os` aceptado, selecciona
  `actual_respaldo` y utiliza únicamente su aportación.
- Sin `python_os` aceptado, si están aceptados `java_secure_random`
  y `javascript_webcrypto`, selecciona `redundante_reducido`.
- Las demás combinaciones detienen la operación.

Un proveedor aceptado puede quedar omitido por la política; omitido
no significa necesariamente fallido.

El combinador recalcula esta selección y rechaza un plan incoherente.
No adquiere bytes ni decide una adquisición alternativa.

## Modos redundantes

Se utiliza SHA-512 sobre la cabecera y los campos siguientes.

Cada campo se codifica como:

longitud de cuatro bytes, unsigned, big-endian
seguida de los bytes del campo.

Campos, en este orden:

1. Version del combinador, ASCII.
2. Version de la politica, ASCII.
3. Proposito, ASCII.
4. Nombre del modo, ASCII.
5. Longitud de salida en bits: entero de dos bytes, big-endian.
6. Cantidad de proveedores seleccionados: entero de un byte.
7. Para cada proveedor seleccionado, en orden canonico:
   - Identificador, ASCII.
   - Aportacion binaria de 32 bytes.

La longitud de cuatro bytes se aplica tambien a los campos
numericos y a cada aportacion.

Orden canonico:
- python_os
- java_secure_random
- javascript_webcrypto
- python_secrets

Solo se incluyen los proveedores seleccionados.

Salida:
primeros ENT/8 bytes del digest SHA-512, donde ENT es
128, 160, 192, 224 o 256.

No se incorporan fechas, rutas, PID, tiempos, mensajes de error,
passphrases ni otras entradas.

## Modo actual_respaldo

Se utiliza directamente el prefijo de ENT/8 bytes de la aportacion
ya aceptada de python_os.

No se calcula SHA-512.
No se vuelve a ejecutar el proveedor.
No se aplica separacion criptografica de proposito en este modo.

## Modo current explícito

La opción CLI `--entropy-mode current` no utiliza este combinador.
La adaptación CLI llama al generador actual recibido y registra
`actual_explicito`, método `os.urandom`, sin versión de política
ni versión de combinador.

No debe confundirse con `actual_respaldo`: este último reutiliza
la aportación de `python_os` ya aceptada durante la adquisición
del modo redundante.

## Fallos

Los errores de coherencia o del hash detienen la operacion.
No activan respaldo ni una nueva adquisicion.

## Privacidad

No registrar ni exportar:
- aportaciones individuales;
- transcript binario;
- digest completo;
- hashes de las aportaciones.

El resultado contiene entropy secreta y debe tratarse como tal.
Excluirla del repr no hace segura una serializacion completa.

## Uso por operacion

Cada nueva generacion debe comenzar con una nueva adquisicion.
Este modulo es determinista y no detecta reutilizacion de entradas.
No es un generador con estado ni un mecanismo de expansion.

## Limites

Este formato es propio del proyecto, no una norma BIP39.
No tiene una auditoria criptografica independiente.
Las pruebas verifican comportamiento, no imprevisibilidad.

No se garantiza proteccion frente a fuentes correlacionadas,
un proceso comprometido, un combinador alterado o un fallo comun.

Una futura implementacion Electrum o de fuentes manuales requiere
su especificacion y revision; no debe reutilizar este proposito
silenciosamente.
