#!/usr/bin/env bash
# OFF-VEHICLE ONLY: reconstruct R6 kernel build tree with unchanged vehicle config.
# Usage: VEHICLE_KERNEL_CONFIG=/path/to/.config bash prepare_kernel.sh R6_ARCHIVE.zip NEW_WORKDIR [CACHE_DIR]
# Requirements: bash, python3, unzip, curl, git, tar, xz, make, gcc, bc, binutils.
set -euo pipefail
KIT=$(cd "$(dirname "$0")/.." && pwd)
R6=$(realpath "${1:?full AVNT+STD+G50+WIDE+R6.zip required}")
WORK=${2:?new work directory required}
CONFIG_SOURCE=$(realpath "${VEHICLE_KERNEL_CONFIG:?Set VEHICLE_KERNEL_CONFIG to a local kernel .config}")
[ -f "$CONFIG_SOURCE" ] || { echo "Kernel config not found: $CONFIG_SOURCE" >&2; exit 2; }
mkdir -p "$WORK"
WORK=$(cd "$WORK" && pwd)
if [ -e "$WORK/STARTED" ]; then echo 'Use a new work directory; previous evidence is preserved.' >&2; exit 2; fi
touch "$WORK/STARTED"
CACHE=${3:-$WORK/cache}
mkdir -p "$CACHE"
CACHE=$(cd "$CACHE" && pwd)
for cmd in python3 unzip curl git tar xz make gcc bc sha256sum; do command -v "$cmd" >/dev/null; done
check() { printf '%s  %s\n' "$1" "$2" | sha256sum -c -; }
unzip -tq "$R6" >/dev/null

KERNEL="$CACHE/linux-3.18.24.tar.xz"
if [ ! -f "$KERNEL" ]; then
 curl -fL --retry 3 https://cdn.kernel.org/pub/linux/kernel/v3.x/linux-3.18.24.tar.xz -o "$KERNEL"
fi
check ed54cf8c3ac6b95fc17b07b3a236bc42719c96fee08fe696cabfb5b8e07f8c1b "$KERNEL"
TOOL="$CACHE/arm-linux-androideabi-4.7"
COMMIT=a1e239a0bb5cd1d69680bf1075883aa9a7bf2429
if [ ! -d "$TOOL" ]; then
 git clone --depth=1 --branch android-4.4.2_r1.0.1 https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/arm/arm-linux-androideabi-4.7 "$TOOL"
fi
test "$(git -C "$TOOL" rev-parse HEAD)" = "$COMMIT"
test -z "$(git -C "$TOOL" status --porcelain --untracked-files=no)"
CROSS="$TOOL/bin/arm-linux-androideabi-"
"${CROSS}gcc" --version
mkdir -p "$WORK/logs" "$WORK/results/experimental"
sha256sum "$R6" > "$WORK/logs/R6_archive.sha256"
unzip -q "$R6" 'AVNT+STD+G50+WIDE+R6/AVNT5W_TCC803XKK_kernel/*' -d "$WORK/vendor"
VENDOR="$WORK/vendor/AVNT+STD+G50+WIDE+R6/AVNT5W_TCC803XKK_kernel"
tar -xJf "$KERNEL" -C "$WORK"
TREE="$WORK/linux-3.18.24"
cp -a "$VENDOR/." "$TREE/"
cp "$CONFIG_SOURCE" "$WORK/results/vehicle.config"
export KBUILD_BUILD_USER=nx4-research KBUILD_BUILD_HOST=off-vehicle
export KBUILD_BUILD_TIMESTAMP='Tue Nov 3 00:00:00 UTC 2026'
export KBUILD_BUILD_VERSION=1
kmake() { make -C "$TREE" O="$OUT" ARCH=arm CROSS_COMPILE="$CROSS" HOSTCC='gcc -fcommon' "$@"; }
OUT="$WORK/out"
mkdir -p "$OUT"
cp "$WORK/results/vehicle.config" "$OUT/.config"
kmake olddefconfig > "$WORK/logs/config.log" 2>&1
cmp "$WORK/results/vehicle.config" "$OUT/.config"
kmake -j4 prepare modules_prepare > "$WORK/logs/prepare.log" 2>&1
printf 'Kernel tree: %s\nKernel output: %s\nCross prefix: %s\n' "$TREE" "$OUT" "$CROSS"
