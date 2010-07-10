import subprocess, sys, re

# Linux specific command syntax and filters go here
if sys.platform in "linux":
	COMMAND = ['iwlist','scan']
	AP_INFO_PATTERN = r"((?:[0-9a-f][0-9a-f]:){5}[0-9a-f][0-9a-f])\s(.[0-9]*)"
		
# OS X specific command syntax and filters go here
elif sys.platform in "darwin":	
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
validBSSIDs = ["00:26:cb:f4:42:f3"]

def getAPs(iterations):
	AP_Dict = {}
	for i in range(iterations):
		print str(i*100/iterations)+"%","|"*(i+1)
		scanner = subprocess.Popen(COMMAND, stdout=subprocess.PIPE)
		output = scanner.communicate()[0]
		lines = output.split("\n")
		for l in lines:
			print l
			info = AP_INFO_REGEX.search(l)
			if info == None or None in info.groups(): continue
			if info.group(1) in validBSSIDs or True: #Currently bypassing list check
				if not (info.group(1) in AP_Dict):
					AP_Dict[info.group(1)] = [0]*i+[]
				AP_Dict[info.group(1)] += [int(info.group(2))]
				for k in AP_Dict:
					if len(AP_Dict[k]) < i+1:
						AP_Dict[k] += [-100]
	return AP_Dict

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

def converge(array, minLen, variance=10, n=0):
	arrayAlt = []
	div = 1
	while len(array) != len(arrayAlt):
		arrayAlt = array[:]
		if len(array) < minLen:
			avg = 0
		else:
			avg = float(sum(array))/len(array)
		array = [x for x in array if abs(avg-x)<variance/div]
		div += n
	if len(array) > 0:
		return float(sum(array))/len(array)
	else:
		return "ZERO ERROR"

# Set up BSSID->Hostname mappings
AP.hostnameFromBSSID;
# Set up Hostname->[X,Y] mappings
AP.XYFromHostname;

if __name__ == '__main__':
	l = getAPs(int(raw_input("\033[1mIterations?: \033[m")))
	for a in l: print a, l[a], converge([x for x in l[a] if x!=-100],len(l[a])/2,10,0)