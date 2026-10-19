> Documento histórico. Las afirmaciones sobre el servidor activo, predeterminado y pruebas pendientes describen ese momento; consultar papers/01-estudio.md y config para el estado final.

# Qwen3.6 Q4_K_M — 3-token MTP test

The regular Ollama model and OpenCode settings were not modified. A separate GGUF copy was made at work/qwen-mtp-test/qwen36-Q4_K_M-mtp.gguf. Its tensor-data SHA256 was checked before conversion; all main quantized weights remain unchanged.

Compatibility conversion: add nextn metadata, extend block_count40→41 and KV-head array40→41; rename MTP tensors into blk.40.nextn layout and ssm_dt into ssm_dt.bias. Two F32 draft-only pre-FC RMSNorm vectors require +1, following upstream conversion/qwen.py. Initial raw-name conversion without this step accepted almost no drafts; those results are not representative of properly converted MTP. Details are in qwen-mtp-compatibilidad.json.

Runtime: installed Ollama llama-server, commit161755f29, explicitly loaded CUDA plugin /usr/local/lib/ollama/cuda_v13/libggml-cuda.so. Initial CPU-only trials are separately labelled and excluded from GPU conclusions.

Final matched settings:128k reserved context, one slot,16CPU threads, Q4_K_M weights, q4_0 K/V cache, Flash Attention, batch/ubatch512. First36 main expert layers and MTP expert tensors inRAM; final4 main expert layers onGPU. Temperature0,seed42,thinking disabled for these measurements. No FP8 or SGLang involved. Three is the maximum number of sequential proposed draft tokens; actual accepted tokens vary per step.

The6-main-expert-layer GPU placement ran out of memory with MTP;4layers fit. This is test-specific placement, not an exact clone of Ollama's automatic memory planner.

| Test | MTP off | 3draft tokens | Accepted drafts |
|---|---:|---:|---:|
|3496-token code input, first response256output|43.45t/s|27.52t/s|180/224|
|3496-token code input, repeated256output|43.19t/s|53.95t/s|180/224|
|Short explanation256output|42.02t/s|46.02t/s|167/261|
|14536-token code input512output|40.98t/s|51.40t/s|359/456|
|14536-token code input, repeated512output|41.31t/s|51.30t/s|359/456|

The14.5k code trials show about24–25% generation speed improvement. First-use overhead and workload affect the result. Generation speed is distinct from total response latency, which includes prompt processing; prompt cache counts differed for the first long tests, so compare their generation timing rather than total wall time.

Tool round-trip: sumar(17,25) emitted valid arguments and returned42 after the simulated tool result, in both modes and in repeated runs. Repeated code output was identical within each mode; MTP and baseline outputs were not byte-identical across modes. This is not a full coding-quality or mathematical sampling-equivalence evaluation.

MTP process GPU memory observed5656MiB, plus desktop and other GPU consumers.128k was reserved but the largest tested input was14.5k, not a full128k. Long conversations, vision, thinking-on agent loops and2drafts were not tested.

Experimental launch after unloading the regular model:
```
ollama stop qwen3.6-agente:latest
bash ${LAB_ROOT}/outputs/iniciar-qwen-mtp3.sh
```
It listens on127.0.0.1:8083, model alias qwen36-mtp-test. It is not installed as the default provider in OpenCode. The test launcher disables thinking to match the benchmark; a production setup should separately validate thinking and vision before replacing Ollama.

After the tests, the isolated server was stopped and the regular Ollama model was reloaded.

Sources:
- https://github.com/ggml-org/llama.cpp/blob/master/conversion/qwen.py
- https://github.com/ggml-org/llama.cpp/blob/master/src/models/qwen35moe.cpp
- https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
