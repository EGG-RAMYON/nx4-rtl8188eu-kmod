# 실차 검증 및 바이너리 추적성

이 문서는 사용자 제공 실차 결과를 단계별로 기록하고, 별도 모듈 패키지의 정적 식별 정보와 구분합니다. 원시 차량 로그와 개인 네트워크 정보는 공개하지 않습니다.

## 시험 환경

| 항목 | 구성 |
|---|---|
| 차량 / 헤드유닛 | Hyundai Tucson NX4 HEV / AVNT STD G50 WIDE R6 |
| Device | `wp_daudioplus_nx4hev_kr` |
| 커널 / 아키텍처 / Android | Linux `3.18.24-tcc` / ARMv7 / Android 4.4.2 |
| USB Wi-Fi | ipTIME N150L / RTL8188EU / VID:PID `0bda:8179` |
| 드라이버 기반 / 진단 마커 | Realtek `5.3.9_28540.20180627` / `NX4D1_20261104` |
| NEMESIS | v1.16.7 |

## 검증 단계

아래 단계는 사용자가 제공한 동일 실차 시험 결과로 보고되었습니다. 공개 문서에는 SSID, MAC, 사설 IP, gateway, VIN, 원시 로그를 넣지 않았습니다.

| 단계 | 상태 | 보고된 확인 |
|---|---|---|
| Module Loaded | 성공 | `insmod r8188eu.ko nx4_diag=1` 반환값 0, `/proc/modules`에 `r8188eu` |
| USB Enumerated | 성공 | RTL8188EU USB ID `0bda:8179` 인식 |
| `wlan0` Created | 성공 | `wlan0` 생성 및 활성화 |
| Link Up | 성공 | `operstate=up`, `carrier=1`; 링크 품질·신호 지표 확인 |
| DHCP | 성공 | `dhcpcd` 실행 및 주소 할당 |
| Internet | 성공 | 숫자 IP 대상 ping, DNS 이름 조회 후 ping; route lookup은 외부 목적지에 대해 `wlan0`를 선택 |
| Wireless ADB | 성공 | TCP 5555 연결, PC의 `adb connect` 후 `device` 상태 및 셸 실행 |

이 결과는 한 차례의 특정 실차 구성 성공으로 기록합니다. 반복성, 다른 네트워크·차량·헤드유닛 조합, 장시간 안정성은 이 표로 입증되지 않습니다.

## Android Auto 프로젝션 상호작용

앞선 시도에서 Android Auto 패키지 `com.google.android.projection.sink`가 활성화된 상태로 USB accessory control request `0x33` / `0x34` / `0x35` 및 `EPROTO -71`가 관찰됐습니다. 패키지를 `pm disable`로 비활성화한 다음 Wi-Fi 연결과 네트워크 통신이 성공한 것이 보고됐습니다.

이는 강한 실험적 연관성입니다. USB 오류의 정확한 발생 계층, Android Auto와의 인과 관계, 공존 가능 여부는 아직 규명되지 않았습니다. 별도 추적: [Integration issue #1](https://github.com/EGG-RAMYON/nx4-rtl8188eu-kmod/issues/1).

## NEMESIS 서비스 상태

Wi-Fi/IP 통신이 성공한 뒤에도 v1.0.3 서비스에서 약 10초 간격으로 `WLAN_UP_ATTEMPT`와 `WLAN_UP_RC=0`가 반복된 것으로 보고됐습니다. 과거 서비스 코드의 `ifconfig wlan0 | grep 'UP '` 조건이 차량의 출력 형식과 불일치해, 이미 활성화된 인터페이스에 다시 up 요청을 했을 가능성이 있습니다. 로그 디렉터리를 쓰기 전에 만드는 순서 문제도 관찰됐습니다.

이 내용은 서비스 상태 판별 및 초기화 문제로 추적하며, 커널 모듈이 무선 연결에 실패했다는 증거로 분류하지 않습니다. v1.0.3 STOP 시 Android Auto 복원은 실차에서 확인됐지만 모든 서비스 수명주기 경로는 확인되지 않았습니다. 별도 추적: [NEMESIS issue #2](https://github.com/EGG-RAMYON/nx4-rtl8188eu-kmod/issues/2).

## 성공 바이너리와 공개 소스의 추적성

2026-11-05 확인 시 GitHub 저장소에는 Release가 없고 첨부된 Release 바이너리도 없습니다. 따라서 “Release 바이너리 = 실차 성공 바이너리”인지 비교할 대상이 아직 없습니다.

| 대상 | 확인된 식별 정보 | 결론 |
|---|---|---|
| NEMESIS v1.0.3 Library 패키지의 `modules/r8188eu.ko` 후보 | 패키지 SHA-256 `0b3d46d7374377075417f8ce9eb22e48645b48559497ca05b47e59d19ef47f08`; 모듈 SHA-256 `0365d9267aa5c1d4c587646bbc354e047f51e9f78424dd4e54e2bbb78e342c02`; Build ID `78d1271e7bde864b2489040a0083d465f19c76c2`; srcversion `5543A85AAE96D4241B7D1F0`; marker `NX4D1_20261104`; vermagic `3.18.24-tcc SMP preempt mod_unload ARMv7 p2v8` | NX4 대상 ABI 및 진단 마커와 일치하는 패키지 후보. 실차 성공 모듈의 hash와 같은지 확인할 기록이 없어 성공 바이너리와 동일하다고 할 수 없음 |
| 이전 load-only preflight 모듈 | SHA-256 `cfc5d76e124a647d983c0de941a37e0dd0b59cdd2a3cb9353c078aecf379b408`; srcversion `1872C91590829C51245CD94`; NX4 진단 마커 없음 | `insmod`만 성공한 별도 바이너리. Wi-Fi 성공 모듈 또는 v1.0.3 후보로 간주하지 않음 |
| 현재 공개 소스 | `main`의 `driver-src/include/nx4_diag.h`에 동일한 진단 마커 문자열 | 마커 문자열만으로 바이너리 동일성이나 재현 빌드를 증명하지 못함 |
| GitHub Release | 2026-11-05 조회 결과 없음 | 공개 Release 바이너리와의 비교 불가 |

### 추적성 결론

v1.0.3 패키지 후보에는 사용자가 보고한 시험 환경과 일치하는 진단 마커, USB ID 및 vermagic이 있습니다. 하지만 테스트 직후 저장한 성공 `.ko` 자체의 SHA-256이나, 그 모듈을 만드는 빌드 기록이 현재 확인되지 않았습니다. 따라서 marker와 ABI 일치는 정황 증거일 뿐, byte-for-byte 동일성 또는 현재 공개 소스에서 나온 재현 빌드의 증명이 아닙니다. 후보 모듈을 실차 성공 Release asset으로 올리거나 그렇게 표시하지 않습니다.

확정하려면 성공 시험에 사용한 모듈 파일의 SHA-256을 확보한 뒤 v1.0.3 후보와 비교하거나, 공개 저장소의 특정 commit에서 NX4 R6 설정·고정 툴체인으로 새로 빌드하고 build manifest / module SHA-256을 보존해야 합니다. 설정 및 원시 로그는 비공개로 두고, Release에는 모듈·manifest·checksum만 포함합니다.