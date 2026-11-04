#!/usr/bin/env python3
# Apply only to the preserved, already ported v5.3.9 source. Every replacement is checked.
from pathlib import Path
import sys
root=Path(sys.argv[1])
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a))
 return s.replace(a,b,1)
def edit(file, signature, transform):
 p=root/file;s=p.read_text();start=s.index(signature+'\n{');end=s.index('\n}',start)+2
 part=s[start:end];s=s[:start]+transform(part)+s[end:];p.write_text(s)
def rep(a,b):return lambda s:once(s,a,b)
files=['os_dep/linux/os_intfs.c','hal/hal_intf.c','hal/rtl8188e/usb/usb_halinit.c','hal/rtl8188e/rtl8188e_hal_init.c','hal/HalPwrSeqCmd.c','os_dep/linux/usb_ops_linux.c','os_dep/linux/usb_intf.c','core/rtw_pwrctrl.c']
for f in files:
 p=root/f;s=p.read_text();first=s.index('#include');end=s.index('\n',first);s=s[:end]+'\n#include <nx4_diag.h>'+s[end:];p.write_text(s)
(root/'include/nx4_diag.h').write_text('''/* NX4D1: diagnostic observations only; no additional device register reads. */
#ifndef NX4_DIAG_H
#define NX4_DIAG_H
extern int nx4_diag;
#define NX4_DIAG(fmt, ...) do { if (nx4_diag) \\
 printk(KERN_NOTICE "NX4D1 %s:%d " fmt "\\n", __func__, __LINE__, ##__VA_ARGS__); } while (0)
#endif
''')
p=root/'os_dep/linux/os_intfs.c';s=p.read_text();s=once(s,'MODULE_VERSION(DRIVERVERSION);','''MODULE_VERSION(DRIVERVERSION);
MODULE_INFO(nx4_diagnostic, "NX4D1_20261104");
int nx4_diag = 1;
module_param(nx4_diag, int, 0644);
MODULE_PARM_DESC(nx4_diag, "NX4D1 initialization diagnostics; 0 disables added logs");
static char *nx4_diag_id = "NX4D1_20261104";
module_param(nx4_diag_id, charp, 0444);
''');p.write_text(s)
f='os_dep/linux/os_intfs.c'
def open_inner(s):
 s=once(s,'\tpadapter->netif_up = _TRUE;','\tNX4_DIAG("OPEN_INNER enter if=%s bup=%u stopped=%u removed=%u hwinit=%u", pnetdev->name, padapter->bup, rtw_is_drv_stopped(padapter), rtw_is_surprise_removed(padapter), rtw_get_hw_init_completed(padapter));\n\tpadapter->netif_up = _TRUE;')
 for call in ['rtw_hal_init(padapter)','rtw_start_drv_threads(padapter)']:
  a='\t\tstatus = '+call+';';s=once(s,a,'\t\tNX4_DIAG("CALL '+call+'");\n'+a+'\n\t\tNX4_DIAG("RESULT '+call+' ret=%u", status);')
 s=once(s,'\t\trtw_intf_start(padapter);','\t\tNX4_DIAG("CALL rtw_intf_start");\n\t\trtw_intf_start(padapter);\n\t\tNX4_DIAG("RESULT rtw_intf_start returned");')
 s=once(s,'\treturn 0;','\tNX4_DIAG("OPEN_INNER success ret=0 bup=%u", padapter->bup);\n\treturn 0;')
 s=once(s,'\treturn -1;','\tNX4_DIAG("OPEN_INNER failure ret=-1 (EPERM) last_status=%u stopped=%u removed=%u", status, rtw_is_drv_stopped(padapter), rtw_is_surprise_removed(padapter));\n\treturn -1;')
 return s
edit(f,'int _netdev_open(struct net_device *pnetdev)',open_inner)
def outer(s):
 a='\tif (pwrctrlpriv->bInSuspend == _TRUE) {'
 s=once(s,a,'\tNX4_DIAG("OPEN enter if=%s suspend=%u keepfw=%u rfstate=%u primary=%u", pnetdev->name, pwrctrlpriv->bInSuspend, pwrctrlpriv->bkeepfwalive, pwrctrlpriv->rf_pwrstate, is_primary_adapter(padapter));\n'+a+'\n\t\tNX4_DIAG("OPEN suspend skip ret=0");')
 s=once(s,'\treturn ret;','\tNX4_DIAG("OPEN exit ret=%d", ret);\n\treturn ret;');return s
edit(f,'int netdev_open(struct net_device *pnetdev)',outer)
def threads(s):
 for field in ['xmitThread','recvThread','cmdThread','evtThread']:
  a='if (IS_ERR(padapter->'+field+')) {'
  s=once(s,a,a+'\n\t\t\t\tNX4_DIAG("THREAD '+field+' failed errno=%ld", PTR_ERR(padapter->'+field+'));')
 s=once(s,'\treturn _status;','\tNX4_DIAG("THREADS exit ret=%u", _status);\n\treturn _status;');return s
edit(f,'u32 rtw_start_drv_threads(_adapter *padapter)',threads)
for signature in ['int  ips_netdrv_open(_adapter *padapter)']:
 edit(f,signature,lambda s:once(s,'\tstatus = rtw_hal_init(padapter);','\tNX4_DIAG("IPS_OPEN hal enter");\n\tstatus = rtw_hal_init(padapter);\n\tNX4_DIAG("IPS_OPEN hal ret=%d", status);'))
f='hal/hal_intf.c'
edit(f,'u32 rtw_hal_power_on(_adapter *padapter)',rep('\tret = padapter->hal_func.hal_power_on(padapter);','\tNX4_DIAG("POWER_ON enter");\n\tret = padapter->hal_func.hal_power_on(padapter);\n\tNX4_DIAG("POWER_ON exit ret=%u", ret);'))
edit(f,'uint\t rtw_hal_init(_adapter *padapter)',lambda s:once(once(s,'\tstatus = padapter->hal_func.hal_init(padapter);','\tNX4_DIAG("HAL enter");\n\tstatus = padapter->hal_func.hal_init(padapter);\n\tNX4_DIAG("HAL chip_init ret=%u", status);'),'\treturn status;','\tNX4_DIAG("HAL exit ret=%u hwinit=%u", status, rtw_get_hw_init_completed(padapter));\n\treturn status;'))
f='hal/rtl8188e/usb/usb_halinit.c'
def power(s):
 s=once(s,'\tif (bMacPwrCtrlOn == _TRUE)','\tNX4_DIAG("POWER_HW cached_mac_on=%u", bMacPwrCtrlOn);\n\tif (bMacPwrCtrlOn == _TRUE)')
 s=once(s,'\t\treturn _FAIL;','\t\tNX4_DIAG("POWER_HW power_sequence ret=0");\n\t\treturn _FAIL;')
 s=once(s,'\treturn _SUCCESS;','\tNX4_DIAG("POWER_HW success ret=1 CR_written=0x%04x", value16);\n\treturn _SUCCESS;') if s.count('\treturn _SUCCESS;')==1 else s
 # The early cached success contains the same substring; insert before the final return only.
 a='\n\treturn _SUCCESS;\n\n}'
 if a in s:s=once(s,a,'\n\tNX4_DIAG("POWER_HW success ret=1 CR_written=0x%04x", value16);'+a)
 return s
edit(f,'static u32 _InitPowerOn_8188EU(_adapter *padapter)',power)
def hal(s):
 s=once(s,'#define HAL_INIT_PROFILE_TAG(stage) do {} while (0)','#define HAL_INIT_PROFILE_TAG(stage) do { NX4_DIAG("HAL_STAGE %s", #stage); } while (0)')
 s=once(s,'\tif (pwrctrlpriv->bkeepfwalive) {','\tNX4_DIAG("HAL_USB enter keepfw=%u suspend=%u rfstate=%u mp=%u", pwrctrlpriv->bkeepfwalive, pwrctrlpriv->bInSuspend, pwrctrlpriv->rf_pwrstate, Adapter->registrypriv.mp_mode);\n\tif (pwrctrlpriv->bkeepfwalive) {\n\t\tNX4_DIAG("HAL_USB keepfw path");')
 import re
 s=re.sub(r'(?m)^(\s*)status = (.+);$',lambda m:m[0]+'\n'+m[1]+'NX4_DIAG("HAL_RESULT '+m[2]+' ret=%u", status);',s)
 s=s.replace('\t\t\treturn status;','\t\t\tNX4_DIAG("HAL_USB early return ret=%u FW_ready=%u", status, pHalData->bFWReady);\n\t\t\treturn status;')
 s=once(s,'\treturn status;\n}','\tNX4_DIAG("HAL_USB exit ret=%u elapsed_ms=%d FW_ready=%u", status, rtw_get_passing_time_ms(init_start_time), pHalData->bFWReady);\n\treturn status;\n}')
 return s
edit(f,'u32 rtl8188eu_hal_init(PADAPTER Adapter)',hal)
f='hal/rtl8188e/rtl8188e_hal_init.c'
for signature,tag in [('static s32 polling_fwdl_chksum(_adapter *adapter, u32 min_cnt, u32 timeout_ms)','FW_CHECKSUM'),('static s32 _FWFreeToGo(_adapter *adapter, u32 min_cnt, u32 timeout_ms)','FW_READY')]:
 edit(f,signature,rep('\treturn ret;','\tNX4_DIAG("'+tag+' ret=%d polls=%u elapsed_ms=%d MCUFWDL=0x%08x cannot_io=%u", ret, cnt, rtw_get_passing_time_ms(start), value32, RTW_CANNOT_IO(adapter));\n\treturn ret;'))
def fw(s):
 s=once(s,'\tpFirmware = (PRT_FIRMWARE_8188E)rtw_zmalloc','\tNX4_DIAG("FW enter wow=%u i_cut=%u", bUsedWoWLANFw, IS_VENDOR_8188E_I_CUT_SERIES(padapter));\n\tpFirmware = (PRT_FIRMWARE_8188E)rtw_zmalloc')
 s=once(s,'\tif (!pFirmware) {','\tif (!pFirmware) {\n\t\tNX4_DIAG("FW allocation failed");')
 s=once(s,'\ttmp_fw_len = IS_VENDOR','\tNX4_DIAG("FW image source=%u length=%u", pFirmware->eFWSource, pFirmware->ulFwLength);\n\ttmp_fw_len = IS_VENDOR')
 s=once(s,'\tpHalData->FirmwareSignature = le16_to_cpu(pFwHdr->Signature);','\tpHalData->FirmwareSignature = le16_to_cpu(pFwHdr->Signature);\n\tNX4_DIAG("FW header version=0x%x sub=0x%x signature=0x%x", pHalData->firmware_version, pHalData->firmware_sub_version, pHalData->FirmwareSignature);')
 s=once(s,'\t\trtStatus = _WriteFW(padapter, pFirmwareBuf, FirmwareLen);','\t\trtStatus = _WriteFW(padapter, pFirmwareBuf, FirmwareLen);\n\t\tif (write_fw <= 8)\n\t\t\tNX4_DIAG("FW_WRITE attempt=%u length=%u ret=%d", write_fw, FirmwareLen, rtStatus);')
 s=once(s,'fwdl_stat:\n','fwdl_stat:\n\tNX4_DIAG("FW_DOWNLOAD result=%d attempts=%u elapsed_ms=%d cannot_io=%u", rtStatus, write_fw, rtw_get_passing_time_ms(fwdl_start_time), RTW_CANNOT_IO(padapter));\n')
 s=once(s,'\treturn rtStatus;','\tNX4_DIAG("FW exit ret=%d", rtStatus);\n\treturn rtStatus;');return s
edit(f,'s32 rtl8188e_FirmwareDownload(PADAPTER padapter, BOOLEAN  bUsedWoWLANFw)',fw)
f='hal/HalPwrSeqCmd.c';p=root/f;s=p.read_text();s=once(s,'\t\t\t\t\tif (pollingCount++ > maxPollingCnt) {','\t\t\t\t\tif (pollingCount++ > maxPollingCnt) {\n\t\t\t\t\t\tNX4_DIAG("POWER_POLL timeout step=%u offset=0x%x masked_value=0x%x mask=0x%x expected=0x%x polls=%u", AryIdx, offset, value, GET_PWR_CFG_MASK(PwrCfgCmd), GET_PWR_CFG_VALUE(PwrCfgCmd) & GET_PWR_CFG_MASK(PwrCfgCmd), pollingCount);');p.write_text(s)
f='os_dep/linux/usb_ops_linux.c'
def usb(s):
 s=once(s,'\tint vendorreq_times = 0;','\tint vendorreq_times = 0;\n\tstatic atomic_t nx4_usb_errors = ATOMIC_INIT(0);')
 s=once(s,'exit:\n\treturn status;','exit:\n\tif (nx4_diag && status != len && atomic_inc_return(&nx4_usb_errors) <= 8)\n\t\tNX4_DIAG("USB_CTRL failure status=%d expected_len=%u request=0x%x value=0x%x index=0x%x direction=%u tries=%d cannot_io=%u (first8)", status, len, request, value, index, requesttype, vendorreq_times, RTW_CANNOT_IO(padapter));\n\treturn status;');return s
edit(f,'int usbctrl_vendorreq(struct intf_hdl *pintfhdl, u8 request, u16 value, u16 index, void *pdata, u16 len, u8 requesttype)',usb)
f='os_dep/linux/usb_intf.c'
edit(f,'static int __init rtw_drv_entry(void)',rep('\tint ret = 0;','\tint ret = 0;\n\tNX4_DIAG("MODULE diagnostic=NX4D1_20261104");'))
edit(f,'static int rtw_drv_init(struct usb_interface *pusb_intf, const struct usb_device_id *pdid)',lambda s:once(once(s,'\t/* step 0. */','\tNX4_DIAG("PROBE enter vid=0x%x pid=0x%x", pdid->idVendor, pdid->idProduct);\n\t/* step 0. */'),'\treturn status == _SUCCESS ? 0 : -ENODEV;','\tNX4_DIAG("PROBE exit raw=%d errno=%d", status, status == _SUCCESS ? 0 : -ENODEV);\n\treturn status == _SUCCESS ? 0 : -ENODEV;'))
f='core/rtw_pwrctrl.c'
edit(f,'int _rtw_pwr_wakeup(_adapter *padapter, u32 ips_deffer_ms, const char *caller)',lambda s:once(once(s,'\t/* for LPS */','\tNX4_DIAG("WAKE enter caller=%s suspend=%u keepfw=%u rfstate=%u", caller, pwrpriv->bInSuspend, pwrpriv->bkeepfwalive, pwrpriv->rf_pwrstate);\n\t/* for LPS */'),'\treturn ret;','\tNX4_DIAG("WAKE exit ret=%d suspend=%u rfstate=%u stopped=%u hwinit=%u", ret, pwrpriv->bInSuspend, pwrpriv->rf_pwrstate, rtw_is_drv_stopped(padapter), rtw_get_hw_init_completed(padapter));\n\treturn ret;'))
print('Applied diagnostic-only instrumentation to',len(files),'C files + header')
