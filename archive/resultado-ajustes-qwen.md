> Documento histórico. Las afirmaciones sobre el servidor activo, predeterminado y pruebas pendientes describen ese momento; consultar papers/01-estudio.md y config para el estado final.

# Pruebas y ajustes de Qwen en Strata

Se mantiene `strata/qwen3.6-agente-strata`, contexto 131072 y salida máxima 8192 tokens.

El fallo original de OpenCode fue una llamada `write` cortada al alcanzar 8192 tokens de salida: JSON incompleto, no agotamiento del contexto de 128k.

Cambios aplicados:
- El servidor OpenAI entrega los argumentos de herramientas solamente cuando la llamada está completa. Una generación cortada termina con `length` sin anunciar una herramienta incompleta.
- El prompt build de OpenCode exige contenido por bloques de hasta 6000 caracteres y ediciones parciales. Se guardó una copia del archivo anterior en ~/.config/opencode/.
- MTP desactivado (`--mtp-draft 0`). Con MTP apareció un acceso ilegal CUDA en la primera prueba. Sin MTP pasaron las pruebas; esto aísla una configuración estable para estas pruebas, sin demostrar la causa exacta del fallo CUDA.
- En Linux se liberan las páginas del archivo mapeado después de copiar los expertos a RAM fijada. La carga observada pasó de unos 193 s a 51–56 s; las condiciones de caché pueden influir.

Validación real del modelo, sin ejecutar herramientas en proyectos:
1. Write de 8 líneas: JSON válido, finish tool_calls, 185 tokens.
2. Write largo limitado a 96 tokens: finish length, ninguna llamada incompleta expuesta.
3. Texto de 80 líneas con instrucción de primer bloque: write válido de 8 líneas.
4. Dos llamadas sucesivas con respuesta de herramienta entre ambas: rutas y contenido exactos, JSON válido.

Además pasaron dos pruebas automáticas del parser (llamada completa con Unicode y llamada truncada).

Generación observada: 45.5 y 47.3 tokens/s en las dos primeras pruebas cortas. No es una medición de rendimiento con 128k ocupados. La reserva de contexto sí sigue en 128k; no se ha llenado para esta validación. Caché de expertos GPU: 0 slots. Strata queda activo en 127.0.0.1:8081.

Para que OpenCode lea el nuevo prompt, reinícialo cuando termine su tarea actual. Reinicio de Strata: bash outputs/iniciar-strata.sh desde este directorio, o utiliza la ruta absoluta del script.
