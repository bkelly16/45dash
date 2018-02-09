import remi.gui as gui
from remi import start, App
import platform, socket, random, re, subprocess, sys, tempfile, os, time, random

#------------------------------------------------------------------------------------------------------------------
rConf = open('45dash.conf','r')
content = rConf.readlines()
global noVolumes, noZpools, ctdbEnabled, nfsEnabled, ctdbText, nfsText, stopIsConfirmed , deleteIsConfirmed
noVolumes = False
noZpools = False
ctdbEnabled = False
ctdbText = ''
nfsEnabled = False
nfsText = ''
ganeshaList = []
stopIsConfirmed = False
deleteIsConfirmed = False
global port, username, password, baseColor, lastBrick
port = int(str(content[0]).replace("port=","").strip("\n"))
username = str(content[1]).replace("username=","").strip("\n")
password = str(content[2]).replace("password=","").strip("\n")
baseColor = str(content[3]).replace("defaultcolor=",'').strip("\n")
lastBrick = (content[4]).replace("lastBrick=",'').strip("\n")
rConf.close()
global numConnectedHosts
global connectedHosts
etcHosts = open('/etc/hosts')
numConnectedHosts = -2
connectedHosts = []
for line in etcHosts:
	numConnectedHosts = numConnectedHosts + 1
	connectedHosts.append(line)
del connectedHosts[0]
del connectedHosts[0]
connectedHostNames = []
for entry in connectedHosts:
	host = re.split("\t", entry)
	connectedHostNames.append(host[1].strip('\n'))

etcHosts.close()




global isAdvanced
isAdvanced = False
global zpoolChoice
zpoolChoice = 'zpool'
global createContainer
global localHost
localHost1 = socket.gethostname()
localHost = ''
for char in localHost1:
	if char != '.':
		localHost = localHost + char
	if char == '.':
		break




 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-# UI RENDERING#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
class FortyFiveDash(App):

	 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-# LOCAL FUNCTIONS #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	def __init__(self, *args):
		res_path = os.path.join(os.path.dirname(__file__), 'res')
		super(FortyFiveDash, self).__init__(*args, static_file_path=res_path)
	#--------------------------------------------Monitor Functions-------------------------------------------------


	#--------------------------------------------Create Functions---------------------------------------------------
	
	def main(self):
		#---------------------------------------Preconfig---------------------------------------------------------
		subprocess.call(["chmod +x /bin/45dash/lsdevpy"], shell=True)
		subprocess.call(["sed -i -e 's/\r$//' lsdevpy"], shell=True)
		subprocess.call(["systemctl start glusterd"], shell=True)
		global lastBrick
	
		#--------------------------------------Error version------------------------------------------------------
		if len(self.retrieveVolumes()) == 0:
			noVolumes = True
		else:
			noVolumes = False
		if len(self.getZpoolStats()) == 0:
			noZpools = True
		else:
			noZpools = False
		global brick
		brick = str(self.driveMapTable()[1][0]).strip('*')
		global choice
		i = 0
		if noVolumes == True:
			choice = 'all'
		elif noVolumes == False:
			choice = str(self.retrieveVolumes()[i])
			while self.infoTableFunction(choice)[3][1].strip(" ").lower() != 'started':
				i = i + 1
				choice = str(self.retrieveVolumes()[i])
		#_________________________________________________________________________________________________________
		#--------------------------------------Main Menu Configuration -------------------------------------------
		#_________________________________________________________________________________________________________
		#--------------------------------------Volume List--------------------------------------------------------
		self.mainMenuVolumeContainer = gui.Widget(width='20%', height=700,style={'padding':'5px','border':'2px solid %s'%baseColor,'float':'left','display':'block','overflow':'auto'})
		self.activeVolumeLabel = gui.Label('Active Volumes', width='100%', height=30)
		self.activeVolumeList = gui.ListView(width='100%',  height=670, style={'float':'left'})
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
		#--------------------------------------Overview Table-----------------------------------------------------------
		global localhost
		self.overviewTableContainer = gui.Widget(width='40%', height=700, style={'padding':'5px','border':'2px solid %s'%baseColor,'float':'left','display':'block','overflow':'auto'})
		self.overviewTableLabel = gui.Label("Overview", width='100%')
		self.overviewTable = gui.Table(width='100%',style={'text-align':'left'})
		self.lclHostRow = gui.TableRow()
		self.lclHost = gui.TableItem('localhost Name	:')
		self.lclHost2 = gui.TableItem(localHost)
		self.lclHostRow.append(self.lclHost)
		self.lclHostRow.append(self.lclHost2)
		self.ipAddrRow = gui.TableRow()
		self.ipAddr = gui.TableItem('IP Address	:')
		self.ipAddr2 = gui.TableItem(socket.gethostbyname(socket.gethostname()))
		self.ipAddrRow.append(self.ipAddr)
		self.ipAddrRow.append(self.ipAddr2)
		self.connectedHostsRow= gui.TableRow(style={'background-color':'Silver'})
		self.connectedHosts1 = gui.TableItem('Number of connected servers: ')
		self.connectedHosts2 = gui.TableItem(numConnectedHosts - 1)
		self.connectedHostsRow.append(self.connectedHosts1)
		self.connectedHostsRow.append(self.connectedHosts2)
		self.numVolumesRow = gui.TableRow(style={'background-color':'Silver'})
		self.numVolumes1 = gui.TableItem('Number of active volumes 	:')
		self.numVolumes2 = gui.TableItem(len(self.retrieveVolumes()))
		self.numVolumesRow.append(self.numVolumes1)
		self.numVolumesRow.append(self.numVolumes2)
		self.numActVolumesRow = gui.TableRow()
		self.numActVolumes1 = gui.TableItem('Number of started volumes 	:')
		self.numActVolumes2 = gui.TableItem(self.getNumActVolumes())
		self.numActVolumesRow.append(self.numActVolumes1)
		self.numActVolumesRow.append(self.numActVolumes2)
		self.numStVolumesRow = gui.TableRow()
		self.numStVolumes1 = gui.TableItem('Number of stopped volumes 	:')
		self.numStVolumes2 = gui.TableItem(str(int(len(self.retrieveVolumes()))-int(self.getNumActVolumes())))
		self.numStVolumesRow.append(self.numStVolumes1)
		self.numStVolumesRow.append(self.numStVolumes2)
		self.numDrivesRow = gui.TableRow(style={'background-color':'Silver'})
		self.numDrives1 = gui.TableItem('Number of connected drives	:')
		self.numDrives2 = gui.TableItem(len(self.driveMapTable())-1)
		self.numDrivesRow.append(self.numDrives1)
		self.numDrivesRow.append(self.numDrives2)
		self.numActDrivesRow = gui.TableRow()
		self.numActDrives1 = gui.TableItem('Number of drives in use	:')
		self.numActDrives2 = gui.TableItem(self.getNumActDrives())
		self.numActDrivesRow.append(self.numActDrives1)
		self.numActDrivesRow.append(self.numActDrives2)
		self.numStDrivesRow = gui.TableRow()
		self.numStDrives1 = gui.TableItem('Number of drives not in use	:')
		self.numStDrives2 = gui.TableItem(self.getNumStDrives())
		self.numStDrivesRow.append(self.numStDrives1)
		self.numStDrivesRow.append(self.numStDrives2)	
		self.numZpoolRow = gui.TableRow(style={'background-color':'Silver'})
		self.numZpool1 = gui.TableItem('Number of Zpools 	:')
		self.numZpool2 = gui.TableItem(len(self.getZpoolStats())-1)
		self.numZpoolRow.append(self.numZpool1)	
		self.numZpoolRow.append(self.numZpool2)
		self.overviewTable.append(self.lclHostRow)
		self.overviewTable.append(self.ipAddrRow)
		self.overviewTable.append(self.connectedHostsRow)
		for entry in connectedHostNames:
			if entry == localHost:
				continue
			elif entry != localHost:
				self.connectedHostRow = gui.TableRow()
				self.connectedHost1 = gui.TableItem('Name of connected server: ')
				self.connectedHost2 = gui.TableItem(entry)
				self.connectedHostRow.append(self.connectedHost1)
				self.connectedHostRow.append(self.connectedHost2)
				self.overviewTable.append(self.connectedHostRow)
		self.overviewTable.append(self.numVolumesRow)
		self.overviewTable.append(self.numActVolumesRow)
		self.overviewTable.append(self.numStVolumesRow)
		self.overviewTable.append(self.numDrivesRow)
		self.overviewTable.append(self.numActDrivesRow)
		self.overviewTable.append(self.numStDrivesRow)
		self.overviewTable.append(self.numZpoolRow)
		self.overviewTableContainer.append(self.overviewTableLabel)
		self.overviewTableContainer.append(self.overviewTable)
		#--------------------------------------Settings----------------------------------------------------------
		self.settingsContainer = gui.Widget(width='37%', height=700, style={'padding':'5px','border':'2px solid %s'%baseColor,'float':'left','display':'block','overflow':'auto'})
		self.settingsLabel = gui.Label('General Settings', width='100%')
		self.usernameLabel = gui.Label('Username:', width='70%', height=30, style={'float':'left'})
		self.usernameEntry = gui.TextInput(width='30%', height=30, style={'float':'right'})
		self.usernameEntry.set_text(username)
		self.passwordLabel = gui.Label('Password:', width='70%', height=30, style={'float':'left'})
		self.passwordEntry = gui.TextInput(width='30%', height=30, style={'float':'right'})
		self.passwordEntry.set_text(password)
		self.portLabel = gui.Label('Port ID:', width='70%', height=30, style={'float':'left'})
		self.portEntry = gui.TextInput(width='30%', height=30, style={'float':'right'})
		self.portEntry.set_text(port)
		self.defaultColorLabel = gui.Label('Choose default color', width='100%', height=30, style={'float':'left'})
		self.defaultColorPicker = gui.ColorPicker(baseColor, width='100%', height=30)
		self.saveSettingsButton = gui.Button('Save Changes (Restart UI to apply changes)', width='100%', height=30)
		self.saveSettingsButton.set_on_click_listener(self.changeSettings)
		self.clearTerminalButton = gui.Button('Clear Terminal', width='100%', height=30)
		self.clearTerminalButton.set_on_click_listener(lambda x: subprocess.call(['clear'], shell=True))
		self.settingsContainer.append(self.settingsLabel)
		self.settingsContainer.append(self.usernameLabel)
		self.settingsContainer.append(self.usernameEntry)
		self.settingsContainer.append(self.passwordLabel)
		self.settingsContainer.append(self.passwordEntry)
		self.settingsContainer.append(self.portLabel)
		self.settingsContainer.append(self.portEntry)
		self.settingsContainer.append(self.defaultColorLabel)	
		self.settingsContainer.append(self.defaultColorPicker)		
		self.settingsContainer.append(self.saveSettingsButton)
		self.settingsContainer.append(self.clearTerminalButton)
		#_________________________________________________________________________________________________________
		#--------------------------------------Create Configuaration----------------------------------------------
		#_________________________________________________________________________________________________________
		#--------------------------------------Host inputs--------------------------------------------------------
		global createHostsContainer
		createHostsContainer = gui.Widget(width='30%', height=600, style={'margin':'0px auto','padding':'5px','border':'2px solid %s'%baseColor,'float':'left','display':'block','overflow':'auto'})
		self.hostsLabel = gui.Label('Hosts Configuration',width='100%', height=30)
		self.hostsInputLabel = gui.Label('Select Number of hosts to be connected', width='70%', height=30, style={'float':'left'})
		self.hostsInputDropDown = gui.DropDown(width='30%', height=30, style={'float':'left'})
		self.hostsInputDropDown.append("")
		for number in range(2,numConnectedHosts+1):
			self.hostsInputDropDown.append(str(number))
		self.hostsInputDropDown.select_by_value("")
		self.hostsInputDropDown.set_on_change_listener(self.hostsInputDropDownFunction)
		createHostsContainer.append(self.hostsLabel)
		createHostsContainer.append(self.hostsInputLabel)
		createHostsContainer.append(self.hostsInputDropDown)

		#--------------------------------------Gluster details----------------------------------------------------
		self.glusterDetailsContainer = gui.Widget(width='30%', height=600,  style={'margin':'0px auto','padding':'5px','border':'2px solid %s'%baseColor,'float':'left','display':'block','overflow':'auto'})
		self.glusterDetailsLabel = gui.Label('Gluster Details', height=30, width='100%', style={'float':'center'})
		self.nameLabel = gui.Label('Name of new volume:', width='70%', height=30, style={'float':'left'})
		self.nameInput = gui.TextInput(width='30%', height=30, style={'float':'right'})
		self.nameInput.set_text('NewVolume')
		self.raidLabel = gui.Label('Select RAID Level (Z2 recommended)', width='70%', height=30, style={'float':'left'})
		self.raidSelection = gui.DropDown.new_from_list(('RAIDZ1', 'RAIDZ2', 'RAIDZ3'), width='30%', height=30, style={'float':'right'})
		self.raidSelection.select_by_value('RAIDZ2')
		self.vDevLabel = gui.Label('Select # of VDevs', width='70%', height=30, style={'float':'left'})
		self.vDevSelection = gui.DropDown.new_from_list(('1','2','3','4','5','6'), width='30%', height=30, style={'float':'right'})
		self.vDevSelection.select_by_value('3')
		self.brickLabel = gui.Label('Select # of bricks for ZFS pool', width='70%', height=30, style={'float':'left'})
		self.brickSelection = gui.DropDown.new_from_list(('2','3','4','5','6','7','8','9','10'), width='30%', height=30, style={'float':'right'})
		self.brickSelection.select_by_value('8')
		self.driveSelectionLabel = gui.Label('Select # of drives for gluster', width='70%', height=30, style={'float':'left'})
		self.driveSelection = gui.DropDown(width='30%', height=30, style={'float':'right'})
		for number in range(2, len(self.driveMapTable())):
			self.driveSelection.append(str(number))
		self.driveSelection.select_by_value(str(len(self.driveMapTable())-1))
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
		self.tuningSelection = gui.DropDown.new_from_list(('SMB filesharing','Virtualization'), width='30%', height=30, style={'float':'right'})
		self.tuningSelection.select_by_value('SMB filesharing')
		self.glusterDetailsContainer.append(self.glusterDetailsLabel)
		self.glusterDetailsContainer.append(self.nameLabel)
		self.glusterDetailsContainer.append(self.nameInput)
		self.glusterDetailsContainer.append(self.raidLabel)
		self.glusterDetailsContainer.append(self.raidSelection)
		self.glusterDetailsContainer.append(self.vDevLabel)
		self.glusterDetailsContainer.append(self.vDevSelection)
		self.glusterDetailsContainer.append(self.brickLabel)
		self.glusterDetailsContainer.append(self.brickSelection)
		self.glusterDetailsContainer.append(self.driveSelectionLabel)
		self.glusterDetailsContainer.append(self.driveSelection)
		self.glusterDetailsContainer.append(self.glusterLabel)
		self.glusterDetailsContainer.append(self.glusterSelection)
		self.glusterDetailsContainer.append(self.tuningSelectionLabel)
		self.glusterDetailsContainer.append(self.tuningSelection)
		self.glusterDetailsContainer.append(self.advancedCheckButton)
		self.glusterDetailsContainer.append(self.resetButton)
		self.glusterDetailsContainer.append(self.createButton)
		#--------------------------------------Sharing protocols--------------------------------------------------
		self.sharingContainer = gui.Widget(width='30%', height=600, style={'margin':'0px auto','padding':'5px','border':'2px solid %s'%baseColor,'float':'left','display':'block','overflow':'auto'})
		self.GaneshaiHostContainer = gui.Widget(width='100%')
		self.sharingLabel = gui.Label('Sharing Protocols', width='100%', height=30, style={'float':'center'})
		self.publicIPLabel = gui.Label('Enter Public IP:', width='70%', height=30, style={'float':'left'})
		self.publicIPEntry = gui.TextInput(width='30%', height=30, style={'float':'left'})
		self.publicIPEntry.set_text("192.168.16.16/16")
		self.enableCtdbButton = gui.Button('Enable CTDB', width='100%', height=30, style={'float':'center'})
		self.enableCtdbButton.set_on_click_listener(self.ctdbFile)
		self.numGaneshaIPLabel = gui.Label('IPs for NFS Ganesha', width='70%', height=30, style={'float':'left'})
		self.numGaneshaIPDropDown = gui.DropDown(width='30%', height=30)
		self.numGaneshaIPDropDown.append(' ')
		for num in range(2,51):
			self.numGaneshaIPDropDown.append(str(num))
		self.numGaneshaIPDropDown.select_by_value(' ')
		self.numGaneshaIPDropDown.set_on_change_listener(self.numGaneshaIPDropDownSelected)
		self.enableGaneshaButton = gui.Button('Enable NFS Ganesha',width='100%', height=30)
		self.enableGaneshaButton.set_on_click_listener(self.nfsFile)
		self.sharingContainer.append(self.sharingLabel)
		self.sharingContainer.append(self.publicIPLabel)
		self.sharingContainer.append(self.publicIPEntry)
		self.sharingContainer.append(self.enableCtdbButton)
		self.sharingContainer.append(self.numGaneshaIPLabel)
		self.sharingContainer.append(self.numGaneshaIPDropDown)
		self.sharingContainer.append(self.GaneshaiHostContainer)
		self.sharingContainer.append(self.enableGaneshaButton)
		#_________________________________________________________________________________________________________
		#--------------------------------------Create - Zpool ----------------------------------------------------
		#_________________________________________________________________________________________________________
		self.zpoolDetailsContainer = gui.Widget(width='30%', height='100%',  style={'margin':'0px auto','padding':'5px','border':'2px solid %s'%baseColor,'float':'center','display':'block','overflow':'auto'})
		self.zpoolNameLabel = gui.Label('Name of new zpool:', width='70%', height=30, style={'float':'left'})
		self.zpoolNameInput = gui.TextInput(width='30%', height=30, style={'float':'right'})
		self.zpoolNameInput.set_text('zpool')
		self.zpoolRaidLabel = gui.Label('Select RAID Level', width='70%', height=30, style={'float':'left'})
		self.zpoolRaidSelection = gui.DropDown.new_from_list(('RAIDZ1', 'RAIDZ2', 'RAIDZ3','mirror','stripe'), width='30%', height=30, style={'float':'right'})
		self.zpoolRaidSelection.select_by_value('RAIDZ2')
		self.zpoolVDevLabel = gui.Label('Select # of VDevs', width='70%', height=30, style={'float':'left'})
		self.zpoolVDevSelection = gui.DropDown(width='30%', height=30, style={'float':'right'})
		for number in range(1,31):
			self.zpoolVDevSelection.append(str(number))
		self.zpoolVDevSelection.select_by_value('3')
		self.zpoolBrickLabel = gui.Label('Select # of drives to use', width='70%', height=30, style={'float':'left'})
		self.zpoolBrickSelection = gui.DropDown(width='30%', height=30, style={'float':'right'})
		self.zpoolBrickSelection.append("")
		for number in range(2,60):
			self.zpoolBrickSelection.append(str(number))
		self.zpoolBrickSelection.select_by_value('2')
		self.zpoolAshiftLabel = gui.Label('Ashift value', width='70%', height=30, style={'float':'left'})
		self.zpoolAshiftInput = gui.TextInput(width='30%', height=30, style={'float':'right'})
		self.zpoolAshiftInput.set_text('9')
		self.zpoolCreateButton = gui.Button('Create Zpool', width='100%', height=30)
		self.zpoolCreateButton.set_on_click_listener(self.createZpool)
		self.zpoolDetailsContainer.append(self.zpoolNameLabel)
		self.zpoolDetailsContainer.append(self.zpoolNameInput)
		self.zpoolDetailsContainer.append(self.zpoolRaidLabel)
		self.zpoolDetailsContainer.append(self.zpoolRaidSelection)
		self.zpoolDetailsContainer.append(self.zpoolVDevLabel)
		self.zpoolDetailsContainer.append(self.zpoolVDevSelection)
		self.zpoolDetailsContainer.append(self.zpoolBrickLabel)
		self.zpoolDetailsContainer.append(self.zpoolBrickSelection)
		self.zpoolDetailsContainer.append(self.zpoolAshiftLabel)
		self.zpoolDetailsContainer.append(self.zpoolAshiftInput)
		self.zpoolDetailsContainer.append(self.zpoolCreateButton)
		#_________________________________________________________________________________________________________
		#--------------------------------------Monitor - Volume Configuation--------------------------------------
		#_________________________________________________________________________________________________________
		#--------------------------------------Volume List-------------------------------------------------------
		self.monitorVolumeContainer = gui.Widget(width='10%', height=700, style={'padding':'5px','border':'2px solid %s'%baseColor,'float':'left','display':'block','overflow':'auto'})
		self.volumeLabel = gui.Label('Active Volumes', width='100%', height=30)
		self.volumeList = gui.ListView(width='100%', style={'float':'left'})
		for volume in self.active_Volume_List:
			infoStatus = self.infoTableFunction(volume)[3][1].strip(" ").lower()
			if infoStatus == "started":
				self.volume = gui.ListItem(volume, style={'color':'#29B809'})
			elif infoStatus == "stopped":
				self.volume = gui.ListItem(volume, style={'color':'#FF0000'})
			self.volumeList.append(self.volume)
		self.volumeList.set_on_selection_listener(self.monitorVolumesListSelected)
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
		self.monitorInfoContainer = gui.Widget(width='49%', height=700, style={'padding':'5px','border':'2px solid %s'%baseColor,'float':'left','display':'block','overflow':'auto'})
		self.infoLabel = gui.Label('Volume Info', width='100%', height=30)
		self.infoTable = gui.Table(width='100%',style={'text-align':'left'})
		if noVolumes == True:
			self.infoLine = gui.TableRow()
			self.infoItem0 = gui.TableItem('No Volumes are present')
			self.infoLine.append(self.infoItem0)
			self.infoTable.append(self.infoLine)
		elif noVolumes == False:	
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
		self.monitorStatusContainer = gui.Widget(width='37%', height=700, style={'padding':'5px','border':'2px solid %s'%baseColor,'float':'left','display':'block','overflow':'auto'})
		self.statusLabel = gui.Label('Volume Status',width="100%", height=30)
		self.statusTable = gui.Table(width='100%')
		self.statusTableTitle = gui.TableRow()
		self.statusTableTitle0 = gui.TableItem("Gluster Process")
		self.statusTableTitle1 = gui.TableItem(" ")
		self.statusTableTitle2 = gui.TableItem("TCP Port")
		self.statusTableTitle3 = gui.TableItem("RDMA Port")
		self.statusTableTitle4 = gui.TableItem("Online")
		self.statusTableTitle5 = gui.TableItem("Pid")
		self.statusTableTitle.append(self.statusTableTitle0)
		self.statusTableTitle.append(self.statusTableTitle1)
		self.statusTableTitle.append(self.statusTableTitle2)
		self.statusTableTitle.append(self.statusTableTitle3)
		self.statusTableTitle.append(self.statusTableTitle4)
		self.statusTableTitle.append(self.statusTableTitle5)
		self.statusTable.append(self.statusTableTitle)
		if noVolumes == True:
			self.StatusLine = gui.TableRow()
			self.StatusItem0 = gui.TableItem('No Volumes are present')
			self.StatusLine.append(self.StatusItem0)
			self.statusTable.append(self.StatusLine)
		elif noVolumes == False:	
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
		self.drivesVolumeListContainer = gui.Widget(width='20%', height=700, style={'padding':'5px','border':'2px solid %s'%baseColor,'float':'left','display':'block','overflow':'auto'})
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
		self.monitorDrivesListContainer=gui.Widget(width='15%', height=450, style={'padding':'5px','border':'2px solid %s'%baseColor,'float':'left','display':'block','overflow':'auto'})
		self.driveLabel = gui.Label('Drive Status', width='100%', height=20)
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
		self.monitorDrivesInfoContainer=gui.Widget(width='34%',height=450, style={'padding':'5px','border':'2px solid %s'%baseColor,'float':'left','display':'block','overflow':'auto'})
		self.detailLabel = gui.Label('Brick Storage', width='100%', height=20)
		self.detailTable = gui.Table(width='100%', style={'text-align':'left'})
		self.detailTable.append_from_list(self.detailText())
		self.monitorDrivesInfoContainer.append(self.detailLabel)
		self.monitorDrivesInfoContainer.append(self.detailTable)
		#--------------------------------------Drive Text Box-----------------------------------------------------
		self.monitorDrivesTextBoxContainer = gui.Widget(width='26%', height=450, style={'padding':'5px','border':'2px solid %s'%baseColor,'float':'left','display':'block','overflow':'auto'})
		self.driveInfoTextLabel = gui.Label('Drive Info', height=30, width='100%')
		self.driveInfoTable = gui.Table(width='100%', style={'text-align':'left'})
		self.driveInfoDefault = gui.TableRow()
		self.driveInfoDefaultItem = gui.TableItem('Select Drive From List To View')
		self.driveInfoDefault.append(self.driveInfoDefaultItem)
		self.driveInfoTable.append(self.driveInfoDefault)
		self.monitorDrivesTextBoxContainer.append(self.driveInfoTextLabel)
		self.monitorDrivesTextBoxContainer.append(self.driveInfoTable)
		#--------------------------------------Drive health box---------------------------------------------------
		self.monitorDrivesHealthContainer = gui.Widget(width='75%', height = 236 ,style={'padding':'5px','border':'2px solid %s'%baseColor,'float':'left','display':'block','overflow':'auto'})
		self.healthListLabel = gui.Label('Drive Health',width='100%', height=15)
		self.healthTable = gui.Table(width='100%',style={'text-align':'left'})
		healthStats = self.getDriveHealth()
		for line in healthStats:
			self.healthLine = gui.TableRow()
			self.healthItem0 = gui.TableItem(line[0])
			self.healthItem1 = gui.TableItem(line[1].replace("_"," ").title())
			self.healthItem9 = gui.TableItem(line[9].replace("_"," ").title())
			self.healthLine.append(self.healthItem0)
			self.healthLine.append(self.healthItem1)
			self.healthLine.append(self.healthItem9)
			self.healthTable.append(self.healthLine)
		self.monitorDrivesHealthContainer.append(self.healthListLabel)
		self.monitorDrivesHealthContainer.append(self.healthTable)
		#_________________________________________________________________________________________________________
		#--------------------------------------Monitor ZPool------------------------------------------------------
		#_________________________________________________________________________________________________________
		self.monitorZpoolZpoolContainer = gui.Widget(width='35%', height=700, style={'padding':'5px','border':'2px solid %s'%baseColor,'float':'left','display':'block','overflow':'auto'})
		self.monitorZpoolLabel = gui.Label('Active Zpools (Select name of zpool to view)', width='100%', height=30)
		self.monitorZpoolTable = gui.Table(width='100%')
		if noZpools == True:
			self.zpoolLine = gui.TableRow()
			self.nozpool = gui.TableItem("No Zpools Present")
			self.zpoolLine.append(self.nozpool)
			self.monitorZpoolTable.append(self.zpoolLine)
		if noZpools == False:
			for line in self.getZpoolStats():
				self.zpoolLine = gui.TableRow()
				self.zpoolName = gui.TableItem(" "+line[0])
				self.zpoolSize = gui.TableItem(line[1])
				self.zpoolAlloc = gui.TableItem(line[2])
				self.zpoolFree = gui.TableItem(line[3])
				self.zpoolHealth = gui.TableItem(line[8])
				self.zpoolLine.append(self.zpoolName)
				self.zpoolLine.append(self.zpoolSize)
				self.zpoolLine.append(self.zpoolAlloc)
				self.zpoolLine.append(self.zpoolFree)
				self.zpoolLine.append(self.zpoolHealth)
				self.monitorZpoolTable.append(self.zpoolLine)
		self.monitorZpoolTable.set_on_table_row_click_listener(self.zpoolTableClicked)
		self.deleteZpoolButton = gui.Button('Delete %s'%zpoolChoice, width='100%', height=30, style={'background-color':'#FF0000'})
		self.deleteZpoolButton.set_on_click_listener(self.deleteZpool)
		self.monitorZpoolZpoolContainer.append(self.monitorZpoolLabel)
		self.monitorZpoolZpoolContainer.append(self.monitorZpoolTable)
		self.monitorZpoolZpoolContainer.append(self.deleteZpoolButton)
		#--------------------------------------Zpool status-------------------------------------------------------
		self.monitorZpoolStatusContainer = gui.Widget(width='45%', height=700, style={'padding':'5px', 'border':'2px solid %s'%baseColor,'float':'left','display':'block','overflow':'auto'})
		self.zpoolStatusLabel = gui.Label('Zpool Status', width='100%', height=30)
		self.zpoolStatusTable = gui.Table(width='100%')
		if noZpools == True:
			self.noZpoolLine = gui.TableRow()
			self.noZpoolLine1 = gui.TableItem('No Zpools Present')
			self.noZpoolLine.append(self.noZpoolLine1)
			self.zpoolStatusTable.append(self.noZpoolLine)
		if noZpools == False:
			for line in self.getZpoolStatus():
				self.zpoolStatusLine = gui.TableRow()
				self.zpoolStatusName = gui.TableItem(line[0])
				self.zpoolState = gui.TableItem(line[1])
				self.zpoolRead = gui.TableItem(line[2])
				self.zpoolWrite = gui.TableItem(line[3])
				self.zpoolCksum = gui.TableItem(line[4])
				self.zpoolStatusLine.append(self.zpoolStatusName)
				self.zpoolStatusLine.append(self.zpoolState)
				self.zpoolStatusLine.append(self.zpoolRead)
				self.zpoolStatusLine.append(self.zpoolWrite)
				self.zpoolStatusLine.append(self.zpoolCksum)
				self.zpoolStatusTable.append(self.zpoolStatusLine)
		self.monitorZpoolStatusContainer.append(self.zpoolStatusLabel)
		self.monitorZpoolStatusContainer.append(self.zpoolStatusTable)
		#_________________________________________________________________________________________________________
		#--------------------------------------Front end configuation---------------------------------------------
		#_________________________________________________________________________________________________________
		#--------------------------------------Appending containers-----------------------------------------------
		global hostsInputContainer
		mainContainer = gui.Widget(width='100%', height='100%', style={'id':'MainContainer'})#,'background-color':'%s'%baseColor,'margin':'0px auto','display': 'block', 'overflow':'auto'})
		monitorContainer = gui.Widget(width='100%', height='100%', style={'background-color':'%s'%baseColor,'margin':'0px auto','display': 'block', 'overflow':'auto'})
		mainCreateContainer = gui.Widget(width='100%', height='100%', style={'background-color':'%s'%baseColor,'margin':'0px auto','display': 'block', 'overflow':'auto'})
		mainMenuContainer = gui.Widget(width='100%', height='100%', style={'background-color':'%s'%baseColor, 'margin':'0px auto','display': 'block', 'overflow':'auto'})
		monitorVolumeContainer = gui.Widget(width='100%', height='100%', style={'background-color':'%s'%baseColor, 'margin':'0px auto','display': 'block', 'overflow':'auto'})
		monitorDrivesContainer = gui.Widget(width='100%', height='100%', style={'background-color':'%s'%baseColor, 'margin':'0px auto','display': 'block', 'overflow':'auto'})
		monitorZpoolContainer = gui.Widget(width='100%', height='100%', style={ 'background-color':'%s'%baseColor,'margin':'0px auto','display': 'block', 'overflow':'auto'})
		createContainer = gui.Widget(width='100%', style={'background-color':'%s'%baseColor,'margin':'0px auto','display': 'block', 'overflow':'auto'})
		createZpoolContainer = gui.Widget(width='100%', height='100%', style={'background-color':'%s'%baseColor,'margin':'0px auto','display': 'block', 'overflow':'auto'})
		#--------------------------------------Main Menu----------------------------------------------------------
		mainMenuContainer.append(self.mainMenuVolumeContainer)
		mainMenuContainer.append(self.overviewTableContainer)
		mainMenuContainer.append(self.settingsContainer)
		#--------------------------------------Create menu--------------------------------------------------------
		createContainer.append(createHostsContainer)
		hostsInputContainer = gui.Widget(width='100%', height=200, style={'display': 'block', 'overflow':'auto'})
		self.advancedContainer = gui.Widget(width='100%', height=150, style={'display':'block', 'overflow':'auto'})
		createContainer.append(self.glusterDetailsContainer)
		createContainer.append(self.sharingContainer)
		#--------------------------------------Create Zpool menu--------------------------------------------------
		createZpoolContainer.append(self.zpoolDetailsContainer)
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
		#--------------------------------------Monitor Zpool Menu-------------------------------------------------
		monitorZpoolContainer.append(self.monitorZpoolZpoolContainer)
		monitorZpoolContainer.append(self.monitorZpoolStatusContainer)
		#--------------------------------------Create TabBox -----------------------------------------------------
		self.createTabBox = gui.TabBox(style={'id':'CreateTabBox'})#'background-color':'%s'%baseColor})
		self.createTabBox.add_tab(createContainer, "Create - Volume", None)
		self.createTabBox.add_tab(createZpoolContainer, "Create - Zpool", None)
		mainCreateContainer.append(self.createTabBox)
		#--------------------------------------Monitor tabbox-----------------------------------------------------
		self.monitorTabBox = gui.TabBox(style={'id':'MonitorTabBox'})#'background-color':'%s'%baseColor, 
		self.monitorTabBox.add_tab(monitorVolumeContainer, "Monitor - Volume", None)
		self.monitorTabBox.add_tab(monitorDrivesContainer, "Monitor - Drives", None)
		self.monitorTabBox.add_tab(monitorZpoolContainer, "Monitor - Zpool", None)
		monitorContainer.append(self.monitorTabBox)
		#--------------------------------------TabBox configuation------------------------------------------------
		self.mainTabBox = gui.TabBox(style={'id':'MainTabBox'})
		self.mainTabBox.add_tab(mainMenuContainer, "Main Menu", None)
		self.mainTabBox.add_tab(mainCreateContainer, "Create", None)
		self.mainTabBox.add_tab(monitorContainer, "Monitor", None)

		#----------------------------------FINAL LAYOUT CONFIG----------------------------------------------------
		mainContainer.append(self.mainTabBox)


		return mainContainer


	#_____________________________________________________________________________________________________________
	#-----------------------------------------------Functions-----------------------------------------------------
	def retrieveVolumes(self):
		subprocess.call(['cd ~'], shell=True)
		s=subprocess.Popen(["gluster volume list"], shell=True, stdout=subprocess.PIPE).stdout
		glusters = s.read().splitlines()
		return glusters

	def updateVolumeLists(self):
		global confirmedStop
		confirmedStop = False
		self.volumeList.empty()
		self.activeVolumeList.empty()
		self.drivesVolumeList.empty()
		volumeList = self.retrieveVolumes()

		for volume in volumeList:
			status = self.infoTableFunction(volume)[3][1].strip(" ").lower()
			if status == "started":
				self.volume = gui.ListItem(volume, style={'color':'#29B809'})
			elif status == "stopped":
				self.volume = gui.ListItem(volume, style={'color':'#FF0000'})
			self.volumeList.append(self.volume)
			self.activeVolumeList.append(self.volume)
			self.drivesVolumeList.append(self.volume)
	
	def updateMonitorTables(self):
		self.statusTable.empty()
		self.statusTableTitle = gui.TableRow()
		self.statusTableTitle0 = gui.TableItem("Gluster Process")
		self.statusTableTitle1 = gui.TableItem(" ")
		self.statusTableTitle2 = gui.TableItem("TCP Port")
		self.statusTableTitle3 = gui.TableItem("RDMA Port")
		self.statusTableTitle4 = gui.TableItem("Online")
		self.statusTableTitle5 = gui.TableItem("Pid")
		self.statusTableTitle.append(self.statusTableTitle0)
		self.statusTableTitle.append(self.statusTableTitle1)
		self.statusTableTitle.append(self.statusTableTitle2)
		self.statusTableTitle.append(self.statusTableTitle3)
		self.statusTableTitle.append(self.statusTableTitle4)
		self.statusTableTitle.append(self.statusTableTitle5)
		self.statusTable.append(self.statusTableTitle)
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
			self.infoTable.append(self.infoLine) #Updates monitor tables by emptying and recreating it

	def overviewTableUpdate(self):
		self.lclHost2.set_text((socket.gethostname()))
		self.ipAddr2.set_text(socket.gethostbyname(socket.gethostname()))
		self.numVolumes2.set_text(len(self.retrieveVolumes()))
		self.numActVolumes2.set_text((self.getNumActVolumes()))
		self.numStVolumes2.set_text(self.getNumStoppedVolumes())
		self.numDrives2.set_text(len(self.driveMapTable())-1)
		self.numActDrives2.set_text(self.getNumActDrives())
		self.numStDrives2.set_text(self.getNumStDrives())
		self.numZpool2.set_text(len(self.getZpoolStats())-1)

	def changeSettings(self, widget):
		newPort = self.portEntry.get_text()
		newUsername = self.usernameEntry.get_text()
		newPassword = self.passwordEntry.get_text()
		newColor = self.defaultColorPicker.get_value()
		if newPort > 8099 or newPort < 8000:
			print "Error 404: Port ID must only be between 8000 and 8099"
			self.notification_message("Error 404", "Port ID must only be between 8000 and 8099")
			return 0
		for char in newUsername:
			if (char < '0' or char > 'z') or (char > '9' and char < 'A') or (char > 'Z' and char < 'a'): 
				print 'Error 405: Username must be alphanumeric'
				self.notification_message('Error 405', "You can't use special characters (%s) in username"%(char))
				return 0
		for char in newPassword:
			if (char < '0' or char > 'z') or (char > '9' and char < 'A') or (char > 'Z' and char < 'a'): 
				print 'Error 406: Password must be alphanumeric'
				self.notification_message('Error 406', "You can't use special characters (%s) in username"%(char))
				return 0
		conf = open('45dash.conf', 'w+')
		conf.write("port=%s\nusername=%s\npassword=%s\ndefaultcolor=%s\nlastBrick=%s\n"%(int(newPort), newUsername, newPassword, newColor, int(lastBrick)))
		conf.close() 
	#_____________________________________________________________________________________________________________
	#-----------------------------------------------Main menu functions-------------------------------------------
	def getNumActVolumes(self):
		volume_List = self.retrieveVolumes()
		count = 0
		for volume in volume_List:
			status = self.infoTableFunction(volume)[3][1].strip(" ").lower()
			if status == "started":
				count = count + 1
			else:
				inte = 1
		return str(count)

	def getNumStoppedVolumes(self):
		volume_List = self.retrieveVolumes()
		count = 0
		for volume in volume_List:
			status = self.infoTableFunction(volume)[3][1].strip(" ").lower()
			if status == "stopped":
				count = count + 1
		return str(count)

	def getNumActDrives(self):
		count = 0
		drives = self.driveMapTable()
		for entry in drives:
			driveAlias1 = str(entry)
			driveAlias1 = driveAlias1.strip("*")
			driveAlias1 = driveAlias1.strip("['")
			driveAlias1 = driveAlias1.strip("']")
			char1 = str(driveAlias1)
			if char1[0] == "*":
				if char1[1] == "*":
					count = count + 1
		return count

	def getNumStDrives(self):
		count = 0
		drives = self.driveMapTable()
		for entry in drives:
			driveAlias1 = str(entry)
			driveAlias1 = driveAlias1.strip("*")
			driveAlias1 = driveAlias1.strip("['")
			driveAlias1 = driveAlias1.strip("']")
			char1 = str(driveAlias1)
			if char1[0] == "*":
				if char1[1] != "*":
					count = count + 1
		return count
	#-----------------------------------------------Create functions----------------------------------------------
	def saveHosts(self):
		global hostsConf, numHosts
		hosts = []
		try:
			numHosts
		except NameError:
			numHosts = None
		if numHosts == None:
			self.notification_message('Error','You must configure your hosts')
			return 0
		for num in range(1, numHosts+1):
			hosts.append(hostsInputContainer.children[num].get_text())
		for entry in hosts:
			for char in entry:
				if (char < '0' or char > 'z') or (char > '9' and char < 'A') or (char > 'Z' and char < 'a'): 
					self.notification_message('Error!', "You can't use special characters (%s) in server name"%(char))
					hostsConf = 401
					return 0
		hostsConf = "[hosts]\n"
		for entry in hosts:
			hostsConf = hostsConf + "%s\n"%entry

	def hostsInputDropDownFunction(self, widget, selection):
		global localHost, numHosts, hostsList
		if selection == '':
			return 0
		hostsList = {}
		hostsInputContainer.empty()
		numHosts = int(selection)
		for num in range(1,numHosts+1):
			if num % 2 == 1:
				self.hostInput = gui.TextInput(width='50%', key=num, height=30, style={'float':'left'})
			if num % 2 == 0:
				self.hostInput = gui.TextInput(width='50%', height=30, style={'float':'right'})
			if num == 1:
				self.hostInput.set_text(localHost)
			else:
				self.hostInput.set_text(connectedHostNames[num-1])
			hostsList[num] = (self.hostInput.get_text())
			hostsInputContainer.append(self.hostInput, num)
		createHostsContainer.append(hostsInputContainer)

	def showAdvanced(self, widget):
		global isAdvanced
		if isAdvanced == False:
			self.advancedCheckButton.set_text('Hide Advanced Options')
			isAdvanced = True
			self.advancedContainer.empty()
			self.ashiftLabel = gui.Label('ashift value:', width='70%', height=30, style={'float':'left'})
			self.ashiftInput = gui.TextInput(width='30%', height=30, style={'float':'right'})
			self.ashiftInput.set_text('9')
			self.paddingLabel = gui.Label('Padding (%)', width='70%', height=30, style={'float':'left'})
			self.paddingInput = gui.TextInput(width='30%', height=30, style={'float':'right'})
			self.paddingInput.set_text("95")
			self.arbiterLabel = gui.Label('Arbiter Bricks (?)', width='70%', height=30, style={'float':'left'})
			self.arbiterInput = gui.TextInput(width='30%', height=30, style={'float':'right'})
			self.arbiterInput.set_text("100G")
			self.advancedContainer.append(self.ashiftLabel)
			self.advancedContainer.append(self.ashiftInput)
			self.advancedContainer.append(self.paddingLabel)
			self.advancedContainer.append(self.paddingInput)
			self.advancedContainer.append(self.arbiterLabel)
			self.advancedContainer.append(self.arbiterInput)
			self.glusterDetailsContainer.append(self.advancedContainer)
		elif isAdvanced == True:
			self.advancedContainer.empty()
			self.advancedCheckButton.set_text('Show Advanced Options')
			isAdvanced = False

	def reset(self, widget):
		self.nameInput.set_text('NewVolume')
		self.raidSelection.select_by_value('RAIDZ2')
		self.vDevSelection.select_by_value('3')
		self.brickSelection.select_by_value('8')
		self.driveSelection.select_by_value(str(len(self.driveMapTable())-1))
		self.glusterSelection.select_by_value('Distributed')
		self.tuningSelection.select_by_value('SMB Filesharing')

	def gDeployFile(self):
		global lastBrick
		global ctdbText
		global nfsText
		subprocess.call(['cd ~'], shell=True)
		f = open("deploy-cluster.conf","w+")
		f.write(hostsConf)
		f.write("\n[tune-profile]\nthroughput-performance\n\n[service1]\naction=enable\nservice=ntpd\nignore_errors=no\n\n[service2]\naction=start\nservice=ntpd\nignore_errors=no\n\n[service3]\naction=disable\nservice=firewalld\nignore_errors=no\n\n[service4]\naction=stop\nservice=firewalld\nignore_errors=no\n\n[service5]\naction=enable\nservice=glusterd\nignore_errors=no\n\n[service6]\naction=start\nservice=glusterd\nignore_errors=no\n\n")
		f.write("[script1]\n")
		f.write("action=execute\nfile=/opt/gtools/bin/dmap -qs 60\n")
		f.write("ignore_script_errors=no\n\n")
		vDevs = self.vDevSelection.get_value()
		raidLevel = self.raidSelection.get_value()
		if isAdvanced:
			f.write("[script2]\naction=execute\nfile=/opt/gtools/bin/zcreate -v %s -l %s -n zpool -d %s -a %s -bq\n"%(vDevs, raidLevel.lower(), self.driveSelection.get_value(), str(self.ashiftInput.get_text())))
		elif not isAdvanced:
			f.write("[script2]\naction=execute\nfile=/opt/gtools/bin/zcreate -v %s -l %s -n zpool -d %s -a 9 -bq\n"%(vDevs, raidLevel.lower(), self.driveSelection.get_value()))
		f.write("ignore_script_errors=no\n\n")
		bricks = self.brickSelection.get_value()
		if isAdvanced:
			f.write("[script3]\naction=execute\nfile=/opt/gtools/bin/mkbrick -n zpool -A %s -C -b %s -p %s -fq\n"%(self.arbiterInput.get_text() ,bricks, str(self.paddingInput.get_text())))
		elif not isAdvanced:
			f.write("[script3]\naction=execute\nfile=/opt/gtools/bin/mkbrick -n zpool -A 100G -C -b %s -p 95 -fq\n"%(bricks))
		f.write("ignore_script_errors=no\n\n[update-file1]\naction=edit\ndest=/usr/lib/systemd/system/zfs-import-cache.service\nreplace=ExecStart=\nline=ExecStart=/usr/local/libexec/zfs/startzfscache.sh\n\n")
		f.write("[script5]\naction=execute\nfile=/opt/gtools/bin/startzfscache\nignore_script_errors=no\n\n")
		
		glusterConfig = self.glusterSelection.get_value()
		glusterName = self.nameInput.get_text()
		mkarbcmd = "/opt/gtools/bin/mkarb -b %d"%int(bricks)
		for num in range(1, numHosts+1):
			mkarbcmd = mkarbcmd + " -n %s"%(hostsInputContainer.children[num].get_text())
		r = subprocess.Popen(mkarbcmd, shell=True, stdout=subprocess.PIPE).stdout
		mkarb = r.read()
		tuneProfile = self.tuningSelection.get_value()
		f.write("[volume1]\naction=create\nvolname=%s\n"%glusterName)
		if glusterConfig == 'Distributed':
			mkarb = ""
			for i in range(int(lastBrick)+1, int(bricks)+int(lastBrick)+1):
				mkarb = mkarb+"/zpool/vol"+str(i)+"/brick,"
				lastBrick = int(lastBrick) + 1
			f.write("replica_count=0\nforce=yes\n")
			if tuneProfile == 'SMB filesharing':
				f.write("key=performance.parallel-readdir,network.inode-lru-limit,performance.md-cache-timeout,performance.cache-invalidation,performance.stat-prefetch,features.cache-invalidation-timeout,features.cache-invalidation,performance.cache-samba-metadata\nvalue=on,50000,600,on,on,600,on,on\n")
			elif tuneProfile == 'Virtualization':
				f.write("key=group,storage.owner-uid,storage.owner-gid,network.ping-timeout,performance.strict-o-direct,network.remote-dio,cluster.granular-entry-heal,features.shard-block-size\nvalue=virt,36,36,30,on,off,enable,64MB\n")
			f.write("brick_dirs=%s"%mkarb)
		if glusterConfig == 'Distributed Replicated':
			f.write("replica_count=3\narbiter_count=1\nforce=yes\nkey=performance.parallel-readdir, network.inode-lru-limit, performance.md-cache-timeout, performance.cache-invalidation, performance.stat-prefetch, features.cache-invalidation-timeout, features.cache-invalidation, performance.cache-samba-metadata\nvalue=on,50000,600,on,on,600,on,on\nbrick_dirs=%s"%mkarb)
			if tuneProfile == 'SMB filesharing':
				f.write("key=performance.parallel-readdir,network.inode-lru-limit,performance.md-cache-timeout,performance.cache-invalidation,performance.stat-prefetch,features.cache-invalidation-timeout,features.cache-invalidation,performance.cache-samba-metadata\nvalue=on,50000,600,on,on,600,on,on\nbrick_dirs=%s"%mkarb)
			elif tuneProfile == 'Virtualization':
				f.write("key=group,storage.owner-uid,storage.owner-gid,network.ping-timeout,performance.strict-o-direct,network.remote-dio,cluster.granular-entry-heal,features.shard-block-size\nvalue=virt,36,36,30,on,off,enable,64MB\nbrick_dirs=%s"%mkarb)
		f.write(ctdbText)
		f.write("\n\n"+nfsText)
		f.close()

	def createPress(self, widget):
		global lastBrick, hostsConf
		self.saveHosts()
		try:
			numHosts
		except NameError:
			numHosts = None
		if numHosts == None:
			return 0
		if (int(self.brickSelection.get_value()) % int(numHosts) != 0) and (ctdbEnabled == True):
			self.notification_message("Error",'# of bricks must be a multiple of replica count')
			return 0
		isRetry = False
		name = self.nameInput.get_text()
		for char in name:
			if (char < '0' or char > 'z') or (char > '9' and char < 'A') or (char > 'Z' and char < 'a'): 
				self.notification_message('Error 401', "You can't use special characters (%s) in gluster name"%(char))
				print "Error 401: Invalid Character used for a name"
				return 0
		start = time.time()
		if hostsConf == 401:
			print "Error 401: Invalid Character used for a name"
			return 0
		if len(self.retrieveVolumes()) != 0:
			for entry in self.retrieveVolumes():
				if name == entry:
					self.notification_message("Error 402", "The name %s is already in use by another gluster"%(name))
					print "Error 402: Name in use"
					return 0
		estimatedTime = random.uniform(79.4, 90.0)
		if nfsEnabled == True:
			estimatedTime = estimatedTime + 30
		if ctdbEnabled == True:
			estimatedTime = estimatedTime + 30
		self.notification_message("Action", "%s is in the oven, estimated time: %s seconds "%(self.nameInput.get_text(), str(round(estimatedTime, 2))))
		entries1 = len(self.retrieveVolumes())
		self.gDeployFile()
		subprocess.call(['gdeploy -c deploy-cluster.conf'], shell=True)
		end = time.time()
		totalTime = end-start
		newEntries = len(self.retrieveVolumes())
		if entries1 == newEntries:
			if not isRetry:
				self.notification_message("Error!", "Don't know what happened but %s couldn't be made. May have been an issue with brick directory, trying again"%self.nameInput.get_text())
				lastBrick = lastBrick+20
				self.gDeployFile()
				subprocess.call(['gdeploy -c deploy-cluster.conf'], shell=True)
				isRetry = True
				totalTime = totalTime*2
			if isRetry:
				if len(self.retrieveVolumes()) == newEntries:
					self.notification_message("Error!", "Don't know what happened but %s couldn't be made."%self.nameInput.get_text())
				else:
					self.notification_message("Success!", "%s has been made, in %s seconds!"%(self.nameInput.get_text(), str(round(totalTime, 2))))
		else:
			currentVolumeList = newEntries
			noVolumes = False
			noZpools = False
			self.updateVolumeLists()
			self.updateMonitorTables()
			self.overviewTableUpdate()
			self.updateZpools()		
			self.notification_message("Success!", "%s has been made, in %s seconds!"%(self.nameInput.get_text(), str(round(totalTime, 2))))
			newPort = self.portEntry.get_text()
			newUsername = self.usernameEntry.get_text()
			newPassword = self.passwordEntry.get_text()
			newColor = self.defaultColorPicker.get_value()
			if newPort > 8099 or newPort < 8000:
				print "Error 404: Port ID must only be between 8000 and 8099"
				self.notification_message("Error 404", "Port ID must only be between 8000 and 8099")
				return 0
			for char in newUsername:
				if (char < '0' or char > 'z') or (char > '9' and char < 'A') or (char > 'Z' and char < 'a'): 
					print 'Error 405: Username must be alphanumeric'
					self.notification_message('Error 405', "You can't use special characters (%s) in username"%(char))
					return 0
			for char in newPassword:
				if (char < '0' or char > 'z') or (char > '9' and char < 'A') or (char > 'Z' and char < 'a'): 
					print 'Error 406: Password must be alphanumeric'
					self.notification_message('Error 406', "You can't use special characters (%s) in username"%(char))
					return 0
			conf = open('45dash.conf', 'w+')
			conf.write("port=%s\nusername=%s\npassword=%s\ndefaultcolor=%s\nlastBrick=%s\n"%(int(newPort), newUsername, newPassword, newColor, int(lastBrick)))
			conf.close() 
		if entries1 != 0:
			self.updateVolumeLists()

	def createZpool(self, widget):
		subprocess.call(['zcreate -d %s -l %s -n %s -v %s -b'%(self.zpoolBrickSelection.get_value(), self.zpoolRaidSelection.get_value().lower(),self.zpoolNameInput.get_text(),self.zpoolVDevSelection.get_value())], shell=True)
	def ctdbFile(self, widget):
		global ctdbText
		global ctdbEnabled
		if ctdbEnabled == True:
			self.notification_message('Action', 'CTDB disabled')
			self.enableCtdbButton.set_text('Enable CTDB')
			ctdbEnabled = False
			ctdbText = ' '
		elif ctdbEnabled == False:
			ctdbEnabled = True
			self.notification_message('Action', 'CTDB Enabled')
			self.enableCtdbButton.set_text('Disable CTDB')
			r = subprocess.Popen(['nmcli connection show'], shell=True, stdout=subprocess.PIPE).stdout
			lines = r.read().splitlines()
			results = []
			for line in lines:
				splitText = line.split()
				results.append(splitText)
			deviceType = results[1][3]
			publicIP = self.publicIPEntry.get_text()
			ctdbText = "\n\n[volume2]\naction=create\nvolname=ctdb\nreplica_count=%s\nforce=yes\nbrick_dirs=/zpool/ctdb/brick\nignore_errors=no\n\n"%(numHosts)
			ctdbText = ctdbText + "[ctdb]\naction=setup\npublic_address=%s %s\nctdb_nodes="%(publicIP, deviceType)
			for entry in connectedHostNames:
				ctdbText=ctdbText+socket.gethostbyname(entry)+','
			ctdbText = ctdbText+"\nvolname=ctdb\n\n[script4]\naction=execute\nfile=/opt/gtools/bin/ctdb-config-d /gluster/lock -g -m smb -w"
			print ctdbText

	def numGaneshaIPDropDownSelected(self, widget, selection):
		global numGanesha
		global ganeshaList
		if selection == '':
			return 0
		self.GaneshaiHostContainer.empty()
		numGanesha = int(selection)
		for num in range(1, numGanesha+1):
			if num % 2 == 1:
				self.ipInput = gui.TextInput(width='50%', height=30, style={'float':'left'})
			if num % 2 == 0:
				self.ipInput = gui.TextInput(width='50%', height=30, style={'float':'right'})
			self.ipInput.set_text('192.168.16.%s'%num)
			self.GaneshaiHostContainer.append(self.ipInput, num)
		ganeshaList = []
		for num in range(1, numGanesha+1):
			ganeshaList.append(self.GaneshaiHostContainer.children[num].get_text())

	def nfsFile(self, widget):
		global nfsText, nfsEnabled, ganeshaList
		if ganeshaList == []:
			self.notification_message('Error','Input valid IPs')
			return 0
		if nfsEnabled == True:
			self.notification_message('Action','NFS Ganesha Disabled')
			self.enableGaneshaButton.set_text('Enable NFS Ganesha')
			nfsEnabled = False
			nfsText = ' '
		elif nfsEnabled == False:
			nfsText = "[nfs-ganesha]\naction=create-cluster\nha-name=ganesha-ha-360\ncluster-nodes="
			hosts = []
			try:
				numHosts
			except NameError:
				numHosts = None
			if numHosts == None:
				self.notification_message('Error','You must configure your hosts')
				return 0
			for num in range(1, numHosts+1):
				hosts.append(hostsInputContainer.children[num].get_text())
			for entry in hosts:
				nfsText = nfsText + entry + ','
			nfsText = nfsText + '\nvip='
			for entry in ganeshaList:
				nfsText = nfsText + entry + ','
			nfsText = nfsText+"\n\n[service7]\naction=enable\nservice=corosync\nignore_errors=no\n\n[service8]\naction=start\nservice=corosync\nignore_errors=no\n\n[service9]\naction=enable\nservice=pacemaker\nignore_errors=no\n\n[service10]\naction=start\nservice=pacemaker\nignore_errors=no\n\n[service11]\naction=enable\nservice=pscd\nignore_errors=no\n\n[service12]\naction=start\nservice=pscd\nignore_errors=no\n\n"
			nfsEnabled = True
			self.enableGaneshaButton.set_text('Disable NFS Ganesha')
			self.notification_message('Action','NFS Ganesha Enabled')
		print nfsText

	#-----------------------------------------------Monitor Functions---------------------------------------------
	def infoTableFunction(self, choice):
		if noVolumes == True:
			print 'No Volumes'
			return 'No Volumes'
		elif noVolumes == False:
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

	def monitorVolumesListSelected(self, widget, selection):
		global choice
		stopIsConfirmed = False
		deleteIsConfirmed = False
		if selection == None:
			return 0
		choice = self.volumeList.children[selection].get_text()
		self.stopButton.set_text("Stop %s"%choice)
		self.startButton.set_text("Start %s"%choice)
		self.deleteButton.set_text("Delete %s"%choice)
		self.updateVolumeLists()
		self.updateMonitorTables()

	def startGluster(self, widget):
		self.notification_message("Action","%s will be started"%choice)
		subprocess.call(["gluster volume start %s"%choice], shell=True)
		numActVol = self.getNumActVolumes()
		numVol = len(self.retrieveVolumes())
		self.updateMonitorTables()
		self.updateVolumeLists()
		self.numActVolumes2.set_text((str(numActVol)))
		self.numStVolumes2.set_text(str(int(numVol)-int(numActVol)))
		self.notification_message("Success", "%s has been started"%choice)
	
	def stopGluster(self, widget):
		global stopIsConfirmed
		if stopIsConfirmed == True:
			self.notification_message("Action","%s will be stopped, this may take a few seconds"%choice)
			initialStatus = self.infoTableFunction(choice)[3][1].strip(" ").lower()
			if initialStatus == 'started':
				subprocess.call(["echo 'y' | gluster volume stop %s"%(choice)], shell=True)
				currentStatus = self.infoTableFunction(choice)[3][1].strip(" ").lower()
				if currentStatus == 'stopped':
					self.updateVolumeLists()
					self.updateMonitorTables()
					numActVol = self.getNumActVolumes()
					numVol = len(self.retrieveVolumes())
					self.numActVolumes2.set_text((str(numActVol)))
					self.numStVolumes2.set_text(str(int(numVol)-int(numActVol)))
					self.notification_message("Success", "Gluster Volume %s has been stopped"%choice)
				if currentStatus != 'stopped':
					self.notification_message("Error!", "Gluster volume %s couldn't be stopped"%choice)
			else:
				self.notification_message("Error!", "Gluster volume %s is already stopped"%choice)
			stopIsConfirmed == False
			return 0

		elif stopIsConfirmed == False:
			self.notification_message("Warning!","Deleting a gluster will make its data inaccesible, press again to confirm")
			stopIsConfirmed = True
	
	def deleteGluster(self, widget):
		global choice
		global deleteIsConfirmed
		if deleteIsConfirmed:
			self.notification_message("Action","%s will be deleted, this may take a few seconds"%choice)
			numVol = len(self.retrieveVolumes())
			if numVol == 1:
				self.notification_message("Error 403", "Last present gluster, ending will cause dashboard to fail")
				print "Error 403: Cannot delete last gluster"
				return 403
			subprocess.call(["echo 'y' | gluster volume delete %s"%(choice)], shell=True)
			numVol2 = len(self.retrieveVolumes())
			if numVol2 == numVol:
				self.notification_message("Error!","Gluster Volume %s wasn't deleted"%choice )
				return 0
			choice = self.retrieveVolumes()[0]
			numActVol = self.getNumActVolumes()
			self.updateMonitorTables()
			self.numActVolumes2.set_text((str(numActVol)))
			self.numStVolumes2.set_text(str(int(numVol)-int(numActVol)))	
			self.updateVolumeLists()
			self.notification_message("Success", "Gluster Volume %s has been deleted"%choice)
			return 0
		elif not deleteIsConfirmed:
			self.notification_message("Warning", "Deleting a volume can be dangerous, press again to continue")
			deleteIsConfirmed = True
			return 0
	
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
	#------------------------------------------------Drives--------------------------------------------
	def driveVolumeListSelected(self, widget, selection):
		global choice
		choice = self.drivesVolumeList.children[selection].get_text()
		self.detailTable.empty()
		self.detailTable.append_from_list(self.detailText())

	def detailText(self):
		r = subprocess.Popen(["gluster volume status %s detail | grep Space"%choice],stdout=subprocess.PIPE, shell=True).stdout
		lines = r.read().splitlines()
		lineCount = 0
		for entry in lines:
			lineCount = lineCount+1
		numBricks = lineCount/2
		bricks = []
		bricks2 = []
		lineParse=0
		for num in range(0,numBricks):
			bricks.append(str("Brick "+str(num)+": /"+lines[lineParse].strip(" ")+"/"+lines[lineParse+1].strip(" ")))
			lineParse = lineParse+2
		for line in bricks:
			splitBricks = re.split(r"/", line)
			bricks2.append(tuple(splitBricks))
		return bricks2

	def driveMapTable(self):
		r = subprocess.Popen("/bin/45dash/lsdevpy -n", stdout=subprocess.PIPE, shell=True).stdout
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
		if self.driveList.children[selection].get_text() == "Drive Alias":
			return 0
		global brick
		brick = self.driveList.children[selection].get_text()
		s=subprocess.Popen(["hdparm -I /dev/disk/by-vdev/%s"%brick], shell=True, stdout=subprocess.PIPE).stdout
		lines = s.read().splitlines()
		r = subprocess.Popen(["df /dev/disk/by-vdev/%s"%brick], shell=True, stdout=subprocess.PIPE).stdout
		lines2 = s.read().splitlines()
		unsplitList = []
		modelNumber = lines[4]
		serialNumber = lines[5]
		firmwareRevision = lines[6]
		unsplitList.append(modelNumber)
		unsplitList.append(serialNumber)
		unsplitList.append(firmwareRevision)
		q = subprocess.Popen(["smartctl -a /dev/disk/by-vdev/%s | grep 'Rotation Rate'"%brick], shell=True, stdout=subprocess.PIPE).stdout
		lines3 = q.read().splitlines()
		for line in lines3:
			if line == "Rotation Rate:    Solid State Device":
				driveType = "\t Type: Solid State Drive"
			else:
				driveType = "Type: Hard Disk Drive "+line
		unsplitList.append(driveType)
		splitList = []
		for entry in unsplitList:
			newEntry = re.split(r':', entry)
			splitList.append(newEntry)
		self.driveInfoTable.empty()
		for entry in splitList:
			self.infoLine = gui.TableRow()
			self.dInfoItem0 = gui.TableItem(entry[0])
			self.dInfoItem1 = gui.TableItem(entry[1])
			self.infoLine.append(self.dInfoItem0)
			self.infoLine.append(self.dInfoItem1)
			self.driveInfoTable.append(self.infoLine)
		self.healthTable.empty()
		healthStats = self.getDriveHealth()
		for line in healthStats:
			self.healthLine = gui.TableRow()
			self.healthItem0 = gui.TableItem(line[0])
			self.healthItem1 = gui.TableItem(line[1].replace("_"," ").title())
			self.healthItem9 = gui.TableItem(line[9].replace("_"," ").title())
			self.healthLine.append(self.healthItem0)
			self.healthLine.append(self.healthItem1)
			self.healthLine.append(self.healthItem9)
			self.healthTable.append(self.healthLine)

	def getDriveHealth(self):
		isSSD = False
		global brick
		q = subprocess.Popen(["smartctl -a /dev/disk/by-vdev/%s | grep 'Rotation Rate'"%brick], shell=True, stdout=subprocess.PIPE).stdout
		lines2 = q.read().splitlines()
		for line in lines2:
			if line == "Rotation Rate:    Solid State Device":
				isSSD = True
		useful =[]
		if isSSD == True:
			s = subprocess.Popen(["smartctl -a /dev/disk/by-vdev/%s"%brick], shell=True, stdout=subprocess.PIPE).stdout
			lines = s.read().splitlines()
			for i in range(55,155):
				if lines[i] == '':
					break
				splitLine = lines[i].split()
				if splitLine[1] == "Unknown_Attribute":
					inte =1
				elif splitLine[1] == "Offline_Uncorrectable":
					inte = 2
				else:
					useful.append(tuple(splitLine))
		elif isSSD == False:
			s = subprocess.Popen(["smartctl -a /dev/disk/by-vdev/%s"%brick], shell=True, stdout=subprocess.PIPE).stdout
			lines = s.read().splitlines()
			for i in range(57,155):
				if lines[i] == '':
					break
				splitLine = lines[i].split()
				if splitLine[1] == "Unknown_Attribute":
					inte =1
				elif splitLine[1] == "Offline_Uncorrectable":
					inte = 2
				else:
					useful.append(tuple(splitLine))
		return useful
	#---------------------------------------Zpool functions----------------------------------------------------
	def getZpoolStats(self):
		s = subprocess.Popen(["zpool list"], shell=True, stdout=subprocess.PIPE).stdout
		lines = s.read().splitlines()
		lines2 = []
		for line in lines:
			splitLine = line.split()
			lines2.append(tuple(splitLine))
		return lines2

	def zpoolTableClicked(self, table, row, item):
		global zpoolChoice
		zpoolChoice = item.get_text()
		if zpoolChoice[0] != ' ' or zpoolChoice == ' NAME':
			self.notification_message("Error!", "Please Select the name of the Zpool you wish to view")
		else:
			self.zpoolStatusTable.empty()
			for line in self.getZpoolStatus():
				self.zpoolStatusLine = gui.TableRow()
				self.zpoolStatusName = gui.TableItem(line[0])
				self.zpoolState = gui.TableItem(line[1])
				self.zpoolRead = gui.TableItem(line[2])
				self.zpoolWrite = gui.TableItem(line[3])
				self.zpoolCksum = gui.TableItem(line[4])
				self.zpoolStatusLine.append(self.zpoolStatusName)
				self.zpoolStatusLine.append(self.zpoolState)
				self.zpoolStatusLine.append(self.zpoolRead)
				self.zpoolStatusLine.append(self.zpoolWrite)
				self.zpoolStatusLine.append(self.zpoolCksum)
				self.zpoolStatusTable.append(self.zpoolStatusLine)
			self.deleteZpoolButton.set_text("Delete %s"%zpoolChoice)

	def getZpoolStatus(self):
		zpool = zpoolChoice.strip('~')
		s = subprocess.Popen(["zpool status %s"%zpool], shell=True, stdout=subprocess.PIPE).stdout
		lines = s.read().splitlines()
		for i in range(0,5):
			del lines[0]
		lines2 = []
		for line in lines:
			splitLine = line.split()
			while len(splitLine) < 5:
				splitLine.append('')
			lines2.append(tuple(splitLine))
		return lines2

	def deleteZpool(self, widget):
		zpool = zpoolChoice.strip(' ')
		subprocess.call(["zpool destroy %s"%(zpool)], shell=True)
		self.notification_message("", "zpool %s has been deleted"%zpool)
		self.monitorZpoolTable.empty()
		for line in self.getZpoolStats():
			self.zpoolLine = gui.TableRow()
			self.zpoolName = gui.TableItem(" "+line[0])
			self.zpoolSize = gui.TableItem(line[1])
			self.zpoolAlloc = gui.TableItem(line[2])
			self.zpoolFree = gui.TableItem(line[3])
			self.zpoolHealth = gui.TableItem(line[8])
			self.zpoolLine.append(self.zpoolName)
			self.zpoolLine.append(self.zpoolSize)
			self.zpoolLine.append(self.zpoolAlloc)
			self.zpoolLine.append(self.zpoolFree)
			self.zpoolLine.append(self.zpoolHealth)
			self.monitorZpoolTable.append(self.zpoolLine)

	def updateZpools(self):
		self.monitorZpoolTable.empty()
		if noZpools == True:
			self.zpoolLine = gui.TableRow()
			self.nozpool = gui.TableItem("No Zpools Present")
			self.zpoolLine.append(self.nozpool)
			self.monitorZpoolTable.append(self.zpoolLine)
		if noZpools == False:
			for line in self.getZpoolStats():
				self.zpoolLine = gui.TableRow()
				self.zpoolName = gui.TableItem(" "+line[0])
				self.zpoolSize = gui.TableItem(line[1])
				self.zpoolAlloc = gui.TableItem(line[2])
				self.zpoolFree = gui.TableItem(line[3])
				self.zpoolHealth = gui.TableItem(line[8])
				self.zpoolLine.append(self.zpoolName)
				self.zpoolLine.append(self.zpoolSize)
				self.zpoolLine.append(self.zpoolAlloc)
				self.zpoolLine.append(self.zpoolFree)
				self.zpoolLine.append(self.zpoolHealth)
				self.monitorZpoolTable.append(self.zpoolLine)
		self.zpoolStatusTable.empty()
		if noZpools == True:
			self.noZpoolLine = gui.TableRow()
			self.noZpoolLine1 = gui.TableItem('No Zpools Present')
			self.noZpoolLine.append(self.noZpoolLine1)
			self.zpoolStatusTable.append(self.noZpoolLine)
		if noZpools == False:
			for line in self.getZpoolStatus():
				self.zpoolStatusLine = gui.TableRow()
				self.zpoolStatusName = gui.TableItem(line[0])
				self.zpoolState = gui.TableItem(line[1])
				self.zpoolRead = gui.TableItem(line[2])
				self.zpoolWrite = gui.TableItem(line[3])
				self.zpoolCksum = gui.TableItem(line[4])
				self.zpoolStatusLine.append(self.zpoolStatusName)
				self.zpoolStatusLine.append(self.zpoolState)
				self.zpoolStatusLine.append(self.zpoolRead)
				self.zpoolStatusLine.append(self.zpoolWrite)
				self.zpoolStatusLine.append(self.zpoolCksum)
				self.zpoolStatusTable.append(self.zpoolStatusLine)


ip = str(socket.gethostbyname(socket.gethostname()))

start(FortyFiveDash, address=ip, port=int(port), multiple_instance=False, start_browser=False, username=username, password=password)
