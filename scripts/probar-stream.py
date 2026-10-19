import os
import urllib.request,json,time,sys
from pathlib import Path
results=[];tools=[{'type':'function','function':{'name':'sumar','parameters':{'type':'object','properties':{'a':{'type':'integer'},'b':{'type':'integer'}},'required':['a','b']}}}]
msgs=[{'role':'user','content':'Usa sumar para calcular 17+25. Después comunica el resultado. Sé breve.'}]
for step in range(2):
 body={'model':os.environ.get('MODEL_ALIAS','qwen36-mtp2'),'messages':msgs,'tools':tools,'stream':True,'temperature':0,'max_tokens':1024,'chat_template_kwargs':{'enable_thinking':True}}
 r=urllib.request.Request(os.environ.get('BASE_URL','http://127.0.0.1:8084/v1')+'/chat/completions',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
 calls={};content='';thought='';finish=None;start=time.monotonic()
 with urllib.request.urlopen(r,timeout=120) as f:
  for raw in f:
   if not raw.startswith(b'data: ') or raw[6:].strip()==b'[DONE]':continue
   d=json.loads(raw[6:])
   for c in d.get('choices',[]):
    finish=c.get('finish_reason') or finish;a=c.get('delta',{});content+=a.get('content') or '';thought+=a.get('reasoning_content') or a.get('reasoning') or ''
    for tc in a.get('tool_calls',[]):
     x=calls.setdefault(tc['index'],{'id':tc.get('id'),'type':'function','function':{'name':'','arguments':''}})
     if tc.get('id'):x['id']=tc['id']
     for key in ('name','arguments'):x['function'][key]+=tc.get('function',{}).get(key,'') or ''
 m={'role':'assistant','content':content,'reasoning_content':thought}
 if calls:m['tool_calls']=list(calls.values())
 if step==0:
  assert finish=='tool_calls' and len(calls)==1,(finish,m)
  tc=next(iter(calls.values()));assert json.loads(tc['function']['arguments'])=={'a':17,'b':25},m
  msgs+=[m,{'role':'tool','tool_call_id':tc['id'],'content':'42'}]
 else:assert finish=='stop' and '42' in content,(finish,m)
 result={'step':step+1,'finish':finish,'reasoning_chars':len(thought),'content':content,'calls':list(calls.values()),'seconds':round(time.monotonic()-start,2)}
 results.append(result);print(json.dumps(result,ensure_ascii=False),flush=True)
assert results[0]['reasoning_chars']>0,'Thinking not emitted'
Path('results/local-stream-thinking.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n')
