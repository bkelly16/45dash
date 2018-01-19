import remi.gui as gui
from remi import start, App
import sys, tempfile, os
import subprocess
import re
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
global choice
choice = 'DontStopMeNow'

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
	def list_view_on_selected(self, widget, selection):
		choice = self.volumeList.children[selection].get_text()
		statusLines = self.statusList()
		#self.statusTable.append_from_list([('Gluster Process','TCP Port', 'RDMA Port', 'Online', 'Pid'), statusLines[0], statusLines[1]])
		self.infoTable.append_from_list([(''),(self.infoList()[1]), (self.infoList()[2]), (self.infoList()[3]), (self.infoList()[4]), (self.infoList()[5]), (self.infoList()[6]), (self.infoList()[7])])
		self.volumeList.empty()
		volumes = self.retrieveVolumes()
		for entry in volumes:
			self.volumeList.append(entry)
		#self.statusTable.append_from_list([('Gluster Process','TCP Port', 'RDMA Port', 'Online', 'Pid'), statusLines[0], statusLines[1]])
	def startGluster(self, widget):
		subprocess.call(["gluster volume start %s"%choice], shell=True)
		self.notification_message("", "Gluster Volume %s has been started"%choice)
	def stopGluster(self, widget):
		subprocess.call(["echo 'y' | gluster volume stop %s"%(choice)], shell=True)
		self.notification_message("", "Gluster Volume %s has been stopped"%choice)
	def deleteGluster(self, widget):
		subprocess.call(["echo 'y' | gluster volume delete %s"%(choice)], shell=True)
		self.notification_message("", "Gluster Volume %s has been deleted"%choice)
	def statusList(self):
		r=subprocess.Popen(['gluster volume status %s' % choice], shell=True, stdout=subprocess.PIPE).stdout
		lines = r.read().splitlines()
		if lines == '\nVolume %s is not started'%choice:
			return [('-','-','-','-','-'), ('-','-','-','-','-')]
		else:
			lines2 = []
			words1 = lines[3].split()
			words2 = lines[4].split()
			words1[0] = words1[0]+' '+words1[1]
			words2[0] = words2[0]+' '+words2[1]
			del words1[1]
			del words2[1]
			wordList1 = []
			wordList2 = []
			for word in words1:
				wordList1.append(word)
			for word in words2:
				wordList2.append(word)
			tuple1 = tuple(wordList1)
			tuple2 = tuple(wordList2)
			final =[]
			final.append(tuple1)
			final.append(tuple2)
			return final
	def infoList(self):
		r = subprocess.Popen(['gluster volume info %s' % choice], shell=True, stdout=subprocess.PIPE).stdout
		lines = r.read().splitlines()
		results = []
		for line in lines:
			splitText = re.split(r':', line)
			results.append(splitText)
		entries = []
		for entry in results:
			tupleEntry = tuple(entry)
			entries.append(tupleEntry)
		return entries
	def driveMap(self):
		takeMeToRoot()
		r=subprocess.check_output("lsdevpy -n", stderr=subprocess.STDOUT, shell=True)
		return r
	def refresh(self, widget):
		#self.statusList()
		self.volumeList.empty()
		volumes = retrieveVolumes()
		for entry in volumes:
			self.volumeList.append(entry)
		self.infoTable.append_from_list([(''),(self.infoList[1]), (self.infoList[2]), (self.infoList[3]), (self.infoList[4]), (self.infoList[5]), (self.infoList[6]), (self.infoList[7])])
		self.notification_message("", "Page refreshed")
	#--------------------------------------------Create Functions---------------------------------------------------
	def gDeployFile(self):
		takeMeToRoot()
		f = open("deploy-cluster.conf","w+")
		f.write("[hosts]\n")
		hostOneName = self.hostOneInput.get_text()
		hostTwoName = self.hostTwoInput.get_text()
		f.write("%s\n" % (hostOneName))
		f.write("%s\n\n" % (hostTwoName))
		f.write("[tune-profile]\n")
		f.write("throughput-performance\n\n")
		f.write("[service1]\n")
		f.write("action=enable\n")
		f.write("service=ntpd\n")
		f.write("ignore_errors=no\n\n")
		f.write("[service2]\n")
		f.write("action=start\n")
		f.write("service=ntpd\n")
		f.write("ignore_errors=no\n\n")
		f.write("[service3]\n")
		f.write("action=disable\n")
		f.write("service=firewalld\n")
		f.write("ignore_errors=no\n\n")
		f.write("[service4]\n")
		f.write("action=stop\n")
		f.write("service=firewalld\n")
		f.write("ignore_errors=no\n\n")
		f.write("[service5]\n")
		f.write("action=enable\n")
		f.write("service=glusterd\n")
		f.write("ignore_errors=no\n\n")
		f.write("[service6]\n")
		f.write("action=start\n")
		f.write("service=glusterd\n")
		f.write("ignore_errors=no\n\n")
		driverCard = '9305'
		chassisSize = self.chassisSizeInput.get_value()
		f.write("[script1:server2]\n")
		f.write("action=execute\n")
		f.write("file=/opt/gtools/bin/dmap -c %s -s %s -q\n"%(driverCard, chassisSize))
		f.write("ignore_script_errors=no\n\n")
		f.write("[script2:server1]\n")
		f.write("action=execute\n")
		f.write("file=/opt/gtools/bin/dmap -c r750 -s 30 -q\n")
		f.write("ignore_script_errors=no\n\n")
		vDevs = self.vDevSelection.get_value()
		raidLevel = self.raidSelection.get_value()
		f.write("[script2]\n")
		f.write("action=execute\n")
		f.write("file=/opt/gtools/bin/zcreate -v %s -l %s -n zpool -a 9 -bq\n"%(vDevs, raidLevel.lower()))
		f.write("ignore_script_errors=no\n\n")
		bricks = self.brickSelection.get_value()
		f.write("[script3]\n")
		f.write("action=execute\n")
		f.write("file=/opt/gtools/bin/mkbrick -n zpool -A 100G -C -b %s -p 95 -fq\n"%(bricks))
		f.write("ignore_script_errors=no\n\n")
		f.write('[update-file1]\n')
		f.write('action=edit\n')
		f.write('dest=/usr/lib/systemd/system/zfs/startzfscache.sh\n\n')
		f.write('[script5]\n')
		f.write('action=execute\n')
		f.write('file=/opt/gtools/bin/startzfscache\n')
		f.write('ignore_script_errors=no\n\n')
		glusterConfig = self.glusterSelection.get_value()
		glusterName = self.nameInput.get_text()
		mkarb = subprocess.Popen(['/opt/gtools/bin/mkarb -b %s -n %s -n %s'%(bricks, hostOneName, hostTwoName)], shell=True, stdout=subprocess.PIPE).stdout	
		f.write("[volume1]\n")
		f.write("action=create\n")
		f.write("volname=%s\n"%glusterName)
		if glusterConfig == 'Distributed':
			f.write("replica_count=0\n")
			f.write("force=yes\n")
			f.write("key=performance.parallel-readdir, network.inode-lru-limit, performance.md-cache-timeout, performance.cache-invalidation, performance.stat-prefetch, features.cache-invalidation-timeout, features.cache-invalidation, performance.cache-samba-metadata\n")
			f.write("value=on,50000,600,on,on,600,on,on\n")
			f.write("brick_dirs=")
			for num in range(0, int(bricks)+1):
				f.write("%s:/zpool/vol%s/brick,"%(hostOneName, str(num)))
			f.write('\n')
		if glusterConfig == 'Distributed Replicated':
			f.write("replica_count=3\n")
			f.write("arbiter_count=1\n")
			f.write("force=yes\n")
			f.write("key=performance.parallel-readdir, network.inode-lru-limit, performance.md-cache-timeout, performance.cache-invalidation, performance.stat-prefetch, features.cache-invalidation-timeout, features.cache-invalidation, performance.cache-samba-metadata\n")
			f.write("value=on,50000,600,on,on,600,on,on\n")
			f.write("brick_dirs=")
			for num in range(0, int(bricks)+1):
				f.write("%s:/zpool/vol%s/brick,"%(hostOneName, str(num)))
			f.write('\n')
		f.close()
	def createPress(self, widget):
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
			self.notification_message("Error!", "Don't know what happened but your gluster didn't work")
		else:
			currentVolumeList = newEntries
			self.notification_message("Success!", "Gluster %s has been made"%(self.nameInput.get_text()))

	def main(self):
		#____________________________________TEMPORARY STUFF_________________________________________________
		global currentVolumeList
		currentVolumeList = self.retrieveVolumes()
		choice = str(self.retrieveVolumes()[0])
		statusLines = self.statusList()
		infoLists = self.infoList()
		#____________________________________CONTAINERS_________________________________________________________
		mainContainer = gui.Widget(width='95%', margin='0px auto', height='100%', style={'display':'block','overflow':'auto'})
		monitorContainer = gui.Widget(width='60%', height='100%', style={'float':'left','display': 'block', 'overflow':'auto'})
		monitorLeftContainer = gui.Widget(width='50%', height='100%', style={'float':'left','display':'block','overflow':'auto'})
		monitorRightContainer = gui.Widget(width='50%', height='100%', style={'float':'right','display':'block', 'overflow':'auto'})
		createContainer = gui.Widget(width='40%', height='100%', style={'float':'right', 'display':'block', 'overflow':'auto'})
		createHostContainer = gui.Widget(width='100%', height= 200, style={'overflow':'auto'})
		#_____________________________________MENUBAR____________________________________________________________
		menu = gui.Menu(width='100%', height='60px')
		menuCreate = gui.MenuItem('Create', margin='0px auto',width=100, height=30)
		menuMonitor = gui.MenuItem('Monitor', margin='0px auto', width=100, height=30)
		title = gui.MenuItem('45Dash', margin='0px auto',width=150, height=30, style={'font-size':'30px', 'text-align':'center'})
		title.set_on_click_listener(self.refresh)
		menu.append(title)
		menubar = gui.MenuBar(width='100%', height='60px')
		monitorMenuBar = gui.MenuBar(width='100%', height= 30)
		monitorMenuBar.append(menuMonitor)
		createMenuBar = gui.MenuBar(width='100%', height= 30)
		createMenuBar.append(menuCreate)
		menubar.append(menu)
		mainContainer.append(menubar)
		monitorContainer.append(monitorMenuBar)
		monitorContainer.append(monitorLeftContainer)
		monitorContainer.append(monitorRightContainer)
		createContainer.append(createMenuBar)
		#____________________________________LOCAL VARIABLES_____________________________________________________
		#------------------------------------ACTIVE VOLUME LIST--------------------------------------------------
		self.volumeLabel = gui.Label('Active Volumes', width='100%', height=30)
		self.volumeList = gui.ListView.new_from_list(currentVolumeList, width='100%', height=100)
		self.volumeList.set_on_selection_listener(self.list_view_on_selected)
		monitorLeftContainer.append(self.volumeLabel)
		monitorLeftContainer.append(self.volumeList)
		#-----------------------------------VOLUME STATUS--------------------------------------------------------		
		self.statusLabel = gui.Label('Volume Status', width='100%', height=30)
		self.statusTable = gui.Table.new_from_list([('Gluster Process','TCP Port', 'RDMA Port', 'Online', 'Pid'), statusLines[0], statusLines[1]])
		monitorLeftContainer.append(self.statusLabel)
		monitorLeftContainer.append(self.statusTable)

		#-------------------------------------VOLUME INFO--------------------------------------------------------
		self.infoLabel = gui.Label('Volume Info', width='100%', height=30)
		self.infoTable = gui.Table.new_from_list([(''), (self.infoList()[1]), (self.infoList()[2]), (self.infoList()[3]),  (self.infoList()[4]),  (self.infoList()[5]),  (self.infoList()[6]),  (self.infoList()[7])],width='100%', height= 400)
		monitorLeftContainer.append(self.infoLabel)
		monitorLeftContainer.append(self.infoTable)

		#-----------------------------------DRIVE MAP-------------------------------------------------------------
		self.driveLabel = gui.Label('Drive Map', width='100%', height=30)
		self.driveMapText = gui.TextInput(height=350, width='100%')#, style={'border': '1px solid black'})
		self.driveMapText.set_text(self.driveMap())
		monitorRightContainer.append(self.driveLabel)
		monitorRightContainer.append(self.driveMapText)
		#-----------------------------------Delete / stop --------------------------------------------------------
		self.startButton = gui.Button('Start Selected Gluster', width='100%', height=30)
		self.startButton.set_on_click_listener(self.startGluster)
		self.stopButton = gui.Button('Stop selected gluster', width='50%', height=30, style={'float':'left'})
		self.stopButton.set_on_click_listener(self.stopGluster)
		self.deleteButton = gui.Button('Delete selected gluster', width='50%', height=30, style={'float':'right'})
		self.deleteButton.set_on_click_listener(self.deleteGluster)
		self.refreshButton = gui.Button('Refresh', width='100%', height=30)
		self.refreshButton.set_on_click_listener(self.refresh)
		monitorRightContainer.append(self.startButton)
		monitorRightContainer.append(self.stopButton)
		monitorRightContainer.append(self.deleteButton)
		monitorRightContainer.append(self.refreshButton)

		#______________________________________Create container___________________________________________________
		#-------------------------------------Host Name Input-----------------------------------------------------
		self.hostsList=[]
		self.glusterConfigurationLabel = gui.Label('Gluster configuration', width='100%', height=30)
		self.hostsLabel = gui.Label('Input host names', width='100%', height=30)
		self.hostsSlider = gui.Slider(10,0,100,5, width='100%', height=20, margin='10px')
		self.hostOneInput = gui.TextInput(width='50%', height=30)
		self.hostOneInput.set_text('Input Local Host name here')
		self.hostTwoInput = gui.TextInput(width='50%', height=30)
		self.hostTwoInput.set_text('Input hosts to be connected')
		self.addHost = gui.Button('Add another host', width='50%', height=30, style={'float':'left'})
		self.deleteHost = gui.Button('Delete host', width='50%', height=30, style={'float':'right'})
		self.addHost.set_on_click_listener(lambda x: createHostContainer.append(gui.TextInput(width='50%', height=30)))
		createContainer.append(self.glusterConfigurationLabel)
		createContainer.append(self.hostsLabel)
		createContainer.append(createHostContainer)
		createHostContainer.append(self.hostOneInput)
		createHostContainer.append(self.hostTwoInput)
		createContainer.append(self.addHost)
		createContainer.append(self.deleteHost)
		#--------------------------------------Gluster Name-------------------------------------------------------
		self.nameLabel = gui.Label('Name of new volume:', width='70%', height=30, style={'float':'left'})
		self.nameInput = gui.TextInput(width='30%', height=30, style={'float':'right'})
		self.nameInput.set_text('NewVolume')
		createContainer.append(self.nameLabel)
		createContainer.append(self.nameInput)
		#--------------------------------------GChassis Size-------------------------------------------------------
		self.chassisSizePrompt = gui.Label('Select Chassis Size', width='70%', height=30, style={'float':'left'})
		self.chassisSizeInput = gui.DropDown.new_from_list(('15','30','45','60'),width='30%', height=30, style={'float':'right'})
		self.chassisSizeInput.select_by_value('30')
		createContainer.append(self.chassisSizePrompt)
		createContainer.append(self.chassisSizeInput)
		#--------------------------------------RAIDZ configuration------------------------------------------------
		self.raidLabel = gui.Label('Select RAID Level (Z2 recommended)', width='70%', height=30, style={'float':'left'})
		self.raidSelection = gui.DropDown.new_from_list(('RAIDZ1', 'RAIDZ2', 'RAIDZ3 (???)'), width='30%', height=30, style={'float':'right'})
		self.raidSelection.select_by_value('RAIDZ2')
		createContainer.append(self.raidLabel)
		createContainer.append(self.raidSelection)
		#--------------------------------------VDev configuration-------------------------------------------------
		self.vDevLabel = gui.Label('Select # of VDevs', width='70%', height=30, style={'float':'left'})
		self.vDevSelection = gui.DropDown.new_from_list(('2','3','4','5','6'), width='30%', height=30, style={'float':'right'})
		self.vDevSelection.select_by_value('3')
		createContainer.append(self.vDevLabel)
		createContainer.append(self.vDevSelection)
		#--------------------------------------Brick configuartion------------------------------------------------
		self.brickLabel = gui.Label('Select # of bricks for ZFS pool', width='70%', height=30, style={'float':'left'})
		self.brickSelection = gui.DropDown.new_from_list(('2','3','4','5','6','7','8'), width='30%', height=30, style={'float':'right'})
		self.brickSelection.select_by_value('8')
		createContainer.append(self.brickLabel)
		createContainer.append(self.brickSelection)
		#--------------------------------------gluster config type------------------------------------------------
		self.glusterLabel = gui.Label('Select gluster configuration', width='70%', height=30, style={'float':'left'})
		self.glusterSelection = gui.DropDown.new_from_list(('Distributed', 'Distributed Replicated'), width='30%', height=30, style={'float':'right'})
		self.glusterSelection.select_by_value('Distributed')
		createContainer.append(self.glusterLabel)
		createContainer.append(self.glusterSelection)
		#--------------------------------------Advanced Button----------------------------------------------------
		self.advancedButton = gui.Button('Show Advanced Options', width='100%', height=30)
		createContainer.append(self.advancedButton)
		#--------------------------------------Create Button------------------------------------------------------
		self.createButton = gui.Button('Create new gluster', width='100%', height=30, style={'float':'left'})
		self.createButton.set_on_click_listener(self.createPress)
		createContainer.append(self.createButton)

		#----------------------------------FINAL LAYOUT CONFIG----------------------------------------------------
		mainContainer.append(monitorContainer)
		mainContainer.append(createContainer)
		return mainContainer

start(MyApp)
