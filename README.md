# qwen_3.6 — Qwen Local Inference Lab

Qwen 3.6 lab.

Configuración, experimentos y resultados de **Qwen3.6-35B-A3B Q4_K_M en OpenCode**, ejecutado en un laptop con RTX 5070 de 8 GB y 32 GB de RAM.

Este repositorio documenta lo que probamos con Ollama/llama.cpp, Strata, MTP y DFlash, junto con una comparación de Bonsai 2 27B ternario. Incluye intentos fallidos, resultados variables y pruebas pendientes. Es un estudio exploratorio de una sola máquina, no un artículo revisado por pares ni un benchmark universal.

## Configuración operativa seleccionada

| Parámetro | Valor |
|---|---|
| Modelo principal | Qwen3.6-35B-A3B, Q4_K_M |
| Decodificación | MTP, máximo de 2 tokens draft |
| Hilos de generación / prefill | 16 / 16 |
| Contexto total | 131.072 tokens |
| Salida máxima declarada | 32.768 tokens, dentro del contexto total |
| Caché K / V | q4_0 / q4_0 |
| Batch / microbatch | 512 / 512 |
| Flash Attention | Activado |
| Temperatura / top_p / top_k | 0,6 / 0,95 / 20 |
| Presence penalty | 0,5 |
| API MTP2 | http://127.0.0.1:8084/v1 |
| Persistencia | Servicio systemd de usuario, al iniciar sesión |

La selección se basa en el funcionamiento observado. No demuestra que esta configuración sea óptima para todos los equipos o tareas.

## Resultados destacados

Un retest sintético con 14.536 tokens de entrada y 512 de salida produjo:

| Configuración | Prefill t/s | Generación inicial t/s | Generación con caché t/s |
|---|---:|---:|---:|
| Baseline, retest | 369,0 | 34,6 | 35,0 |
| MTP3, retest | 356,8 | 36,0 | 37,3 |
| MTP2, retest posterior | 368,9 | 48,3 | 45,2 |
| DFlash4, sesión anterior | 120,8 | 33,0 | 51,9 |

**Estas filas no son promedios de una campaña aleatorizada.** Hubo variaciones entre sesiones y estados de memoria. DFlash necesitó microbatch 128 para caber en VRAM, mientras baseline/MTP usaron 512. Su mejora con caché vino acompañada de prefill más lento y un fallo de visión en la combinación probada.

En tareas reales, restaurar 16/16 coincidió con recuperar generación de ~15–19 a ~32 tokens/s; también se reinició el servidor y cambió la memoria residente. No atribuimos esa recuperación exclusivamente a los hilos.

## Documentación

- [Estudio principal: método, resultados y limitaciones](papers/01-estudio.md)
- [Prefill desde cero, memoria y pruebas pendientes](papers/02-prefill-memoria.md)
- [Reproducción, perfiles y servicio persistente](REPRODUCIBILITY.md)
- [Bitácora de intentos, incluidos los fallidos](EXPERIMENTS.md)
- [Resultados numéricos](results/)
- [Informes históricos](archive/): sus afirmaciones sobre el servidor activo pueden estar obsoletas.
- [Referencias primarias](REFERENCES.md)
- [Conversión histórica del GGUF legado](conversion/README.md)

## Uso

Revisar primero [REPRODUCIBILITY.md](REPRODUCIBILITY.md). Los pesos y motores se obtienen por separado. Con un GGUF compatible y las rutas adaptadas:

```bash
export MODEL_PATH=/ruta/qwen36-Q4_K_M-mtp.gguf
export MMPROJ_PATH=/ruta/proyector-compatible
bash scripts/serve.sh mtp2
```

Los perfiles disponibles son `baseline`, `mtp2`, `mtp3` y `dflash4`. Ejecutar un solo servidor a la vez. Seleccionar un perfil en OpenCode no inicia su backend. El launcher portable tiene validación sintáctica; las mediciones históricas proceden de los launchers usados durante el estudio, no de una reproducción independiente de este repositorio.

Los scripts de conversión son evidencia histórica específica del export legado; requieren revisión y adaptación manual. No aplicar automáticamente la corrección de normas a modelos que ya sean compatibles.

## Alcance y privacidad

No se incluyen pesos, API keys, conversaciones, bases de datos OpenCode, código de proyectos privados ni binarios de terceros. Se excluyeron las respuestas de los JSON exportados; [el manifiesto de procedencia](results/provenance.json) documenta la transformación. Los archivos de resultados locales de nuevas pruebas se ignoran por git.

Quedan pendientes comparaciones controladas de hilos y batch, réplicas suficientes y evaluación integral de calidad. No se publican propuestas como si fueran experimentos completados.

Corte documental: **20 de octubre de 2026, Australia/Sydney**. Preparado localmente; no requiere autenticarse en GitHub para consultarlo.
