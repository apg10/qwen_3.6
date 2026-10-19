import struct,json
p='/usr/share/ollama/.ollama/models/blobs/sha256-f5ee307a2982106a6eb82b62b2c00b575c9072145a759ae4660378acda8dcf2d'
f=open(p,'rb')
def num(fmt):return struct.unpack('<'+fmt,f.read(struct.calcsize(fmt)))[0]
def string():return f.read(num('Q')).decode()
def val(t):
 if t==8:return string()
 if t==9:
  et,n=num('I'),num('Q');return [val(et) for _ in range(n)]
 return num({0:'B',1:'b',2:'H',3:'h',4:'I',5:'i',6:'f',7:'?',10:'Q',11:'q',12:'d'}[t])
assert f.read(4)==b'GGUF';version=num('I');nt,nk=num('Q'),num('Q');meta={}
for _ in range(nk):
 k=string();v=val(num('I'))
 if any(x in k for x in ['architecture','nextn','block_count','context_length']):meta[k]=v
names=[]
for _ in range(nt):
 name=string();nd=num('I');dims=[num('Q') for _ in range(nd)];typ=num('I');offset=num('Q')
 if name.startswith('mtp') or 'nextn' in name:names.append({'name':name,'dims':dims,'type':typ})
print(json.dumps({'meta':meta,'mtp_tensors':names},indent=2))
