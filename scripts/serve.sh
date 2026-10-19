#!/usr/bin/env bash
set -euo pipefail
PROFILE=${1:-mtp2}
: "${MODEL_PATH:?Set MODEL_PATH to the compatible Qwen Q4_K_M GGUF}"
SERVER=${LLAMA_SERVER:-/usr/local/lib/ollama/llama-server}
if [[ -f /usr/local/lib/ollama/cuda_v13/libggml-cuda.so ]]; then
 export GGML_BACKEND_PATH=${GGML_BACKEND_PATH:-/usr/local/lib/ollama/cuda_v13/libggml-cuda.so}
 export LD_LIBRARY_PATH="/usr/local/lib/ollama:/usr/local/lib/ollama/cuda_v13:${LD_LIBRARY_PATH:-}"
fi
case "$PROFILE" in
 baseline) mode=none; drafts=0; port=8086; alias=qwen36-baseline; ub=512;;
 mtp2) mode=draft-mtp; drafts=2; port=8084; alias=qwen36-mtp2; ub=512;;
 mtp3) mode=draft-mtp; drafts=3; port=8083; alias=qwen36-mtp-test; ub=512;;
 dflash4) mode=draft-dflash; drafts=4; port=8085; alias=qwen36-dflash4; ub=128;;
 *) echo 'Profiles: baseline, mtp2, mtp3, dflash4' >&2; exit 2;;
esac
args=(-m "$MODEL_PATH" --host 127.0.0.1 --port "${PORT:-$port}" --alias "$alias"
 -c 131072 -np 1 -t 16 --threads-batch "${PREFILL_THREADS:-16}" -ngl 99 --n-cpu-moe 36 --fit off
 -b "${BATCH:-512}" -ub "${UBATCH:-$ub}" -fa on -ctk q4_0 -ctv q4_0 --jinja
 --spec-type "$mode" --spec-draft-n-max "$drafts"
 --override-tensor 'blk\.40\.ffn_(gate|up|down)_exps\.weight=CPU'
 --reasoning on --chat-template-kwargs '{"preserve_thinking":true}'
 --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0 --presence-penalty 0.5 --repeat-penalty 1)
if [[ $mode == draft-dflash ]]; then
 : "${DRAFT_PATH:?Set DRAFT_PATH to DFlash Q8_0 GGUF}"
 args+=(-md "$DRAFT_PATH" --spec-draft-ngl 99 --spec-draft-type-k q4_0 --spec-draft-type-v q4_0)
elif [[ $mode == draft-mtp ]]; then
 args+=(--spec-draft-cpu-moe --spec-draft-ngl 99)
fi
if [[ -n ${MMPROJ_PATH:-} && $mode != draft-dflash ]]; then
 args+=(--mmproj "$MMPROJ_PATH" --no-mmproj-offload)
fi
# Do not silently evict another model. Callers must stop the old server first.
python3 - <<'PY'
import urllib.request,json,sys
for p in [8081,8082,8083,8084,8085,8086]:
 try:urllib.request.urlopen(f'http://127.0.0.1:{p}/health',timeout=0.5).close()
 except OSError:continue
 sys.exit(f'Another server is active on {p}; stop it before starting this profile.')
try:d=json.load(urllib.request.urlopen('http://127.0.0.1:11434/api/ps',timeout=1))
except OSError:d={}
if d.get('models'):sys.exit('Ollama has models loaded; unload them first.')
PY
exec "$SERVER" "${args[@]}"
