import dbus
import NetworkManager as NM


for dev in NM.NetworkManager.GetDevices():
    print dev
    print type(dev)
    print NM.NetworkManager.GetDevices()
    print "-----------------------------"
    if dev.DeviceType != NM.NM_DEVICE_TYPE_WIFI:
        print "ENTERED IF"
        print dev.DeviceType
        continue
    #else:
        print "ENTERED ELSE"
        print dev
        print dev.DeviceType
    for ap in dev.SpecificDevice().GetAccessPoints():
        print type(ap)
        print len(ap)
        print "%-30s %dMHz %d%%" %(ap.Ssid, ap.Frequency, ap.Strength)
    print "end"       

# 2 - WiFi
# 14 - Generic
# 1 - Ethernet

##for dev in NM.NetworkManager.GetAccessPoint():
##    print dev
##    print type(dev)
##    print NM.NetworkManager.GetAccessPoint()
##    print "-----------------------------"

