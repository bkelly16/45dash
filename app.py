import remi.gui as gui
from remi import start, App
import sys, tempfile, os
import subprocess
import re
import platform, socket
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-GLOBAL FUNCTION DECLARATIONS#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def takeMeToRoot():
	subprocess.call(['cd ../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../..'], shell=True)


def splitLine(text):
	words = text.split()
	words[0] = words[0]+words[1]
	del words[1]
	wordList = []
	for word in words:
		wordList.append(word)
	return wordList


#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-GLOBAL VARIABLE DECLARATION#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

global hostCount
hostCount = 2
global hosts
hosts = []

 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-# UI RENDERING#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
class MyApp(App):

	 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-# LOCAL FUNCTIONS #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-# 
	def __init__(self, *args):
		super(MyApp, self).__init__(*args)
	#--------------------------------------------Monitor Functions-------------------------------------------------
	def retrieveVolumes(self):
		takeMeToRoot()
		s=subprocess.Popen(["gluster volume list"], shell=True, stdout=subprocess.PIPE).stdout
		glusters = s.read().splitlines()
		return glusters

	def brickStatus(self, widget, selection):
		brick = self.driveList.children[selection].get_text()
		s=subprocess.Popen(["hdparm -I /dev/disk/by-vdev/%s"%brick], shell=True, stdout=subprocess.PIPE).stdout
		lines = s.read().splitlines()
		modelNumber = lines[4]
		message = modelNumber + "in use"
		self.notification_message("Brick Info", message)

	
		self.autoRefresh()
	
	def driveMap(self):
		takeMeToRoot()
		r=subprocess.check_output("lsdevpy -n", stderr=subprocess.STDOUT, shell=True)
		return r
	def driveMapTable(self):
		r = subprocess.Popen("lsdevpy -n", stdout=subprocess.PIPE, shell=True).stdout
		lines = r.read().splitlines()

		lines2 = []
		for i in range(0,15):
			lines2.append(lines[i+3])
		lines3 = ['']
		for str in lines2:
			lines3.append(str.split())

		for entry in lines3:
			tuple(entry)
		newChar = []
		lines4 = []
		for string in lines3:
			for char in string:
				if char[0] == "*":
					if char[1]=="*":
						newChar.append(char)
					else:
						newChar.append(char)
				else:
					inte = 1
		lines4 =['Drive Alias']
		for str2 in newChar:
			lines4.append(str2.split())
		for entry in lines4:
			tuple(entry)
		return lines4
	def detailText(self):
		r = subprocess.Popen(["gluster volume status %s detail | grep Space"%choice],stdout=subprocess.PIPE, shell=True).stdout
		lines = r.read().splitlines()
		lineCount = 0
		for entry in lines:
			lineCount = lineCount+1
		numBricks = lineCount/2
		bricks = []
		lineParse=0
		for num in range(0,numBricks):
			bricks.append(str("Brick "+str(num)+": "+lines[lineParse].strip(" ")+"|"+lines[lineParse+1].strip(" ")))
			lineParse = lineParse+2
		return bricks
					#print lineCount/2
		#print lines

	def autoRefresh(self):
		global choice
		if choice == '':
			choice = self.retrieveVolumes()[0]
		#self.statusTable.append_from_list([('Gluster Process','TCP Port', 'RDMA Port', 'Online', 'Pid'), self.statusList()[0], self.statusList()[1]], True)
		self.detailList.empty()
		details = self.detailText()
		for entry in details:
			self.brick = gui.ListItem(entry)
			self.detailList.append(self.brick)
		self.volumeList.empty()
		volume_List = self.retrieveVolumes()
		for volume in volume_List:
			status = self.infoTableFunction(volume)[3][1].strip(" ").lower()
			if status == "started":
				self.volume = gui.ListItem(volume, style={'color':'#29B809'})
			elif status == "stopped":
				self.volume = gui.ListItem(volume, style={'color':'#FF0000'})
			self.volumeList.append(volume)
		#self.infoTable.append_from_list([(''),(self.infoTableFunction(choice)[1]), (self.infoList(choice)[2]), (self.infoList(choice)[3]), (self.infoList(choice)[4]), (self.infoList(choice)[5]), (self.infoList(choice)[6]), (self.infoList(choice)[7])])

	def refresh(self, widget):
		#self.statusList()
		self.statusTable.append_from_list([('Gluster Process','TCP Port', 'RDMA Port', 'Online', 'Pid'), statusList(choice)[0], statusList(choice)[1]])
		self.volumeList.empty()
		volume_List = self.retrieveVolumes()
		self.detailList.empty()
		details = self.detailText()
		for entry in details:
			self.brick = gui.ListItem(entry)
			self.detailList.append(self.brick)
		for volume in volume_List:
			statusLine = self.infoList(volume)[4]
			status = statusLine[1]
			status = status.strip(" ")
			status = status.lower()
			if status == "started":
				self.volume = gui.ListItem(volume, style={'color':'#29B809'})
			elif status == "stopped":
				self.volume = gui.ListItem(volume, style={'color':'#FF0000'})
			self.volumeList.append(self.volume)
		#self.infoTable.append_from_list([(''),(self.infoList(choice)[1]), (self.infoList(choice)[2]), (self.infoList(choice)[3]), (self.infoList(choice)[4]), (self.infoList(choice)[5]), (self.infoList(choice)[6]), (self.infoList(choice)[7])])

	#--------------------------------------------Create Functions---------------------------------------------------
	def passwordlessSSH(self):
		subprocess.call(['cd ~'], shell=True)
		subprocess.call(['cd etc'], shell=True)


	def addHostPress(self, widget):
		global hostCount
		hostCount = hostCount + 1
		hostInputs = []
		hostInputs[hostCount] =  gui.TextInput(width='50%', height=30)
		createHostContainer.append(hostInputs[hostCount])
	def numHostsChange(self, widget, newValue):
		global numHosts
		numHosts = self.hostsSpinBox.get_value()
		for num in numHosts:
			hostTextInput = gui.TextInput(width='50%', height=30)
			hostTextInput.set_text('Input host name')
			createHostContainer.append(hostTextInput, numHosts)
		for num in numHosts:
			createHostContainer
	def raidLevelSelected(self, widget, selection):
		#level = self.raidSelection.children[selection].get_text()
		inte = 1
	def gDeployFile(self):
		takeMeToRoot()
		f = open("deploy-cluster.conf","w+")
		f.write(hostsConf)
		f.write("\n[tune-profile]\nthroughput-performance\n\n[service1]\naction=enable\nservice=ntpd\nignore_errors=no\n\n[service2]\naction=start\nservice=ntpd\nignore_errors=no\n\n[service3]\naction=disable\nservice=firewalld\nignore_errors=no\n\n[service4]\naction=stop\nservice=firewalld\nignore_errors=no\n\n[service5]\naction=enable\nservice=glusterd\nignore_errors=no\n\n[service6]\naction=start\nglusterd\nignore_errors=no\n\n")
		#chassisSize = self.chassisSizeInput.get_value()
		f.write("[script1]\n")
		f.write("action=execute\nfile=/opt/gtools/bin/dmap -qs 60\n")
		f.write("ignore_script_errors=no\n\n")
		vDevs = self.vDevSelection.get_value()
		raidLevel = self.raidSelection.get_value()
		f.write("[script2]\naction=execute\nfile=/opt/gtools/bin/zcreate -v %s -l %s -n zpool -a 9 -bq\n"%(vDevs, raidLevel.lower()))
		f.write("ignore_script_errors=no\n\n")
		bricks = self.brickSelection.get_value()
		f.write("[script3]\naction=execute\nfile=/opt/gtools/bin/mkbrick -n zpool -A 100G -C -b %s -p 95 -fq\n"%(bricks))
		f.write("ignore_script_errors=no\n\n[update-file1]\naction=edit\ndest=/usr/lib/systemd/system/zfs-import-cache.service\nreplace=ExecStart=\nline=ExecStart=/usr/local/libexec/zfs/startzfscache.sh\n\n[script5]\naction=execute\nfile=/opt/gtools/bin/startzfscache\nignore_script_errors=no\n\n")
		glusterConfig = self.glusterSelection.get_value()
		glusterName = self.nameInput.get_text()
		r = subprocess.Popen(['/opt/gtools/bin/mkarb -b %s -n %s -n %s'%(bricks, "server2", "server1")], shell=True, stdout=subprocess.PIPE).stdout
		mkarb = r.read()
		tuneProfile = self.tuningSelection.get_value()
		f.write("[volume1]\naction=create\nvolname=%s\n"%glusterName)
		if glusterConfig == 'Distributed':
			f.write("replica_count=0\nforce=yes\n")
			if tuneProfile == 'Default':
				key=performance.parallel-readdir, network.inode-lru-limit, performance.md-cache-timeout, performance.cache-invalidation, performance.stat-prefetch, features.cache-invalidation-timeout, features.cache-invalidation, performance.cache-samba-metadata\nvalue=on,50000,600,on,on,600,on,on\nbrick_dirs=%s\n"%mkarb)
		
		if glusterConfig == 'Distributed Replicated':
			f.write("replica_count=3\narbiter_count=1\nforce=yes\nkey=performance.parallel-readdir, network.inode-lru-limit, performance.md-cache-timeout, performance.cache-invalidation, performance.stat-prefetch, features.cache-invalidation-timeout, features.cache-invalidation, performance.cache-samba-metadata\nvalue=on,50000,600,on,on,600,on,on\nbrick_dirs=%s\n"%mkarb)
		f.close()
	def showAdvanced(self, widget):
		advancedContainer = gui.Widget(width='100%', height=200)
		self.ashiftLabel = gui.Label('ashift value:', width='50%', height=30, style={'float':'left'})
		self.ashiftInput = gui.TextInput(width='50%', height=30, style={'float':'right'})
		self.ashiftInput.set_text('9')
		self.paddingLabel = gui.Label('Padding (%)', width='50%', height=30, style={'float':'left'})
		self.paddingInput = gui.TextInput(width='50%', height=30, style={'float':'right'})
		self.paddingInput.set_text("95")
		self.arbiterLabel = gui.Label('Arbiter Bricks (?)', width='50%', height=30, style={'float':'left'})
		self.arbiterInput = gui.TextInput(width='50%', height=30, style={'float':'right'})
		self.arbiterInput.set_text("100G")
		advancedContainer.append(self.ashiftLabel)
		advancedContainer.append(self.ashiftInput)
		advancedContainer.append(self.paddingLabel)
		advancedContainer.append(self.paddingInput)
		advancedContainer.append(self.arbiterLabel)
		advancedContainer.append(self.arbiterInput)
		createContainer.append(advancedContainer)
	def reset(self, widget):
		self.hostOneInput.set_text('Localhost')
		self.hostTwoInput.set_text('server1')
		self.nameInput.set_text('NewVolume')
		self.chassisSizeInput.select_by_value('30')
		self.raidSelection.select_by_value('RAIDZ2')
		self.vDevSelection.select_by_value('3')
		self.brickSelection.select_by_value('8')
		self.glusterSelection.select_by_value('Distributed')

	def createPress(self, widget):
		self.saveHosts()
		self.notification_message("Action", "%s is in the oven "%self.nameInput.get_text())
		entries = self.retrieveVolumes()
		entryCount = 0
		for entry in entries:
			entryCount = entryCount + 1
		self.gDeployFile()
		subprocess.call(['gdeploy -c deploy-cluster.conf'], shell=True)
		newEntries = self.retrieveVolumes()
		newEntryCount = 0
		self.volumeList.empty()
		volumes = self.retrieveVolumes()
		for entry in volumes:
			self.volumeList.append(entry)
		for newEntry in newEntries:
			newEntryCount = newEntryCount + 1
		if entryCount == newEntryCount:
			self.notification_message("Error!", "Don't know what happened but %s couldn't be made"%self.nameInput.get_text())
		else:
			currentVolumeList = newEntries
			self.notification_message("Success!", "Gluster %s has been made"%(self.nameInput.get_text()))
		self.autoRefresh()
	def main(self):
		#____________________________________TEMPORARY STUFF_________________________________________________

		global currentVolumeList
		currentVolumeList = self.retrieveVolumes()
		global choice
		choice = str(self.retrieveVolumes()[0])
		self.detailText()
		statusLines = self.statusTableFunction()
		infoLists = self.infoTableFunction(choice)
		#____________________________________CONTAINERS_________________________________________________________
		mainContainer = gui.Widget(width='98%', margin='0px auto', height='100%', style={'display':'block','overflow':'auto'})
		mainMenuContainer = gui.Widget(width='98%', margin='0px auto', height='100%', style={'display':'block','overflow':'auto'})
		monitorLeftContainer = gui.Widget(width='55%', height='100%', style={'float':'left','display':'block','overflow':'auto'})
		global monitorRightContainer
		monitorRightContainer = gui.Widget(width='45%', height='100%', style={'float':'right','display':'block', 'overflow':'auto'})
		createHostContainer = gui.Widget()
		createContainer = gui.Widget()
		#____________________________________LOCAL VARIABLES_____________________________________________________
		#-----------------------------------DRIVE MAP-------------------------------------------------------------
		self.driveLabel = gui.Label('Drive Status', width='100%', height=30)
		self.driveList = gui.ListView()
		drive_List = self.driveMapTable()
		for entry in drive_List:
			driveAlias = str(entry)
			driveAlias = driveAlias.strip("*")
			driveAlias = driveAlias.strip("['")
			driveAlias = driveAlias.strip("']")
			char = str(driveAlias)
			if char[0] == "*":
				if char[1] == "*":
					driveAlias = driveAlias.strip("*")
					self.drive = gui.ListItem(driveAlias, style={'color':'#29B809'})
				else:
					driveAlias = driveAlias.strip("*")
					self.drive = gui.ListItem(driveAlias, style={'color':'#FF6100'})
			else:
				self.drive = gui.ListItem(driveAlias)
				

			self.driveList.append(self.drive)
			self.driveList.set_on_selection_listener(self.brickStatus)
		monitorRightContainer.append(self.driveLabel)		
		monitorRightContainer.append(self.driveList)

		#-----------------------------------Detail List --------------------------------------------------------
		self.detailLabel = gui.Label('Brick Storage', width='100%', height=30)
		self.detailList = gui.ListView()
		spaceList = self.detailText()
		for entry in spaceList:
			self.brick = gui.ListItem(entry)
			self.detailList.append(self.brick)
		monitorRightContainer.append(self.detailLabel)
		monitorRightContainer.append(self.detailList)



		#--------------------------------------Main Menu Configuration -------------------------------------------
		#--------------------------------------Volume List--------------------------------------------------------
		self.mainMenuVolumeContainer = gui.Widget(width='20%', height='100%', style={'float':'left','display':'block','overflow':'auto'})
		self.activeVolumeLabel = gui.Label('Active Volumes', width='100%', height='10%')
		self.activeVolumeList = gui.ListView(width='100%', height='90%', style={'float':'left'})
		self.active_Volume_List = self.retrieveVolumes() 
		for vol in self.active_Volume_List:
			volumeStatus = self.infoTableFunction(vol)[3][1].strip(" ").lower() #Retrieves status by calling gluster info and makes it easy to call by string
			if volumeStatus =='started':
				self.volumeListItem = gui.ListItem(vol, style={'color':'#29B809'}) #Checks status and colors green if started or red if stopped
			elif volumeStatus =='stopped':
				self.volumeListItem = gui.ListItem(vol, style={'color':'#FF0000'})
			else:
				self.volumeListItem = gui.ListItem(vol)
			self.activeVolumeList.append(self.volumeListItem)
		self.mainMenuVolumeContainer.append(self.activeVolumeLabel)
		self.mainMenuVolumeContainer.append(self.activeVolumeList)
		#_________________________________________________________________________________________________________
		#--------------------------------------Create Configuaration----------------------------------------------
		#_________________________________________________________________________________________________________
		#--------------------------------------Host inputs--------------------------------------------------------
		global createHostsContainer
		createHostsContainer = gui.Widget(width='98%', height=300, style={'padding':'5px','border':'0px solid #851919','float':'left','display':'block','overflow':'auto'})
		self.hostsLabel = gui.Label('Hosts Configuration',width='98%', height=30)
		self.hostsInputLabel = gui.Label('Select Number of hosts to be connected', width='70%', height=30, style={'float':'left'})
		self.hostsInputDropDown = gui.DropDown(width='30%', height=30, style={'float':'left'})
		for number in range(2,25):
			self.hostsInputDropDown.append(str(number))
		self.hostsInputDropDown.select_by_value("")
		self.hostsInputDropDown.set_on_change_listener(self.hostsInputDropDownFunction)
		self.testButton = gui.Button('Save Hosts', width='98%')
		self.testButton.set_on_click_listener(self.saveHosts)
		createHostsContainer.append(self.hostsLabel)
		createHostsContainer.append(self.hostsInputLabel)
		createHostsContainer.append(self.hostsInputDropDown)
		createHostsContainer.append(self.testButton)
		#--------------------------------------Gluster details----------------------------------------------------
		self.glusterDetailsContainer = gui.Widget(width='98%', height=400,  style={'padding':'5px','border':'0px solid #851919','float':'left','display':'block','overflow':'auto'})
		self.nameLabel = gui.Label('Name of new volume:', width='70%', height=30, style={'float':'left'})
		self.nameInput = gui.TextInput(width='30%', height=30, style={'float':'right'})
		self.nameInput.set_text('NewVolume')
		self.raidLabel = gui.Label('Select RAID Level (Z2 recommended)', width='70%', height=30, style={'float':'left'})
		self.raidSelection = gui.DropDown.new_from_list(('RAIDZ1', 'RAIDZ2', 'RAIDZ3'), width='30%', height=30, style={'float':'right'})
		self.raidSelection.select_by_value('RAIDZ2')
		self.raidSelection.set_on_change_listener(self.raidLevelSelected)
		self.vDevLabel = gui.Label('Select # of VDevs', width='70%', height=30, style={'float':'left'})
		self.vDevSelection = gui.DropDown.new_from_list(('2','3','4','5','6'), width='30%', height=30, style={'float':'right'})
		self.vDevSelection.select_by_value('3')
		self.brickLabel = gui.Label('Select # of bricks for ZFS pool', width='70%', height=30, style={'float':'left'})
		self.brickSelection = gui.DropDown.new_from_list(('2','3','4','5','6','7','8'), width='30%', height=30, style={'float':'right'})
		self.brickSelection.select_by_value('8')
		self.advancedCheckButton = gui.Button('Show advanced options', width='100%', height=30, style={'float':'left'})
		self.advancedCheckButton.set_on_click_listener(self.showAdvanced)
		self.resetButton = gui.Button('Reset to defaults', width='100%', height=30)
		self.resetButton.set_on_click_listener(self.reset)
		self.createButton = gui.Button('Create new gluster', width='100%', height=30, style={'float':'left'})
		self.createButton.set_on_click_listener(self.createPress)
		self.glusterLabel = gui.Label('Select Gluster Configuation', width='70%', height=30, style={'float':'left'})
		self.glusterSelection=gui.DropDown.new_from_list(('Distributed','Distributed Replicated'), width='30%', height=30, style={'float':'right'})
		self.glusterSelection.select_by_value('Distributed')
		self.tuningSelection = gui.DropDown.new_from_list(('Default','SMB filesharing','Virtualization'))
		self.tuningSelection.select_by_value('Default')
		self.glusterDetailsContainer.append(self.nameLabel)
		self.glusterDetailsContainer.append(self.nameInput)
		self.glusterDetailsContainer.append(self.raidLabel)
		self.glusterDetailsContainer.append(self.raidSelection)
		self.glusterDetailsContainer.append(self.vDevLabel)
		self.glusterDetailsContainer.append(self.vDevSelection)
		self.glusterDetailsContainer.append(self.brickLabel)
		self.glusterDetailsContainer.append(self.brickSelection)
		self.glusterDetailsContainer.append(self.glusterLabel)
		self.glusterDetailsContainer.append(self.glusterSelection)
		self.glusterDetailsContainer.append(self.tuningSelection)
		self.glusterDetailsContainer.append(self.advancedCheckButton)
		self.glusterDetailsContainer.append(self.resetButton)
		self.glusterDetailsContainer.append(self.createButton)
		#_________________________________________________________________________________________________________
		#--------------------------------------Monitor - Volume Configuation--------------------------------------
		#_________________________________________________________________________________________________________
		#--------------------------------------Volume List-------------------------------------------------------
		self.monitorVolumeContainer = gui.Widget(width='10%', height=700, style={'padding':'5px','border':'2px solid #851919','float':'left','display':'block','overflow':'auto'})
		self.volumeLabel = gui.Label('Active Volumes', width='100%', height='10%')
		self.volumeList = gui.ListView(width='100%', style={'float':'left'})
		for volume in self.active_Volume_List:
			infoStatus = self.infoTableFunction(volume)[3][1].strip(" ").lower()
			if infoStatus == "started":
				self.volume = gui.ListItem(volume, style={'color':'#29B809'})
			elif infoStatus == "stopped":
				self.volume = gui.ListItem(volume, style={'color':'#FF0000'})
			self.volumeList.append(self.volume)
		self.volumeList.set_on_selection_listener(self.list_view_on_selected)
		self.startButton = gui.Button('Start %s'%choice, width='100%', height=50,style={'background-color':'#29B809'})
		self.startButton.set_on_click_listener(self.startGluster)
		self.stopButton = gui.Button('Stop %s'%choice, width='100%', height=50, style={'background-color':'orange'})
		self.stopButton.set_on_click_listener(self.stopGluster)
		self.deleteButton = gui.Button('Delete %s'%choice, width='100%', height=50, style={'background-color':'#FF0000'})
		self.deleteButton.set_on_click_listener(self.deleteGluster)
		self.monitorVolumeContainer.append(self.volumeLabel)
		self.monitorVolumeContainer.append(self.volumeList)
		self.monitorVolumeContainer.append(self.startButton)
		self.monitorVolumeContainer.append(self.stopButton)
		self.monitorVolumeContainer.append(self.deleteButton)
		#--------------------------------------Volume info Table---------------------------------------------------
		self.monitorInfoContainer = gui.Widget(width='49%', height=700, style={'padding':'5px','border':'2px solid #851919','float':'left','display':'block','overflow':'auto'})
		self.infoLabel = gui.Label('Volume Info', width='100%', height=30)
		self.infoTable = gui.Table(width='100%')
		for line in self.infoTableFunction(choice):
			self.infoLine = gui.TableRow()
			self.infoItem0 = gui.TableItem(line[0])
			self.infoItem1 = gui.TableItem(line[1])
			self.infoItem2 = gui.TableItem(line[2])
			self.infoLine.append(self.infoItem0)
			self.infoLine.append(self.infoItem1)
			self.infoLine.append(self.infoItem2)
			self.infoTable.append(self.infoLine)
		self.monitorInfoContainer.append(self.infoLabel)
		self.monitorInfoContainer.append(self.infoTable)
		#--------------------------------------Volume Status Table-----------------------------------------------
		self.monitorStatusContainer = gui.Widget(width='37%', height=700, style={'padding':'5px','border':'2px solid #851919','float':'right','display':'block','overflow':'auto'})
		self.statusLabel = gui.Label('Volume Status',width="100%", height=30)
		self.statusTable = gui.Table(width='100%')
		for line in self.statusTableFunction():
			self.statusLine = gui.TableRow()
			self.statusItem0 = gui.TableItem(line[0])
			self.statusItem1 = gui.TableItem(line[1])
			self.statusItem2 = gui.TableItem(line[2])
			self.statusItem3 = gui.TableItem(line[3])
			self.statusItem4 = gui.TableItem(line[4])
			self.statusItem5 = gui.TableItem(line[5])
			self.statusItem6 = gui.TableItem(line[6])
			self.statusLine.append(self.statusItem0)
			self.statusLine.append(self.statusItem1)
			self.statusLine.append(self.statusItem2)
			self.statusLine.append(self.statusItem3)
			self.statusLine.append(self.statusItem4)
			self.statusLine.append(self.statusItem5)
			self.statusLine.append(self.statusItem6)
			self.statusTable.append(self.statusLine)
		self.monitorStatusContainer.append(self.statusLabel)
		self.monitorStatusContainer.append(self.statusTable)
		#_________________________________________________________________________________________________________
		#--------------------------------------Front end configuation---------------------------------------------
		#_________________________________________________________________________________________________________
		#--------------------------------------Appending containers-----------------------------------------------
		monitorContainer = gui.Widget(width='98%', height='100%', style={'background-color':'#851919','margin':'0px auto','display': 'block', 'overflow':'auto'})
		mainCreateContainer = gui.Widget(width='40%', height='100%', style={'background-color':'#851919','margin':'0px auto','display': 'block', 'overflow':'auto'})
		#--------------------------------------Main Menu----------------------------------------------------------
		mainMenuContainer.append(self.mainMenuVolumeContainer)
		#--------------------------------------Create menu--------------------------------------------------------
		mainCreateContainer.append(createHostsContainer)
		global hostsInputContainer
		hostsInputContainer = gui.Widget(width='100%', height=200, style={'display': 'block', 'overflow':'auto'})
		mainCreateContainer.append(self.glusterDetailsContainer)
		#--------------------------------------Monitor Menu-------------------------------------------------------
		monitorContainer.append(self.monitorVolumeContainer)
		monitorContainer.append(self.monitorInfoContainer)
		monitorContainer.append(self.monitorStatusContainer)
		#--------------------------------------TabBox configuation------------------------------------------------
		self.mainTabBox = gui.TabBox()
		self.mainTabBox.add_tab(mainMenuContainer, "Main Menu", None)
		self.mainTabBox.add_tab(mainCreateContainer, "Create", None)
		self.mainTabBox.add_tab(monitorContainer, "Monitor - Volume", None)
		#----------------------------------FINAL LAYOUT CONFIG----------------------------------------------------
		mainContainer.append(self.mainTabBox)
		return mainContainer

	#_____________________________________________________________________________________________________________
	#-----------------------------------------------Functions-----------------------------------------------------
	#_____________________________________________________________________________________________________________
	#-----------------------------------------------Create functions----------------------------------------------
	def saveHosts(self, widget):
		hosts = []
		for num in range(1, numHosts+1):
			hosts.append(hostsInputContainer.children[num].get_text())
		global hostsConf
		hostsConf = "[hosts]\n"
		for entry in hosts:
			hostsConf = hostsConf + "%s\n"%entry
		hostsConf + "\n"
		print hostsConf
	def hostsInputDropDownFunction(self, widget, selection):
		global hostsList
		hostsList = {}
		hostsInputContainer.empty()
		global numHosts
		numHosts = int(selection)
		for num in range(1,numHosts+1):
			if num % 2 == 1:
				self.hostInput = gui.TextInput(width='50%', key=num, height=30, style={'float':'left'})
			if num % 2 == 0:
				self.hostInput = gui.TextInput(width='50%', height=30, style={'float':'right'})
			self.hostInput.set_text('server%d'%num)
			hostsList[num] = (self.hostInput.get_text())
			hostsInputContainer.append(self.hostInput, num)
		createHostsContainer.append(hostsInputContainer)

	#-----------------------------------------------Monitor Functions---------------------------------------------
	def autoRefresh(self):
		global choice
		if choice == '':
			choice = self.retrieveVolumes()[0]
		
		self.statusTable.empty()
		for line in self.statusTableFunction():
			self.statusLine = gui.TableRow()
			self.statusItem0 = gui.TableItem(line[0])
			self.statusItem1 = gui.TableItem(line[1])
			self.statusItem2 = gui.TableItem(line[2])
			self.statusItem3 = gui.TableItem(line[3])
			self.statusItem4 = gui.TableItem(line[4])
			self.statusItem5 = gui.TableItem(line[5])
			self.statusItem6 = gui.TableItem(line[6])
			self.statusLine.append(self.statusItem0)
			self.statusLine.append(self.statusItem1)
			self.statusLine.append(self.statusItem2)
			self.statusLine.append(self.statusItem3)
			self.statusLine.append(self.statusItem4)
			self.statusLine.append(self.statusItem5)
			self.statusLine.append(self.statusItem6)
			self.statusTable.append(self.statusLine)
		self.infoTable.empty()
		for line in self.infoTableFunction(choice):
			self.infoLine = gui.TableRow()
			self.infoItem0 = gui.TableItem(line[0])
			self.infoItem1 = gui.TableItem(line[1])
			self.infoItem2 = gui.TableItem(line[2])
			self.infoLine.append(self.infoItem0)
			self.infoLine.append(self.infoItem1)
			self.infoLine.append(self.infoItem2)
			self.infoTable.append(self.infoLine)

		self.detailList.empty()
		details = self.detailText()
		for entry in details:
			self.brick = gui.ListItem(entry)
			self.detailList.append(self.brick)
		self.volumeList.empty()
		volume_List = self.retrieveVolumes()
		for volume in volume_List:
			status = self.infoTableFunction(volume)[3][1].strip(" ").lower()
			if status == "started":
				self.volume = gui.ListItem(volume, style={'color':'#29B809'})
			elif status == "stopped":
				self.volume = gui.ListItem(volume, style={'color':'#FF0000'})
			self.volumeList.append(self.volume)



	def list_view_on_selected(self, widget, selection):
		global choice
		choice = self.volumeList.children[selection].get_text()
		self.autoRefresh()
		self.detailList.empty()
		details = self.detailText()
		for entry in details:
			self.brick = gui.ListItem(entry)
			self.detailList.append(self.brick)

	def startGluster(self, widget):
		subprocess.call(["gluster volume start %s"%choice], shell=True)
		self.notification_message("", "Gluster Volume %s has been started"%choice)
		self.volumeList.empty()
		volume_List = self.retrieveVolumes()
		for volume in volume_List:
			status = self.infoTableFunction(volume)[3][1].strip(" ").lower()
			if status == "started":
				self.volume = gui.ListItem(volume, style={'color':'#29B809'})
			elif status == "stopped":
				self.volume = gui.ListItem(volume, style={'color':'#FF0000'})
			self.volumeList.append(self.volume)
		self.autoRefresh()


	def stopGluster(self, widget):
		initialStatus = self.infoTableFunction(choice)[3][1].strip(" ").lower()
		if initialStatus == 'started':
			subprocess.call(["echo 'y' | gluster volume stop %s"%(choice)], shell=True)
			self.volumeList.empty()
			volume_List = self.retrieveVolumes()
			for volume in volume_List:
				status = self.infoTableFunction(volume)[3][1].strip(" ").lower()
				if status == "started":
					self.volume = gui.ListItem(volume, style={'color':'#29B809'})
				elif status == "stopped":
					self.volume = gui.ListItem(volume, style={'color':'#FF0000'})
				self.volumeList.append(self.volume)
			currentStatus = self.infoTableFunction(choice)[3][1].strip(" ").lower()
			if currentStatus == 'stopped':
				self.notification_message("", "Gluster Volume %s has been stopped"%choice)
			if currentStatus != 'stopped':
				self.notificaiotn_message("Error!", "Gluster volume %s couldn't be stopped"%choice)
		else:
			self.notification_message("Error!", "Gluster volume %s is already stopped"%choice)
		self.autoRefresh()
	
	def deleteGluster(self, widget):
		subprocess.call(["echo 'y' | gluster volume delete %s"%(choice)], shell=True)
		self.notification_message("", "Gluster Volume %s has been deleted"%choice)
		self.volumeList.empty()
		volumes = self.retrieveVolumes()
		for volume in volumes:
			status = self.infoTableFunction(volume)[3][1].strip(" ").lower()
			if status == "started":
				self.volume = gui.ListItem(volume, style={'color':'#29B809'})
			elif status == "stopped":
				self.volume = gui.ListItem(volume, style={'color':'#FF0000'})
			self.volumeList.append(self.volume)



	def statusTableFunction(self):
		status = self.infoTableFunction(choice)[3][1].strip(" ").lower()
		if status == "started":
			r=subprocess.Popen(['gluster volume status %s' % choice], shell=True, stdout=subprocess.PIPE).stdout
			lines = r.read().splitlines()
			del lines[0]
			del lines[0]
			del lines[0]
			lines2 = []
			for line in lines:
				if line[0] == '-':
					lines.remove(line)
				else:
					splitText = line.split()
					if line[0] == 'Brick':
						line[0] = line[0] + " " + line[1]
						del line[1]
					while len(splitText) < 7:
						splitText.append("")
					lines2.append(splitText)
			entries = []
			for entry in lines2:
				tupleEntry = tuple(entry)
				entries.append(tupleEntry)
			return entries

		else:
			blankList = [('Volume is not started','','','','','','')]
			return blankList

	def infoTableFunction(self, choice):
		r = subprocess.Popen(['gluster volume info %s' % choice], shell=True, stdout=subprocess.PIPE).stdout
		lines = r.read().splitlines()
		results = []
		for line in lines:
			splitText = re.split(r':', line)
			while len(splitText) < 3:
				splitText.append("")
			results.append(splitText)
		entries = []
		for entry in results:
			tupleEntry = tuple(entry)
			entries.append(tupleEntry)
		del entries[0]
		return entries
start(MyApp)
