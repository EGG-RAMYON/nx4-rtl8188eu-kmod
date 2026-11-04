#!/usr/bin/env python3
import pathlib,subprocess,sys,json
ko,kout,nm,out=sys.argv[1:]
undefined=[x.split()[-1] for x in subprocess.check_output([nm,'-u',ko],text=True).splitlines() if x.strip()]
exports={}
for obj in pathlib.Path(kout).rglob('*.o'):
 if 'scripts' in obj.parts:continue
 for line in subprocess.check_output([nm,str(obj)],text=True,stderr=subprocess.DEVNULL).splitlines():
  fields=line.split()
  if len(fields)==3 and fields[2].startswith('__ksymtab_'):
   exports.setdefault(fields[2][10:],[]).append(str(obj.relative_to(kout)))
rows=[{'symbol':s,'export_objects':exports.get(s,[])} for s in undefined]
missing=[x['symbol'] for x in rows if not x['export_objects']]
pathlib.Path(out).write_text(json.dumps({'scope':'Exports in objects locally compiled from reconstructed R6 source with unchanged supplied vehicle config; not actual vehicle exports','total':len(rows),'matched':len(rows)-len(missing),'unverified':missing,'symbols':rows},indent=2))
print('total',len(rows),'matched',len(rows)-len(missing),'unverified',missing)
