# NX4 Gen5W RTL8188EU diagnostics

현대 투싼 NX4 HEV Gen5W의 RTL8188EU USB Wi-Fi 초기화 실패를 조사하는 **실험용 소스 공개 프로젝트**입니다. 현대자동차·현대모비스·Realtek의 공식 프로젝트가 아닙니다.

## 현재 상태

- 대상: Linux 3.18.24-tcc / ARMv7 / Android 4.4.2, ipTIME N150L (`0bda:8179`).
- 기반 드라이버: Realtek v5.3.9_28540.20180627, aircrack-ng/rtl8188eus 고정 커밋.
- NX4D1 초기화 경로 계측 소스를 포함합니다. 모듈의 실제 차량 로딩 및 Wi-Fi 통신은 검증하지 않았습니다.
- 실행 스크립트에는 USB 기반의 진단·복원 흐름이 포함됩니다. 차량에서의 동작은 검증되지 않았습니다.
- 이번 공개본은 **소스 전용**입니다. `.ko`, 제조사 분할 압축, 툴체인, NEMESIS.data, 실차 수집 로그는 포함하지 않습니다. USB_READY는 소스 템플릿이며 바로 실행할 완성 USB 키트가 아닙니다.

## 구성

| 경로 | 내용 |
|---|---|
| driver-src/ | 포팅 및 NX4D1 계측이 적용된 전체 드라이버 소스 |
| patches/ | cfg80211 포팅, 진단 계측, 차량 셸 수정 패치 |
| scripts/ | 커널 준비, ARM 빌드, ABI/심볼 비교 도구 |
| vehicle/, USB_READY/ | NEMESIS 실행용 자체 진단 스크립트 |
| tests/ | 차량 명령을 모의 처리하는 호스트 시험 |
| SOURCES.md | 원본 URL, 고정 커밋, 입력 해시 |
| LICENSE, LICENSE_SCOPE.md | GPL v2 전문 및 적용 범위 |
| CHANGES.md | 수정 내역 및 날짜 |

## 빌드와 시험

제조사 R6 분할 소스와 대상 시스템의 커널 `.config`를 별도로 확보해야 합니다. 차량별 설정 파일은 공개 저장소에 포함하지 않습니다. 두 빌드 스크립트 모두 `VEHICLE_KERNEL_CONFIG=/path/to/.config` 환경 변수를 지정해 실행하세요. 현재 `driver-src/`에는 패치가 이미 적용되어 있으므로 패치를 중복 적용하지 마세요.

호스트 모의시험:

```sh
python3 tests/test_vehicle_scripts.py
```

USB_READY는 소스 템플릿이며, 직접 빌드한 진단 모듈과 사용자가 별도로 보관한 원본 모듈이 필요합니다.

차량별 설정·빌드 로그·진단 결과 파일은 공개 저장소에 포함하지 않았습니다. 이 저장소의 코드로 실제 차량 동작을 보증하지 않습니다.

## 출처와 라이선스

드라이버의 GPL v2 고지와 기존 저작권 표시를 유지합니다. 이 프로젝트의 추가 코드·스크립트·문서도 GPL-2.0-only로 제공합니다. 개별 파일의 기존 별도 고지는 그대로 적용됩니다. [출처](SOURCES.md)와 [범위](LICENSE_SCOPE.md)를 참조하세요.

## GitHub 게시

이 프로젝트는 [EGG-RAMYON/nx4-rtl8188eu-kmod](https://github.com/EGG-RAMYON/nx4-rtl8188eu-kmod)에 공개됩니다. [게시 정보](PUBLISH.md)와 함께 원본 출처 및 라이선스 범위를 확인하세요.
