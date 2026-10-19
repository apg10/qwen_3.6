import os
import urllib.request,json,time,sys
from pathlib import Path
mode=sys.argv[1];results=[]
def call(label,body):
 b={'model':os.environ.get('MODEL_ALIAS','qwen36-mtp2'),'temperature':0,'seed':42,'stream':False,'max_tokens':512,'chat_template_kwargs':{'enable_thinking':False},**body}
 r=urllib.request.Request(os.environ.get('BASE_URL','http://127.0.0.1:8084/v1')+'/chat/completions',data=json.dumps(b).encode(),headers={'Content-Type':'application/json'});start=time.monotonic()
 with urllib.request.urlopen(r,timeout=1800) as f:d=json.load(f)
 x={'case':label,'seconds':round(time.monotonic()-start,2),'timings':d.get('timings'),'usage':d.get('usage'),'choices':d.get('choices')};results.append(x)
 Path(f'results/local-{mode}.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({k:v for k,v in x.items() if k!='choices'}),flush=True);return d['choices'][0]['message']
text='\n'.join(f'Requisito {i}: validar entradas y preservar el orden en la operación {i}.' for i in range(640))
for label,prompt in [('code',text+'\nEscribe una implementación Python de un almacén clave-valor con caducidad, bloqueo y pruebas. Solo código.'),('code-repeat',text+'\nEscribe una implementación Python de un almacén clave-valor con caducidad, bloqueo y pruebas. Solo código.')]:call(label,{'messages':[{'role':'user','content':prompt}]})
tools=[{'type':'function','function':{'name':'sumar','parameters':{'type':'object','properties':{'a':{'type':'integer'},'b':{'type':'integer'}},'required':['a','b']}}}]
msgs=[{'role':'user','content':'Usa sumar para calcular 17+25. Después comunica el resultado.'}]
m=call('tool',{'messages':msgs,'tools':tools});tc=m.get('tool_calls',[]);assert len(tc)==1,tc;assert json.loads(tc[0]['function']['arguments'])=={'a':17,'b':25}
msgs+=[m,{'role':'tool','tool_call_id':tc[0]['id'],'content':'42'}];m=call('tool-result',{'messages':msgs,'tools':tools});assert '42' in m.get('content',''),m
print('Tools passed',flush=True)
