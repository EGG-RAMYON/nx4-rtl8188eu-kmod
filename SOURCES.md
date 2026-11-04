# Original sources / 원본 출처

| 구성요소 | 원본 및 고정 기준 | 포함 여부 |
|---|---|---|
| RTL8188EU 드라이버 | https://github.com/aircrack-ng/rtl8188eus | 수정된 소스 포함 |
| 드라이버 고정 커밋 | https://github.com/aircrack-ng/rtl8188eus/tree/af3bf004458f76b7aec33e9ba552cd382ed1f5c3 | 기존 빌드 기록 기준 |
| 현대모비스 공개 소스 | https://www.mobis.com/opensource/list.do | 별도 다운로드 |
| 현대모비스 R&D 오픈소스 안내 | https://www.mobis.com/kr/tech/rnd.do | 안내 링크 |
| Linux 3.18.24 | https://cdn.kernel.org/pub/linux/kernel/v3.x/linux-3.18.24.tar.xz | 빌드 시 다운로드 |
| Android ARM GCC 4.7 | https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/arm/arm-linux-androideabi-4.7 | 별도 다운로드 |
| GCC 고정 커밋 | https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/arm/arm-linux-androideabi-4.7/+/a1e239a0bb5cd1d69680bf1075883aa9a7bf2429 | android-4.4.2_r1.0.1 태그 및 커밋 검사 |
| NEMESIS | https://github.com/xwtk/hmg_nemesis | 실행 환경의 출처만 표기; 해당 프로젝트 코드/페이로드 미포함 |
| GPL v2 공식 전문 | https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html | LICENSE에 전문 포함 |

드라이버 원저작자는 Realtek Corporation이며 aircrack-ng 및 파일에 기재된 기여자의 고지를 유지합니다. vehicle/NEMESIS.sh는 이 진단 작업의 실행 스크립트이며 NEMESIS 원본 전체나 공식 배포본이 아닙니다.

제조사 자료명: `AVNT+STD+G50+WIDE+R6.zip.001`, `.002`; 내부 커널 경로: `AVNT+STD+G50+WIDE+R6/AVNT5W_TCC803XKK_kernel`.
제조사 포털은 확인했지만 해당 R6 자료의 현재 직접 다운로드 URL은 확인하지 못했습니다. 다른 릴리스로 대체하지 마세요.

## 재현 입력 SHA-256

```text
b9d4a7e3121b5429943bced5108e97077bf4850b95eb3fb436ae11aaac87329a  AVNT+STD+G50+WIDE+R6.zip.001
a0bb839d526331d76bd2ba657bc943a585ff75bcf11b732aebe72c4bc6e9e806  AVNT+STD+G50+WIDE+R6.zip.002
ed54cf8c3ac6b95fc17b07b3a236bc42719c96fee08fe696cabfb5b8e07f8c1b  linux-3.18.24.tar.xz
```

해시는 기존 빌드 스크립트에 기록된 값입니다. 이번 공개 준비에서 제조사 압축 전체를 다시 다운로드·검증하지 않았습니다. 커널 트리는 Linux 3.18.24 위에 R6 소스를 덮어써 누락된 빌드 시스템을 복원합니다. 차량 펌웨어 전체와 동일한 트리라는 의미는 아닙니다.
