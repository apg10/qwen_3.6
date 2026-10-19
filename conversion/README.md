# Conversión histórica, no instalador automático

Estos scripts conservan la transformación específica del GGUF legado usado en el estudio. NO ejecutar sin adaptar rutas, revisar el encabezado y trabajar sobre una copia. Usan rutas relativas al árbol original y el manifiesto histórico. `corregir-normas.py` depende del parser de `inspeccionar-gguf-mtp.py` y de los offsets del manifiesto. No son convertidores universales ni se han validado aquí sobre otro GGUF. El código en estos archivos es evidencia histórica y debe leerse antes de ejecutarse.

La fuente fue el blob Ollama sha256-f5ee307a2982106a6eb82b62b2c00b575c9072145a759ae4660378acda8dcf2d. No se incluye ningún peso. Bloques40→41; metadata nextn; renombres MTP y ssm_dt.bias; +1 en dos vectores F32 del draft. El resto de pesos cuantizados principales se conserva. Usar preferentemente un GGUF que ya tenga MTP compatible; no aplicar de nuevo la corrección +1.
