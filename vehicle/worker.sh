#!/system/bin/sh
# Runs only from internal temporary storage. Only raises the verified RTL8188EU wlan interface.
trap '' HUP
umask 077
SESSION=$1
SYS=${NX4_SYS_ROOT:-/sys}
PROC=${NX4_PROC_ROOT:-/proc}
WAIT=${NX4_WAIT_SECONDS:-180}
[ -d "$SESSION" ] || exit 2
cd "$SESSION" || exit 2
status() { echo "$*" > status.tmp; mv status.tmp status; }
snapshot() {
    date
    cat "$PROC/modules"
    cat "$PROC/net/dev"
    [ -n "$IFACE" ] && {
        cat "$SYS/class/net/$IFACE/flags" "$SYS/class/net/$IFACE/operstate" 2>/dev/null
        ls -l "$SYS/class/net/$IFACE/device/driver" "$SYS/class/net/$IFACE/device/driver/module"
    }
}
find_iface() {
    FOUND=; COUNT=0
    for NETPATH in "$SYS"/class/net/wlan*; do
        [ -d "$NETPATH" ] || continue
        V=$(cat "$NETPATH/device/../idVendor" 2>/dev/null)
        P=$(cat "$NETPATH/device/../idProduct" 2>/dev/null)
        D=$(readlink "$NETPATH/device/driver" 2>/dev/null)
        M=$(readlink "$NETPATH/device/driver/module" 2>/dev/null)
        [ "$V:$P" = 0bda:8179 ] || continue
        [ "${D##*/}" = 8188eu ] || continue
        [ "${M##*/}" = r8188eu ] || continue
        FOUND=${NETPATH##*/}; COUNT=$((COUNT + 1))
    done
    [ "$COUNT" -eq 1 ]
}
echo $$ > worker.pid
echo WORKER_STARTED > worker_started
status WAIT_DONGLE
{ id; uname -a; cat "$PROC/self/status"; cat "$PROC/self/attr/current" 2>/dev/null; command -v getenforce >/dev/null && getenforce; } > environment.txt 2>&1
dmesg > dmesg_armed.txt 2>&1
N=0; IFACE=
while [ "$N" -lt "$WAIT" ]; do
    if find_iface; then IFACE=$FOUND; break; fi
    [ "$COUNT" -gt 1 ] && { status MULTIPLE_MATCHING_INTERFACES; exit 3; }
    sleep 1; N=$((N + 1))
done
if [ -z "$IFACE" ]; then
    status WAIT_DONGLE_TIMEOUT
    snapshot > timeout_snapshot.txt 2>&1
    dmesg > dmesg_after.txt 2>&1
    exit 4
fi
echo "$IFACE" > interface.txt
status BOUND "$IFACE"
snapshot > before_up.txt 2>&1
dmesg > dmesg_before_up.txt 2>&1
# Check the marker again immediately before the single test.
ID=$(cat "$SYS/module/r8188eu/parameters/nx4_diag_id" 2>/dev/null)
[ "$ID" = NX4D1_20261104 ] || { status WRONG_MODULE; exit 5; }
FLAGS=$(cat "$SYS/class/net/$IFACE/flags" 2>/dev/null)
case "$FLAGS" in 0x*|[0-9]*) ;; *) status INVALID_FLAGS; exit 5;; esac
if [ $((FLAGS & 1)) -ne 0 ]; then
    status ALREADY_UP_NO_TEST
    dmesg > dmesg_after.txt 2>&1
    exit 0
fi
status UP_RUNNING "$IFACE"
# Capture the child's result without depending on USB storage or logcat.
(
    date > up_result.txt
    ifconfig "$IFACE" up >> up_result.txt 2>&1 &
    IOCTLPID=$!
    echo "$IOCTLPID" > ifconfig.pid
    wait "$IOCTLPID"
    RC=$?
    echo "IFCONFIG_RC=$RC" >> up_result.txt
    echo "$RC" > up.exit.tmp
    mv up.exit.tmp up.exit
) </dev/null > up_worker.stdout 2>&1 &
UPPID=$!
echo "$UPPID" > up_worker.pid
N=0
while [ ! -f up.exit ] && [ "$N" -lt 30 ]; do
    sleep 1; N=$((N + 1))
done
if [ ! -f up.exit ]; then
    # Do not force-unload a module or kill an ioctl blocked in kernel space.
    status UP_TIMEOUT_CHILD_MAY_REMAIN "$UPPID"
    cat "$PROC/$UPPID/status" > up_timeout_process.txt 2>&1
    IOCTLPID=$(cat ifconfig.pid 2>/dev/null)
    [ -n "$IOCTLPID" ] && cat "$PROC/$IOCTLPID/status" > ifconfig_timeout_process.txt 2>&1
    snapshot > after_up.txt 2>&1
    dmesg > dmesg_after.txt 2>&1
    exit 6
fi
wait "$UPPID"
snapshot > after_up.txt 2>&1
dmesg > dmesg_after.txt 2>&1
sleep 5
snapshot > after_5s.txt 2>&1
dmesg > dmesg_after_5s.txt 2>&1
grep NX4D1 dmesg_after_5s.txt > diagnostic_markers.txt
RC=$(cat up.exit)
status COMPLETE "IFCONFIG_RC=$RC"
sync
