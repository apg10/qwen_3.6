# Reproducción

## Requisitos y alcance

Linux, Python3, git y un llama-server con CUDA, qwen35moe, MTP y DFlash compatibles. Para la prueba de imágenes se necesita Pillow. El ejemplo se basa en la instalación Ollama0.4.1-dev/commit161755f29 observada; rutas y formatos pueden cambiar entre builds. El binario debe soportar `--spec-type`, `--threads-batch`, caché q4_0 y tensor overrides. No se incluye instalador de motores ni descarga automática de pesos.

El launcher portable deriva de los scripts ejecutados, pero no se ha lanzado como una nueva inferencia durante la preparación de este repo, para no interrumpir el servidor del usuario. La validación aquí es sintáctica; los resultados publicados provienen de los launchers históricos descritos en el paper. La variante legacy de los scripts de conversión requiere adaptación manual. Esto no es una reproducción independiente desde cero.

## Arranque manual

Desde la raíz del repo:

```bash
export MODEL_PATH=/ruta/qwen36-Q4_K_M-mtp.gguf
export MMPROJ_PATH=/ruta/proyector-o-blob-original-con-vision
export DRAFT_PATH=/ruta/qwen36-DFlash-Q8_0.gguf
bash scripts/serve.sh mtp2
```

Un solo modelo activo. Las alternativas son `mtp3`, `dflash4` y `baseline`. DFlash4 no habilita visión: falló el test de imágenes. El launcher no descarga modelos ni detiene otros procesos. El GGUF principal de23GB no cabe entero en8GB de VRAM; la colocación de expertos CPU es intencionada.

## OpenCode

Fusionar `config/opencode.example.json` con la configuración propia; no sustituir ciegamente el archivo existente. Copiar el plugin `config/qwen-mtp-params.ts` a `~/.config/opencode/plugins/`. Reiniciar OpenCode para cargar proveedores/plugins. Seleccionar:

| Perfil | ID OpenCode | Puerto |
|---|---|---:|
| MTP2 | llamacpp-mtp2/qwen3.6-mtp2 |8084|
| MTP3 | llamacpp-mtp/qwen3.6-mtp3 |8083|
| DFlash4 | llamacpp-dflash4/qwen3.6-dflash4 |8085|

Seleccionar el perfil no inicia su backend. El ejemplo conserva32768 de salida mediante plugin y131072 de contexto. Entrada + salida deben caber dentro del contexto; no implica131072 de entrada más32768 de salida. `steps:80` es un límite separado; alcanzarlo no es agotar el contexto. En el historial se propuso160, pero no se aplicó.

## Servicio persistente

Adaptar rutas en `config/qwen-mtp2.service.example`, guardarlo como `~/.config/systemd/user/qwen-mtp2.service`. Crear `~/.config/qwen-local-inference-lab/model.env` desde el ejemplo. No poner credenciales en ese archivo.

```bash
systemctl --user daemon-reload
systemctl --user enable --now qwen-mtp2
systemctl --user status qwen-mtp2
journalctl --user -u qwen-mtp2 -f
```

Arranca al iniciar sesión; no se configuró linger ni arranque antes del login. Para otro perfil, detener el servicio primero. Reiniciar el servicio borra la caché KV aunque el chat OpenCode siga intacto.

## Benchmark sintético

```bash
BASE_URL=http://127.0.0.1:8084/v1 MODEL_ALIAS=qwen36-mtp2 python3 scripts/benchmark.py mtp2
BASE_URL=http://127.0.0.1:8084/v1 MODEL_ALIAS=qwen36-mtp2 python3 scripts/probar-stream.py
BASE_URL=http://127.0.0.1:8084/v1 MODEL_ALIAS=qwen36-mtp2 python3 scripts/probar-vision.py
```

El benchmark genera640 requisitos sintéticos:14536 tokens en el tokenizer medido. Temperatura0, seed42, thinking desactivado, salida512 tokens en las dos respuestas de código. Primera petición y repetición exacta; tool roundtrip sumar(17,25) y42. Los scripts guardan respuestas locales ignoradas por git; revisar antes de compartirlas. No evalúan la calidad de una tarea completa. Variantes históricas usaron presence_penalty0; el launcher final usa0.5: para reproducir exactamente los números antiguos hay que restaurar explícitamente0 en una copia experimental.

Para un A/B de hilos válido: mismo prompt, microbatch, temperatura, perfil energético y estado de caché de archivos. Reiniciar entre pruebas de caché KV vacía; repetir y alternar16/24/32. Caché KV fría NO equivale necesariamente a caché de archivos fría. Registrar tiempo de carga separado del prefill. No ejecutar varias inferencias paralelas en estaGPU.

## Monitoreo

```bash
journalctl --user -u qwen-mtp2 -f | grep --line-buffered -E 'prompt eval time|eval time|n_gen =|draft acceptance'
vmstat 1
nvidia-smi
```

En vmstat descartar la primera fila, que resume desde arranque. `si/so` son intercambio activo, no tamaño ocupado de swap. Comparar ms de prefill y tokens nuevos además de t/s; entradas de18 tokens tienen gran coste fijo. `tg` es generación media; `tg_3s` ventana reciente; nunca sumar tokens del prompt como si fueran generados.
