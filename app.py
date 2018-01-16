import remi.gui as gui
from remi import start, App
import sys, tempfile, os
import subprocess
import re
#_______________________________________________GLOBAL FUNCTION DECLARATIONS______________________________________________
def takeMeToRoot():
	subprocess.call(['cd ../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../..'], shell=True)
def retrieveVolumes():
	takeMeToRoot()
	s=subprocess.Popen(["gluster volume list"], shell=True, stdout=subprocess.PIPE).stdout
	glusters = s.read().splitlines()
	return glusters
def displaySStatus(choice):
	return subprocess.check_output(["gluster volume status %s" % str(choice)], stderr=subprocess.STDOUT, shell=True)
def displaySInfo(choice):
    return subprocess.check_output(["gluster volume info %s" % str(choice)], stderr=subprocess.STDOUT, shell=True)
def driveMap():
    takeMeToRoot()
    r=subprocess.check_output("lsdevpy -n", stderr=subprocess.STDOUT, shell=True)
    return r
def statusList(choice):
	r=subprocess.Popen(['gluster volume status %s' % choice], shell=True, stdout=subprocess.PIPE).stdout
	lines = r.read().splitlines()
	return lines
def splitLine(text):
	words = text.split()
	words[0] = words[0]+words[1]
	del words[1]
	wordList = []
	for word in words:
		wordList.append(word)
	return wordList
def infoList(choice):
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

#________________________________________________GLOBAL VARIABLE DECLARATION______________________________________
volumeList = retrieveVolumes()
volumeList.append('all')
#________________________________________________UI RENDERING______________________________________________________
class MyApp(App):
	#____________________________________________LOCAL FUNCTIONS__________________________________________________ 
	def __init__(self, *args):
		super(MyApp, self).__init__(*args)

	def list_view_on_selected(self, widget, selection):
		choice = self.volumeList.children[selection].get_text()
		statusLines = statusList(choice)
		self.statusTable.append_from_list([('Gluster Process','TCP Port', 'RDMA Port', 'Online', 'Pid'), (splitLine(statusLines[3])), (splitLine(statusLines[4]))])
		self.infoTable.append_from_list([(''),(infoList(choice)[1]), (infoList(choice)[2]), (infoList(choice)[3]), (infoList(choice)[4]), (infoList(choice)[5]), (infoList(choice)[6]), (infoList(choice)[7])])#,width='100%', height= 400)#(splitLine(infoLists[1])), splitLine(infoLists[2]), splitLine(infoLists[3]), splitLine(infoLists[4]), splitLine(infoLists[5]), splitLine(infoLists[6]), splitLine(infoLists[7])], width='100%', height= 400)

	def main(self):
		#____________________________________TEMPORARY STUFF_________________________________________________
		choice = 'all'
		statusLines = statusList(choice)
		infoLists = infoList(choice)
		#____________________________________CONTAINERS_________________________________________________________

		container = gui.Widget(width='80%', margin='0px auto', height='100%', style={'display': 'block', 'overflow':'auto'})
		leftContainer = gui.Widget(width='50%', height='100%', style={'float':'left','display':'block','overflow':'auto'})
		rightContainer = gui.Widget(width='50%', height='100%', style={'float':'right','display':'block', 'overflow':'auto'})
		menu = gui.Menu(width='100%', height='30px')
		menuCreate = gui.MenuItem('Create', width=100, height=30)
		menuMonitor = gui.MenuItem('Monitor', width=100, height=30)
		title = gui.MenuItem('45Dash', width=150, height=30)
		#_____________________________________MENUBAR____________________________________________________________
		menu.append(title)
		menu.append(menuCreate)
		menu.append(menuMonitor)
		menubar = gui.MenuBar(width='100%', height='30px')
		menubar.append(menu)
		container.append(menubar)
		container.append(leftContainer)
		container.append(rightContainer)
		#____________________________________LOCAL VARIABLES_____________________________________________________
		#------------------------------------ACTIVE VOLUME LIST--------------------------------------------------
		self.volumeLabel = gui.Label('Active Volumes', width='100%', height=30)
		self.volumeList = gui.ListView.new_from_list(volumeList, width='100%', height=100)
		self.volumeList.set_on_selection_listener(self.list_view_on_selected)
		leftContainer.append(self.volumeLabel)
		leftContainer.append(self.volumeList)
		#-----------------------------------VOLUME STATUS--------------------------------------------------------		
		self.statusLabel = gui.Label('Volume Status', width='100%', height=30)
		self.statusTable = gui.Table.new_from_list([('Gluster Process','TCP Port', 'RDMA Port', 'Online', 'Pid'), (splitLine(statusLines[3])), (splitLine(statusLines[4]))], height=100, width='100%')	
		leftContainer.append(self.statusLabel)
		leftContainer.append(self.statusTable)

		#-------------------------------------VOLUME INFO--------------------------------------------------------
		self.infoLabel = gui.Label('Volume Info', width='100%', height=30)
		self.infoText = gui.TextInput(height=300, width='100%')# , style={'border': '1px solid black'})
		self.infoText.set_text(displaySInfo(choice))
		self.infoTable = gui.Table.new_from_list([(''), (infoList(choice)[1]), (infoList(choice)[2]), (infoList(choice)[3]), (infoList(choice)[4]), (infoList(choice)[5]), (infoList(choice)[6]), (infoList(choice)[7])],width='100%', height= 400)#(splitLine(infoLists[1])), splitLine(infoLists[2]), splitLine(infoLists[3]), splitLine(infoLists[4]), splitLine(infoLists[5]), splitLine(infoLists[6]), splitLine(infoLists[7])], width='100%', height= 400)
		leftContainer.append(self.infoLabel)
		leftContainer.append(self.infoTable)

		#-----------------------------------DRIVE MAP-------------------------------------------------------------
		self.driveLabel = gui.Label('Drive Map', width='100%', height=30)
		self.driveMapText = gui.TextInput(height=350, width='100%')#, style={'border': '1px solid black'})
		self.driveMapText.set_text(driveMap())
		rightContainer.append(self.driveLabel)
		rightContainer.append(self.driveMapText)
		#----------------------------------FINAL LAYOUT CONFIG----------------------------------------------------
		return container

start(MyApp)
