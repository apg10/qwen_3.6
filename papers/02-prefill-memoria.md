# Prefill frío, caché y memoria: observaciones y plan de validación

## Pregunta

¿Cómo reducir el tiempo antes de la primera respuesta cuando OpenCode envía un historial grande sin cachéKV? MTP ayuda a generación, no elimina el procesamiento del prompt. A270t/s,100000 tokens requieren unos370s. Son estimaciones, no resultados de todas las entradas posibles.

## Caché y compactación

El chat persistente deOpenCode no es la cachéKV enRAM del servidor. Reiniciar llama-server la vacía aunque continúe el mismo chat. Compactar cambia el prefijo del prompt y puede reducir la coincidencia reutilizable; no siempre obliga a reprocesar absolutamente todo. En continuidad se vieron coincidencias de97–99,9% y entradas nuevas de18–2041 tokens, con prefill0,7–9s. Un t/s bajo con18 tokens no se extrapola linealmente a100k: hay coste fijo.

## RAM y swap

Las capturas dehtop mostraban~11GiB usados y6GiBswap. Linux contabiliza pesosmmap también como caché de archivos; no significa que Qwen solo use11GiB. Una lectura de/proc mostró~26,9GiB RSS (aprox18GiBfile-backed) más~6,1GiBswap. Otra mostró~25,2GiBRSS y5,6GiBswap. Son muestras diferentes; no sumarlas ni tratar filecache como reserva totalmente libre adicional. MemAvailable incluye páginas recuperables cuyo descarte puede obligar a releer pesos.

Swap del sistema llegó a8GiB ocupados. Se observaron lecturas de~8MiB/s en una muestra, pero otras tuvieron si/so casi0. Swap ocupada NO demuestra thrashing actual. Tras reiniciar el servidor se redujo a~1,4–1,9GiB en otras sesiones. No se ejecutó swapoff ni mlock: fijar todo el modelo podría desplazar cachés/otras aplicaciones y empeorar la presión de memoria. Tampoco se cambió swappiness60.

## Experimento de hilos

Hardware16 núcleos físicos/32 hilos lógicos. Configuración inicial-t16 y threads-batch heredado16. Se probó threads-batch24 manteniendo generación16. Estos pools actúan en fases distintas, no son16+16 núcleos reservados; sin afinidad no se garantiza un hilo por núcleo físico.

Una prueba real después del reinicio procesó desde cero un historial de~75k tokens. A51262 tokens y170,56s alcanzó300,55t/s; cero cachéKV reutilizada. Esa fue una muestra parcial, no el tiempo final de todo el prompt. Durante ese tramo hubo poca actividadswap. Las capturas y extractos conservados no proporcionan un A/B del mismo prompt con16.

En otra sesión con24 de prefill se observó generación15–19t/s y prefill274–283t/s. Se restauró16/16 mediante reinicio, y la siguiente tarea mostró generación~32t/s y prefill264–270t/s, con contexto~106k y~90,7k reutilizados. La recuperación de generación fue grande, pero threads de generación siempre fueron16 y el reinicio cambióswap/caché. No se puede concluir que threads-batch24 cause por sí solo la reducción de generación. El perfil final16/16 es conservador y funcionó bien, no una demostración universal de optimalidad.

## Lo no probado

32 hilos prefill NO medidos. Batch actual512 y microbatch512. Se propuso b1024/ub512 y luego b1024/ub1024 si cabeVRAM, pero NO se ejecutó. Tampoco se comparó load-mode none frente ammap, afinidad por núcleo ni reducción de memoria de trabajo de forma controlada. El vídeo se documentó como capacidad del modelo sin ensayoOpenCode. No se configura un monitor que ejecute inferencias mientras trabaja el usuario.

## Protocolo recomendado

1. Capturar un prompt sintético fijo representativo de75k tokens, sin contenido privado, y tokenizarlo con el mismo motor. Usar max_tokens1 para aislarprefill y otra prueba de512 para comprobar generación.
2. Comparar16/24/32 hilos de prefill con generación16. Alternar el orden y repetir al menos3 veces. MantenerMTP2, presencia0.5, contexto128k, colocaciónexpertos ybatch iguales.
3. Vaciar solo cachéKV mediante reinicio entre intentos; registrar por separado el estado de caché de archivos. No usar drop_caches global en un equipo ocupado. Mismo perfil de energía y alimentación, observar temperaturas.
4. Registrar prompt_ms/prompt_n/cache_n, latencia hasta primer token, generación, GPU memoria/W/temperatura, vmstatsi/so y lecturasdisco. La primera filavmstat es promedio de arranque y debe excluirse.
5. Evaluar batch en un experimento separado; si hayOOM restaurar la configuración funcional. No conservar un cambio solo por mayor t/s si perjudica latencia, calidad o estabilidad.

Estos pasos describen trabajo futuro, no resultados ya obtenidos. La exportación de logs reales incluye solo métricas seleccionadas; no prompts, herramientas de proyectos o razonamientos privados.
