#!/system/bin/sh
# NX4 diagnostic launcher; ARM -> USB/dongle swap -> COLLECT. No bcmdhd or system edits.
umask 077
USB=${NX4_USB_ROOT:-/storage/usb0}
BASE=${NX4_BASE_ROOT:-/data/local/tmp/nx4_r8188eu_diag}
SYS=${NX4_SYS_ROOT:-/sys}
PROC=${NX4_PROC_ROOT:-/proc}
SHELLBIN=${NX4_SHELL:-/system/bin/sh}
PAYLOAD=$USB/NX4_DIAG
mkdir -p "$BASE" || exit 1
LAUNCH=$USB/NX4_DIAG_LAUNCH.txt
exec > "$LAUNCH" 2>&1
echo 'NX4D1 launcher script_revision=3'
ACTION_FILE=$USB/NX4_DIAG_ACTION.txt
if [ ! -f "$ACTION_FILE" ]; then
    echo "STOP: ACTION_FILE_MISSING $ACTION_FILE"
    echo 'Copy NX4_DIAG_ACTION.txt from USB_READY to the USB root.'
    exit 1
fi
if [ ! -r "$ACTION_FILE" ]; then
    echo "STOP: ACTION_FILE_UNREADABLE $ACTION_FILE"
    exit 1
fi
ACTION=
IFS= read -r ACTION < "$ACTION_FILE"
# Literal CR and UTF-8 BOM: no external text-processing commands needed.
CR=''
BOM='﻿'
ACTION=${ACTION%"$CR"}
ACTION=${ACTION#"$BOM"}
echo "action=[$ACTION]"
case "$ACTION" in
    ARM|COLLECT|RESTORE) ;;
    *) echo 'STOP: ACTION_FILE_INVALID_OR_EMPTY; first line must be ARM, COLLECT, or RESTORE'; exit 1;;
esac
date
# Android toolbox id may not implement -u. Inspect the exact plain-id UID field.
ID_TEXT=$(id 2>&1)
echo "$ID_TEXT"
case "${ID_TEXT%% *}" in
    uid=0|uid=0\(*) ;;
    *) echo 'STOP: root required (plain id did not confirm uid=0)'; exit 1;;
esac
SESSION=
if [ -f "$BASE/current" ]; then
    NAME=$(cat "$BASE/current")
    case "$NAME" in session_[0-9]* ) SESSION=$BASE/$NAME;; *) echo 'STOP: invalid session pointer'; exit 1;; esac
    case "$NAME" in *[!a-zA-Z0-9_]* ) echo 'STOP: invalid session name'; exit 1;; esac
fi
bound_realtek() {
    for N in "$SYS"/class/net/*; do
        M=$(readlink "$N/device/driver/module" 2>/dev/null)
        [ "${M##*/}" = r8188eu ] && return 0
    done
    return 1
}
active_session() {
    [ -n "$SESSION" ] && [ -f "$SESSION/status" ] || return 1
    OLD_BOOT=$(cat "$SESSION/boot_id.txt" 2>/dev/null)
    NOW_BOOT=$(cat "$PROC/sys/kernel/random/boot_id" 2>/dev/null)
    [ -n "$OLD_BOOT" ] && [ -n "$NOW_BOOT" ] && [ "$OLD_BOOT" != "$NOW_BOOT" ] && return 1
    S=$(cat "$SESSION/status")
    case "$S" in
        WAIT_DONGLE|BOUND*|UP_RUNNING*|UP_TIMEOUT*) return 0;;
    esac
    return 1
}
case "$ACTION" in
COLLECT)
    [ -n "$SESSION" ] && [ -d "$SESSION" ] || { echo 'No session'; exit 1; }
    DEST=$USB/NX4_DIAG_RESULTS/${SESSION##*/}
    mkdir -p "$DEST" || exit 1
    # Repeat COLLECT safely if worker is still running; never mark partial logs complete.
    for F in "$SESSION"/*.txt "$SESSION"/*.log "$SESSION"/*.stdout "$SESSION"/*.pid "$SESSION"/status "$SESSION"/up.exit "$SESSION"/worker_started; do
        [ -f "$F" ] || continue
        cp "$F" "$DEST/" || { echo "COPY_FAILED $F"; exit 1; }
    done
    cat "$SESSION/status" > "$DEST/collection_status.txt"
    dmesg > "$DEST/dmesg_at_collect.txt" 2>&1
    cat "$PROC/modules" > "$DEST/modules_at_collect.txt"
    echo "Collected: $DEST"
    cat "$DEST/collection_status.txt"
    wc -c "$DEST"/*
    sync
    ;;
ARM)
    active_session && { echo 'STOP: previous session active or ioctl timed out. Collect first; do not force unload.'; exit 1; }
    [ "$(uname -r)" = 3.18.24-tcc ] || { echo 'STOP: wrong kernel'; exit 1; }
    bound_realtek && { echo 'STOP: remove Realtek dongle before ARM'; exit 1; }
    for C in readlink cmp insmod rmmod ifconfig dmesg; do
        command -v "$C" >/dev/null 2>&1 || { echo "STOP: missing $C"; exit 1; }
    done
    for F in diagnostic/r8188eu.ko baseline/r8188eu.ko worker.sh; do
        [ -s "$PAYLOAD/$F" ] || { echo "STOP: missing $PAYLOAD/$F"; exit 1; }
    done
    NAME=session_$(date +%Y%m%d_%H%M%S)_$$
    SESSION=$BASE/$NAME
    mkdir "$SESSION" || exit 1
    cp "$PAYLOAD/diagnostic/r8188eu.ko" "$SESSION/diagnostic.ko" || exit 1
    cp "$PAYLOAD/baseline/r8188eu.ko" "$SESSION/baseline.ko" || exit 1
    cp "$PAYLOAD/worker.sh" "$SESSION/worker.sh" || exit 1
    cmp "$PAYLOAD/diagnostic/r8188eu.ko" "$SESSION/diagnostic.ko" || exit 1
    cmp "$PAYLOAD/baseline/r8188eu.ko" "$SESSION/baseline.ko" || exit 1
    cat "$PROC/sys/kernel/random/boot_id" > "$SESSION/boot_id.txt" 2>/dev/null
    cat "$PROC/modules" > "$SESSION/modules_before.txt"
    for F in "$SYS/module/r8188eu/parameters/"*; do
        [ -f "$F" ] || continue
        echo "PARAMETER ${F##*/}" >> "$SESSION/original_parameters.txt"
        cat "$F" >> "$SESSION/original_parameters.txt"
    done
    dmesg > "$SESSION/dmesg_before_load.txt" 2>&1
    echo "$NAME" > "$BASE/current.tmp"; mv "$BASE/current.tmp" "$BASE/current"
    if grep -q '^r8188eu ' "$PROC/modules"; then
        rmmod r8188eu > "$SESSION/unload.txt" 2>&1 || { echo 'UNLOAD_FAILED' > "$SESSION/status"; cat "$SESSION/unload.txt"; exit 1; }
    fi
    insmod "$SESSION/diagnostic.ko" nx4_diag=1 > "$SESSION/insmod.txt" 2>&1
    RC=$?; echo "INSMOD_RC=$RC" >> "$SESSION/insmod.txt"
    dmesg > "$SESSION/dmesg_after_load.txt" 2>&1
    if [ "$RC" -ne 0 ]; then
        echo LOAD_FAILED > "$SESSION/status"
        echo COLLECT > "$USB/NX4_DIAG_ACTION.txt"
        cat "$SESSION/insmod.txt"; exit 1
    fi
    ID=$(cat "$SYS/module/r8188eu/parameters/nx4_diag_id" 2>/dev/null)
    [ "$ID" = NX4D1_20261104 ] || { echo WRONG_MODULE > "$SESSION/status"; exit 1; }
    echo COLLECT > "$USB/NX4_DIAG_ACTION.txt"
    # Both the worker's code, cwd and output remain off removable storage.
    (trap '' HUP; cd "$SESSION" || exit 1; exec "$SHELLBIN" "$SESSION/worker.sh" "$SESSION") </dev/null > "$SESSION/worker.stdout" 2>&1 &
    PID=$!
    N=0
    while [ ! -f "$SESSION/worker_started" ] && [ "$N" -lt 5 ]; do sleep 1; N=$((N + 1)); done
    if [ ! -f "$SESSION/worker_started" ] || ! kill -0 "$PID" 2>/dev/null; then
        echo WORKER_START_FAILED > "$SESSION/status"; echo 'STOP: worker did not start'; exit 1
    fi
    echo "ARMED: worker=$PID session=$NAME"
    echo 'Swap USB memory for the Realtek dongle within 180 seconds; wait 60 seconds; reconnect memory for COLLECT.'
    sync
    ;;
RESTORE)
    active_session && { echo 'STOP: active/timed-out session; collect and resolve before restore'; exit 1; }
    bound_realtek && { echo 'STOP: remove dongle before RESTORE'; exit 1; }
    [ -n "$SESSION" ] && [ -s "$SESSION/baseline.ko" ] || { echo 'STOP: no preserved baseline'; exit 1; }
    if grep -q '^r8188eu ' "$PROC/modules"; then
        ID=$(cat "$SYS/module/r8188eu/parameters/nx4_diag_id" 2>/dev/null)
        [ "$ID" = NX4D1_20261104 ] || { echo 'STOP: currently loaded module is not this diagnostic build'; exit 1; }
        rmmod r8188eu || exit 1
    fi
    insmod "$SESSION/baseline.ko" > "$SESSION/restore.txt" 2>&1
    RC=$?; echo "RESTORE_RC=$RC" >> "$SESSION/restore.txt"
    cat "$SESSION/restore.txt"
    [ "$RC" -eq 0 ] && echo RESTORED_BASELINE_DEFAULT_PARAMS > "$SESSION/status"
    echo COLLECT > "$USB/NX4_DIAG_ACTION.txt"
    sync
    exit "$RC"
    ;;
*) echo 'Set NX4_DIAG_ACTION.txt to ARM, COLLECT, or RESTORE'; exit 1;;
esac
