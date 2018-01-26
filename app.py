import remi.gui as gui
from remi import start, App
import sys, tempfile, os
import subprocess
import re
import platform, socket

global brick
brick = '1-1'

 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-# UI RENDERING#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
class MyApp(App):

	 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-# LOCAL FUNCTIONS #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	def __init__(self, *args):
		super(MyApp, self).__init__(*args)
	#--------------------------------------------Monitor Functions-------------------------------------------------
	def retrieveVolumes(self):
		subprocess.call(['cd ~'], shell=True)
		s=subprocess.Popen(["gluster volume list"], shell=True, stdout=subprocess.PIPE).stdout
		glusters = s.read().splitlines()
		return glusters

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

	#--------------------------------------------Create Functions---------------------------------------------------

	def reset(self, widget):
		self.nameInput.set_text('NewVolume')
		self.chassisSizeInput.select_by_value('30')
		self.raidSelection.select_by_value('RAIDZ2')
		self.vDevSelection.select_by_value('3')
		self.brickSelection.select_by_value('8')
		self.glusterSelection.select_by_value('Distributed')
		self.tuningSelection.select_by_value('Default')

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


		#_________________________________________________________________________________________________________
		#--------------------------------------Main Menu Configuration -------------------------------------------
		#_________________________________________________________________________________________________________
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
		#--------------------------------------Drawings-----------------------------------------------------------
		self.overviewTableContainer = gui.Widget(width='70%', height=700, stlye={'float':'left','display':'block','overflow':'auto'})
		self.overviewTableLabel = gui.Label("Overview", width='100%')
		self.overviewTable = gui.Table()
		self.lclHostRow = gui.TableRow()
		self.lclHost = gui.TableItem('localhost Name	:')
		self.lclHost2 = gui.TableItem(socket.gethostname())
		self.lclHostRow.append(self.lclHost)
		self.lclHostRow.append(self.lclHost2)
		self.ipAddrRow = gui.TableRow()
		self.ipAddr = gui.TableItem('IP Address	:')
		self.ipAddr2 = gui.TableItem()


		self.overviewTable.append(self.lclHostRow)
		self.overviewTableContainer.append(self.overviewTable)

		#_________________________________________________________________________________________________________
		#--------------------------------------Create Configuaration----------------------------------------------
		#_________________________________________________________________________________________________________
		#--------------------------------------Host inputs--------------------------------------------------------
		global createHostsContainer
		createHostsContainer = gui.Widget(width='98%', height=300, style={'padding':'5px','border':'0px solid #851919','float':'left','display':'block','overflow':'auto'})
		self.hostsLabel = gui.Label('Hosts Configuration',width='98%', height=30)
		self.hostsInputLabel = gui.Label('Select Number of hosts to be connected', width='70%', height=30, style={'float':'left'})
		self.hostsInputDropDown = gui.DropDown(width='30%', height=30, style={'float':'left'})
		self.hostsInputDropDown.append("")
		for number in range(2,25):
			self.hostsInputDropDown.append(str(number))
		self.hostsInputDropDown.select_by_value("")
		self.hostsInputDropDown.set_on_change_listener(self.hostsInputDropDownFunction)
		createHostsContainer.append(self.hostsLabel)
		createHostsContainer.append(self.hostsInputLabel)
		createHostsContainer.append(self.hostsInputDropDown)
		#--------------------------------------Gluster details----------------------------------------------------
		self.glusterDetailsContainer = gui.Widget(width='98%', height=300,  style={'padding':'5px','border':'0px solid #851919','float':'left','display':'block','overflow':'auto'})
		self.nameLabel = gui.Label('Name of new volume:', width='70%', height=30, style={'float':'left'})
		self.nameInput = gui.TextInput(width='30%', height=30, style={'float':'right'})
		self.nameInput.set_text('NewVolume')
		self.raidLabel = gui.Label('Select RAID Level (Z2 recommended)', width='70%', height=30, style={'float':'left'})
		self.raidSelection = gui.DropDown.new_from_list(('RAIDZ1', 'RAIDZ2', 'RAIDZ3'), width='30%', height=30, style={'float':'right'})
		self.raidSelection.select_by_value('RAIDZ2')
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
		self.tuningSelectionLabel = gui.Label('Select tuning profile', width='70%', height=30, style={'float':'left'})
		self.tuningSelection = gui.DropDown.new_from_list(('Default','SMB filesharing','Virtualization'), width='30%', height=30, style={'float':'right'})
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
		self.glusterDetailsContainer.append(self.tuningSelectionLabel)
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
		#--------------------------------------Monitor - Drives --------------------------------------------------
		#_________________________________________________________________________________________________________
		#--------------------------------------Drive Info --------------------------------------------------------
		self.drivesVolumeListContainer = gui.Widget(width='20%', height=700, style={'padding':'5px','border':'2px solid #851919','float':'left','display':'block','overflow':'auto'})
		self.drivesVolumeListLabel = gui.Label('Active Volumes', height=30, width='100%')
		self.drivesVolumeList = gui.ListView()
		for volume in self.retrieveVolumes():
			drivesInfoStatus = self.infoTableFunction(volume)[3][1].strip(" ").lower()
			if drivesInfoStatus == "started":
				self.volume = gui.ListItem(volume, style={'color':'#29B809'})
			elif drivesInfoStatus == "stopped":
				self.volume = gui.ListItem(volume, style={'color':'#FF0000'})
			self.drivesVolumeList.append(self.volume)
		self.drivesVolumeListContainer.append(self.drivesVolumeListLabel)
		self.drivesVolumeListContainer.append(self.drivesVolumeList)
		self.drivesVolumeList.set_on_selection_listener(self.driveVolumeListSelected)
		#-------------------------------------------------------------------------------------
		self.monitorDrivesListContainer=gui.Widget(width='14%', height=450, style={'padding':'5px','border':'2px solid #851919','float':'left','display':'block','overflow':'auto'})
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
		self.monitorDrivesListContainer.append(self.driveLabel)
		self.monitorDrivesListContainer.append(self.driveList)
		#--------------------------------------Drive info---------------------------------------------------------
		self.monitorDrivesInfoContainer=gui.Widget(width='32%',height=450, style={'padding':'5px','border':'2px solid #851919','float':'left','display':'block','overflow':'auto'})
		self.detailLabel = gui.Label('Brick Storage', width='100%', height=30)
		self.detailList = gui.ListView()
		spaceList = self.detailText()
		for entry in spaceList:
			self.brick = gui.ListItem(entry)
			self.detailList.append(self.brick)
		self.monitorDrivesInfoContainer.append(self.detailLabel)
		self.monitorDrivesInfoContainer.append(self.detailList)
		#--------------------------------------Drive Text Box-----------------------------------------------------
		self.monitorDrivesTextBoxContainer = gui.Widget(width='26%', height=450, style={'padding':'5px','border':'2px solid #851919','float':'left','display':'block','overflow':'auto'})
		global driveInfoText
		driveInfoTextLabel = gui.Label('Drive Info', height=30, width='100%')
		driveInfoText = gui.TextInput(False,width='100%', height=300)
		driveInfoText.set_text('Select a drive from list to view information')
		self.monitorDrivesTextBoxContainer.append(driveInfoTextLabel)
		self.monitorDrivesTextBoxContainer.append(driveInfoText)
		#--------------------------------------Drive health box---------------------------------------------------
		self.monitorDrivesHealthContainer = gui.Widget(width='75%', height = 235 ,style={'padding':'5px','border':'2px solid #851919','float':'left','display':'block','overflow':'auto'})
		self.healthListLabel = gui.Label('Drive Health',width='100%', height=30)
		self.healthTable = gui.Table(width='100%')
		healthStats = self.getDriveHealth()
		for line in healthStats:
			self.healthLine = gui.TableRow()
			self.healthItem0 = gui.TableItem(line[0])
			self.healthItem1 = gui.TableItem(line[1])
			self.healthItem9 = gui.TableItem(line[9])
			self.healthLine.append(self.healthItem0)
			self.healthLine.append(self.healthItem1)
			self.healthLine.append(self.healthItem9)
			self.healthTable.append(self.healthLine)
		self.monitorDrivesHealthContainer.append(self.healthListLabel)
		self.monitorDrivesHealthContainer.append(self.healthTable)

		#_________________________________________________________________________________________________________
		#--------------------------------------Front end configuation---------------------------------------------
		#_________________________________________________________________________________________________________
		#--------------------------------------Appending containers-----------------------------------------------
		global createContainer
		mainContainer = gui.Widget(width='98%', height='100%', style={'margin':'0px auto','display': 'block', 'overflow':'auto'})
		mainMenuContainer = gui.Widget(width='98%', height=700, style={'background-color':'#851919','margin':'0px auto','display': 'block', 'overflow':'auto'})
		monitorVolumeContainer = gui.Widget(width='98%', height='100%', style={'background-color':'#851919','margin':'0px auto','display': 'block', 'overflow':'auto'})
		monitorDrivesContainer = gui.Widget(width='98%', height='100%', style={'background-color':'#851919','margin':'0px auto','display': 'block', 'overflow':'auto'})
		createContainer = gui.Widget(width='40%', height='100%', style={'background-color':'#851919','margin':'0px auto','display': 'block', 'overflow':'auto'})
		#--------------------------------------Main Menu----------------------------------------------------------
		mainMenuContainer.append(self.mainMenuVolumeContainer)
		mainMenuContainer.append(self.overviewTableContainer)
		#--------------------------------------Create menu--------------------------------------------------------

		createContainer.append(createHostsContainer)
		global hostsInputContainer
		hostsInputContainer = gui.Widget(width='100%', height=200, style={'display': 'block', 'overflow':'auto'})
		global advancedContainer
		advancedContainer = gui.Widget(width='100%', height=150, style={'display':'block', 'overflow':'auto'})
		createContainer.append(self.glusterDetailsContainer)
		#--------------------------------------Monitor Menu-------------------------------------------------------
		monitorVolumeContainer.append(self.monitorVolumeContainer)
		monitorVolumeContainer.append(self.monitorInfoContainer)
		monitorVolumeContainer.append(self.monitorStatusContainer)
		#--------------------------------------Monitor Drives Menu------------------------------------------------
		monitorDrivesContainer.append(self.drivesVolumeListContainer)
		monitorDrivesContainer.append(self.monitorDrivesInfoContainer)
		monitorDrivesContainer.append(self.monitorDrivesListContainer)
		monitorDrivesContainer.append(self.monitorDrivesTextBoxContainer)
		monitorDrivesContainer.append(self.monitorDrivesHealthContainer)

		#--------------------------------------TabBox configuation------------------------------------------------
		self.mainTabBox = gui.TabBox()
		self.mainTabBox.add_tab(mainMenuContainer, "Main Menu", None)
		self.mainTabBox.add_tab(createContainer, "Create", None)
		self.mainTabBox.add_tab(monitorVolumeContainer, "Monitor - Volume", None)
		self.mainTabBox.add_tab(monitorDrivesContainer, "Monitor - Drives", None)
		#----------------------------------FINAL LAYOUT CONFIG----------------------------------------------------
		mainContainer.append(self.mainTabBox)
		self.getDriveHealth()
		return mainContainer

	#_____________________________________________________________________________________________________________
	#-----------------------------------------------Functions-----------------------------------------------------
	#_____________________________________________________________________________________________________________
	#-----------------------------------------------Create functions----------------------------------------------
	def saveHosts(self):
		hosts = []
		for num in range(1, numHosts+1):
			hosts.append(hostsInputContainer.children[num].get_text())
		global hostsConf
		hostsConf = "[hosts]\n"
		for entry in hosts:
			hostsConf = hostsConf + "%s\n"%entry
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
			if num == 1:
				self.hostInput.set_text(socket.gethostname())
			else:
				self.hostInput.set_text('server%d'%num)
			hostsList[num] = (self.hostInput.get_text())
			hostsInputContainer.append(self.hostInput, num)
		createHostsContainer.append(hostsInputContainer)
	def showAdvanced(self, widget):
		advancedContainer.empty()
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
		self.nameInput.set_text('NewVolume')
		self.chassisSizeInput.select_by_value('30')
		self.raidSelection.select_by_value('RAIDZ2')
		self.vDevSelection.select_by_value('3')
		self.brickSelection.select_by_value('8')
		self.glusterSelection.select_by_value('Distributed')
		self.tuningSelection.select_by_value('Default')
	def gDeployFile(self):
		subprocess.call(['cd ~'], shell=True)
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
		mkarbCommand = "/opt/gtools/bin/mkarb -b %s -n %s -n %s"%(bricks, "server2", "server1")
		#for num in range(0,numHosts):
		#	mkarbCommand = mkarbCommand + "-n %s"%(hostsList[str(num)])
		#mkarbCommand = mkarbCommand + " \n"
		r = subprocess.Popen(mkarbCommand, shell=True, stdout=subprocess.PIPE).stdout
		mkarb = r.read()
		tuneProfile = self.tuningSelection.get_value()
		f.write("[volume1]\naction=create\nvolname=%s\n"%glusterName)
		if glusterConfig == 'Distributed':
			f.write("replica_count=0\nforce=yes\n")
			if tuneProfile == 'Default':
				f.write("key=performance.parallel-readdir, network.inode-lru-limit, performance.md-cache-timeout, performance.cache-invalidation, performance.stat-prefetch, features.cache-invalidation-timeout, features.cache-invalidation, performance.cache-samba-metadata\nvalue=on,50000,600,on,on,600,on,on\nbrick_dirs=%s\n"%mkarb)
			elif tuneProfile == 'SMB filesharing':
				f.write("key=performance.parallel-readdir,network.inode-lru-limit,performance.md-cache-timeout,performance.cache-invalidation,performance.stat-prefetch,features.cache-invalidation-timeout,features.cache-invalidation,performance.cache-samba-metadata\nvalue=on,50000,600,on,on,600,on,on\nbrick_dirs=%s\n"%mkarb)
			elif tuneProfile == 'Virtualization':
				f.write("key=group,storage.owner-uid,storage.owner-gid,network.ping-timeout,performance.strict-o-direct,network.remote-dio,cluster.granular-entry-heal,features.shard-block-size\nvalue=virt,36,36,30,on,off,enable,64MB")
		if glusterConfig == 'Distributed Replicated':
			f.write("replica_count=3\narbiter_count=1\nforce=yes\nkey=performance.parallel-readdir, network.inode-lru-limit, performance.md-cache-timeout, performance.cache-invalidation, performance.stat-prefetch, features.cache-invalidation-timeout, features.cache-invalidation, performance.cache-samba-metadata\nvalue=on,50000,600,on,on,600,on,on\nbrick_dirs=%s\n"%mkarb)
			if tuneProfile == 'Default':
				f.write("key=performance.parallel-readdir, network.inode-lru-limit, performance.md-cache-timeout, performance.cache-invalidation, performance.stat-prefetch, features.cache-invalidation-timeout, features.cache-invalidation, performance.cache-samba-metadata\nvalue=on,50000,600,on,on,600,on,on\nbrick_dirs=%s\n"%mkarb)
			elif tuneProfile == 'SMB filesharing':
				f.write("key=performance.parallel-readdir,network.inode-lru-limit,performance.md-cache-timeout,performance.cache-invalidation,performance.stat-prefetch,features.cache-invalidation-timeout,features.cache-invalidation,performance.cache-samba-metadata\nvalue=on,50000,600,on,on,600,on,on\nbrick_dirs=%s\n"%mkarb)
			elif tuneProfile == 'Virtualization':
				f.write("key=group,storage.owner-uid,storage.owner-gid,network.ping-timeout,performance.strict-o-direct,network.remote-dio,cluster.granular-entry-heal,features.shard-block-size\nvalue=virt,36,36,30,on,off,enable,64MB")

		f.close()
	#-----------------------------------------------Monitor Functions---------------------------------------------
	
	def autoRefresh(self):
		global choice
		if choice == '':
			choice = self.retrieveVolumes()[0]
		self.stopButton.set_text("Stop %s"%choice)
		self.startButton.set_text("Start %s"%choice)
		self.deleteButton.set_text("Delete %s"%choice)
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
	#------------------------------------------------Drives--------------------------------------------
	def driveVolumeListSelected(self, widget, selection):
		global choice
		choice = self.drivesVolumeList.children[selection].get_text()
		self.autoRefresh()

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

	def brickStatus(self, widget, selection):
		driveInfoText.set_text(" ")
		global brick
		brick = self.driveList.children[selection].get_text()
		s=subprocess.Popen(["hdparm -I /dev/disk/by-vdev/%s"%brick], shell=True, stdout=subprocess.PIPE).stdout
		lines = s.read().splitlines()
		r = subprocess.Popen(["df /dev/disk/by-vdev/%s"%brick], shell=True, stdout=subprocess.PIPE).stdout
		lines2 = s.read().splitlines()
		modelNumber = lines[4]
		serialNumber = lines[5]
		firmwareRevision = lines[6]
		message = modelNumber + "\n" + serialNumber + "\n" + firmwareRevision + "\n"
		driveInfoText.set_text(message)
		self.healthTable.empty()
		healthStats = self.getDriveHealth()
		for line in healthStats:
			self.healthLine = gui.TableRow()
			self.healthItem0 = gui.TableItem(line[0])
			self.healthItem1 = gui.TableItem(line[1])
			self.healthItem9 = gui.TableItem(line[9])
			self.healthLine.append(self.healthItem0)
			self.healthLine.append(self.healthItem1)
			self.healthLine.append(self.healthItem9)
			self.healthTable.append(self.healthLine)


		self.autoRefresh()
	def getDriveHealth(self):
		global brick
		s = subprocess.Popen(["smartctl -a /dev/disk/by-vdev/%s"%brick], shell=True, stdout=subprocess.PIPE).stdout
		lines = s.read().splitlines()
		useful =[]
		for i in range(55,73):
			splitLine = lines[i].split()
			if splitLine[1] == "Unknown_Attribute":
				inte =1
			elif splitLine[1] == "Offline_Uncorrectable":
				inte = 2
			else:
				useful.append(tuple(splitLine))
		return useful


start(MyApp)
