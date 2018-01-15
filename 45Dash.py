from Tkinter import *
from ttk import *
import sys, tempfile, os
import subprocess

#def choice(choiced):
#    if choiced == True:
createMenu = Tk()
createMenu.configure(background='#a1dbcd')
createMenu.title("Create")
createMenu.style = Style()
createMenu.style.theme_use("clam")
#    if choiced == False:
root = Tk()
root.configure(backgroun='#a1dbcd')
root.title("Monitor")
root.style = Style()
root.style.theme_use("clam")

#startMenu = Tk()
#startMenu.configure(background='#a1dbcd')
#startMenu.style = Style()
#startMenu.style.theme_use('clam')
#startMenuMsg = Message(startMenu, text="What would you like to do?")
#startMenuMsg.pack()
#createButton = Button(startMenu, text="Create", command=choice(True))
#monitorButton = Button(startMenu, text="Monitor", command=choice(False))
#createButton.pack()
#monitorButton.pack()

def choice(choiced):
    if choiced == True:
        createMenu = Tk()
        createMenu.configure(background='#a1dbcd')
        createMenu.style = Style()
        createMenu.style.theme_use("clam")
    if choiced == False:
        master = Tk()
        master.configure(backgroun='#a1dbcd')
        master.style = Style()
        master.style.theme_use("clam")

#--------------------------BACKEND--------------------------------------------------------------
def takeMeToRoot():
    #while (subprocess.check_output("pwd", stderr=subprocess.STDOUT, shell=True) != '/'):
    subprocess.call(['cd ../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../..'], shell=True)
def monitor():
    print "Monitor"
def createStorage(): # Run dmap, using entries from driver and chassis size, and then continues to create zcreate
    takeMeToRoot()
    subprocess.call(['wipedev -a'], shell=True)
    if driver[:1] != "l":
        subprocess.call([('dmap -c {} -s {}' .format(driver[:1], str(ChassisSize.get())))], shell=True)
    else:
        subprocess.call([('dmap -c 9305 -s {}' .format(str(ChassisSize.get())))], shell=True)
    subprocess.call([('zcreate -n {} -l {} -v {} -b' .format(Name.get(), RAIDEntry.get().lower(), VDEVEntry.get()))], shell=True)
    subprocess.call(['lsdev'], shell=True)
def mkbrick():
    takeMeToRoot()
    subprocess.call([('mkbrick -n {} -C -A -b {}'.format(Name.get(), BrickEntry.get()))], shell=True)
    subprocess.call(['firewall-cmd --permanent --add-port=24007-24008/tcp'], shell=True)
    subprocess.call(['firewall-cmd --permanent --add-port=4379/tcp'], shell=True)
    subprocess.call(['firewall-cmd --reload'], shell=True)
    subprocess.call(['systemctl enable glusterd'], shell=True)
    subprocess.call([("gluster peer probe {}" .format(str(AddrEntry.get())))], shell=True)
def preConfig():
    takeMeToRoot()
    subprocess.call(['wget images.45drives.com/gtools/preconfig'], shell=True)
    subprocess.call(['chmod +x ./preconfig'], shell=True)
    subprocess.call(['./preconfig -af'], shell=True)
def Config():
    takeMeToRoot()
    subprocess.call(['./preconfig -af'], shell=True)
def gCreate():
    takeMeToRoot()
    subprocess.call(['vim /root/vol.conf'], shell=True)
    writeToVim()
    subprocess.call([('gcreate -c /root/vol.conf -b {} -n {}'.format(AddrEntry.get()))], shell=True)
def CTDBCreate():
    takeMeToRoot()
    subprocess.call(['vim /root/ctdb.conf'])
    writeToVimCTDB()
    subprocess.call([('gcreate -c /root/ctdb.conf -b {} -n {}'.format(AddrEntry.get()))], shell=True)
    subprocess.call(['mkdir /mnt/ctdb'])
    subprocess.call(['echo localhost:/ctdb/mnt/ctdb glusterfs defaults,_netdev 0 0 >> /etc/fstab'], shell=True)
    subprocess.call(['mount /mnt/ctdb'], shell=True)
    subprocess.call(['firewall-cmd --permanent --add-ports=49152-49156/tcp'], shell=True)
    subprocess.call(['firewall-cmd --permanent --add-ports=2049/tcp'], shell=True)
    subprocess.call(['firewall-cmd --reload'], shell=True)
def writeToVim():
    takeMeToRoot()
    EDITOR = os.environ.get('EDITOR', "vim")
    with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
        tf.write("gluster volume create tank replica 2 \ \n")
        tf.write("HOST1:/zpool/vol1/brick HOST2:/zpool/vol2/brick \ \n")
        tf.write("HOST2:/zpool/vol1/brick HOST1:/zpool/vol2/brick \ \n")
        tf.write("force")
        tf.flush()
        call([EDITOR, tf.name])
        tf.seek(0)
        edited_message = tf.read
def writeToVimCTDB():
    takeMeToRoot()
    EDITOR = os.environ.get('EDITOR', "vim")
    with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
        tf.write("gluster volume create ctdb replica 2 \ \n")
        tf.write("gluster1:/zpool/ctdb/brick gluster2:/zpool/ctdb/brick \ \n")
        tf.write("force")
        tf.flush()
        call([EDITOR, tf.name])
        tf.seek(0)
        edited_message = tf.read

#-------------------------INTERFACE STYLING---------------------------------------------------
w = Label(createMenu, text="GlusterDASH", background='#a1dbcd')
w.pack()
#------------------------PRECONFIG BUTTONS---------------------------------------------------
PreConfigFrame = Frame(createMenu)
PreConfigFrame.pack(pady = 10, padx = 100, fill=X)
b3 = Button(createMenu, text="Run PreConfiguration (Will reboot system)", command=preConfig )
b3.pack()
b3 = Button(createMenu, text="Run PreConfiguration (Only run after reboot)", command=Config )
b3.pack()
#-------------------------NAME ENTRY BLOCK--------------------------------------------------
NameFrame = Frame(createMenu)
NameFrame.pack(pady = 10, padx = 100)
NameEntry = StringVar(createMenu)
Label(NameFrame, text="Storage Pool Name", background='#a1dbcd').grid(row=1, column=1)
v = StringVar()
Name = Entry(createMenu, textvariable=v)
Name.pack()
v.set("Gluster1")
#--------------------------DRIVER CONTROLLER BLOCK-------------------------------------------
ControllerFrame = Frame(createMenu)
ControllerFrame.pack(pady = 10, padx = 100)
ControllerEntry = StringVar(createMenu)
choices = { "","R750 (HighPoint R750)","R750 (HighPoint R750)", "LSI (LSI 9201 -24i)", "Adaptec (Adaptec HBA-1000i, ASR-81605Z)"}
ControllerEntry.set("R750 (HighPoint R750)") # set the default option
popupMenu = OptionMenu(ControllerFrame, ControllerEntry, *choices)
Label(ControllerFrame, text="Volume Disk Controller", background='#a1dbcd').grid(row = 1, column = 1)
popupMenu.grid(row = 2, column =1)
def change_dropdown(*args):
    print( ControllerEntry.get() )
ControllerEntry.trace('w', change_dropdown)
driver = ControllerEntry.get().lower()

#TypeFrame = Frame(createMenu)
#TypeFrame.pack(pady = 10, padx = 100)
#TypeEntry = StringVar(createMenu)
#choices = { "","Replicated", "Distributed", "Distributed Replicated","Striped", "Distributed Striped"}
#TypeEntry.set("Distributed") # set the default option
#Label(TypeFrame, text=" Volume Architecture Type ", background='#a1dbcd').grid(row = 1, column = 1)
#popupMenu.grid(row = 2, column =1)
#def change_dropdown(*args):
#    print( TypeEntry.get() )
#TypeEntry.trace('w', change_dropdown)
#---------------------------CHASSIS SIZE BLOCK------------------------------------------------
ChassisFrame = Frame(createMenu)
ChassisFrame.pack(pady = 10, padx = 100)
ChassisSize = StringVar(createMenu)
choices = { "", "","30","45","60"}
ChassisSize.set("45") # set the default option
popupMenu = OptionMenu(ChassisFrame, ChassisSize, *choices)
Label(ChassisFrame, text="Choose chassis size", background='#a1dbcd').grid(row = 1, column = 1)
popupMenu.grid(row = 2, column =1)
def change_dropdown(*args):
    print( ChassisSize.get() )
ChassisSize.trace('w', change_dropdown)
#--------------------------VDEV SPEC BLOCK----------------------------------------------------
VDEVFrame = Frame(createMenu)
VDEVFrame.pack(pady = 10, padx = 100)
VDEVEntry = StringVar(createMenu)
choices = {"",3,4,5,6}
VDEVEntry.set("3") # set the default option
popupMenu = OptionMenu(VDEVFrame, VDEVEntry, *choices)
Label(VDEVFrame, text="# of VDEVS", background='#a1dbcd').grid(row = 1, column = 1)
popupMenu.grid(row = 2, column =1)
def change_dropdown(*args):
    print( VDEVEntry.get() )
VDEVEntry.trace('w', change_dropdown)
#------------------------------RAID BLOCK-------------------------------------------------------
RAIDFrame = Frame(createMenu)
RAIDFrame.pack(pady = 10, padx = 100)
RAIDEntry = StringVar(createMenu)
choices = { "", "","RAIDZ1","RAIDZ2"}
RAIDEntry.set("RAIDZ2 (Recommended)") # set the default option
popupMenu = OptionMenu(RAIDFrame, RAIDEntry, *choices)
Label(RAIDFrame, text="RAID level", background='#a1dbcd').grid(row = 1, column = 1)
popupMenu.grid(row = 2, column =1)
def change_dropdown(*args):
    print( RAIDEntry.get() )
RAIDEntry.trace('w', change_dropdown)
#------------------------------CREATE ZPOOL BUTTON---------------------------------------------
ButtonFrame = Frame(createMenu)
ButtonFrame.pack(pady = 10, padx = 100)
b = Button(createMenu, text="Create Storage Pool", command=createStorage)
b.pack()
#-----------------------------BRICK BLOCK------------------------------------------------------
BrickFrame = Frame(createMenu)
BrickFrame.pack(pady = 10, padx = 100)
BrickEntry = StringVar(createMenu)
choices = { "",2,3,4,5,6}
BrickEntry.set(2) # set the default option
popupMenu = OptionMenu(BrickFrame, BrickEntry, *choices)
Label(BrickFrame, text="Number of Bricks", background='#a1dbcd').grid(row = 1, column = 1)
popupMenu.grid(row = 2, column =1)
def change_dropdown(*args):
    print( BrickEntry.get() )
BrickEntry.trace('w', change_dropdown)
#----------------------------ADDR BLOCK-------------------------------------------------------
AddrFrame = Frame(createMenu)
AddrFrame.pack(pady = 10, padx = 100)
AddrEntry = StringVar(createMenu)
Label(AddrFrame, text="Peer Address", background='#a1dbcd').grid(row=1, column =1)
q = StringVar()
Addr = Entry(createMenu, textvariable=q)
Addr.pack()
q.set("Server2")
#----------------------------MKBRICK BLOCK----------------------------------------------------
BrickButtonFrame = Frame(createMenu)
BrickButtonFrame.pack(pady = 10, padx = 100)
b2 = Button(createMenu, text="Make Brick / Firewall Ports", command=mkbrick)
b2.pack()

#-----------------------------Vim info block / button---------------------------------------------------
VimFrame = Frame(createMenu)
VimFrame.pack(pady = 10, padx = 100)
VimEntry = StringVar(createMenu)
VimChoices = { "", "Linked list (4 nodes, 4 bricks)", "Distributed Replica (4 nodes, 4 bricks)", "Distributed (4 nodes, 4 bricks)"}
VimEntry.set("Linked list (4 nodes, 4 bricks)")
popupMenu = OptionMenu(VimFrame, VimEntry, *VimChoices)
Label(VimFrame, text="Gluster Configuation", background='#a1dbcd').grid(row = 1, column = 1)
popupMenu.grid(row = 2, column = 1)
def change_dropdown(*args):
    print( VimEntry.get())
VimEntry.trace('w', change_dropdown)
VimButtonFrame = Frame(createMenu)
VimButtonFrame.pack(pady = 10, padx = 100)
b3 = Button(createMenu, text='Create Gluster Volume', command=gCreate)
b3.pack()
#_________________________________MONITOR STUFF_________________________________________________
#---------------------------------MONITOR BACKEND----------------------------------------------
def createVolumeList():
    takeMeToRoot()
    s=subprocess.Popen(["gluster volume list"], shell=True, stdout=subprocess.PIPE).stdout
    glusters = s.read().splitlines()
    return glusters
def volumeList():
    return subprocess.check_output("gluster volume list", stderr=subprocess.STDOUT, shell=True)
def displayStatus():
    return subprocess.check_output("gluster volume status all", stderr=subprocess.STDOUT, shell=True)
def displayInfo():
    return subprocess.check_output("gluster volume info all", stderr=subprocess.STDOUT, shell=True)
def driveMap():
    takeMeToRoot()
    r=subprocess.check_output("lsdev", stderr=subprocess.STDOUT, shell=True)
    badString = "1;30m"
    new=r.strip(badString)
    return new
#--------------------------------MONITOR FRONTEND------------------------------------------------
VolumeArea = Text(root, height=50, width=20)
VolumeArea.pack(pady=10, padx=10, side=LEFT)
VolumeArea.insert(END, volumeList())
VolumeArea.config(state=DISABLED)

DriveMapArea = Text(root, height=50, width=40)
DriveMapArea.pack(pady=10, padx=10, side=LEFT)
DriveMapArea.insert(END, driveMap())
DriveMapArea.config(state=DISABLED)

StatusArea = Text(root, height=25)
StatusArea.pack(pady=10, padx=10)
StatusArea.insert(END, displayStatus())
StatusArea.config(state=DISABLED)

InfoArea = Text(root, height=25)
InfoArea.pack(pady=10, padx=10)
InfoArea.insert(END, displayInfo())
InfoArea.config(state=DISABLED)

#------------------------------GENERATE INTERFACE----------------------------------------------
mainloop()
