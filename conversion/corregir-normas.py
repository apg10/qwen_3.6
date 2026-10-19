from pathlib import Path
import struct,json,hashlib
# Parse original header only; the tensor offsets in the compatibility copy are unchanged.
s=Path('work/inspeccionar-gguf-mtp.py').read_text();exec(s.split('names=[]')[0]);tensors={}
for _ in range(nt):
 name=string();nd=num('I');dims=[num('Q') for _ in range(nd)];typ=num('I');offset=num('Q');tensors[name]=(dims,typ,offset)
manifest_path=Path('outputs/qwen-mtp-compatibilidad.json');m=json.loads(manifest_path.read_text());srcbase=m['source_data_offset'];destbase=m['copy_data_offset'];changes=[]
with Path(m['copy']).open('r+b') as out:
 for name in ['mtp.pre_fc_norm_embedding.weight','mtp.pre_fc_norm_hidden.weight']:
  dims,typ,offset=tensors[name];assert typ==0 and len(dims)==1
  f.seek(srcbase+offset);raw=f.read(4*dims[0]);old=struct.unpack('<'+'f'*dims[0],raw);new=struct.pack('<'+'f'*dims[0],*(x+1.0 for x in old))
  out.seek(destbase+offset);out.write(new);changes.append({'source_tensor':name,'operation':'F32 RMSNorm weight + 1, per upstream Qwen conversion','bytes':len(new),'source_sha256':hashlib.sha256(raw).hexdigest(),'converted_sha256':hashlib.sha256(new).hexdigest(),'data_offset':offset})
m['weights_unchanged']=False;m['main_quantized_weights_unchanged']=True;m['mtp_norm_conversions']=changes;manifest_path.write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(changes,indent=2))
