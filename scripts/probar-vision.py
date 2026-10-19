import os
from PIL import Image,ImageDraw
from pathlib import Path
import io,base64,json,urllib.request,time
im=Image.new('RGB',(384,192),'white');draw=ImageDraw.Draw(im);draw.rectangle((24,40,136,152),fill='red');draw.ellipse((240,40,352,152),fill='blue');p=Path('results/local-vision-test.png');im.save(p)
b64=base64.b64encode(p.read_bytes()).decode()
b={'model':os.environ.get('MODEL_ALIAS','qwen36-mtp2'),'stream':False,'temperature':0,'max_tokens':256,'chat_template_kwargs':{'enable_thinking':False},'messages':[{'role':'user','content':[{'type':'image_url','image_url':{'url':'data:image/png;base64,'+b64}},{'type':'text','text':'Describe the two colored shapes: give their colors, shapes and whether they are on the left or right. Answer briefly in English.'}]}]}
r=urllib.request.Request(os.environ.get('BASE_URL','http://127.0.0.1:8084/v1')+'/chat/completions',data=json.dumps(b).encode(),headers={'Content-Type':'application/json'});t=time.monotonic()
with urllib.request.urlopen(r,timeout=120) as f:d=json.load(f)
text=d['choices'][0]['message'].get('content','').lower();assert all(x in text for x in ['red','blue','square','circle','left','right']),text
Path('results/local-vision.json').write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n');print(text,round(time.monotonic()-t,2),'s',flush=True)
