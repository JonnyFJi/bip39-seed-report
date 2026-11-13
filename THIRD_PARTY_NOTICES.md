# Avisos de terceros

Fecha de revisión inicial: 12 de octubre de 2026.
Actualización documental: 11 de noviembre de 2026.
Repositorio revisado: JonnyFJi/bip39-seed-report.
Commit base de la revisión inicial:
`c2300751fb56f8a9873612798347c15a47a6ac9a`.

## Alcance y estado

El código original del proyecto usa MIT según LICENSE. Ese archivo no sustituye las licencias o avisos de material de terceros.

Este documento identifica datos incluidos y dependencias externas. Es un inventario inicial, no una certificación legal completa, SBOM exhaustiva ni auditoría de vulnerabilidades. Algunos orígenes históricos y textos del artefacto exacto siguen pendientes. No interpretar las referencias al upstream actual como prueba del commit desde el que se copió originalmente un archivo.

La actualización del 11 de noviembre distingue el material incorporado
al repositorio de las dependencias y runtimes utilizados externamente
en los ensayos de entropy. No completa la revisión de licencias de
todos los artefactos ni establece la procedencia histórica de los
fragmentos de código.

La publicación preparada no contempla redistribuir venvs, paquetes
instalados, node_modules, JDK/JRE, ejecutables de Node ni clases Java
compiladas. Esa separación debe comprobarse en la selección final
de archivos; no se deduce únicamente de las reglas de .gitignore.

## 1. Datos incluidos en el repositorio

### Wordlist BIP39 inglesa

- Ubicación: BIP39_OFFICIAL_WORDLIST dentro de bip39_seed_report.py.
- Contenido: 2048 palabras inglesas de referencia BIP39.
- Proyecto upstream de referencia: https://github.com/trezor/python-mnemonic
- Especificación de referencia: https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki
- Licencia upstream consultada: MIT.
- Aviso upstream consultado: Copyright (c) 2013-2016 Pavol Rusnak.
- LICENSE upstream, identificador Git consultado: b1357446497a09f87bc5e956d5c45b77e28f8545.
- SHA-256 utilizado para la representación local (palabras unidas por LF, sin LF adicional al final): 187db04a869dd9bc7be80d21a86497d692c0db6abd3aa8cb6be5d618ff757fae.
- Pendiente: documentar el commit/artefacto histórico exacto del que se incorporó la lista. No atribuir otros fragmentos de código automáticamente a este origen.

### Vectores BIP39

- Ubicación: test/vectors.json.
- Proyecto upstream declarado/de referencia: trezor/python-mnemonic, archivo vectors.json.
- Licencia del proyecto upstream consultado: MIT; conservar el texto del apartado 2.
- SHA-256 de los bytes locales registrados: fa3b937b7cff9c9b8ecd3aa011faeb8d6dd67993174b72326e83f4de8fdb30f8.
- Identificador Git del contenido publicado: d362a5d4eb1ba800a52aec30116915cd4576e1fd.
- No son secretos de usuario. No deben utilizarse para fondos reales.
- Pendiente: fijar una referencia upstream inmutable y comparar sus bytes con la copia distribuida; comprobar si el artefacto exacto contiene otros avisos aplicables.

## 2. Texto de licencia upstream de python-mnemonic

El aviso siguiente reproduce el LICENSE consultado del proyecto upstream de referencia. Complementa, no reemplaza, el LICENSE del código original de este repositorio.

```text
The MIT License (MIT)

Copyright (c) 2013-2016 Pavol Rusnak

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 3. Dependencias directas externas

Se importan desde el entorno; no se observó una copia vendorizada de sus paquetes en la estructura revisada. Sus avisos originales deben mantenerse si se redistribuyen paquetes, wheels, binarios, entornos o una aplicación empaquetada.

| Paquete fijado | Proyecto | Licencia de referencia | Estado |
|---|---|---|---|
| mnemonic==0.21 | https://github.com/trezor/python-mnemonic | MIT | Metadatos públicos identifican MIT; verificar avisos del artefacto 0.21 exacto |
| bip-utils==2.9.3 | https://github.com/ebellocchia/bip_utils | MIT | Proyecto identifica MIT; verificar aviso/copyright del artefacto 2.9.3 exacto |
| cryptography==44.0.3 | https://github.com/pyca/cryptography | Apache-2.0 OR BSD-3-Clause | Documentación 44.0.3 describe licencia alternativa; conservar archivos originales al redistribuir |

No copiar como aviso histórico de bip-utils 2.9.3 el copyright del branch upstream actual sin cotejar el artefacto de esa versión. No interpretar OR como obligación de relicenciar esas dependencias bajo MIT.

## 4. Dependencias transitivas observadas

El log del entorno del usuario registró cbor2, crcmod, ecdsa, pycryptodome, PyNaCl, ed25519-blake2b, coincurve, py-sr25519-bindings, cffi, six, pycparser y asn1crypto.

Este listado no es un bloqueo ni un inventario completo. Los wheels o componentes nativos pueden incluir otros materiales (por ejemplo bibliotecas criptográficas) con avisos propios. Licencias y copyright exactos de cada artefacto: pendientes de inventariar antes de redistribuir el entorno o binarios.

En el registro inicial, la salida 'Requirement already satisfied'
refleja paquetes existentes, incluidos paquetes de usuario y del sistema;
ese registro no acredita una instalación limpia.

El listado anterior corresponde al entorno existente comunicado
inicialmente, no al entorno virtual de verificación.

Posteriormente se comunicó una instalación en .venv-verificacion
con versiones transitivas diferentes y suites satisfactorias.
asn1crypto no aparece en ese segundo log.

Los registros describen entornos observados; no constituyen un
bloqueo de dependencias ni un inventario exhaustivo de licencias.

La comprobación posterior de otra copia del 10 de noviembre utilizó
un venv nuevo e instaló de nuevo los paquetes Python. Se comunicaron
instalaciones de crcmod y ed25519-blake2b mediante setup.py install,
con resultado satisfactorio; no se describe como una instalación
exclusivamente desde wheels.

Ese ensayo no inspeccionó de forma exhaustiva los LICENSE/NOTICE
de cada distribución o componente nativo. Tampoco convierte los
listados históricos en un único inventario común a todos los entornos.

Detalle:
[Resultados de preparación de otra copia](test/RESULTADOS_COPIA_ENTROPY_2026-11-10.md).

## 5. Runtimes y auxiliares de la integración entropy

### Runtimes externos observados

La integración utiliza comandos configurados para Python, Java y Node.
Los registros locales identifican los siguientes runtimes; no son
artefactos incorporados automáticamente al repositorio por utilizarlos:

| Componente observado | Versión comunicada | Alcance del registro |
|---|---|---|
| CPython | 3.10.12 | Intérprete utilizado en los entornos Linux registrados |
| OpenJDK y javac | 11.0.33 | Consultas posteriores y compilación Java de la copia |
| Node.js | v24.22.2 | Ejecutable externo seleccionado en la configuración local |

Las versiones no identifican por sí solas el distribuidor, el paquete
de instalación ni todos sus componentes. No se asigna aquí una licencia
única a Python, Java o Node ni se extiende MIT del proyecto a esos runtimes.

La comprobación de otra copia reutilizó los runtimes base existentes
del mismo equipo. Un venv nuevo o una recompilación Java no constituye
una nueva instalación de todos esos componentes.

El inventario de rutas, versiones y hashes no sustituye los archivos
de licencia del artefacto exacto. Si se cambia el formato de distribución
para incluir runtimes, bibliotecas, entornos o binarios, deberá revisarse
el inventario y conservarse la documentación de terceros aplicable
antes de preparar ese paquete.

Detalle:
[Inventario de runtimes Linux](docs/RUNTIMES_ENTROPY_LINUX_2026-11-10.md).

### Fuentes y auxiliares distribuidos por el proyecto

La actualización contempla módulos Python, fuentes Java y auxiliares
JavaScript/CommonJS, además de sus pruebas. Utilizar una API de Python,
Java o Node no identifica por sí solo la procedencia de esas fuentes
ni demuestra que se haya incorporado código de sus implementaciones.

La autoría y procedencia de los fragmentos distribuidos deben revisarse
por archivo. Si contienen material adaptado o copiado de terceros,
se deben identificar el origen y los avisos correspondientes; no se
presume que todo el contenido quede cubierto únicamente por el LICENSE
del código original del proyecto.

Las clases Java generadas localmente son resultados de compilación.
Sus hashes y diferencias respecto de una clase histórica no determinan
la licencia ni demuestran una compilación reproducible.
No se incluyen como sustituto de las fuentes o de sus avisos.

## 6. Verificación pendiente y mantenimiento

- Fijar origen exacto de wordlist y vectores, conservando avisos aplicables.
- Inspeccionar los LICENSE/NOTICE de las versiones directas exactas y sus distribuciones.
- Inventariar dependencias transitivas y componentes nativos si se redistribuyen.
- Revisar código incorporado de otras fuentes y añadir avisos adicionales cuando correspondan.
- Registrar versión, hash de artefacto y origen sin incluir rutas privadas innecesarias.
- Revisar este documento al cambiar datos, dependencias o formato de distribución.
- Comprobar la procedencia y los avisos de los módulos y auxiliares
  incorporados en la integración entropy, sin atribuirlos automáticamente
  a los proveedores de las APIs utilizadas.
- Identificar distribuidor, artefacto exacto y documentación de licencia
  de los runtimes si se propone redistribuirlos.
- Comprobar que la selección final de publicación excluye entornos,
  dependencias instaladas y binarios locales no previstos para distribución.

No atribuir a JonnyFJi la autoría del material de terceros ni eliminar sus avisos. Las referencias a estándares no implican patrocinio, aprobación ni auditoría por sus autores.
