import struct,json,hashlib,os
from pathlib import Path
src=Path('/usr/share/ollama/.ollama/models/blobs/sha256-f5ee307a2982106a6eb82b62b2c00b575c9072145a759ae4660378acda8dcf2d');out=Path('work/qwen-mtp-test/qwen36-Q4_K_M-mtp.gguf');out.parent.mkdir(exist_ok=True)
f=src.open('rb')
def n(fmt):return struct.unpack('<'+fmt,f.read(struct.calcsize(fmt)))[0]
def st():return f.read(n('Q')).decode()
def v(t):
 if t==8:return st()
 if t==9:
  et,c=n('I'),n('Q');return (et,[v(et) for _ in range(c)])
 return n({0:'B',1:'b',2:'H',3:'h',4:'I',5:'i',6:'f',7:'?',10:'Q',11:'q',12:'d'}[t])
def encstr(s):b=s.encode();return struct.pack('<Q',len(b))+b
def encval(t,x):
 if t==8:return encstr(x)
 if t==9:return struct.pack('<IQ',x[0],len(x[1]))+b''.join(encval(x[0],a) for a in x[1])
 return struct.pack('<'+{0:'B',1:'b',2:'H',3:'h',4:'I',5:'i',6:'f',7:'?',10:'Q',11:'q',12:'d'}[t],x)
assert f.read(4)==b'GGUF';version=n('I');nt,nk=n('Q'),n('Q');metadata=[];changed=[];alignment=32
for _ in range(nk):
 start=f.tell();key=st();typ=n('I');value=v(typ);end=f.tell();f.seek(start);raw=f.read(end-start)
 if key=='general.alignment':alignment=value
 if key=='qwen35moe.block_count':value=41
 elif key.startswith('qwen35moe.') and typ==9 and len(value[1])==40:
  et,arr=value;value=(et,arr+[False if 'recurrent' in key else (2 if 'head_count_kv' in key else arr[-1])])
 else:metadata.append(raw);continue
 metadata.append(encstr(key)+struct.pack('<I',typ)+encval(typ,value));changed.append(key)
key='qwen35moe.nextn_predict_layers';metadata.append(encstr(key)+struct.pack('<II',4,1));changed.append(key)
tensors=[];renames=[]
for _ in range(nt):
 name=st();nd=n('I');dims=[n('Q') for _ in range(nd)];typ=n('I');offset=n('Q');old=name
 if name.startswith('mtp.layers.0.'):name='blk.40.'+name[len('mtp.layers.0.'):]
 elif name in {'mtp.fc.weight','mtp.norm.weight','mtp.pre_fc_norm_embedding.weight','mtp.pre_fc_norm_hidden.weight'}:
  name={'mtp.fc.weight':'blk.40.nextn.eh_proj.weight','mtp.norm.weight':'blk.40.nextn.shared_head_norm.weight','mtp.pre_fc_norm_embedding.weight':'blk.40.nextn.enorm.weight','mtp.pre_fc_norm_hidden.weight':'blk.40.nextn.hnorm.weight'}[name]
 if name.endswith('.ssm_dt'):name+='.bias'
 if old!=name:renames.append([old,name])
 tensors.append(encstr(name)+struct.pack('<I',nd)+struct.pack('<'+'Q'*nd,*dims)+struct.pack('<IQ',typ,offset))
old_data=(f.tell()+alignment-1)//alignment*alignment
header=b'GGUF'+struct.pack('<IQQ',version,nt,len(metadata))+b''.join(metadata)+b''.join(tensors);new_data=(len(header)+alignment-1)//alignment*alignment
h=hashlib.sha256()
with out.open('wb') as dest:
 dest.write(header);dest.write(b'\0'*(new_data-len(header)));f.seek(old_data)
 while b:=f.read(16*1024*1024):h.update(b);dest.write(b)
with out.open('rb') as check:
 check.seek(new_data);verify=hashlib.file_digest(check,'sha256').hexdigest()
assert verify==h.hexdigest()
manifest={'source':str(src),'copy':str(out.resolve()),'metadata_changed':changed,'renames':renames,'source_data_offset':old_data,'copy_data_offset':new_data,'weight_data_sha256':verify,'weights_unchanged':True}
Path('outputs/qwen-mtp-compatibilidad.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'copy':str(out),'metadata':changed,'renamed_tensors':len(renames),'weights_unchanged':True}),flush=True)
