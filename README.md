# NX4 Gen5W RTL8188EU diagnostics

현대 투싼 NX4 HEV Gen5W의 RTL8188EU USB Wi-Fi 초기화 문제를 조사하는 **실험용 소스 공개 프로젝트**입니다. 현대자동차·현대모비스·Realtek의 공식 프로젝트가 아닙니다.

## 현재 상태

- 대상 커널: Linux 3.18.24-tcc / ARMv7 / Android 4.4.2, ipTIME N150L (`0bda:8179`).
- 기반 드라이버: Realtek v5.3.9_28540.20180627, aircrack-ng/rtl8188eus 고정 커밋.
- NX4D1 초기화 계측 소스와 커널 일치 모듈이 있습니다. 모듈 삽입은 확인됐지만, `wlan0` 생성 및 무선 통신은 확인되지 않았습니다.
- [Releases](https://github.com/EGG-RAMYON/nx4-rtl8188eu-kmod/releases)에 실험용 `r8188eu.ko`가 있습니다. 파일의 vermagic과 ARM 아키텍처는 NX4 커널 기준이며, 차종·헤드유닛·펌웨어 차이에 따른 호환성은 보장하지 않습니다.
- 공개 저장소에는 차량별 커널 설정, 차량 수집 로그, NEMESIS.data, 제조사 커널 소스 분할 파일, 툴체인, `.ko`가 포함되지 않습니다. `.ko`는 Release asset으로만 제공합니다. USB_READY는 실행 완성품이 아닌 소스 템플릿입니다.

## 구성

| 경로 | 내용 |
|---|---|
| driver-src/ | 포팅과 NX4D1 계측이 적용된 전체 드라이버 소스 |
| patches/ | cfg80211 포팅, 진단 계측, 차량 셸 수정 패치 |
| scripts/ | NX4 커널 준비, ARM 모듈 빌드, ABI/심볼 검사 |
| vehicle/, USB_READY/ | NEMESIS 실행용 자체 진단 스크립트 |
| tests/ | 차량 명령을 모의 처리하는 호스트 시험 |
| SOURCES.md | 원본 URL, 고정 커밋, 입력 해시 |
| LICENSE, LICENSE_SCOPE.md | GPL v2 전문 및 적용 범위 |
| CHANGES.md | 수정 내역 및 날짜 |

## NX4 커널로 빌드

NX4에서 추출한 **정확한 커널 `.config`**와 제조사 R6 커널 소스 분할 파일이 필요합니다. 이 입력 파일은 공개 저장소에 올리지 마세요. `scripts/prepare_kernel.sh`가 입력 해시, 커널 버전, 고정된 ARM GCC 4.7 툴체인을 확인하고, 설정을 바꾸지 않은 상태로 커널 빌드 트리를 준비합니다. 상세 절차와 명령은 [BUILD_NX4.md](BUILD_NX4.md)를 따르세요.

빌드 완료 시 스크립트가 다음을 확인합니다: 설정 파일 변경 여부, 모듈의 USB ID와 vermagic, ARM 심볼, SHA-256. 이 확인은 ABI 형식과 대상 식별을 검사하며, 실차에서 Wi-Fi 동작을 보증하지 않습니다.

호스트 모의시험:

```sh
python3 tests/test_vehicle_scripts.py
```

## 출처와 라이선스

드라이버의 GPL v2 고지와 기존 저작권 표시를 유지합니다. 이 프로젝트의 추가 코드·스크립트·문서도 GPL-2.0-only로 제공합니다. 개별 파일의 기존 별도 고지는 그대로 적용됩니다. [출처](SOURCES.md)와 [라이선스 범위](LICENSE_SCOPE.md)를 확인하세요.

차량 로그를 공개할 때는 SSID, MAC, IP, VIN, 파일 경로 등 식별 정보를 제거하세요.