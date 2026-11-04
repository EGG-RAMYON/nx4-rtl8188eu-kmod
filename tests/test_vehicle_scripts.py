#!/usr/bin/env python3
"""Host mocks only. No real module/network operations or vehicle testing."""
import os,pathlib,tempfile,subprocess,time,json,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1];reports=[]
FIXTURES=tempfile.TemporaryDirectory(prefix="nx4-script-tests-")
MOCK='''#!/usr/bin/python3
import os,sys,pathlib,time
r=pathlib.Path(os.environ['MOCK_ROOT']);cmd=pathlib.Path(sys.argv[0]).name
with (r/'commands.txt').open('a') as f:f.write(cmd+' '+' '.join(sys.argv[1:])+'\\n')
if cmd=='id':
 if len(sys.argv)>1:print('id: unsupported option');sys.exit(1)
 print('uid='+os.environ.get('MOCK_UID','0')+'(mock) gid=0(root) context=kernel');sys.exit(0)
if cmd=='uname':print('3.18.24-tcc');sys.exit(0)
if cmd=='sleep':time.sleep(0.01);sys.exit(0)
if cmd=='sync':sys.exit(0)
if cmd=='dmesg':print('MOCK ONLY: NX4D1 OPEN_INNER failure ret=-1');sys.exit(0)
if cmd=='insmod':
 p=r/'sys/module/r8188eu/parameters';p.mkdir(parents=True,exist_ok=True)
 if 'diagnostic' in sys.argv[1]:(p/'nx4_diag_id').write_text('NX4D1_20261104\\n')
 (r/'proc/modules').write_text('bcmdhd 816292 0 - Live 0x0\\nr8188eu 1000000 0 - Live 0x0\\n');sys.exit(0)
if cmd=='rmmod':
 assert sys.argv[1:] == ['r8188eu']
 (r/'proc/modules').write_text('bcmdhd 816292 0 - Live 0x0\\n')
 p=r/'sys/module/r8188eu/parameters/nx4_diag_id'
 if p.exists():p.unlink()
 sys.exit(0)
if cmd=='ifconfig':
 assert sys.argv[1:]==['wlan0','up']
 mode=os.environ.get('MOCK_UP','fail')
 if mode=='hang':time.sleep(5)
 if mode=='success':
  (r/'sys/class/net/wlan0/flags').write_text('0x1003\\n');sys.exit(0)
 print('error: SIOCSIFFLAGS (Operation not permitted)');sys.exit(255)
sys.exit(127)
'''
def setup(mode='fail',wait='180'):
 r=pathlib.Path(tempfile.mkdtemp(prefix='nx4-mock-',dir=FIXTURES.name))
 for d in ['bin','usb/NX4_DIAG/diagnostic','usb/NX4_DIAG/baseline','proc/net','proc/self/attr','proc/sys/kernel/random','sys/class/net','sys/module/r8188eu/parameters','sys/bus/usb/drivers/8188eu','base']:(r/d).mkdir(parents=True,exist_ok=True)
 for name in ['id','uname','sleep','sync','dmesg','insmod','rmmod','ifconfig']:
  p=r/'bin'/name;p.write_text(MOCK);p.chmod(0o755)
 for mode2 in ['diagnostic','baseline']:(r/f'usb/NX4_DIAG/{mode2}/r8188eu.ko').write_bytes(b'MOCK_MODULE')
 shutil.copy(ROOT/'vehicle/worker.sh',r/'usb/NX4_DIAG/worker.sh')
 (r/'usb/NX4_DIAG_ACTION.txt').write_text('ARM\n')
 (r/'proc/modules').write_text('bcmdhd 816292 0 - Live 0x0\nr8188eu 1000000 0 - Live 0x0\n')
 (r/'proc/net/dev').write_text('MOCK rmnet0 untouched\n');(r/'proc/self/status').write_text('CapEff: mock\n');(r/'proc/self/attr/current').write_text('mock\n');(r/'proc/sys/kernel/random/boot_id').write_text('boot1\n')
 (r/'sys/bus/usb/drivers/8188eu/module').symlink_to(r/'sys/module/r8188eu')
 e=os.environ|{'PATH':str(r/'bin')+':'+os.environ['PATH'],'MOCK_ROOT':str(r),'NX4_USB_ROOT':str(r/'usb'),'NX4_BASE_ROOT':str(r/'base'),'NX4_SYS_ROOT':str(r/'sys'),'NX4_PROC_ROOT':str(r/'proc'),'NX4_SHELL':'/bin/sh','NX4_WAIT_SECONDS':wait,'MOCK_UP':mode}
 return r,e
def launch(r,e,action):
 (r/'usb/NX4_DIAG_ACTION.txt').write_text(action+'\n')
 return subprocess.run(['/bin/sh',str(ROOT/'vehicle/NEMESIS.sh')],env=e,timeout=5).returncode
def session(r):return r/'base'/(r/'base/current').read_text().strip()
def bind(r,vendor='0bda'):
 u=r/'sys/bus/usb/devices/4-1';i=u/'4-1:1.0';n=i/'net/wlan0';n.mkdir(parents=True)
 (u/'idVendor').write_text(vendor);(u/'idProduct').write_text('8179');(i/'driver').symlink_to(r/'sys/bus/usb/drivers/8188eu');(n/'device').symlink_to(i)
 (n/'flags').write_text('0x1002\n');(n/'operstate').write_text('down\n');(r/'sys/class/net/wlan0').symlink_to(n)
def await_status(s,prefix):
 deadline=time.monotonic()+6
 while time.monotonic()<deadline:
  if (s/'status').exists() and (s/'status').read_text().startswith(prefix):return
  time.sleep(.02)
 raise AssertionError((s,(s/'status').read_text() if (s/'status').exists() else 'missing'))
for script in ['NEMESIS.sh','worker.sh']:
 assert 'printf' not in (ROOT/'vehicle'/script).read_text()
r,e=setup();e['MOCK_UID']='2000';assert launch(r,e,'ARM')!=0
assert not (r/'base/current').exists()
assert 'insmod ' not in (r/'commands.txt').read_text()
reports.append({'scenario':'nonroot plain id','status':'PASS','checks':['rejected before module changes']})
for label,content,valid in [('LF',b'ARM\n',True),('CRLF',b'ARM\r\n',True),('BOM',b'\xef\xbb\xbfARM\r\n',True),('no newline',b'ARM',True),('empty',b'',False),('invalid',b'ARMX\n',False),('missing',None,False)]:
 r,e=setup();e['MOCK_UID']='2000'
 action=r/'usb/NX4_DIAG_ACTION.txt'
 if content is None:action.unlink()
 else:action.write_bytes(content)
 result=subprocess.run(['/bin/sh',str(ROOT/'vehicle/NEMESIS.sh')],env=e,timeout=5)
 assert result.returncode!=0
 log=(r/'usb/NX4_DIAG_LAUNCH.txt').read_text()
 assert ('STOP: root required' in log)==valid,(label,log)
 assert not (r/'base/current').exists()
 reports.append({'scenario':'action '+label,'status':'PASS'})
for mode in ['fail','success']:
 r,e=setup(mode);assert launch(r,e,'ARM')==0;s=session(r)
 assert (r/'usb/NX4_DIAG_ACTION.txt').read_text().strip()=='COLLECT'
 assert launch(r,e,'ARM')!=0 # active run not overwritten
 bind(r);await_status(s,'COMPLETE')
 expected='255' if mode=='fail' else '0';assert (s/'up.exit').read_text().strip()==expected
 before=(r/'commands.txt').read_text();assert launch(r,e,'COLLECT')==0
 assert (r/'commands.txt').read_text().count('insmod ')==before.count('insmod ')
 assert (r/'usb/NX4_DIAG_RESULTS'/s.name/'dmesg_after.txt').stat().st_size>0
 assert launch(r,e,'RESTORE')!=0 # bound device blocks module unload
 (r/'sys/class/net/wlan0').unlink();assert launch(r,e,'RESTORE')==0
 commands=(r/'commands.txt').read_text();assert commands.count('ifconfig wlan0 up')==1
 assert 'rmmod bcmdhd' not in commands
 reports.append({'scenario':mode,'status':'PASS','checks':['ARM detachment handshake','duplicate ARM blocked','one matching-interface up','COLLECT nonempty and no reload','RESTORE blocked while bound','baseline restore after detach']})
r,e=setup(wait='8');assert launch(r,e,'ARM')==0;s=session(r);bind(r,'ffff');await_status(s,'WAIT_DONGLE_TIMEOUT');assert 'ifconfig ' not in (r/'commands.txt').read_text();reports.append({'scenario':'wrong VID','status':'PASS'})
r,e=setup('hang');assert launch(r,e,'ARM')==0;s=session(r);bind(r);await_status(s,'UP_TIMEOUT');assert launch(r,e,'RESTORE')!=0;assert launch(r,e,'COLLECT')==0;time.sleep(5.1);reports.append({'scenario':'hung ifconfig','status':'PASS','checks':['timeout preserved','no forced unload','logs collectable']})
path=ROOT/'evidence/vehicle_script_mock_tests.json';path.write_text(json.dumps({'scope':'HOST MOCKS ONLY; no hardware executed','results':reports},indent=2));print(path.read_text())
