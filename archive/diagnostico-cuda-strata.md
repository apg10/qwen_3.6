> Documento histórico. Las afirmaciones sobre el servidor activo, predeterminado y pruebas pendientes describen ese momento; consultar papers/01-estudio.md y config para el estado final.

# Diagnóstico CUDA

El arranque terminaba correctamente; el fallo aparecía al empezar a decodificar, incluso con una petición de 17 tokens. CUDA informó acceso ilegal de memoria en engine.cpp:551 y el proceso quedó bloqueado durante la salida.

El fallo se reprodujo con MTP desactivado y también con --no-graph. Al activar CUDA_LAUNCH_BLOCKING=1 junto con --no-graph, una respuesta corta y las tres pruebas de herramientas terminaron correctamente. Esto apunta a un problema de sincronización, pero no identifica todavía la operación causante ni demuestra estabilidad con contextos largos.

La configuración local conserva ambos ajustes de diagnóstico. Velocidad observada en las pruebas: 40.3–42.6 tokens/s. Contexto 131072, salida solicitada hasta 32768 y fit_max_tokens siguen activos.

Se cambió la salida fatal del motor a std::_Exit(1), tras imprimir y vaciar el registro, para evitar que destructores del runtime o de trabajadores bloqueados impidan terminar. Compilación completada.
