import remi.gui as gui
from remi import start, App
import sys, tempfile, os
import subprocess
import re
import platform, socket

global brick
brick = '1-1'
global zpoolChoice
zpoolChoice = 'zpool'
global createContainer
global hostsInputContainer
hostsInputContainer = gui.Widget(width='100%', height=200, style={'display': 'block', 'overflow':'auto'})
global createHostsContainer
createHostsContainer = gui.Widget(width='98%', height=300, style={'padding':'5px','border':'0px solid #7cdaff','float':'left','display':'block','overflow':'auto'})




 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-# UI RENDERING#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
class FortyFiveDash(App):

	 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-# LOCAL FUNCTIONS #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	def __init__(self, *args):
		super(FortyFiveDash, self).__init__(*args)
	#--------------------------------------------Monitor Functions-------------------------------------------------
	def retrieveVolumes(self):
		subprocess.call(['cd ~'], shell=True)
		s=subprocess.Popen(["gluster volume list"], shell=True, stdout=subprocess.PIPE).stdout
		glusters = s.read().splitlines()
		return glusters

	#--------------------------------------------Create Functions---------------------------------------------------

	def reset(self, widget):
		self.nameInput.set_text('NewVolume')
		self.raidSelection.select_by_value('RAIDZ2')
		self.vDevSelection.select_by_value('3')
		self.brickSelection.select_by_value('8')
		self.glusterSelection.select_by_value('Distributed')
		self.tuningSelection.select_by_value('Default')
	
	def main(self):

		global choice
		choice = str(self.retrieveVolumes()[0])
		if len(self.retrieveVolumes()) == 0:
			global createContainer
			global createHostsContainer
			self.errorContainer = gui.Widget(width='40%', height='100%', style={'margin':'0px auto','display': 'block', 'overflow':'auto'})
			createHostsContainer = gui.Widget(width='98%', height=300, style={'padding':'5px','border':'0px solid #7cdaff','float':'left','display':'block','overflow':'auto'})
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
			hostsInputContainer = gui.Widget(width='100%', height=200, style={'display': 'block', 'overflow':'auto'})

			#--------------------------------------Gluster details----------------------------------------------------
			
			self.glusterDetailsContainer = gui.Widget(width='98%', height=300,  style={'padding':'5px','border':'0px solid #7cdaff','float':'left','display':'block','overflow':'auto'})
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
			self.warningLabel = gui.Label('Warning! No glusters found, make one here and relaunch the app')
			self.errorContainer.append(self.warningLabel)
			self.errorContainer.append(createHostsContainer)
			self.errorContainer.append(self.glusterDetailsContainer)
			return self.errorContainer
		#_________________________________________________________________________________________________________
		#--------------------------------------Main Menu Configuration -------------------------------------------
		#_________________________________________________________________________________________________________
		#--------------------------------------Volume List--------------------------------------------------------
		self.mainMenuVolumeContainer = gui.Widget(width='20%', height=700,style={'padding':'5px','border':'2px solid #7cdaff','float':'left','display':'block','overflow':'auto'})
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
		self.overviewTableContainer = gui.Widget(width='40%', height=700, style={'padding':'5px','border':'2px solid #7cdaff','float':'left','display':'block','overflow':'auto'})
		self.overviewTableLabel = gui.Label("Overview", width='100%')
		self.overviewTable = gui.Table(width='100%')
		self.lclHostRow = gui.TableRow()
		self.lclHost = gui.TableItem('localhost Name	:')
		self.lclHost2 = gui.TableItem(socket.gethostname())
		self.lclHostRow.append(self.lclHost)
		self.lclHostRow.append(self.lclHost2)
		self.ipAddrRow = gui.TableRow()
		self.ipAddr = gui.TableItem('IP Address	:')
		self.ipAddr2 = gui.TableItem(socket.gethostbyname(socket.gethostname()))
		self.ipAddrRow.append(self.ipAddr)
		self.ipAddrRow.append(self.ipAddr2)
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
		self.numStVolumes2 = gui.TableItem(self.getNumStoppedVolumes())
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
		self.overviewTable.append(self.numVolumesRow)
		self.overviewTable.append(self.numActVolumesRow)
		self.overviewTable.append(self.numStVolumesRow)
		self.overviewTable.append(self.numDrivesRow)
		self.overviewTable.append(self.numActDrivesRow)
		self.overviewTable.append(self.numStDrivesRow)
		self.overviewTable.append(self.numZpoolRow)
		self.overviewTableContainer.append(self.overviewTableLabel)
		self.overviewTableContainer.append(self.overviewTable)

		#_________________________________________________________________________________________________________
		#--------------------------------------Create Configuaration----------------------------------------------
		#_________________________________________________________________________________________________________
		#--------------------------------------Host inputs--------------------------------------------------------
		createHostsContainer = gui.Widget(width='40%', height=300, style={'margin':'0px auto','padding':'5px','border':'2px solid #7cdaff','float':'center','display':'block','overflow':'auto'})
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
		self.glusterDetailsContainer = gui.Widget(width='40%', height=300,  style={'margin':'0px auto','padding':'5px','border':'2px solid #7cdaff','float':'center','display':'block','overflow':'auto'})
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
		self.tuningSelection = gui.DropDown.new_from_list(('SMB filesharing','Virtualization'), width='30%', height=30, style={'float':'right'})
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
		#--------------------------------------Create - Zpool ----------------------------------------------------
		#_________________________________________________________________________________________________________
		self.zpoolDetailsContainer = gui.Widget(width='98%', height=300,  style={'padding':'5px','border':'0px solid #7cdaff','float':'left','display':'block','overflow':'auto'})
		self.zpoolNameLabel = gui.Label('Name of new zpool:', width='70%', height=30, style={'float':'left'})
		self.zpoolNameInput = gui.TextInput(width='30%', height=30, style={'float':'right'})
		self.zpoolNameInput.set_text('zpool')
		self.zpoolRaidLabel = gui.Label('Select RAID Level', width='70%', height=30, style={'float':'left'})
		self.zpoolRaidSelection = gui.DropDown.new_from_list(('RAIDZ1', 'RAIDZ2', 'RAIDZ3'), width='30%', height=30, style={'float':'right'})
		self.zpoolRaidSelection.select_by_value('RAIDZ2')
		self.zpoolVDevLabel = gui.Label('Select # of VDevs', width='70%', height=30, style={'float':'left'})
		self.zpoolVDevSelection = gui.DropDown.new_from_list(('2','3','4','5','6'), width='30%', height=30, style={'float':'right'})
		self.zpoolVDevSelection.select_by_value('3')
		self.zpoolBrickLabel = gui.Label('Select # of bricks for ZFS pool', width='70%', height=30, style={'float':'left'})
		self.zpoolBrickSelection = gui.DropDown.new_from_list(('2','3','4','5','6','7','8'), width='30%', height=30, style={'float':'right'})
		self.zpoolBrickSelection.select_by_value('8')
		self.zpoolDetailsContainer.append(self.zpoolNameLabel)
		self.zpoolDetailsContainer.append(self.zpoolNameInput)
		self.zpoolDetailsContainer.append(self.zpoolRaidLabel)
		self.zpoolDetailsContainer.append(self.zpoolRaidSelection)
		self.zpoolDetailsContainer.append(self.zpoolVDevLabel)
		self.zpoolDetailsContainer.append(self.zpoolVDevSelection)
		self.zpoolDetailsContainer.append(self.zpoolBrickLabel)
		self.zpoolDetailsContainer.append(self.zpoolBrickSelection)
		#_________________________________________________________________________________________________________
		#--------------------------------------Monitor - Volume Configuation--------------------------------------
		#_________________________________________________________________________________________________________
		#--------------------------------------Volume List-------------------------------------------------------
		self.monitorVolumeContainer = gui.Widget(width='10%', height=700, style={'padding':'5px','border':'2px solid #7cdaff','float':'left','display':'block','overflow':'auto'})
		self.volumeLabel = gui.Label('Active Volumes', width='100%', height='10%')
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
		self.monitorInfoContainer = gui.Widget(width='49%', height=700, style={'padding':'5px','border':'2px solid #7cdaff','float':'left','display':'block','overflow':'auto'})
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
		self.monitorStatusContainer = gui.Widget(width='37%', height=700, style={'padding':'5px','border':'2px solid #7cdaff','float':'left','display':'block','overflow':'auto'})
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
		self.drivesVolumeListContainer = gui.Widget(width='20%', height=700, style={'padding':'5px','border':'2px solid #7cdaff','float':'left','display':'block','overflow':'auto'})
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
		self.monitorDrivesListContainer=gui.Widget(width='15%', height=450, style={'padding':'5px','border':'2px solid #7cdaff','float':'left','display':'block','overflow':'auto'})
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
		self.monitorDrivesInfoContainer=gui.Widget(width='34%',height=450, style={'padding':'5px','border':'2px solid #7cdaff','float':'left','display':'block','overflow':'auto'})
		self.detailLabel = gui.Label('Brick Storage', width='100%', height=20)
		self.detailList = gui.ListView()
		spaceList = self.detailText()
		for entry in spaceList:
			self.brick = gui.ListItem(entry)
			self.detailList.append(self.brick)
		self.monitorDrivesInfoContainer.append(self.detailLabel)
		self.monitorDrivesInfoContainer.append(self.detailList)
		#--------------------------------------Drive Text Box-----------------------------------------------------
		self.monitorDrivesTextBoxContainer = gui.Widget(width='26%', height=450, style={'padding':'5px','border':'2px solid #7cdaff','float':'left','display':'block','overflow':'auto'})
		global driveInfoText
		driveInfoTextLabel = gui.Label('Drive Info', height=30, width='100%')
		driveInfoText = gui.TextInput(False,width='100%', height=300)
		driveInfoText.set_text('Select a drive from list to view information')
		self.monitorDrivesTextBoxContainer.append(driveInfoTextLabel)
		self.monitorDrivesTextBoxContainer.append(driveInfoText)
		#--------------------------------------Drive health box---------------------------------------------------
		self.monitorDrivesHealthContainer = gui.Widget(width='75%', height = 236 ,style={'padding':'5px','border':'2px solid #7cdaff','float':'left','display':'block','overflow':'auto'})
		self.healthListLabel = gui.Label('Drive Health',width='100%', height=19)
		self.healthTable = gui.Table(width='100%')
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
		self.monitorZpoolZpoolContainer = gui.Widget(width='35%', height=700, style={'padding':'5px','border':'2px solid #7cdaff','float':'left','display':'block','overflow':'auto'})
		self.monitorZpoolLabel = gui.Label('Active Zpools (Select name of zpool to view)', width='100%', height=30)
		self.monitorZpoolTable = gui.Table(width='100%')
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
		self.monitorZpoolStatusContainer = gui.Widget(width='45%', height=700, style={'padding':'5px', 'border':'2px solid #7cdaff','float':'left','display':'block','overflow':'auto'})
		self.zpoolStatusLabel = gui.Label('Zpool Status', width='100%', height=30)
		self.zpoolStatusTable = gui.Table(width='100%')
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
		global createContainer
		global hostsInputContainer
		mainContainer = gui.Widget(width='98%', height='100%', style={'margin':'0px auto','display': 'block', 'overflow':'auto'})
		mainMenuContainer = gui.Widget(width='98%', height='100%', style={ 'margin':'0px auto','display': 'block', 'overflow':'auto'})
		monitorVolumeContainer = gui.Widget(width='98%', height='100%', style={ 'margin':'0px auto','display': 'block', 'overflow':'auto'})
		monitorDrivesContainer = gui.Widget(width='98%', height='100%', style={ 'margin':'0px auto','display': 'block', 'overflow':'auto'})
		monitorZpoolContainer = gui.Widget(width='98%', height='100%', style={ 'margin':'0px auto','display': 'block', 'overflow':'auto'})
		createContainer = gui.Widget(width='98%', height=700, style={'margin':'0px auto','display': 'block', 'overflow':'auto'})
		createZpoolContainer = gui.Widget(width='40%', height='100%', style={'margin':'0px auto','display': 'block', 'overflow':'auto'})
		#--------------------------------------Main Menu----------------------------------------------------------
		mainMenuContainer.append(self.mainMenuVolumeContainer)
		mainMenuContainer.append(self.overviewTableContainer)
		#--------------------------------------Create menu--------------------------------------------------------
		createContainer.append(createHostsContainer)
		hostsInputContainer = gui.Widget(width='100%', height=200, style={'display': 'block', 'overflow':'auto'})
		advancedContainer = gui.Widget(width='100%', height=150, style={'display':'block', 'overflow':'auto'})
		createContainer.append(self.glusterDetailsContainer)
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
		#--------------------------------------TabBox configuation------------------------------------------------
		self.mainTabBox = gui.TabBox(style={'background-color':'#7cdaff'})
		self.mainTabBox.add_tab(mainMenuContainer, "Main Menu", None)
		self.mainTabBox.add_tab(createContainer, "Create - Volume", None)
		#self.mainTabBox.add_tab(createZpoolContainer, "Create - Zpool", None)
		self.mainTabBox.add_tab(monitorVolumeContainer, "Monitor - Volume", None)
		self.mainTabBox.add_tab(monitorDrivesContainer, "Monitor - Drives", None)
		self.mainTabBox.add_tab(monitorZpoolContainer, "Monitor - Zpool", None)
		#----------------------------------FINAL LAYOUT CONFIG----------------------------------------------------
		mainContainer.append(self.mainTabBox)
		self.getDriveHealth()
		return mainContainer

	#_____________________________________________________________________________________________________________
	#-----------------------------------------------Functions-----------------------------------------------------
	def updateVolumeLists(self):
		self.volumeList.empty()
		volume_List = self.retrieveVolumes()
		for volume in volume_List:
			status = self.infoTableFunction(volume)[3][1].strip(" ").lower()
			if status == "started":
				self.volume = gui.ListItem(volume, style={'color':'#29B809'})
			elif status == "stopped":
				self.volume = gui.ListItem(volume, style={'color':'#FF0000'})
			self.volumeList.append(self.volume)

		self.activeVolumeList.empty()
		active_Volume_List = self.retrieveVolumes()
		for vol in self.active_Volume_List:
			volumeStatus = self.infoTableFunction(vol)[3][1].strip(" ").lower() #Retrieves status by calling gluster info and makes it easy to call by string
			if volumeStatus =='started':
				self.volumeListItem = gui.ListItem(vol, style={'color':'#29B809'}) #Checks status and colors green if started or red if stopped
			elif volumeStatus =='stopped':
				self.volumeListItem = gui.ListItem(vol, style={'color':'#FF0000'})
			else:
				self.volumeListItem = gui.ListItem(vol)
			self.activeVolumeList.append(self.volumeListItem)

		self.drivesVolumeList.empty()
		for volume in self.retrieveVolumes():
			drivesInfoStatus = self.infoTableFunction(volume)[3][1].strip(" ").lower()
			if drivesInfoStatus == "started":
				self.volume = gui.ListItem(volume, style={'color':'#29B809'})
			elif drivesInfoStatus == "stopped":
				self.volume = gui.ListItem(volume, style={'color':'#FF0000'})
			self.drivesVolumeList.append(self.volume)

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

	#-----------------------------------------------Create functions----------------------------------------------
	def saveHosts(self):
		global hostsConf
		hosts = []
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
		if selection == '0':
			return 0
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
		mkarbcmd = "/opt/gtools/bin/mkarb -b %s"%bricks
		for num in range(1, numHosts+1):
			mkarbcmd = mkarbcmd + "-n %s"%(hostsInputContainer.children[num].get_text())
		r = subprocess.Popen(mkarb, shell=True, stdout=subprocess.PIPE).stdout
		mkarb = r.read()
		tuneProfile = self.tuningSelection.get_value()
		f.write("[volume1]\naction=create\nvolname=%s\n"%glusterName)
		if glusterConfig == 'Distributed':
			mkarb = ""
			for i in range(1, int(bricks)+1):
				mkarb = mkarb+"/zpool/vol"+str(i)+"/brick,"
			f.write("replica_count=0\nforce=yes\n")
			#if tuneProfile == 'SMB filesharing':
			f.write("key=performance.parallel-readdir,network.inode-lru-limit,performance.md-cache-timeout,performance.cache-invalidation,performance.stat-prefetch,features.cache-invalidation-timeout,features.cache-invalidation,performance.cache-samba-metadata\nvalue=on,50000,600,on,on,600,on,on\nbrick_dirs=%s"%mkarb)
			#elif tuneProfile == 'Virtualization':
			#	f.write("key=group,storage.owner-uid,storage.owner-gid,network.ping-timeout,performance.strict-o-direct,network.remote-dio,cluster.granular-entry-heal,features.shard-block-size\nvalue=virt,36,36,30,on,off,enable,64MB")
		
		if glusterConfig == 'Distributed Replicated':
			f.write("replica_count=3\narbiter_count=1\nforce=yes\nkey=performance.parallel-readdir, network.inode-lru-limit, performance.md-cache-timeout, performance.cache-invalidation, performance.stat-prefetch, features.cache-invalidation-timeout, features.cache-invalidation, performance.cache-samba-metadata\nvalue=on,50000,600,on,on,600,on,on\nbrick_dirs=%s"%mkarb)
			if tuneProfile == 'SMB filesharing':
				f.write("key=performance.parallel-readdir,network.inode-lru-limit,performance.md-cache-timeout,performance.cache-invalidation,performance.stat-prefetch,features.cache-invalidation-timeout,features.cache-invalidation,performance.cache-samba-metadata\nvalue=on,50000,600,on,on,600,on,on\nbrick_dirs=%s"%mkarb)
			elif tuneProfile == 'Virtualization':
				f.write("key=group,storage.owner-uid,storage.owner-gid,network.ping-timeout,performance.strict-o-direct,network.remote-dio,cluster.granular-entry-heal,features.shard-block-size\nvalue=virt,36,36,30,on,off,enable,64MB")

		f.close()

	def createPress(self, widget):
		self.saveHosts()
		if hostsConf == 401:
			print "Error 401: Invalid Character used for a name"
			return 0
		name = self.nameInput.get_text()
		for char in name:
			if (char < '0' or char > 'z') or (char > '9' and char < 'A') or (char > 'Z' and char < 'a'): 
				self.notification_message('Error 401', "You can't use special characters (%s) in gluster name"%(char))
				print "Error 401: Invalid Character used for a name"
				return 0
		for entry in self.retrieveVolumes():
			if name == entry:
				self.notification_message("Error 402", "The name %s is already in use by another gluster"%(name))
				print "Error 402: Name in use"
				return 0
		self.notification_message("Action", "%s is in the oven "%self.nameInput.get_text())
		entries = self.retrieveVolumes()
		entryCount = 0
		for entry in entries:
			entryCount = entryCount + 1
		self.gDeployFile()
		subprocess.call(['gdeploy -c deploy-cluster.conf'], shell=True)
		newEntries = self.retrieveVolumes()
		newEntryCount = 0
		for newEntry in newEntries:
			newEntryCount = newEntryCount + 1
		if entryCount == newEntryCount:
			self.notification_message("Error!", "Don't know what happened but %s couldn't be made"%self.nameInput.get_text())
		else:
			currentVolumeList = newEntries
			self.notification_message("Success!", "Gluster %s has been made"%(self.nameInput.get_text()))
		self.updateVolumeLists()
	#-----------------------------------------------Monitor Functions---------------------------------------------
	def monitorVolumesListSelected(self, widget, selection):
		global choice
		if choice == '':
			choice = self.retrieveVolumes()[0]
		choice = self.volumeList.children[selection].get_text()
 
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
		self.stopButton.set_text("Stop %s"%choice)
		self.startButton.set_text("Start %s"%choice)
		self.deleteButton.set_text("Delete %s"%choice)
		self.updateVolumeLists()

	def startGluster(self, widget):
		subprocess.call(["gluster volume start %s"%choice], shell=True)
		self.notification_message("", "Gluster Volume %s has been started"%choice)
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
		self.overviewTableUpdate()
		self.updateVolumeLists()

	def stopGluster(self, widget):
		initialStatus = self.infoTableFunction(choice)[3][1].strip(" ").lower()
		if initialStatus == 'started':
			subprocess.call(["echo 'y' | gluster volume stop %s"%(choice)], shell=True)
			
			currentStatus = self.infoTableFunction(choice)[3][1].strip(" ").lower()
			if currentStatus == 'stopped':
				self.notification_message("", "Gluster Volume %s has been stopped"%choice)
			if currentStatus != 'stopped':
				self.notificaiotn_message("Error!", "Gluster volume %s couldn't be stopped"%choice)
		else:
			self.notification_message("Error!", "Gluster volume %s is already stopped"%choice)
		
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
		self.numStVolumes2.set_text(self.getNumStoppedVolumes())
		self.overviewTableUpdate()
		self.updateVolumeLists()
		
	def deleteGluster(self, widget):
		if len(self.retrieveVolumes()) == 1:
			self.notification_message("Error 403", "Last present gluster, ending will cause dashboard to fail")
			print "Error 403: Cannot delete last gluster"
			return 403
		subprocess.call(["echo 'y' | gluster volume delete %s"%(choice)], shell=True)
		self.notification_message("", "Gluster Volume %s has been deleted"%choice)
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
		self.overviewTableUpdate()
		self.updateVolumeLists()

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
		self.detailList.empty()
		details = self.detailText()
		for entry in details:
			self.brick = gui.ListItem(entry)
			self.detailList.append(self.brick)

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
			bricks.append(str("Brick "+str(num)+": "+lines[lineParse].strip(" ")+" -- | -- "+lines[lineParse+1].strip(" ")))
			lineParse = lineParse+2
		return bricks

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
			self.healthItem1 = gui.TableItem(line[1].replace("_"," ").title())
			self.healthItem9 = gui.TableItem(line[9].replace("_"," ").title())
			self.healthLine.append(self.healthItem0)
			self.healthLine.append(self.healthItem1)
			self.healthLine.append(self.healthItem9)
			self.healthTable.append(self.healthLine)

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

ip = str(socket.gethostbyname(socket.gethostname()))
start(FortyFiveDash, address=ip, port=8081, multiple_instance=True, start_browser=False, username='ADMIN', password='ADMIN')
