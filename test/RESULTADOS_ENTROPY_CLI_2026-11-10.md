# Resultados de integración entropy CLI — 10 de noviembre de 2026

## Identidad y alcance

Registro de una ejecución local comunicada por el mantenedor. La revisión de los artefactos JSON confirma los resultados indicados; no constituye una nueva ejecución por parte del revisor ni una auditoría criptográfica independiente.

- Batería de referencia: `output/bateria_local_8jy797o3`.
- Intérprete indicado en los comandos: `.venv-regresion-entropy-cli/bin/python`.
- Alcance activo: Linux local. No se atribuyen estos resultados a Windows/macOS.
- No se recibió el `entorno.json` de esta batería para esta revisión documental. Las versiones completas del entorno deben consultarse en su copia local; no se trasladan automáticamente las de registros anteriores.

SHA-256 del núcleo `bip39_seed_report.py`:

```text
b29675e5d91f52fd6c109a777b820945c01c12ef88e6f9926f61cc6e204e20d6
```

## Resultado automático comprobado

| Comprobación | Resultado |
|---|---|
| Etapas planificadas y completadas | 25 / 25 |
| Métodos unittest acumulados | 362 |
| Suite del ejecutor dentro de la batería | 33 métodos |
| Fallos, errores, omisiones, fallos esperados, éxitos inesperados | 0 |
| Registros del worker rechazados | 0 |
| Entradas del inventario del núcleo alcanzadas | 73 / 73 |
| Archivos del manifiesto | 49 |
| Hashes anteriores y posteriores | Iguales |
| Conjunto de archivos protegido | Conservado |
| Código final | 0 |

Los 362 métodos son la suma de `methods` de las etapas. Las etapas de vectores, cifrado y entrada segura utilizan otros procedimientos y registran cero métodos unittest; no se suman como unidades homogéneas. La ejecución individual adicional del ejecutor terminó con 33 métodos, OK y código 0 según la transcripción; no se vuelve a sumar a 362.

## Desglose de etapas

| Etapa | Métodos unittest | Estado |
|---|---:|---|
| `01_vectores` | 0 | OK |
| `02_cifrado` | 0 | OK |
| `03_entrada` | 0 | OK |
| `04_contenedor` | 18 | OK |
| `05_escritura` | 15 | OK |
| `06_regresion` | 9 | OK |
| `07_ux` | 18 | OK |
| `08_integral` | 28 | OK |
| `09_inspector` | 42 | OK |
| `10_ejecutor` | 33 | OK |
| `11_entropy_cli_integration` | 17 | OK |
| `12_entropy_combiner` | 25 | OK |
| `13_entropy_coordinator` | 13 | OK |
| `14_entropy_generation` | 15 | OK |
| `15_entropy_generation_bip39` | 6 | OK |
| `16_entropy_integration` | 14 | OK |
| `17_entropy_java_inspection` | 8 | OK |
| `18_entropy_java_provider` | 10 | OK |
| `19_entropy_node_inspection` | 13 | OK |
| `20_entropy_node_selection` | 14 | OK |
| `21_entropy_policy` | 14 | OK |
| `22_entropy_process_runner` | 18 | OK |
| `23_entropy_python_helpers` | 14 | OK |
| `24_entropy_python_real` | 5 | OK |
| `25_entropy_webcrypto_provider` | 13 | OK |

## Corrección del manifiesto JavaScript

La batería anterior `output/bateria_local_082q7ze7` registró 25 etapas, 360 métodos, 73/73 entradas y 46 archivos conservados, con código 0. Su manifiesto no incluía archivos `.cjs`; se conserva como evidencia de ese alcance anterior.

La corrección añadió `.cjs` y `.mjs` a las extensiones de fuentes, hizo obligatorios los dos auxiliares conocidos y añadió las pruebas 32 y 33 del ejecutor. En la nueva batería quedaron registrados y conservados estos tres archivos:

| Archivo | SHA-256 |
|---|---|
| `entropy_helpers/node_entropy_probe.cjs` | `f1107db2f79999e8c31ede4bf7228eddf60d9f9f2c5d42a99359e547ce99ac97` |
| `entropy_helpers/webcrypto_provider.cjs` | `8de44f14b4f4dffc93b58b914a7846452fe3ecb78b82b0491e849ffd154e82aa` |
| `test/js/test_webcrypto_provider.cjs` | `bd0b27a62c0097f6c3b925ca3fa8e2dceb7e248ddf75c10c7cc9bb37fa18593b` |

No se modifican los manifiestos de la batería anterior para atribuirle estos archivos. El salto de 46 a 49 entradas incluye también la prueba JavaScript.

## Evidencia manual separada

Los seis casos siguientes se comunicaron antes de la actualización del ejecutor. Su consolidación local es `output/consolidacion_entropy_cli_uzhSlsMl`. Los estados proceden de las transcripciones, no de una repetición al generar este documento.

| Caso | Referencia local | Resultado comunicado |
|---|---|---|
| Redundante predeterminado, JSON | `output/lab_entropy_cli_khVzRoNT/redundante.json` | Satisfactorio |
| Current explícito, JSON | `output/lab_entropy_current_D1a0rJQU/current.json` | Satisfactorio |
| Importación hexadecimal, JSON | `output/lab_import_hex_3pMughab/import_hex.json` | Satisfactorio |
| Importación binaria, JSON | `output/lab_import_bin_j9Ikf7D5/import_bin.json` | Satisfactorio |
| Importación de mnemonic completa, JSON | `output/lab_import_mnemonic_PVHpzM6p/import_mnemonic.json` | Satisfactorio |
| Redundante, TXT cifrado | `output/lab_entropy_txt_WbugC7mI/redundante.txt` | Satisfactorio tras corregir el verificador auxiliar |

En el primer caso se aceptó expresamente una advertencia por contraseña de exportación de laboratorio de menos de ocho caracteres. No es una validación de fuerza de contraseña.

La primera comprobación auxiliar TXT falló por expectativas incorrectas de cabecera y alineación. La comprobación corregida pasó sobre el mismo reporte, sin regenerarlo. Es una incidencia del procedimiento de comprobación, no un fallo demostrado del exportador.

El inspector JSON comunicó comprobaciones de BIP39, seed con passphrase vacía y estructura; no una verificación independiente de todas las direcciones. El inspector TXT verificó autenticación, cabecera y red. El bloque adicional TXT comprobó el texto registrado de modos, proveedores e indicadores; no recalculó BIP39, seed ni derivaciones.

`manual_terminal_tests` permanece pendiente en el resumen automático por diseño. No debe editarse para incorporar aprobaciones manuales.

## Límites y trabajo pendiente

- El inventario 73/73 registra entradas a funciones y métodos del núcleo; no cobertura completa de líneas, ramas o módulos externos.
- El manifiesto incluye fuentes seleccionadas y archivos obligatorios. No identifica automáticamente todos los binarios de runtimes, archivos `.class`, dependencias, directorios ocultos o documentos del proyecto.
- La conservación de hashes entre dos momentos no demuestra procedencia ni ausencia de cambios transitorios intermedios.
- Los proveedores pueden compartir fuentes del sistema operativo; no se certifica independencia entre interfaces ni imprevisibilidad de muestras.
- Los seis casos manuales no cubren todas las longitudes, redes, passphrases, modos degradados o reconstrucción de última palabra.
- No se declara una nueva validación de ventanas GNOME, espera real de timeout, Windows o macOS.
- Faltan la revisión documental general de generación y las instrucciones completas de instalación de esta integración; este documento no certifica instalación desde cero.
- No se declara una release, publicación, commit ni aprobación para custodia o producción.

## Identidad de los artefactos revisados

Los nombres siguientes son relativos al directorio de la batería. Estos hashes identifican las copias JSON recibidas para la revisión documental.

| Archivo | SHA-256 |
|---|---|
| `resumen.json` | `518d6aed905a659a4c25c4d0fecc956fd444ebebe5144abb27a856749129315f` |
| `hashes_antes.json` | `d8c646864deaee2d5a3490648eb966c82ae6ae27538527ef7eee03012bb3bd6e` |
| `hashes_despues.json` | `d8c646864deaee2d5a3490648eb966c82ae6ae27538527ef7eee03012bb3bd6e` |

## Manifiesto conservado en esta ejecución

Esta tabla reproduce las 49 entradas de los manifiestos coincidentes. Si la documentación cambia después del ensayo, el manifiesto histórico sigue identificando los bytes ensayados, no la edición posterior.

| Archivo | SHA-256 antes y después |
|---|---|
| `bip39_seed_report.py` | `b29675e5d91f52fd6c109a777b820945c01c12ef88e6f9926f61cc6e204e20d6` |
| `bip39_seed_report.py.sha256` | `98b85eff70d37b8aaec719b59d2bab9f1681edb6496df3de93919571df420654` |
| `entropy_all_config.py` | `1f6ceae2f9e193995e50937b7691be9f3388029ec30f5b993d20579f52a7aec6` |
| `entropy_cli_support.py` | `ed0d3ba18a1406159c08fe402ed914792ce5a0063be0a6278058b33435a3e49e` |
| `entropy_combiner.py` | `bc001b091585776905b40a9e217685eff75f031c91945694cb57185df0063cc8` |
| `entropy_coordinator.py` | `42574747c5a64cc6882c776dc3c3da670e551305ccb80dc6318bd3ff8dde2041` |
| `entropy_generation.py` | `d0d18f47cffbde335e0e456fc012cfc7c2ad6a6b7ba724c89f0a26cb77dbc53a` |
| `entropy_helpers/JavaEntropyProbe.java` | `3b1eba981d0d5f5c4c9f111ae0baac9615dfb444c906b9baf7b65ce9d0229b8f` |
| `entropy_helpers/JavaEntropyProvider.java` | `fe71fcd3326a56136834989f475c43de5fd5038390838e7f2e51d347b8bb16c6` |
| `entropy_helpers/node_entropy_probe.cjs` | `f1107db2f79999e8c31ede4bf7228eddf60d9f9f2c5d42a99359e547ce99ac97` |
| `entropy_helpers/python_entropy_provider.py` | `4f47c50a966bc20ce4cabc60feb10b20c2c392c69d8028d6c958b855be62061a` |
| `entropy_helpers/webcrypto_provider.cjs` | `8de44f14b4f4dffc93b58b914a7846452fe3ecb78b82b0491e849ffd154e82aa` |
| `entropy_java_config.py` | `e814f32e0abdc5e97e18064f106d27b3d28dce3e72c3642e01f813d50b51b9a6` |
| `entropy_policy.py` | `00df94e5af6f62a6437c62b6844ef2812472e106b90bd2b37b8c8dddcb782d9a` |
| `entropy_process_runner.py` | `39dde54534efb6620d1ccaa1aef6837fd20763ae7bed62419c73a8cdc33b2420` |
| `entropy_python_config.py` | `1fe21f1a71e8f26a8331a66dea7c738ad4cbbc1cbaea5f79c518c0f83f97b3c2` |
| `inspeccionar_reporte_cifrado.py` | `89a3cba173ee044c296be621e3cde38d71f7a33f5a303a2cb3bebed2699c8ce9` |
| `inspect_java_entropy.py` | `1a46722f97c52e8deba62d497d35f1304af2c07cac664891ffc606761f1e8e48` |
| `inspect_node_entropy.py` | `16b27b468fa5c0c8c37fc8fbe639e91b4d11bdb97666767eafc270fbf2f261f8` |
| `requirements.txt` | `8ea097a7976ef92f7453cd88d9108ada1ffee1be8056d79b918749020f8862c7` |
| `test/README.md` | `73fcc60e80179d3bdc2a34e549b396742d22f17db9d8bd77c94ecfe5cfcacc6d` |
| `test/ejecutar_bateria_local.py` | `8f012c40031eedb9858c78152be2b4af871e19a14849e357cb6a08abf4cfccbd` |
| `test/js/test_webcrypto_provider.cjs` | `bd0b27a62c0097f6c3b925ca3fa8e2dceb7e248ddf75c10c7cc9bb37fa18593b` |
| `test/test_cifrado_report.py` | `9c2f30718abe3ffbc65ad1aaf30c3c438550a8d93ea1a554885e1da280eb1fa1` |
| `test/test_contenedor_report.py` | `309b3be8af5ae9be2499925166ade3b4b184141d29c1ad7c8d10711106dbc86d` |
| `test/test_ejecutar_bateria_local.py` | `3807bec322965acc068ce7463a79cbd867cd634687a5837fc743b78291b0361d` |
| `test/test_entrada_segura.py` | `1658daccca58acc8d2494b2d731a73c3c198102446ea822545bf742b77c274c4` |
| `test/test_entropy_cli_integration.py` | `ad86f45e2f2dd9137e0823bdd083a435ac47f1c84b02abfcd8c25c94f2bb01e9` |
| `test/test_entropy_combiner.py` | `be2924340d4903379895cca60c24e84757c2c1e30195e87cb0502106eadcb280` |
| `test/test_entropy_coordinator.py` | `d9f2cccb124deb1f1c82e1f5844733ecb7f1d1a176ad60dfcf338d42b4298b05` |
| `test/test_entropy_generation.py` | `437540a710a5e91d5198f384809d2fa4e96bc1dcfc361a945f1d2e43bd4f9e18` |
| `test/test_entropy_generation_bip39.py` | `96985e9ba0d949aaea09b69f0d46b444d250b20b71dc8dae8432d82b2db67d90` |
| `test/test_entropy_integration.py` | `df3b70ea988914781949d88ee108c3f30b04a182ebe08c1649d26403e76562d5` |
| `test/test_entropy_java_inspection.py` | `a76aea60afbd98f72416c068618f5b4088dc66142acb3dc63863661bd3104bdc` |
| `test/test_entropy_java_provider.py` | `3c347bc75bf7b3a8fa379409f52413c405d0233d73f98f17c16df65b0c182cc3` |
| `test/test_entropy_node_inspection.py` | `0bae235ca799a5542c15db46ae32d4908ea7666b04868ea24431e6b9a7c03140` |
| `test/test_entropy_node_selection.py` | `d2f4a2d2d8eb4179a178892d2144a8f06d2c03985ac0bcf910ae82e145ef0ebc` |
| `test/test_entropy_policy.py` | `3475f36ef33806782669f34df5bd6c0c3b519fd763e892e18ac893ca4f8c6edb` |
| `test/test_entropy_process_runner.py` | `eab803c3e0ba290798c194a53904fbab364c9d0c9d605b49405aedf8e374d42c` |
| `test/test_entropy_python_helpers.py` | `77350b5f6bc8fa49e2b695f6a2e5edc318bdd636aa2fad4a43745229dc311dd7` |
| `test/test_entropy_python_real.py` | `733d802dad6d24ef8e6b00bd830a73b960ef27aefc82eb4bfec4f96b770e5a1b` |
| `test/test_entropy_webcrypto_provider.py` | `2afa1492b81a7b31387579a91ccf35d03e332802a6a20bf2e354927a7421eae3` |
| `test/test_escritura_report.py` | `9ef2f829998140c65a652bdaf14f879c5a1a748c5ed65a480103408880963f4c` |
| `test/test_inspeccionar_reporte_cifrado.py` | `d788865d599f92591c492d4ddf97eaa127e3d5ce4a148885f946faec6912c974` |
| `test/test_regresion_vectores_ultima_palabra.py` | `d98f58e0d627e63d606eec9ebbe8d7fa1e5d5effbbc30b84cd7e2665274826dc` |
| `test/test_revision_integral_report.py` | `f30a1eb6b3a1cf37e552acfee2d50d65b7b0e57e51ea19d4fd055b244c4864f8` |
| `test/test_ux_terminal_report.py` | `712a14a0d7a07a4cbcd8786bf84c0977acc25606c6d18475724ec97eef96d82b` |
| `test/vectors.json` | `fa3b937b7cff9c9b8ecd3aa011faeb8d6dd67993174b72326e83f4de8fdb30f8` |
| `test/verificar_export_laboratorio.py` | `95f0be119e0fb475c5f9a1becb7ffc34b6f9ad7b873bdc4583cd943104dba76a` |

## Conservación de la evidencia

No editar los JSON, logs, inventarios ni manifiestos de ejecuciones anteriores. Registrar correcciones posteriores en documentos o ejecuciones nuevos. No publicar reportes cifrados, contraseñas, mnemonic, seed ni claves privadas como parte de esta evidencia.
