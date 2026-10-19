# Inferencia local de Qwen3.6 en un laptop de8GB: estudio exploratorio de MTP y DFlash

**Autor del experimento:** apg10. **Asistencia técnica y redacción:** Codex. **Corte documental:**2026-10-20, Australia/Sydney. Informe de caso, sin revisión por pares.

## Resumen

Se estudió Qwen3.6-35B-A3B Q4_K_M en OpenCode sobre CPU+GPU híbrida. Se compararon generación autoregresiva, MTP2/MTP3 y DFlash3/4/8, además de explorar Strata y Bonsai2 27B ternario. La selección operativa final fueMTP2,16 hilos para generación y prefill, contexto131072 y salida32768, presence_penalty0.5. Los resultados variaron significativamente entre ejecuciones: MTP3 mostró inicialmente~51t/s frente a~41 de baseline, pero su retest fue36–37t/s frente a35. MTP2 en un retest separado alcanzó45–48t/s. DFlash aceleró respuestas repetidas con caché, pero las restricciones de memoria obligaron a reducir microbatch y su prefill fue mucho más lento. No se demuestra un ganador universal.

## Equipo y software

Lenovo Legion Pro5 16ADR10; Ryzen9 8945HX,16 núcleos/32 hilos; RAM31,1GiB (~32GB comerciales); RTX5070 Laptop8GB. Diferentes capturas muestran8151 o~7682MiB totales y~49–50W durante carga: no confundir esos estados ni equiparar estaGPU con una5070Ti de escritorio. Temperaturas observadas generalmente69–77°C. Linux con escritorio, OpenCode y otras aplicaciones abiertos. La carga del sistema no se controló como en laboratorio.

Motor MTP/DFlash: llama-server empaquetado conOllama,0.4.1-dev, commit161755f29. CUDA plugin se cargó explícitamente desde cuda_v13. Los primeros intentos sin plugin fueronCPU-only y se excluyen. El GGUF fuente deOllama tiene23GB y metadata/visión/MTP legado; no esFP8. No se ejecutóSGLang, tp8, niNEXTN conFP8. KV principal:q4_0 paraK yV; FlashAttention activado.

## Preparación de MTP

Se trabajó sobre una copia del modelo, manteniendo intacto el original. Conversión metadata:block_count40→41, extensión dehead_count_kv y nextn_predict_layers1. Renombres mtp.layers.0→blk.40 y nextn; ssm_dt→ssm_dt.bias. Dos vectores F32 de prenormalización del draft se convirtieron con+1, siguiendo el patrón del convertidorQwen. Antes de esta corrección la aceptación era casi0; después pasó a valores útiles. Los pesos cuantizados principales no cambiaron; por tanto no se afirma que todo el archivo sea byte-idéntico. El manifiesto numérico conserva offsets y hashes para auditoría.

El MTP propuesto reutiliza una cabeza predictiva en varios pasos;2 o3 drafts no significa2 o3 modelos completos. La colocación de seis capas expertas principales enGPU agotó memoria. Se usaron36 capas de expertos principales enCPU, cuatro finales enGPU; expertosMTP enCPU. Es una distribución manual, no réplica exacta del planificador automáticoOllama.

## Método

Petición sintética con640 requisitos repetibles y generación de código Python de almacén clave-valor,14536 tokens de entrada y512 de salida. Dos peticiones: primera y repetición exacta. Temperatura0, seed42, thinking desactivado en este benchmark. Contexto131072 reservado, un slot,16 hilos, batch/microbatch512 salvoDFlash microbatch128. Luego tool roundtrip sumar17+25 y comunicar42. Las pruebas adicionales de streaming/thinking e imágenes se separan del benchmark de velocidad.

La carga del modelo se excluye del tiempo de generación. La latencia de petición incluyeprefill y generación, por lo que un alto t/s de generación no garantiza respuesta más rápida. Los experimentos iniciales y retests no son mediciones simultáneas, no tienen intervalos de confianza y cambiaron condiciones de caché/temperatura/memoria. Los nombres fresh/earlier son etiquetas históricas relativas, no una garantía de igualdad térmica.

## Resultados numéricos

| Configuración | Prefill t/s | Generación primera t/s | Generación caché t/s | Petición primera s | Petición caché s |
|---|---:|---:|---:|---:|---:|
| Baseline (fresh) | 369.0 | 34.6 | 35.0 | 54.19 | 14.79 |
| MTP3 (fresh) | 356.8 | 36.0 | 37.3 | 54.96 | 13.93 |
| MTP2 (production settings retest) | 368.9 | 48.3 | 45.2 | 50.02 | 11.51 |
| MTP2 (earlier) | 367.1 | 42.5 | 40.3 | 51.64 | 12.89 |
| DFlash3 (earlier) | 121.9 | 38.0 | 51.3 | 132.69 | 10.14 |
| DFlash4 (earlier) | 120.8 | 33.0 | 51.9 | 135.82 | 10.04 |
| DFlash8 (earlier) | 127.3 | 25.0 | 47.4 | 134.68 | 10.98 |

Baseline yMTP3 fresh se midieron consecutivamente. MTP2 production retest se hizo después, con el proyector de visión y los ajustes de producción presentes, pero thinking desactivado en la petición medida. MTP2 earlier no tenía el mismo estado de integración. DFlash conservó la colocación principal de expertos pero necesitóub128; esto compara configuraciones viables, no aísla exclusivamente el algoritmo.

En la comparación inicial, baseline40,98/41,31t/s, MTP242,53/40,27 yMTP351,40/51,30. La conclusión inicial de~24–25% a favorMTP3 solo aplica a esa sesión. El retest baseline34,60/34,98 frente aMTP336,00/37,27 dio~4–7% de mejora de generación y latencia inicial casi igual. El MTP2 posterior48,25/45,18 fue prometedor, pero no autoriza una afirmación estadística de superioridad permanente.

## DFlash: memoria, bloque y visión

Draft Q8_0:421MB; alternativaQ4_K_M236MB disponible pero NO probada. Sus pesos son menores que solo los tres tensores expertosMTP (~523MB); esto no equivale a menor uso total en ejecución. Conub512 falló una reservaCUDA de~975MiB. Conub128 arrancó y se observó~369MiB libre en una muestra. El prefill inicial de14,5k tardó114–120s frente a39–41s en baseline/MTP. Las repeticiones exactas tardaron~10–11s porque se reutilizó casi todo el prompt.

La metadata declara block_size16 como límite entrenado. El código upstream deDFlash ordinario construye un bloque de n_max+1 contando el ancla. Por tanto n_max8 no es bloque total8; este último sería n_max7 y no se midió. n_max3,4,8 son máximos de tokens draft; la aceptación descendió aproximadamente73%,64%,45% en las primeras muestras. Mayor aceptación tampoco garantiza mayor velocidad, porque importa cuántos tokens se aceptan por pasada y cuánto cuesta proponer/verificar.

DFlash4 pasó tools, streaming y thinking. Imágenes fallaron conHTTP500: posicionesKV no consecutivas (X3,Y16). No se demuestra que todas las versionesDFlash fallen con imágenes; se documenta esta combinación local. El perfil publicadoDFlash4 se anuncia como texto solo. MTP2 yMTP3 pasaron el test de cuadrado rojo a la izquierda y círculo azul a la derecha.

## Strata y Bonsai

Strata se probó concontexto128k y expert cache0. Hubo erroresCUDA de acceso ilegal, también sinMTP. El workaround CUDA_LAUNCH_BLOCKING=1 junto a no-graph permitió pruebas cortas40,3–42,6t/s, sin demostrar estabilidad larga. Liberar páginas de pesos mapeadas tras copia a memoria fijada coincidió con un arranque193s→51–56s; no se aisló el efecto de caché. Se corrigió la exposición de toolcalls incompletas para que un finish length no entregaraJSON truncado. Capturas de uso real mostraron~28–32t/s; son evidencia observacional.

Bonsai2 27B PTQ1_0 (~5,95GB) funcionó con el forkPrismML llama.cpp b10777-e3de71522. Generación observada7,44–13,35t/s según colocaciónKV y tamaño de entrada/salida. KV enRAM alcanzó prefill487–511t/s en esas pruebas, pero no se debe extrapolar aQwen ni afirmar mejor calidad. Pasó herramienta sumar; no se evaluó visión o una tarea completa. GLM Q3 solo quedó propuesto, sin resultado local validado.

## Integración y fallos de agente

El límite8192 cortaba escrituras de herramientas; se aumentó a32768 y se aplicó pluginOpenCode para mantener ese presupuesto. Entrada+salida nunca pueden exceder131072; el error98595+32768>131072 era correcto. No se garantiza que declarar32k de salida reserve siempre32k en todos los proveedores. El aviso MAXIMUM STEPS fue el límite80 del agentbuild, separado del contexto y deCUDA.

Se observaron bucles de razonamiento: un caso20835 caracteres con79 menciones rollback fue cancelado. No permite culparMTP sin A/B del mismo prompt. Se ajustó presence_penalty0→0.5, manteniendo temp0.6/topp0.95/topk20/minp0/repeat_penalty1. Pasó prueba corta de generación con valor efectivo0.5; no es demostración de eliminación de bucles a largo plazo. No se redujo la salida o el contexto como solución oculta.

PerfilesMTP3/8083,MTP2/8084,DFlash4/8085 separados. Elegir perfil enOpenCode no inicia backend: ECONNREFUSED8084 se resolvió arrancandoMTP2. Se instaló servicio de usuario al login para persistencia y se dejóMTP2 predeterminado. No existe cambio automático de motor al seleccionar otro perfil.

## Discusión y límites

Resultados exploratorios de una máquina compartida con escritorio y aplicaciones. No hay réplicas aleatorizadas suficientes, evaluación integral de calidad, prueba llena128k sintética, control térmico estricto ni demostración de equivalencia exacta de distribución. Los outputs repetidos coincidieron dentro de ciertos modos pero no fueron byte-idénticos entrebaseline yMTP. Los tests de herramientas/visión son smoke tests, no suites exhaustivas.

Los datos más sólidos son las mediciones puntuales, errores reproducidos y parámetros efectivos. Las relaciones causales sobre hilos, swap o reinicio son hipótesis cuando hubo más de una condición cambiante. El trabajo pendiente se recoge en el segundo paper. No se presentan propuestas de batch, afinidad, mlock ni vídeo como experimentos realizados.
