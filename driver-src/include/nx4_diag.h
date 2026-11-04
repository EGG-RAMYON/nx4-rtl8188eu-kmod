/* NX4D1: diagnostic observations only; no additional device register reads. */
#ifndef NX4_DIAG_H
#define NX4_DIAG_H
extern int nx4_diag;
#define NX4_DIAG(fmt, ...) do { if (nx4_diag) \
 printk(KERN_NOTICE "NX4D1 %s:%d " fmt "\n", __func__, __LINE__, ##__VA_ARGS__); } while (0)
#endif

/* NX4 project modifications (2026-11-04): cfg80211 backport and/or NX4D1 diagnostics. See patches/ and CHANGES.md. Publication notice added 2026-11-05. */
