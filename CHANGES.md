# Changes / 변경 기록

- 2026-11-04: Linux 3.18 cfg80211 API 포팅 및 NX4D1 초기화 진단 로그. 상세 변경은 patches/ 참조.
- R2: printf 의존성 및 id -u 기반 root 검사 수정.
- R3: tr 없이 ARM/COLLECT/RESTORE 읽기; LF/CRLF/BOM 및 오류 구분. 실차 미검증.
- 2026-11-05: GitHub 소스 공개 구성, GPL v2 전문, 출처/범위 문서 및 수정 파일 끝의 고지 추가. 실행 로직 변경 없음.

수정 고지 추가 대상:
- `driver-src/Makefile`
- `driver-src/core/rtw_debug.c`
- `driver-src/core/rtw_pwrctrl.c`
- `driver-src/hal/HalPwrSeqCmd.c`
- `driver-src/hal/hal_intf.c`
- `driver-src/hal/rtl8188e/rtl8188e_hal_init.c`
- `driver-src/hal/rtl8188e/usb/usb_halinit.c`
- `driver-src/include/nx4_diag.h`
- `driver-src/os_dep/linux/ioctl_cfg80211.c`
- `driver-src/os_dep/linux/ioctl_cfg80211.h`
- `driver-src/os_dep/linux/os_intfs.c`
- `driver-src/os_dep/linux/rtw_cfgvendor.c`
- `driver-src/os_dep/linux/usb_intf.c`
- `driver-src/os_dep/linux/usb_ops_linux.c`

차량별 빌드 및 진단 기록은 공개 저장소에서 제외한다. 패치는 고지 추가 전 변경을 보존하며, 현재 driver-src에는 이미 포팅 및 진단 수정이 적용되어 있다.

- 2026-11-05: 사용자 제공 실차 결과(무선 연결, DHCP, 인터넷, Wireless ADB)를 단계별 검증 문서로 추가. Android Auto 상호작용과 NEMESIS 서비스 상태 판별을 별도 이슈로 분리. 성공 바이너리와 공개 소스의 byte identity는 미확인으로 명시.
