# NX4 R6 커널을 사용한 빌드

이 절차는 **NX4에서 추출한 커널 설정과 해당 차량용 R6 커널 소스**로 RTL8188EU 모듈을 교차 빌드합니다. 커널 소스와 설정은 공개 저장소에 포함되어 있지 않습니다. 필요한 권한을 가진 사용자가 별도로 준비하고, 개인 작업 디렉터리에서만 사용하세요.

## 입력 파일

- 사용자가 준비한 완전한 제조사 압축 파일 `$HOME/private/nx4/AVNT+STD+G50+WIDE+R6.zip`
- NX4 대상 시스템에서 확보한 정확한 `.config`
- Bash, Python 3, unzip, curl, git, tar, xz, make, GCC, bc, sha256sum, binutils

빌드 설정 파일은 커널 빌드 시 생성된 커널 설정이어야 합니다. 임의의 ARM defconfig나 호스트의 `/boot/config-$(uname -r)`로 대체하지 마세요. 설정은 공개 저장소에 커밋하지 마세요.

## 1. 커널 빌드 트리 준비

저장소 루트에서 실행합니다. 경로에 공백이 있어도 따옴표를 유지하세요.

```sh
export VEHICLE_KERNEL_CONFIG="$HOME/private/nx4/.config"
WORK="$HOME/build/nx4-r6"
mkdir -p "$WORK"

bash scripts/prepare_kernel.sh \
  "$HOME/private/nx4/AVNT+STD+G50+WIDE+R6.zip" \
  "$WORK"
```

스크립트는 완전한 R6 ZIP의 무결성(`unzip -tq`)을 검사하고 입력 파일의 SHA-256을 `$WORK/logs/R6_archive.sha256`에 기록한 뒤 Linux 3.18.24 커널 기반에 R6 커널 소스를 적용합니다. 사용자가 ZIP을 분할 업로드했더라도 먼저 원본 ZIP으로 복원한 파일 하나를 지정하면 됩니다. 현재 공개된 원본 ZIP의 고정 SHA-256은 없으므로 기록된 해시와 신뢰하는 원본의 해시를 비교하세요. 지정한 `.config`를 `$WORK/out/.config`로 복사한 뒤 `olddefconfig` 및 `modules_prepare`를 실행합니다. `olddefconfig` 후 설정이 한 줄이라도 달라지면 빌드를 중단합니다. 로그는 `$WORK/logs/` 아래에 남습니다.

처음 실행할 때 커널 기준 소스와 고정 커밋의 Android ARM GCC 4.7 툴체인을 다운로드합니다. 네트워크 접속이 되는 Linux 빌드 호스트에서 실행하세요. 준비가 끝나면 경로는 다음과 같습니다.

- 커널 소스: `$WORK/linux-3.18.24`
- 준비된 커널 출력: `$WORK/out`
- 크로스 컴파일러 prefix: `$WORK/cache/arm-linux-androideabi-4.7/bin/arm-linux-androideabi-`

## 2. RTL8188EU 모듈 빌드

```sh
BUILD="$WORK/r8188eu-build"
bash scripts/build.sh \
  "$WORK/linux-3.18.24" \
  "$WORK/out" \
  "$WORK/cache/arm-linux-androideabi-4.7/bin/arm-linux-androideabi-" \
  "$BUILD"
```

성공하면 `$BUILD/r8188eu.ko`와 다음 검증 파일이 생성됩니다.

- `module_info.txt`: ELF/ARM 정보, USB ID, vermagic
- `undefined_symbols.txt`: 커널 심볼 참조 목록
- `module.sha256`: 모듈 SHA-256
- `build.log`: 빌드 로그

스크립트는 USB ID `0bda:8179`, vermagic `3.18.24-tcc SMP preempt mod_unload ARMv7 p2v8`, 그리고 입력 `.config`의 무변경을 확인합니다. 빌드된 모듈을 차량에 설치하거나 로드하는 동작은 자동으로 하지 않습니다. 실제 장착·운영 전에는 원본 상태를 백업하고, 본인이 통제하는 시험 환경에서 확인하세요.

## 문제 해결

- `Set VEHICLE_KERNEL_CONFIG`: 환경 변수가 실제 `.config` 파일을 가리키는지 확인합니다.
- `vehicle config differs`: 실행 중 커널 설정을 수정하지 말고, 정확한 NX4 설정과 R6 소스 조합인지 확인합니다.
- ZIP 무결성/내부 경로 오류: 완전한 `AVNT+STD+G50+WIDE+R6.zip`인지, 손상되지 않았는지 확인하세요. `$WORK/logs/R6_archive.sha256`로 실행에 사용한 파일을 식별할 수 있습니다.
- GCC clone/커널 다운로드 실패: 네트워크가 허용된 Linux 빌드 호스트에서 다시 준비합니다.
- `invalid module format` 또는 unknown symbols: 실행 중인 차량 커널의 `uname -r`, 모듈 vermagic, 커널 ABI와 설정이 일치하는지 확인합니다.

빌드 결과의 USB ID·vermagic·SHA-256 검증은 목표 식별과 정적 ABI 정보를 확인하는 단계이며 실차 Wi-Fi 통신을 보증하지 않습니다. 성공 시험에 사용한 바이너리의 SHA-256과 빌드 기록을 별도로 대조하세요. 공개 설정·분할 커널 소스·원시 로그는 Release에 첨부하지 않습니다. 현재 실차 결과와 바이너리 추적성 상태는 [VALIDATION.md](VALIDATION.md)를 참조하세요.