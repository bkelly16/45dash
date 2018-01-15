import remi.gui as gui
from remi import start, App
import sys, tempfile, os
import subprocess

def takeMeToRoot():
	subprocess.call(['cd ../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../..'], shell=True)
def retrieveVolumes():
	takeMeToRoot()
	s=subprocess.Popen(["gluster volume list"], shell=True, stdout=subprocess.PIPE).stdout
	glusters = s.read().splitlines()
	return glusters
def displayStatus():
    return subprocess.check_output("gluster volume status all", stderr=subprocess.STDOUT, shell=True)
def displaySStatus(choice):
	return subprocess.check_output(["gluster volume status %s" % str(choice)], stderr=subprocess.STDOUT, shell=True)
def displayInfo():
    return subprocess.check_output("gluster volume info all", stderr=subprocess.STDOUT, shell=True)
def displaySInfo(choice):
    return subprocess.check_output(["gluster volume info %s" % str(choice)], stderr=subprocess.STDOUT, shell=True)
def driveMap():
    takeMeToRoot()
    r=subprocess.check_output("lsdev", stderr=subprocess.STDOUT, shell=True)
    badString = "1;30m"
    new=r.strip(badString)
    return new
def statusList(choice):
	r=subprocess.Popen(['gluster volume status %s' % choice], shell=True, stdout=subprocess.PIPE).stdout
	lines = r.read().splitlines()
	return lines
def splitLine(text):
	words = text.split()
	wordList = []
	for word in words:
		wordList.append(word)
	return wordList








volumeList = retrieveVolumes()
volumeList.append('all')
print retrieveVolumes()

class MyApp(App):
	def __init__(self, *args):
		super(MyApp, self).__init__(*args)

	def list_view_on_selected(self, widget, selection):
		choice = self.volumeList.children[selection].get_text()
		statusLines = statusList(choice)
		if choice == 'all':
			self.statusTable = gui.Table.new_from_list([('Gluster Process','TCP Port', 'RDMA', 'Port', 'Online', 'Pid'), (splitLine(statusLines[3])), (splitLine(statusLines[4])), (splitLine(statusLines[13])),(splitLine(statusLines[14])),(splitLine(statusLines[23])),(splitLine(statusLines[24]))], height=100, width='100%')
			self.statusText.set_text(displaySStatus(choice))
			self.infoText.set_text(displaySInfo(choice))
		else:
			self.statusTable = gui.Table.new_from_list([('Gluster Process','TCP Port', 'RDMA', 'Port', 'Online', 'Pid'), (splitLine(statusLines[3])), (splitLine(statusLines[4]))], height=100, width='100%')
			self.statusText.set_text(displaySStatus(choice))
			self.infoText.set_text(displaySInfo(choice))

	def main(self):
		choice = 'all'
		statusLines = statusList('testvol1')
		container = gui.Widget(width='80%', margin='0px auto', height='90%', style={'display': 'block', 'overflow':'auto'})
		leftContainer = gui.Widget(width='50%', height='100%', style={'float':'left','display':'block','overflow':'auto'})
		rightContainer = gui.Widget(width='50%', height='100%', style={'float':'right','display':'block', 'overflow':'auto'})
		menu = gui.Menu(width='100%', height='30px')
		menuCreate = gui.MenuItem('Create', width=100, height=30)
		menuMonitor = gui.MenuItem('Monitor', width=100, height=30)
		title = gui.MenuItem('45Dash', width=150, height=30)
		menu.append(title)
		menu.append(menuCreate)
		menu.append(menuMonitor)
		menubar = gui.MenuBar(width='100%', height='30px')
		menubar.append(menu)
		self.statusLabel = gui.Label('Volume Status', width='100%', height=30)
		self.volumeLabel = gui.Label('Active Volumes', width='100%', height=30)
		self.infoLabel = gui.Label('Volume Info', width='100%', height=30)
		self.driveLabel = gui.Label('Drive Map', width='100%', height=30)
		self.volumeList = gui.ListView.new_from_list(volumeList, width='100%', height=200)
		self.volumeList.set_on_selection_listener(self.list_view_on_selected)
		self.statusText = gui.TextInput(height=450, width='100%')#), style={'border': '1px solid black'})
		self.statusText.set_text(displaySStatus(choice))
		self.statusTable = gui.Table.new_from_list([('Gluster Process','TCP Port', 'RDMA', 'Port', 'Online', 'Pid'), (splitLine(statusLines[3])), (splitLine(statusLines[4]))], height=100, width='100%')
		self.infoText = gui.TextInput(height=300, width='100%')# , style={'border': '1px solid black'})
		self.infoText.set_text(displaySInfo(choice))
		self.driveMapText = gui.TextInput(height=350, width='100%')#, style={'border': '1px solid black'})
		self.driveMapText.set_text(driveMap())
		leftContainer.append(self.volumeLabel)
		leftContainer.append(self.volumeList)
		leftContainer.append(self.statusLabel)
		leftContainer.append(self.statusTable)
		leftContainer.append(self.statusText)
		rightContainer.append(self.infoLabel)
		rightContainer.append(self.infoText)
		rightContainer.append(self.driveLabel)
		rightContainer.append(self.driveMapText)
		container.append(menubar)
		container.append(leftContainer)
		container.append(rightContainer)
		return container




start(MyApp)