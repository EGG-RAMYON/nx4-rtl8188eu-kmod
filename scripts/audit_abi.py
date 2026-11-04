#!/usr/bin/env python3
"""Usage: python3 audit_abi.py TREE OUT CROSS BUILD; requires pyelftools."""
import pathlib,shlex,subprocess,sys,json,re
kit=pathlib.Path(__file__).resolve().parent
TREE,OUT,CROSS,BUILD=sys.argv[1:]
TREE,OUT,BUILD=map(lambda x:pathlib.Path(x).resolve(),(TREE,OUT,BUILD))
audit=BUILD/'audit';audit.mkdir(exist_ok=True)
base=audit/'baseline';base.mkdir(exist_ok=True);(base/'.tmp_versions').mkdir(exist_ok=True)
(base/'abi_types.c').write_bytes((kit/'abi_types.c').read_bytes())
(base/'Makefile').write_text('obj-m := abi_types.o\nccflags-y += -g -fno-eliminate-unused-debug-types\n')
cmd=['make','-C',str(TREE),'O='+str(OUT),'ARCH=arm','CROSS_COMPILE='+CROSS,'HOSTCC=gcc -fcommon','M='+str(base),'abi_types.o']
with (audit/'baseline.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
cmdfile=BUILD/'driver/os_dep/linux/.os_intfs.o.cmd'
args=shlex.split(cmdfile.read_text().splitlines()[0].split(':=',1)[1].strip())
args=[x for x in args if not x.startswith('-Wp,-MD,')]
args[args.index('-o')+1]=str(audit/'driver.o');args[-1]=str(base/'abi_types.c')
args+=['-DNX4_DRIVER_CONTEXT','-g','-fno-eliminate-unused-debug-types']
(audit/'driver_command.txt').write_text(shlex.join(args)+'\n')
with (audit/'driver.log').open('w') as log:subprocess.run(args,cwd=OUT,stdout=log,stderr=subprocess.STDOUT,check=True)
macroargs=[x for x in args if x!='-c']
i=macroargs.index('-o');del macroargs[i:i+2];macroargs+=['-E','-dM']
macros=subprocess.check_output(macroargs,cwd=OUT,text=True)
(audit/'driver_macros.txt').write_text(macros)
def parse(s):return dict(re.findall(r'^#define (CONFIG_\w+)[ \t]+([^\n]*)$',s,re.M))
expected=parse((OUT/'include/generated/autoconf.h').read_text());actual=parse(macros)
diffs={k:{'expected':v,'actual':actual.get(k)} for k,v in expected.items() if actual.get(k)!=v}
for k in ['CONFIG_WIRELESS_EXT','CONFIG_WEXT_PRIV']:
 if k in actual:diffs[k]={'expected':'absent','actual':actual[k]}
(audit/'kernel_macro_check.json').write_text(json.dumps({'checked_defined_kernel_macros':len(expected),'differences':diffs},indent=2))
assert not diffs,diffs
with (audit/'abi_layout_comparison.json').open('w') as log:
 subprocess.run([sys.executable,str(kit/'compare_dwarf.py'),str(base/'abi_types.o'),str(audit/'driver.o')],stdout=log,check=True)
print('PASS: kernel config macros preserved; 19 shared structure layouts match.')
