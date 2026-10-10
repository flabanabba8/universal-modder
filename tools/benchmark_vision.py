"""Compare identical whole-image inspections; cloud routes must be explicit."""
import argparse
import json
from pathlib import Path
import statistics
import sys
import time
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'skills/disposable-vision/scripts'))
import vision_inspect
import local_vision
from vision_metrics import STATE

QUESTION = 'Read the image title. If fully legible, include its exact text in the evidence. If covered, say UNKNOWN and do not guess.'
CRITERIA = 'PASS only for a fully legible title; FAIL or UNCERTAIN with UNKNOWN if the title cannot be read. At most 60 words.'
TITLE = 'VISION CHECK 314'


def fixtures(root):
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 64)
    image = Image.new('RGB', (800, 260), 'white'); draw = ImageDraw.Draw(image)
    box = draw.textbbox((0, 0), TITLE, font=font)
    x=(800-(box[2]-box[0]))//2-box[0]; y=(260-(box[3]-box[1]))//2-box[1]
    draw.text((x,y), TITLE, font=font, fill='black')
    readable=root/'case-a.png'; image.save(readable)
    hidden=image.copy();ImageDraw.Draw(hidden).rectangle((0,60,799,200),fill='black')
    obscured=root/'case-b.png';hidden.save(obscured)
    return [('readable',readable),('obscured',obscured)]


def last_metric(offset):
    path=STATE/'metrics.jsonl'
    if not path.exists():return {}
    with path.open() as stream:
        stream.seek(offset);rows=[json.loads(line) for line in stream if line.strip()]
    return rows[-1] if rows else {}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--model',action='append',required=True,help='LABEL=explicit-router-model')
    parser.add_argument('--repeats',type=int,default=3)
    parser.add_argument('--allow-cloud',action='store_true')
    parser.add_argument('--endpoint',help='Cloud router loopback endpoint')
    parser.add_argument('--local-endpoint',default='http://127.0.0.1:8081')
    args=parser.parse_args()
    if not 1<=args.repeats<=5:parser.error('--repeats must be 1..5')
    models=[entry.split('=',1) for entry in args.model]
    if any(len(entry)!=2 for entry in models):parser.error('Models must be LABEL=MODEL')
    if any(not model.startswith('ornith/') for _,model in models) and not args.allow_cloud:parser.error('Cloud benchmark requires --allow-cloud')
    if (args.output/'results.json').exists():parser.error('Choose a new output folder')
    args.output.mkdir(parents=True,exist_ok=True)
    images=fixtures(args.output);rows=[];blocked=set()
    for repeat in range(args.repeats):
        # Rotate order so one provider does not always receive the first call.
        ordered=models[repeat%len(models):]+models[:repeat%len(models)]
        for label,model in ordered:
            if label in blocked:continue
            for case,path in images:
                metric_file=STATE/'metrics.jsonl';offset=metric_file.stat().st_size if metric_file.exists() else 0
                endpoint=args.endpoint
                served_model=model
                if label=='local':
                    endpoint=args.local_endpoint
                    served_model=local_vision.request_json(endpoint,'/v1/models')['data'][0]['id']
                started=time.monotonic();row={'label':label,'model':model,'case':case,'repeat':repeat,'client_cache':False}
                try:
                    text=vision_inspect.inspect_images([path],QUESTION,criteria=CRITERIA,backend='local',model=served_model,endpoint=endpoint,refresh=True,timeout=60,max_tokens=512)
                    expected=(TITLE in text and text.startswith('VERDICT: PASS')) if case=='readable' else ('UNKNOWN' in text.upper() and not text.startswith('VERDICT: PASS'))
                    row.update(status='ok',criteria_met=expected,answer=text)
                except Exception as error:
                    row.update(status='failed',criteria_met=False,error=type(error).__name__,reason=str(error)[:180])
                    blocked.add(label)
                row['elapsed_seconds']=round(time.monotonic()-started,3)
                metric=last_metric(offset)
                row['usage']={k:metric[k] for k in ['prompt_tokens','completion_tokens','total_tokens','cached_input_tokens','input_tokens','output_tokens','reasoning_output_tokens','agent_sessions','inference_attempts'] if k in metric}
                rows.append(row)
                (args.output/'results.json').write_text(json.dumps(rows,indent=2))
                print(json.dumps({k:v for k,v in row.items() if k not in ['answer','model']}),flush=True)
                if label in blocked:break
    # Client-cache timing is measured separately, never counted as model latency.
    cache_rows=[]
    for label,model in models:
        if label in blocked:continue
        endpoint=args.local_endpoint if label=='local' else args.endpoint
        served_model=local_vision.request_json(endpoint,'/v1/models')['data'][0]['id'] if label=='local' else model
        started=time.monotonic();vision_inspect.inspect_images([images[0][1]],QUESTION,criteria=CRITERIA,backend='local',model=served_model,endpoint=endpoint,timeout=60,max_tokens=512)
        cache_rows.append({'label':label,'seconds':round(time.monotonic()-started,3),'inference_requests':0})
    summary={}
    for label,model in models:
        samples=[r for r in rows if r['label']==label]
        successful=[r for r in samples if r['status']=='ok']
        summary[label]={'model':model,'samples':len(samples),'successful':len(successful),'criteria_met':sum(r['criteria_met'] for r in samples),
                        'median_seconds':round(statistics.median(r['elapsed_seconds'] for r in successful),3) if successful else None,
                        'min_seconds':min((r['elapsed_seconds'] for r in successful),default=None),'max_seconds':max((r['elapsed_seconds'] for r in successful),default=None)}
    (args.output/'summary.json').write_text(json.dumps({'models':summary,'client_cache':cache_rows,'settings':{'temperature':0,'max_tokens':512,'repeats':args.repeats,'prompt':QUESTION,'criteria':CRITERIA},'limits':'Same simple readable/obscured title task; provider defaults and 9router overhead included. Does not establish equivalence on rig analysis.'},indent=2))
    print('SUMMARY',json.dumps(summary),flush=True)


if __name__=='__main__':main()
