#ifdef NX4_DRIVER_CONTEXT
#include <drv_types.h>
#endif
#include <linux/netdevice.h>
#include <linux/usb.h>
#include <net/cfg80211.h>
#include <net/iw_handler.h>
struct net_device nx4_net_device;
struct net_device_ops nx4_net_device_ops;
struct wireless_dev nx4_wireless_dev;
struct wiphy nx4_wiphy;
struct cfg80211_ops nx4_cfg80211_ops;
struct cfg80211_scan_request nx4_scan;
struct cfg80211_connect_params nx4_connect;
struct station_info nx4_station;
struct ieee80211_channel nx4_channel;
struct ieee80211_supported_band nx4_band;
struct usb_driver nx4_usb_driver;
struct usb_device nx4_usb_device;
struct usb_interface nx4_usb_interface;
struct urb nx4_urb;
struct sk_buff nx4_skb;
struct device nx4_device;
struct work_struct nx4_work;
struct timer_list nx4_timer;
struct iw_handler_def nx4_iw_handlers;
