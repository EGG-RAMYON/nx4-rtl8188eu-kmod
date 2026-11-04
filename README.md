# NX4 Gen5W RTL8188EU diagnostics

현대 투싼 NX4 HEV Gen5W의 RTL8188EU USB Wi-Fi 초기화 실패를 조사하는 **실험용 소스 공개 프로젝트**입니다. 현대자동차·현대모비스·Realtek의 공식 프로젝트가 아닙니다.

## 현재 상태

- 대상: Linux 3.18.24-tcc / ARMv7 / Android 4.4.2, ipTIME N150L (`0bda:8179`).
- 기반 드라이버: Realtek v5.3.9_28540.20180627, aircrack-ng/rtl8188eus 고정 커밋.
- 기존 모듈: 실차 insmod·바인딩·wlan0 생성 성공이 보고됐으나 `ifconfig wlan0 up`은 EPERM으로 실패합니다.
- NX4D1 진단 모듈: 이전 ARM 교차 빌드와 정적 검증 기록을 포함합니다. 실차 로딩 및 Wi-Fi 통신 성공은 확인하지 않았습니다.
- 실행 스크립트: R2 차량 실행은 동작 선택 전에 실패했습니다. 포함된 R3는 tr 의존성을 제거했으며, 실차 재시험이 필요합니다.
- 이번 공개본은 **소스 전용**입니다. `.ko`, 제조사 분할 압축, 툴체인, NEMESIS.data, 실차 수집 로그는 포함하지 않습니다. USB_READY는 소스 템플릿이며 바로 실행할 완성 USB 키트가 아닙니다.

## 구성

| 경로 | 내용 |
|---|---|
| driver-src/ | 포팅 및 NX4D1 계측이 적용된 전체 드라이버 소스 |
| patches/ | cfg80211 포팅, 진단 계측, 차량 셸 수정 패치 |
| scripts/ | 커널 준비, ARM 빌드, ABI/심볼 비교 도구 |
| vehicle/, USB_READY/ | NEMESIS 실행용 자체 진단 스크립트 |
| inputs/ | 기존 차량 커널 설정 |
| tests/ | 차량 명령을 모의 처리하는 호스트 시험 |
| evidence/ | 이전 빌드·정적 검사 및 호스트 모의시험 기록 |
| SOURCES.md | 원본 URL, 고정 커밋, 입력 해시 |
| LICENSE, LICENSE_SCOPE.md | GPL v2 전문 및 적용 범위 |
| README_KO.md | 기존 상세 기술 보고서. 바이너리 경로는 원래 키트 기준 |
| CHANGES.md | 수정 내역 및 날짜 |

## 빌드와 시험

[상세 빌드 방법](README_KO.md#빌드-재현)에 따라 제조사 R6 분할 소스를 별도로 확보하고 `scripts/prepare_kernel.sh`, `scripts/build.sh`를 실행합니다. 입력 체크섬이 다르면 중단합니다. 현재 driver-src에 패치를 중복 적용하지 마세요.

호스트 모의시험:

```sh
python3 tests/test_vehicle_scripts.py
```

차량 적용은 [시험 절차](VEHICLE_TEST_KO.md)와 [R3 수정](SCRIPT_FIX_R3_KO.md)을 함께 확인하세요. USB_READY 사용에는 직접 빌드한 진단 모듈 및 별도로 보존한 기존 모듈이 각각 필요합니다. 이 저장소는 기존 정상 로드 모듈을 대체 제공하지 않습니다.

검증 기록의 구조체 19개·멤버 661개, 설정 매크로 1,122개, 외부 참조 심볼 187개 비교 결과는 확보한 소스/설정 기준입니다. 실제 차량 커널 전체 ABI나 무선 동작의 보증이 아닙니다. 이번 공개 준비에서는 ARM 모듈을 다시 컴파일하지 않았습니다.

## 출처와 라이선스

드라이버의 GPL v2 고지와 기존 저작권 표시를 유지합니다. 이 프로젝트의 추가 코드·스크립트·문서도 GPL-2.0-only로 제공합니다. 개별 파일의 기존 별도 고지는 그대로 적용됩니다. [출처](SOURCES.md)와 [범위](LICENSE_SCOPE.md)를 참조하세요.

## GitHub 게시

이 프로젝트는 [EGG-RAMYON/nx4-rtl8188eu-kmod](https://github.com/EGG-RAMYON/nx4-rtl8188eu-kmod)에 공개됩니다. [게시 정보](PUBLISH.md)와 함께 원본 출처 및 라이선스 범위를 확인하세요.
