#!/usr/bin/env bash
# Usage: VEHICLE_KERNEL_CONFIG=/path/to/.config bash build.sh KERNEL_TREE KERNEL_OUT CROSS_PREFIX NEW_BUILD_DIR
# Does not install or load modules. Kernel output must be prepared with supplied vehicle config.
set -euo pipefail
KIT=$(cd "$(dirname "$0")/.." && pwd)
TREE=$(realpath "${1:?kernel source required}")
OUT=$(realpath "${2:?prepared output required}")
CROSS=${3:?ARM GCC 4.7 prefix required}
BUILD=${4:?new build directory required}
CONFIG_SOURCE=$(realpath "${VEHICLE_KERNEL_CONFIG:?Set VEHICLE_KERNEL_CONFIG to a local kernel .config}")
[ -f "$CONFIG_SOURCE" ] || { echo "Kernel config not found: $CONFIG_SOURCE" >&2; exit 2; }
mkdir -p "$BUILD"
BUILD=$(cd "$BUILD" && pwd)
[ ! -e "$BUILD/driver" ] || { echo 'Use a new build directory'; exit 2; }
cp "$CONFIG_SOURCE" "$BUILD/vehicle.config"
cmp "$BUILD/vehicle.config" "$OUT/.config"
if grep -Eq '^#define CONFIG_(WIRELESS_EXT|WEXT_PRIV) ' "$OUT/include/generated/autoconf.h"; then
 echo 'Incompatible generated config'; exit 2
fi
cp -a "$KIT/driver-src" "$BUILD/driver"
export KBUILD_BUILD_USER=nx4 KBUILD_BUILD_HOST=off-vehicle
export KBUILD_BUILD_TIMESTAMP='Tue Nov 3 00:00:00 UTC 2026'
export KBUILD_BUILD_VERSION=1
make -C "$TREE" O="$OUT" ARCH=arm CROSS_COMPILE="$CROSS" HOSTCC='gcc -fcommon' \
 M="$BUILD/driver" CONFIG_RTL8188EU=m CONFIG_PLATFORM_I386_PC=n USER_MODULE_NAME=r8188eu \
 USER_EXTRA_CFLAGS='-DCONFIG_LITTLE_ENDIAN -DCONFIG_IOCTL_CFG80211 -DRTW_USE_CFG80211_STA_EVENT -Werror' \
 CONFIG_MP_INCLUDED=n CONFIG_WIFI_MONITOR=n CONFIG_BR_EXT=n \
 CONFIG_LOAD_PHY_PARA_FROM_FILE=n CONFIG_EFUSE_CONFIG_FILE=n -j4 modules 2>&1 | tee "$BUILD/build.log"
cmp "$BUILD/vehicle.config" "$OUT/.config"
cp "$BUILD/driver/r8188eu.ko" "$BUILD/r8188eu.ko"
"${CROSS}readelf" -h -A -p .modinfo "$BUILD/r8188eu.ko" > "$BUILD/module_info.txt"
"${CROSS}nm" -u "$BUILD/r8188eu.ko" > "$BUILD/undefined_symbols.txt"
grep -q 'usb:v0BDAp8179' "$BUILD/module_info.txt"
grep -q '3.18.24-tcc SMP preempt mod_unload ARMv7 p2v8' "$BUILD/module_info.txt"
sha256sum "$BUILD/r8188eu.ko" > "$BUILD/module.sha256"
echo 'Cross-build complete with unchanged supplied vehicle config. Hardware compatibility remains untested.'
