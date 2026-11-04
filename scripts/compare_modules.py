#!/usr/bin/env python3
import sys,json,hashlib,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
old,new,nm,out=sys.argv[1:]
def read(p):
 with open(p,'rb') as f:
  e=ELFFile(f);syms=e.get_section_by_name('.symtab');fw={}
  for s in syms.iter_symbols():
   if s.name.startswith('array_mp_8188e_') and '_fw_' in s.name and s['st_size']:
    sec=e.get_section(s['st_shndx']);a=s['st_value']-sec['sh_addr'];fw[s.name]=hashlib.sha256(sec.data()[a:a+s['st_size']]).hexdigest()
  return {'machine':e['e_machine'],'class':e.elfclass,'little_endian':e.little_endian,'modinfo':e.get_section_by_name('.modinfo').data().decode().strip('\0').split('\0'),'firmware':fw}
a,b=read(old),read(new)
def info(x,k):return sorted(i.split('=',1)[1] for i in x['modinfo'] if i.startswith(k+'='))
def imports(p):return sorted(x.split()[-1] for x in subprocess.check_output([nm,'-u',p],text=True).splitlines())
x,y=imports(old),imports(new)
r={'baseline_sha256':hashlib.sha256(Path(old).read_bytes()).hexdigest(),'diagnostic_sha256':hashlib.sha256(Path(new).read_bytes()).hexdigest(),'machine':b['machine'],'ELF_class':b['class'],'little_endian':b['little_endian'],'vermagic_baseline':info(a,'vermagic'),'vermagic_diagnostic':info(b,'vermagic'),'vermagic_equal':info(a,'vermagic')==info(b,'vermagic'),'USB_aliases_equal':info(a,'alias')==info(b,'alias'),'baseline_imports':len(x),'diagnostic_imports':len(y),'added_imports':sorted(set(y)-set(x)),'removed_imports':sorted(set(x)-set(y)),'firmware_arrays_equal':a['firmware']==b['firmware'],'firmware_arrays_baseline':a['firmware'],'firmware_arrays_diagnostic':b['firmware'],'diagnostic_identity':info(b,'nx4_diagnostic'),'hardware_test':'NOT_PERFORMED'}
Path(out).write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
assert r['vermagic_equal'] and r['USB_aliases_equal'] and not r['added_imports'] and not r['removed_imports'] and r['firmware_arrays_equal'] and len(b['firmware'])>0
