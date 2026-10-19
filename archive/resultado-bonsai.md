> Documento histórico. Las afirmaciones sobre el servidor activo, predeterminado y pruebas pendientes describen ese momento; consultar papers/01-estudio.md y config para el estado final.

# Bonsai 2 27B en la RTX5070 Laptop8GB

Modelo: prism-ml/Ternary-Bonsai-2-27B-gguf, PTQ1_0,5946648928bytes. SHA256 verificado:53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3. Una parte defectuosa de la descarga fue reparada antes de cargarlo.
Motor: PrismML llama.cpp b10777-e3de71522, CUDA12.8, en work/bonsai-demo/bin/cuda. Bibliotecas CUDA12 existentes de Ollama, sin sustituirlas. Modelo y calibración en work/bonsai-models.

Pruebas sin razonamiento, temperatura0,semilla42. Contexto reservado131072, una sesión,12hilos. Entrada/código sintético, no una evaluación de calidad de código.

| Configuración | Entrada total | Generación |
|---|---:|---:|
| Ajuste automático de capas, KV GPU q4_0 calibrada |3496|8.73t/s (512tokens)|
| Ajuste automático de capas, KV GPU q4_0 calibrada |14536|7.44t/s (512tokens)|
| Pesos GPU y KV en RAM q4_0 calibrada |3496|13.35t/s (256tokens)|
| Pesos GPU y KV en RAM q4_0 calibrada |14536|9.63t/s (256tokens)|

La variante KV en RAM tuvo lectura nueva de contexto de487–511t/s. VRAM del proceso observada5862MiB. Se conservan128k reservados, pero no se llenaron128k en la prueba. Los presupuestos de salida distintos y cargas del sistema limitan la comparación fina.

Herramientas: sumar(17,25) produjo JSON correcto; después de una respuesta simulada42, comunicó42 correctamente. No se ejecutaron operaciones en proyectos del usuario.

Conclusión: en estas pruebas fue más lento que las mediciones anteriores de Qwen3.6 MoE del usuario (~29–34t/s con contextos largos). Menor tamaño en disco no implica más velocidad. No se evaluó todavía una tarea completa de programación ni visión.

Se dejó activo el servidor con pesosGPU y KV enRAM. Puerto127.0.0.1:8082. OpenCode: bonsai/bonsai2-27b-ptq1. Se añadió proveedor con entrada de texto; no hay proyector de visión instalado. Se preservó ollama/qwen3.6-agente como modelo predeterminado y se guardó respaldo de configuración. La salida declarada de Bonsai es32000, compatible con el límite predeterminado de OpenCode.

Arranque:
`bash ${LAB_ROOT}/outputs/iniciar-bonsai.sh`

El script rechaza arrancar si Ollama tiene modelos cargados. No cargar simultáneamente Qwen y Bonsai para la comparación.
