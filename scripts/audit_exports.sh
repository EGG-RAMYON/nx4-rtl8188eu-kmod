#!/usr/bin/env bash
# Usage: bash audit_exports.sh TREE OUT CROSS MODULE_KO REPORT_JSON
set -euo pipefail
TREE=$(realpath "${1:?}"); OUT=$(realpath "${2:?}"); CROSS=${3:?}; KO=$(realpath "${4:?}"); REPORT=${5:?}
SCRIPTS=$(cd "$(dirname "$0")" && pwd)
make -C "$TREE" O="$OUT" ARCH=arm CROSS_COMPILE="$CROSS" HOSTCC='gcc -fcommon' -j4 \
 net/wireless/ kernel/ lib/ mm/ net/core/ net/ipv4/ net/ipv6/ fs/proc/ \
 drivers/usb/core/ drivers/base/power/ arch/arm/lib/ \
 arch/arm/kernel/armksyms.o arch/arm/kernel/process.o net/ethernet/eth.o \
 net/sched/sch_generic.o fs/open.o fs/seq_file.o
python3 "$SCRIPTS/check_exports.py" "$KO" "$OUT" "${CROSS}nm" "$REPORT"
python3 - "$REPORT" <<'PY'
import json,sys
r=json.load(open(sys.argv[1])); assert not r['unverified'], r['unverified']
PY
