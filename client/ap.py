import subprocess, sys, re

# Linux specific command syntax and filters go here
if "linux" in sys.platform:
    COMMAND = ['iwlist','scan']
    AP_INFO_PATTERN = r"((?:[0-9a-f][0-9a-f]:){5}[0-9a-f][0-9a-f])\s(.[0-9]*)"
        
# OS X specific command syntax and filters go here
elif "darwin" in sys.platform:    
    COMMAND = ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport','-s']
    AP_INFO_PATTERN = r"((?:[0-9a-f][0-9a-f]:){5}[0-9a-f][0-9a-f])\s(.[0-9]*)"
                    
# Windows specific command syntax and filters go here
elif sys.platform in ["win32","cygwin"]:
    COMMAND = ['netsh','show','networks','mode=bssid']
    AP_INFO_PATTERN = r"((?:[0-9a-f][0-9a-f]:){5}[0-9a-f][0-9a-f])\s(.[0-9]*%)"      
        
# If we're on an unsupported platform
else:
    sys.exit("Unsupported platform.")

#############################################    
# Now for all the platform-independent code
#############################################
AP_INFO_REGEX = re.compile(AP_INFO_PATTERN)

def getAPs():
    scanner = subprocess.Popen(COMMAND, stdout=subprocess.PIPE)
    output = scanner.communicate()[0]
    lines = output.split("\n")
    APs = []
    for l in lines:
        info = AP_INFO_REGEX.search(l)
        if info == None or None in info.groups(): continue
        APs.append(AP(info.group(1), info.group(2)))
    return APs

class AP ():
    hostnameFromBSSID = {}
    XYFromHostname = {}
    def __init__(self,BSSID,RSSI):
        self.BSSID = BSSID
        self.RSSI = RSSI
        self.hostname = self._getHostname()
        [self.x, self.y] = self._getXY()
    def __str__(self):
        return "AP [" + str(self.hostname) + "] / [" + str(self.BSSID) + "] at " + \
                str((self.x,self.y)) + ": " + str(self.RSSI)
    def __repr__(self):
        return "<AP BSSID=" + self.BSSID +">"
    def _getHostname(self):
        return AP.hostnameFromBSSID.get(self.BSSID)
    def _getXY(self):
        return AP.XYFromHostname.get(self.hostname,[None,None])
        
# Set up BSSID->Hostname mappings
AP.hostnameFromBSSID;
# Set up Hostname->[X,Y] mapings
AP.XYFromHostname;

if __name__ == '__main__':
    l = getAPs()
    for a in l: print a