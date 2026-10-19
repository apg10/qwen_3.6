# Bitácora de intentos

| Etapa | Acción o intento | Resultado y estado |
|---|---|---|
| Ollama inicial | Qwen local Q4_K_M; contexto131072 | Referencia cotidiana; FP8/SGLang no se utilizaron |
| Salida8192 | Escritura enorme de herramienta truncada | JSON incompleto, finish length; no era contexto lleno |
| Herramientas Strata | No exponer tool call hasta completar argumentos; prueba de truncamiento | Tools cortas y roundtrip pasaron |
| Edición por bloques | Prompt de build con límite6000 caracteres por llamada | Regla aplicada; no garantiza obediencia del modelo |
| Salida32768 | Aumentar salida y plugin OpenCode | Resuelto límite8192; error posterior de entrada98595+salida32768>131072 documentado |
| Strata arranque y RAM | Liberar páginas mapeadas tras copiar expertos a RAM fijada | Arranque observado193s→51–56s; caché no controlada |
| Strata CUDA | MTP off, no-graph, CUDA_LAUNCH_BLOCKING=1 | Fallo también sin MTP; workaround corto40–43t/s, no prueba de estabilidad larga |
| Strata fatal exit | std::_Exit(1) para evitar bloqueo de destructores | Compilación completada; parche histórico no equivale a arreglo del acceso ilegal |
| Strata uso real | Contexto128k, expert cache0 | Capturas~28–32t/s; cortes también aparecieron con llama.cpp, no atribuir todos aStrata |
| Visión Ollama | Modalities texto+imagen en OpenCode | Usuario confirmó imágenes funcionando |
| Vídeo | Consulta documentación/capacidad del modelo | No se validó vídeo extremo a extremo en OpenCode |
| GLM Q3 | Propuesta de descarga | Sin benchmark local completado en la evidencia disponible |
| Bonsai2 27B PTQ1_0 | Descarga~5,95GB; variante KV GPU y RAM | Generación7,44–13,35t/s; menor disco no implicó mayor velocidad |
| MTP preparación | Copia de GGUF, renombres nextn y metadata | Principal cuantizado intacto; conversión específica del export legado |
| MTP aceptación~0 | Primer intento sin +1 en dos prenorms | Corregido en vectores F32 del draft; no usar estos primeros números como rendimiento final |
| CUDA ausente | Primeros arranques standalone sin plugin explícito | CPU-only, excluidos de conclusiones GPU |
| MTP VRAM | Seis capas de expertos GPU | OOM; cuatro capas GPU sí cabían |
| MTP2/MTP3 | Comparaciones sintéticas y retests | Ventaja cambió entre sesiones; no ganador universal |
| OpenCode real | CLI bash smoke | Tool y respuesta final correctas; no evaluación completa de proyecto |
| DFlash3/4/8 | Q8 draft421MB; block entrenado16 | Warm47–52t/s; prefill121–127t/s conub128 |
| DFlash VRAM | ub512 | OOM al reservar~975MiB compute; ub128 arrancó |
| DFlash visión | Imágenes conDFlash4 | HTTP500 por secuencia KV no consecutiva; perfil texto solo |
| DFlash bloque8 | n_max8 probado | Es8 drafts+ancla; bloque total8 sería n_max7, NO se probó |
| Persistencia | systemd usuario MTP2; perfiles puertos separados | Solucionó conexión rechazada tras reiniciar; arranque al login |
| Bucle razonamiento |20835 caracteres,79 menciones rollback | Cancelado; no prueba causal contraMTP |
| Repetición | presence_penalty0→0.5 | Generación corta verificada; efecto anti-bucle a largo plazo no evaluado sistemáticamente |
| Máximo de pasos | Agent build steps80 | Aviso de límite de pasos, distinto de tokens/contexto |
| Hilos16→24 | Cambiar solo threads-batch | Prefill frío largo~300t/s; faltó control idéntico16 |
| Reinicio y lentitud | Generación15–19t/s con24 prefill, swap ocupada8GiB | Observacional, sin swap activo en algunas muestras |
| Volver16/16 | Reinicio y restauración | Generación~32t/s; swap~1,4GiB; causalidad no aislada |
| Batch1024 | Propuesta b1024/ub512 y luegoub1024 | NO ejecutada; no hay resultado para publicar |
| Afinidad, mlock, swapoff | Consideradas/discutidas | No aplicadas; no atribuir mejoras inexistentes |
| MTP SGLang/NEXTN | Ejemplo del usuario conFP8 ytp8 | No ejecutado en el laptop |

Las fechas exactas de cada etapa temprana no están completamente preservadas. Se evita inventar timestamps y se conserva el orden relativo de la conversación. Los resultados tienen prioridad sobre afirmaciones operativas de los archivos históricos.
