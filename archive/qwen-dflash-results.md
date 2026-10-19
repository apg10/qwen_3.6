> Documento histórico. Las afirmaciones sobre el servidor activo, predeterminado y pruebas pendientes describen ese momento; consultar papers/01-estudio.md y config para el estado final.

# Qwen3.6 DFlash comparison

128k allocated context, 14,536-token prompt, 512 generated tokens per case. Same main Q4_K_M and expert placement; DFlash Q8_0 requires prompt microbatch128 rather than512 to fit VRAM. Therefore this compares practical configurations, not an isolated algorithm-only effect.

| Mode | First generation t/s | Cached generation t/s | Input t/s | First request seconds |
|---|---:|---:|---:|---:|
| mtp3-dflash-control | 37.99 | 36.31 | 359.01 | 55.41 |
| dflash3 | 37.96 | 51.33 | 121.94 | 132.69 |
| dflash4 | 32.96 | 51.86 | 120.84 | 135.82 |

Keep MTP3 as default for now: DFlash improves the cached response but processing new input is substantially slower with the memory settings needed here. DFlash4 warm gain over DFlash3 is only about1%; DFlash3 has faster first generation. Single first/cached sample per mode; not a full128k input or sustained agent benchmark.

DFlash trained block size16, configured draft cap3 or4. Q8_0 draft file421MB; Q4_K_M variant236MB exists but was not tested. Draft weights fit GPU, full23GB main model cannot fit8GB VRAM. Runtime cache/workspace allocations also consume memory. Initial DFlash ub512 failed allocating975MiB compute buffer; ub128 worked with approximately369MiB free in one sample.

Original OpenCode settings remain unchanged. MTP3 is restored after testing. Optional experimental DFlash command (stop the active model first):

```bash
bash ${LAB_ROOT}/work/qwen-mtp-test/iniciar-dflash.sh 3
```

Thinking + streaming tool call validation passed under DFlash4. Image validation failed HTTP500 with draft KV-cache positions inconsistent (X=3,Y=16); see dflash4-ub128.log. This is another reason to retain MTP3 for OpenCode. DFlash3 image path not separately tested.

DFlash8 draft cap: first generation 24.98t/s, cached 47.35t/s. Tools passed. Slower than3/4 drafts. Code inspection: trained block_size16 is a limit; ordinary DFlash runtime block has n_max+1 tokens including the anchor. For total block8 use n_max7; that exact setting was not benchmarked.
