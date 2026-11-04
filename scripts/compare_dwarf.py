#!/usr/bin/env python3
import json, sys
from elftools.elf.elffile import ELFFile
TYPES = 'net_device net_device_ops wireless_dev wiphy cfg80211_ops cfg80211_scan_request cfg80211_connect_params station_info ieee80211_channel ieee80211_supported_band usb_driver usb_device usb_interface urb sk_buff device work_struct timer_list iw_handler_def'.split()
def inspect(path):
 result={}
 with open(path,'rb') as f:
  for cu in ELFFile(f).get_dwarf_info().iter_CUs():
   for d in cu.iter_DIEs():
    if d.tag != 'DW_TAG_structure_type':continue
    attrs=d.attributes
    name=attrs.get('DW_AT_name')
    if not name:continue
    name=name.value.decode()
    if name not in TYPES or 'DW_AT_byte_size' not in attrs:continue
    members=[]
    for m in d.iter_children():
     if m.tag!='DW_TAG_member':continue
     item={}
     for key in ['DW_AT_name','DW_AT_data_member_location','DW_AT_bit_size','DW_AT_bit_offset']:
      if key in m.attributes:
       v=m.attributes[key].value
       item[key.removeprefix('DW_AT_')]=v.decode() if isinstance(v,bytes) else v
     members.append(item)
    result[name]={'size':attrs['DW_AT_byte_size'].value,'members':members}
 assert set(result)==set(TYPES),set(TYPES)-set(result)
 return result
baseline,driver=map(inspect,sys.argv[1:3])
rows=[{'type':t,'baseline_size':baseline[t]['size'],'driver_size':driver[t]['size'],'member_count':len(baseline[t]['members']),'match':baseline[t]==driver[t]} for t in TYPES]
print(json.dumps({'status':'PASS' if all(r['match'] for r in rows) else 'FAIL','scope':'19 shared structures: size and direct member offsets/bitfields; reconstructed R6 headers, not running vehicle memory','types':rows,'baseline':baseline,'driver':driver},indent=2))
assert all(r['match'] for r in rows)
