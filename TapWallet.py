from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from time import sleep
from random import *
from threading import *
import inspect

import bitcoin_core_framework as bitcoin_core
from test_framework import *
from bitcoinlib.services.services import *
from MuSig1 import c_MultiSig
from TapTree import TapRootClass
from helperFunctions import *

from TapTree import mainnet

selectedContainer=[]
service_=2


def make_lambda(a):
	return lambda x:console.copyText((a))
class keyCreationContainer:  #Top Box where public keys are created
	def __init__(self,root,x_pos,y_pos):
		self.container_KeyCreation = tk.LabelFrame(root)
		self.container_KeyCreation.pack()
		self.container_KeyCreation.place(height=127,width=590, x=x_pos,y=y_pos)

		self.entropy="key"
		self.privKey=None
		self.pubKey="0x00"
		self.typedLabel="Alice"#Give the Pubkey a label
		self.typedEntropy = StringVar()#Entropy Textfield
		self.typedPrivKey = StringVar()#Private Key Textfield
		self.typedPubKey = StringVar()#Public Key Textfield

		##Static Key Information
		self.label_label=tk.Label(self.container_KeyCreation,text="Label:");         self.label_label.pack();   self.label_label.place(height=20,x=4,y=2)
		self.label_entropy=tk.Label(self.container_KeyCreation,text="Entropy:");     self.label_entropy.pack(); self.label_entropy.place(height=20,x=4,y=27)
		self.label_privKey=tk.Label(self.container_KeyCreation,text="Private Key:"); self.label_privKey.pack(); self.label_privKey.place(height=20,x=4,y=52)
		self.label_pubKey=tk.Label(self.container_KeyCreation,text="Public Key:");   self.label_pubKey.pack();  self.label_pubKey.place(height=20,x=4,y=77)

		##Editable Key Information

		self.entry_Label=tk.Entry(self.container_KeyCreation);self.entry_Label.pack()
		self.entry_Label.place(height=20, x=100, y=2);self.entry_Label.delete(0, 'end');self.entry_Label.insert(0,self.typedLabel)

		
		self.entry_Entropy = tk.Entry(self.container_KeyCreation,textvariable=self.typedEntropy,bg="#CCCCEE")
		self.entry_Entropy.pack();self.entry_Entropy.bind("<KeyRelease>", self.getPubkeyFromEntropy);self.entry_Entropy.place(height=20, x=100, y=27)

		self.create_rnd_key=tk.Button(self.container_KeyCreation,text="Create a random key pair",command=self.getPubkeyFromRandom)
		self.create_rnd_key.pack()
		self.create_rnd_key.place(height=20, x=300, y=27)
		
		self.entry_PrivKey=tk.Entry(self.container_KeyCreation,textvariable=self.typedPrivKey,bg="#EECCCC")
		self.entry_PrivKey.pack();self.entry_PrivKey.bind("<KeyRelease>", self.getPubkeyFromPriv);self.entry_PrivKey.place(height=20,width=430, x=100, y=52)

		
		self.entry_PubKey=tk.Entry(self.container_KeyCreation,textvariable=self.typedPubKey)
		self.entry_PubKey.pack();self.entry_PubKey.bind("<KeyRelease>", self.getPubKeyfromPubKey);self.entry_PubKey.place(height=20,width=430, x=100, y=77)

		self.var_isMine=IntVar(value=True)
		self.check_isMine=tk.Checkbutton(self.container_KeyCreation, text="Do you own this public key?", variable=self.var_isMine)
		self.check_isMine.pack();self.check_isMine.place(height=20, x=4, y=102)
		

		self.button=tk.Button(self.container_KeyCreation,text="Add Key",bg="#00469b",fg="#FFFFFF",command=self.addPubKeyToContainer)
		self.button.pack()
		self.button.place(height=20, x=200, y=102)

		
		#self.is_checked=False
		

	def setText(self,noPriv=False):
		self.label_privKey.config(text="Private Key:")
		self.label_pubKey.config(text="Public Key:")
		self.label_label.config(text="Label:")

		self.entry_Entropy.delete(0, 'end')
		self.entry_Entropy.insert(0,self.entropy)
		if(self.privKey is None):self.entry_PrivKey.delete(0, 'end')
		if(self.privKey and noPriv==False):
			self.entry_PrivKey.delete(0, 'end')

			hexPriv=str(hex(self.privKey.secret))[2:]
			#if(len(hexPriv)<64):
			#	for i in range(0,64-len(hexPriv)):
			#		hexPriv="0"+hexPriv
			self.entry_PrivKey.insert(0,hexPriv)
		self.entry_PubKey.delete(0, 'end')
		self.entry_PubKey.insert(0,self.pubKey)

	def getPubkeyFromRandom(self):
		self.privKey,self.pubKey=generate_bip340_key_pair()
		self.entry_PrivKey.configure(fg="#000000")
		self.entropy=""
		self.check_isMine.select()
		self.setText()
	def getPubkeyFromEntropy(self,event=None):
		if(self.typedEntropy.get()==self.entropy):
			return;
		self.entropy=self.entry_Entropy.get()
		self.entry_PrivKey.configure(fg="#000000")
		sha=sha256(self.entropy.encode("utf-8"))
		self.privKey,self.pubKey=generate_bip340_key_pair(sha)
		self.check_isMine.select()
		self.setText()

	def getPubkeyFromPriv(self,event=None):
		if(event.keycode==17):return
		typedKey=self.typedPrivKey.get()
		if(typedKey==str(self.privKey)):
			return;
		#self.privKey=self.entry_PrivKey.get()
		if(len(typedKey)<64):
				for i in range(0,64-len(typedKey)):
					typedKey="0"+typedKey
		if(len(typedKey)==64):priv=bytes.fromhex(typedKey)
		if(len(typedKey)>64):self.entry_PrivKey.configure(fg="#ff0000");return
		else:self.entry_PrivKey.configure(fg="#000000")
		#else:priv=int(typedKey).to_bytes(32, byteorder='big')
		self.privKey,self.pubKey=generate_bip340_key_pair(priv)
		self.entropy=""
		self.check_isMine.select()
		self.setText(noPriv=True)
		

	def getPubKeyfromPubKey(self,event=None):

		if(self.typedPubKey.get()==str(self.pubKey)):
			return;
		self.privKey=None
		self.entropy=""
		self.pubKey=ECPubKey().set(bytes.fromhex(self.entry_PubKey.get()))
		self.check_isMine.deselect()
		self.setText()

	def addPubKeyToContainer(self):
		if(gui.TapRootContainer):
			#print("Can't add more public keys when taproot address was already created")
			console.printText("Can't add more public keys when taproot address was already created")
			return
		
		gui.addPubKeyContainer(self.entry_Label.get(),self.privKey,self.pubKey,[],self.var_isMine.get())




class c_Container: #Moveable Parent Container, can be a public key or script container
	def __init__(self,x_pos,y_pos,label,pubKey,parentArray,isMine):
		self.x_pos=x_pos

		if(self.x_pos==None):
			random_=randrange(0,gui.guix-100)
			self.x_pos=20+random_

		if(y_pos>gui.guiy-60):y_pos=gui.guiy-60
		self.y_pos=y_pos
		
		self.sizeX=225
		self.sizeY=60
		self.parentArray=parentArray
		self.childList=[]
		
		self.pubKey=None #Used by PubKey Container
		self.label=label
		
		self.active=True
		self.isMine=isMine

		self.root=gui.container_Script
		self.mouseDown=False
		self.mouseX=x_pos
		self.mouseY=y_pos
		self.isMini=False

		

		self.container = tk.LabelFrame(self.root)
		self.container.pack()
		self.container.place(height=self.sizeY,width=self.sizeX, x=self.x_pos,y=self.y_pos)
		self.container.bind('<Button-1>', self.onClick)
		self.container.bind('<B1-Motion>', self.onMove)
		self.container.bind('<Control-Button-1>', self.flag)
		self.container.bind('<Double-Button-1>', self.doubleClick)
		self.container.bind('<Button-3>',lambda x:console.copyText(str(pubKey)))

		self.highlightContainer=tk.Label(self.container,bg="#00FFFF")
		self.highlightContainer.pack()
		self.highlightContainer.place(height=15, x=14, y=2)
		self.highlightContainer.bind('<Button-1>', self.onClick)
		self.highlightContainer.bind('<B1-Motion>', self.onMove)
		self.highlightContainer.bind('<Control-Button-1>', self.flag)
		self.highlightContainer.bind('<Double-Button-1>', self.doubleClick)
		self.highlightContainer.bind('<Button-3>',lambda x:console.copyText(str(pubKey)))

		#text_l=tk.Label(self.highlightContainer,text="Selected",bg="#00FFFF")
		#text_l.pack()
		self.highlightContainer.place_forget()

		#text.place(height=15, x=1, y=2)

		self.label_label=tk.Label(self.container)
		self.label_label.pack()
		self.label_label.place(height=15, x=14, y=2)
		self.label_label.bind('<Button-1>', self.onClick)
		self.label_label.bind('<B1-Motion>', self.onMove)
		self.label_label.bind('<Control-Button-1>', self.flag)
		self.label_label.bind('<Double-Button-1>', self.doubleClick)
		self.label_label.bind('<Button-3>',lambda x:console.copyText(str(pubKey)))
		

		publabel1=slice(0,len(str(pubKey))//2)
		publabel2=slice(len(str(pubKey))//2,len(str(pubKey)))

		if(isinstance(self,c_Container_Script)):
			txt=str(shortenHexString(pubKey,True))
			if(self.timelockDelay>0):
				txt=txt+"\nRelative Timelock: "+str(self.timelockDelay)
			if(self.timelock>0):
				txt=txt+"\nAbsolute Timelock: "+str(self.timelock)
			self.label_label2=tk.Label(self.container,text=txt, justify=LEFT)
		else:
			self.label_label2=tk.Label(self.container,text=str(pubKey)[publabel1]+"\n"+str(pubKey)[publabel2])
		self.label_label2.pack()
		self.label_label2.place(height=25, x=4, y=22)
		self.label_label2.bind('<Button-1>', self.onClick)
		self.label_label2.bind('<B1-Motion>', self.onMove)
		self.label_label2.bind('<Control-Button-1>', self.flag)
		self.label_label2.bind('<Double-Button-1>', self.doubleClick)
		self.label_label2.bind('<Button-3>',lambda x:console.copyText(str(pubKey)))
		self.changeColor()
		self.line=[]
		if(parentArray!=None):
			for i in range(0, len(parentArray)):
				middleX=self.x_pos+(self.sizeX/2)
				middleY=self.y_pos+(self.sizeY/2)
				self.line.append(gui.canvas.create_line(middleX,middleY,parentArray[i].x_pos+(self.sizeX/2),parentArray[i].y_pos++(self.sizeY/2)))

		self.buttonMinimize=Button(self.container,bg="#FF8080", text="-", command=self.minimizeContainer)
		self.buttonMinimize.pack()
		self.buttonMinimize.place(height=15,width=15,x=2,y=0)

		self.buttonExit=Button(self.container,bg="#FF8080", text="X", command=self.removeContainer)
		self.buttonExit.pack()
		self.buttonExit.place(height=15,width=15,x=205,y=0)

		

		

	def onClick(self,event):
		self.mouseDown=True
		self.mouseX=self.root.winfo_pointerx()
		self.mouseY=self.root.winfo_pointery()

		if(self.x_pos<0):self.x_pos=0
		if(self.y_pos<0):self.y_pos=0
		if(self.x_pos>self.root.winfo_width()-self.sizeX):self.x_pos=self.root.winfo_width()-self.sizeX
		if(self.y_pos>self.root.winfo_height()-self.sizeY):self.y_pos=self.root.winfo_height()-self.sizeY

	def onMove(self,event,x=None,y=None):
		
		if(x!=None and y!=None):#onMove was called by parent
			self.x_pos=x
			self.y_pos=y
		
		else:
			

			if(self.mouseDown==False):return

			self.x_pos+=self.root.winfo_pointerx()-self.mouseX
			self.y_pos+=self.root.winfo_pointery()-self.mouseY

		
			self.mouseX=self.root.winfo_pointerx()
			self.mouseY=self.root.winfo_pointery()
		
			#tempX=self.x_pos
			#tempY=self.y_pos

			if(self.x_pos<0):self.x_pos=0
			if(self.y_pos<0):self.y_pos=0
			if(self.x_pos>self.root.winfo_width()-self.sizeX):self.x_pos=self.root.winfo_width()-self.sizeX
			if(self.y_pos>self.root.winfo_height()-self.sizeY):self.y_pos=self.root.winfo_height()-self.sizeY
		
		
		self.container.place(height=self.sizeY,width=self.sizeX, x=self.x_pos,y=self.y_pos)
		for i in range (0,len(self.childList)):
			self.childList[i].updateLine()

		if self.parentArray!=None:
			middleX=self.x_pos+(self.sizeX/2)
			middleY=self.y_pos+(self.sizeY/2)

			for i in range (0,len(self.parentArray)):
				gui.canvas.coords(self.line[i],middleX,middleY,self.parentArray[i].x_pos+(self.sizeX/2),self.parentArray[i].y_pos+(self.sizeY/2))

	def changeColor(self):

		color="#000000"

		if(self.isMine):
			if(isinstance(self,c_Container_PubKey)):color="#0099FF"
			if(isinstance(self,c_Container_Script)):color="#DC7A7A"
			if(isinstance(self,c_Container_Hash)):color="#16e971"
			if(isinstance(self,c_Container_Taproot)):color="#47C718"
			#pub "#0099FF","#CCEBFF"
			#script "#DC7A7A","#F5D6D6"
			#Hash "#16e971","E8FDF1"

			#self.container.config(bg=self.color)
			#self.label_label.config(bg=self.color)
			#self.label_label2.config(bg=self.color)
		else:
			if(isinstance(self,c_Container_PubKey)):color="#CCEBFF"
			if(isinstance(self,c_Container_Script)):color="#F5D6D6"
			if(isinstance(self,c_Container_Hash)):color="#E8FDF1"
			#self.container.config(bg=self.inactiveColor)
			#self.label_label.config(bg=self.inactiveColor)
			#self.label_label2.config(bg=self.inactiveColor)
		self.container.config(bg=color)
		self.label_label.config(bg=color)
		self.label_label2.config(bg=color)
		
	def flag(self,event):
		
		
		for i in range(0,len(selectedContainer)):
			if(selectedContainer[i]==self):
				self.changeColor()
				selectedContainer.remove(self)
				return

		#if(gui.TapRootContainer==None):#Don't flag when Taproot Address exists
		self.container.config(bg="#ff1a1a")
		self.label_label.config(bg="#ff1a1a")
		self.label_label2.config(bg="#ff1a1a")
		selectedContainer.append(self)

	def minimizeContainer(self):
		if(self.isMini):
			self.isMini=False
			self.sizeY=60
			self.sizeX=225
			
		else:
			self.isMini=True
			self.sizeY=25
			self.sizeX=120

		self.container.place(height=self.sizeY,width=self.sizeX, x=self.x_pos,y=self.y_pos)

	def removeContainer(self):

		for i in range(0,len(self.parentArray)):
			gui.canvas.delete(self.line[i])

		for i in range(0,len(self.childList)):
			self.childList[i].removeContainer()

	
		gui.removeKeyContainer(self)
		self.container.destroy()

	def updateLine(self):
		if(self.parentArray==None):
			return


		tempX=self.x_pos
		tempY=self.y_pos
		if(tempX<0):tempX=0
		if(tempY<0):tempY=0
		if(tempX>gui.guix-self.sizeX):tempX=gui.guix-self.sizeX
		if(tempY>gui.guiy-self.sizeY):tempY=gui.guiy-self.sizeY
		middleX=tempX+(self.sizeX/2)
		middleY=tempY+(self.sizeY/2)

		for i in range(0,len(self.parentArray)):
			gui.canvas.coords(self.line[i],middleX,middleY,self.parentArray[i].x_pos+(self.parentArray[i].sizeX/2),self.parentArray[i].y_pos+(self.parentArray[i].sizeY/2))
	
	def doubleClick(self,event):
		return

	def setParentActive(self):
		for a in range(0,len(self.parentArray)):
			container=self.parentArray[a]
			container.active=True
			container.setParentActive()


class c_Container_PubKey (c_Container):
	def __init__(self,x_pos,y_pos,privKey,pubKey,label,parentArray,isMine=False):
		
		c_Container.__init__(self,x_pos,y_pos,label,pubKey,parentArray,isMine)
		

		self.label_label.config(text="PubKey: "+str(label))
		self.highlightContainer.config(text="PubKey: "+str(label))
		self.privKey=privKey
		self.pubKey=pubKey
		self.lastTimelock=0

		if(x_pos==None):
			random_=randrange(0,1000)
			self.x_pos=20+random_

		if(self.y_pos>gui.guiy-self.sizeY):self.y_pos=gui.guiy-self.sizeY

		self.container.place(height=self.sizeY,width=self.sizeX, x=self.x_pos,y=self.y_pos)
		
		self.updateLine()

		self.editTimelock=0
		self.tab1=0
		self.tab2=0
		self.editLabel=0
		if(len(str(privKey))>5):print("Adding KeyPair: ",str(hex(privKey.secret))[2:]," - ",str(pubKey))
		elif(len(parentArray)==0):
			print("Adding Pubkey: ",str(pubKey))

	def doubleClick(self,event):
		
		self.scriptWindow = Toplevel(self.root)
		self.scriptWindow.title("Create Script or Taproot")
		self.scriptWindow.geometry("600x400")

		

		label1=Label(self.scriptWindow,text="Public Key:    "+str(self.label)+":")
		label1.pack()
		label1.place(x=5,y=15,anchor="nw")
		#Label(self.scriptWindow,text =str(self.label)).pack()
		#Label(self.scriptWindow,text ="PubKey: "+str(self.pubKey)).pack()
		data_string = StringVar()
		data_string.set(str(self.pubKey))
		e=Entry(self.scriptWindow,textvariable=data_string,fg="black",bg="white",bd=0,state="readonly")
		e.pack()
		e.place(x=150,y=17,width=400)

		scriptFrame = tk.LabelFrame(self.scriptWindow)
		scriptFrame.pack()
		scriptFrame.place(height=265,width=590, x=5,y=60)

		label=Label(scriptFrame,text="Create a script of the above key to specify spending conditions")
		label.pack()
		label.place(x=5,y=0,anchor="nw")
		labelLabel=tk.Label(scriptFrame,text="Add a label to script:")
		labelLabel.pack()
		labelLabel.place(height=15,x=5,y=30)
		
		self.editLabel=tk.Entry(scriptFrame)
		self.editLabel.pack()
		self.editLabel.place(height=15,width=80,x=150,y=30)
		self.editLabel.insert(0,str(self.label))

		labelTimelock=tk.Label(scriptFrame,text="Add a timelock to script:")
		labelTimelock.pack()
		labelTimelock.place(height=15,x=5,y=55)

		self.radioTimelockVar=IntVar(value=1)
		radioTimelock0=tk.Radiobutton(scriptFrame,text="No Timelock",variable=self.radioTimelockVar,value=1,command=self.showNoTimelock)
		radioTimelock0.pack()
		radioTimelock0.place(x=150,y=53)
		radioTimelock1=tk.Radiobutton(scriptFrame,text="Relative Timelock",variable=self.radioTimelockVar,value=2,command=self.showRelTimelock)
		radioTimelock1.pack()
		radioTimelock1.place(x=250,y=53)
		radioTimelock2=tk.Radiobutton(scriptFrame,text="Absolute Timelock",variable=self.radioTimelockVar,value=3,command=self.showAbsTimelock)
		radioTimelock2.pack()
		radioTimelock2.place(x=380,y=53)

		self.containerRelTimelock= tk.LabelFrame(scriptFrame,borderwidth=0)
		self.containerRelTimelock.pack()
		

		labelRelTimelock=tk.Label(self.containerRelTimelock,text="When the address receives funds, this script can only\nspend them after you wait the specified amount of blocks")
		labelRelTimelock.pack()
		labelRelTimelock.place(x=5,y=5)

		labelRelTimelock2=tk.Label(self.containerRelTimelock,text="This script can only spend after                     blocks have passed")
		labelRelTimelock2.pack()
		labelRelTimelock2.place(x=5,y=40)

		self.editRelTimelock=tk.Entry(self.containerRelTimelock)
		self.editRelTimelock.pack()
		self.editRelTimelock.place(height=15,width=50,x=177,y=40)

		self.containerAbsTimelock= tk.LabelFrame(scriptFrame,borderwidth=0)
		self.containerAbsTimelock.pack()
		#self.containerAbsTimelock.place(height=50,width=400,x=5,y=150)

		labelAbsTimelock=tk.Label(self.containerAbsTimelock,text="This script can only spend the funds\nat or after the specified block height")
		labelAbsTimelock.pack()
		labelAbsTimelock.place(x=5,y=5)

		labelAbsTimelock2=tk.Label(self.containerAbsTimelock,text="This script can only spend at or after block height")
		labelAbsTimelock2.pack()
		labelAbsTimelock2.place(x=5,y=40)

		self.editAbsTimelock=tk.Entry(self.containerAbsTimelock)
		self.editAbsTimelock.pack()
		self.editAbsTimelock.place(height=15,width=50,x=275,y=42)
		
		labelPassword=tk.Label(scriptFrame,text="Add a password to script: <<Not supported yet>>")
		labelPassword.pack()
		labelPassword.place(height=15,x=5,y=160)

		buttonScript=tk.Button(scriptFrame,text="Create Script", command=self.createScript,bg="#DC7A7A")
		buttonScript.pack()
		buttonScript.place(height=20,width=100,x=5,y=235)

		taprootFrame = tk.LabelFrame(self.scriptWindow)
		taprootFrame.pack()
		taprootFrame.place(height=60,width=590, x=5,y=330)

		buttonTaprootAddress=tk.Button(taprootFrame,text="Create Taproot", command=lambda:gui.calcKeyReleasedTapRoot(key=self),bg="#47C718")
		buttonTaprootAddress.pack()
		buttonTaprootAddress.place(height=20,width=100,x=5,y=20)

		labelInfo=tk.Label(taprootFrame,text="Creating a taproot address from this key\nwill delete all other scripts and keys\napart from parent keys")
		labelInfo.pack()
		labelInfo.place(x=120,y=5)

		self.LabelErrorTimeLock=tk.Label(self.scriptWindow,text="",fg="#FF0000")
		self.LabelErrorTimeLock.pack()
		self.LabelErrorTimeLock.place(x=220,y=35)
	
	def showNoTimelock(self):
		self.containerAbsTimelock.place_forget()
		self.containerRelTimelock.place_forget()

		self.editRelTimelock.delete(0, 'end')
		self.editAbsTimelock.delete(0, 'end')

	def showRelTimelock(self):
		self.containerAbsTimelock.place_forget()
		self.containerRelTimelock.place(height=75,width=400,x=150,y=80)
		self.editAbsTimelock.delete(0, 'end')

	def showAbsTimelock(self):
		self.containerRelTimelock.place_forget()
		self.containerAbsTimelock.place(height=75,width=400,x=150,y=80)
		self.editRelTimelock.delete(0, 'end')


	def createScript(self):

		if(gui.TapRootContainer):
			console.printText("Can't create a script when taproot address is already created")
			return

		if(len(self.editRelTimelock.get())>0):
			if(self.editRelTimelock.get().isnumeric()==False):
				console.printText("TimeLock must be a positive number or empty")
				return
			if(int (self.editRelTimelock.get())>65535 or int (self.editRelTimelock.get())<=0):
				console.printText("Rel TimeLock must be between 1 and 65535")
				return

		elif(len(self.editAbsTimelock.get())>0):
			if(self.editAbsTimelock.get().isnumeric()==False):
				console.printText("TimeLock must be a positive number or empty")
				return
			if(int (self.editAbsTimelock.get())>16777216 or int(self.editAbsTimelock.get())<=0):
				console.printText("Abs TimeLock must be bewteen 1 and 16777216")
				return


		
		self.LabelErrorTimeLock.config(text="")

		timelockdelay=0
		timelock=0

		if(len(self.editRelTimelock.get())>0):
			timelockdelay=int(self.editRelTimelock.get())
		elif(len(self.editAbsTimelock.get())>0):
			timelock=int(self.editAbsTimelock.get())

		tapLeaf,tapleaf_hash=tapTree.construct_Tapleaf(self.pubKey,timelockdelay,timelock)
		print("Adding Script: "+tapLeaf.script.hex()+" for Pubkey: "+str(self.pubKey)+"  TimeLockRel: "+str(timelockdelay)+"  TimeLockAbs: "+str(timelock))
		print("Adding TapBranch: "+tapleaf_hash.hex()+" for Script: ",tapLeaf.script.hex())
		#print(hash_.hex())

		parentArray=[]
		parentArray.append(self)
		child,child2=gui.addTapleafContainer(self.editLabel.get(),tapLeaf,timelockdelay,timelock,tapleaf_hash,parentArray,self.x_pos,self.isMine)
		self.childList.append(child)
		child.childList.append(child2)
		child.onMove(None)

		self.scriptWindow.destroy()

class c_Container_Script(c_Container):
	def __init__(self,label,script,timelockDelay,timelock,parentArray,isMine=False):
		x=parentArray[0].x_pos
		y=parentArray[0].y_pos+parentArray[0].sizeY+10

		self.timelockDelay=timelockDelay
		self.timelock=timelock

		c_Container.__init__(self,x,y,label,str(script.hex()),parentArray,isMine)


		self.label_label.config(text="Script: "+str(label))
		self.highlightContainer.config(text="Script: "+str(label))
		self.script=script
		self.label_label.bind('<Double-Button-1>', self.doubleClick)
		self.container.bind('<Double-Button-1>', self.doubleClick)
		


		self.container.place(height=self.sizeY,width=self.sizeX, x=self.x_pos,y=self.y_pos)

		self.updateLine()
		#middleX=self.x_pos+(self.sizeX/2)
		#middleY=self.y_pos+(self.sizeY/2)

		#self.line=gui.canvas.create_line(middleX,middleY,parent.x_pos+(self.sizeX/2),parent.y_pos++(self.sizeY/2))

	def doubleClick(self,event):
		
		self.scriptWindow = Toplevel(self.root)
		self.scriptWindow.title("See Script Details")
		self.scriptWindow.geometry("650x120")

		label=Label(self.scriptWindow,text="Script:    "+str(self.label)+":")
		label.pack()
		label.place(x=5,y=15)
		data_string = StringVar()
		data_string.set(str(self.script.hex()))
		e=Entry(self.scriptWindow,textvariable=data_string,fg="black",bg="white",bd=0,state="readonly")
		e.pack()
		e.place(x=150,y=17,width=500)

		label=Label(self.scriptWindow,text="PubKey:    "+str(self.parentArray[0].label)+":")
		label.pack()
		label.place(x=5,y=40)
		data_string = StringVar()
		data_string.set(str(self.parentArray[0].pubKey))
		e=Entry(self.scriptWindow,textvariable=data_string,fg="black",bg="white",bd=0,state="readonly")
		e.pack()
		e.place(x=150,y=42,width=400)

		if(self.timelockDelay>0):
			label=Label(self.scriptWindow,text="Relative TimeLock: ")
			data_string = StringVar()
			data_string.set(str(self.timelockDelay))
		if(self.timelock>0):
			label=Label(self.scriptWindow,text="Absolute TimeLock: ")
			data_string = StringVar()
			data_string.set(str(self.timelock))
		if(self.timelockDelay>0 or self.timelock>0):
			label.pack()
			label.place(x=5,y=65)
			e=Entry(self.scriptWindow,textvariable=data_string,fg="black",bg="white",bd=0,state="readonly")
			e.pack()
			e.place(x=150,y=67,width=400)


		
		#labelPassword=tk.Label(self.scriptWindow,text="Add a password to script: <<Not supported yet>>")
		#labelPassword.pack()
		#labelPassword.place(height=15,x=5,y=220)
		


	def flag(self,event):
		#Method Overwrite:
		#A script can only be flagged if a taproot address is already created.
		#A flagged script will be chosen for Script Path Signing
		if(gui.TapRootContainer==None):
			return

		c_Container.flag(self,event)

	def createTapbranch(self):
		tapBranch,hash_=tapTree.construct_Tapbranch(self.script)
		parentArray=[]
		parentArray.append(self)
		child=gui.addHashContainer(self.editLabel.get(),tapBranch,hash_,parentArray)
		self.childList.append(child)

	def onMove(self,event):
		c_Container.onMove(self,event)
		if(len(self.childList)!=1):
			print("Error in c_Container_Hash, onMove(). a script should always have exactly one child (a hash)")
			return

		self.childList[0].onMove(event,self.x_pos,self.y_pos+self.sizeY)

class c_Container_Hash(c_Container):
	def __init__(self,x_pos,y_pos,label,tapLeaf,hash_,parentArray,isMine=False):
		c_Container.__init__(self,x_pos,y_pos,label,str(hash_.hex()),parentArray,isMine)

		if(len(self.parentArray)==1):self.label_label.config(text="TapLeaf")
		else: self.label_label.config(text="TapBranch")
		self.tapLeaf=tapLeaf
		self.hash_=hash_
		self.label_balance=None

		if(self.x_pos==None):
			random_=randrange(0,100)
			self.x_pos=20+random_*10

		if(self.y_pos>gui.guiy-self.sizeY):self.y_pos=gui.guiy-self.sizeY

		


		if(self.y_pos>gui.guiy-self.sizeY):self.y_pos=gui.guiy-self.sizeY

		self.container.place(height=self.sizeY,width=self.sizeX, x=self.x_pos,y=self.y_pos)

		self.updateLine()
		if(len(self.parentArray)==1):self.buttonExit.destroy()

	def onMove(self,event,x=None,y=None):
		if(len(self.parentArray)==1 and x==None):
			self.parentArray[0].onMove(event)
			return#Only parent is a script. In that case the container only move when parent is called
		
		c_Container.onMove(self,event,x,y)

class c_Container_Taproot(c_Container):
	def __init__(self,x_pos,y_pos,internalKey,merkleRoot):
		
		self.internalKey=internalKey
		self.merkleRoot=merkleRoot
		self.taptree=None
		self.tapTweak=None
		self.tapTweak_bytes=None

		if(self.merkleRoot==None):#No scripts involved
			rootKey=selectedContainer[0]
			self.tapTweak_bytes = tagged_hash("TapTweak", self.internalKey.pubKey.get_bytes())
		
		else:#With scriptTree
			taptree = TapTree(key=self.internalKey.pubKey, root=merkleRoot.tapLeaf)
			self.taptree = taptree.construct()
			self.tapTweak_bytes=self.taptree[1]

		#print([taprootObject])
		taproot_pubkey_b = self.internalKey.pubKey.tweak_add(self.tapTweak_bytes).get_bytes()
		self.TapRootAddress = program_to_witness(1, taproot_pubkey_b,main=mainnet)
		self.tapTweak=ECKey().set(self.tapTweak_bytes)
		self.tweakedPubkey=ECPubKey().set(taproot_pubkey_b)


		self.tweaked_privkey=None
		if(self.internalKey.privKey):
			self.tweaked_privkey=self.internalKey.privKey.add(self.tapTweak_bytes)
			self.tweaked_privkey,pub=generate_bip340_key_pair(self.tweaked_privkey.secret)#createTapRootFromPriv(str(self.tweaked_privkey.secret))[0]
			
			
		#print("NEW: "+str(self.tweakedPubkey)+" : "+str(self.tweakedPubkey.get_y()))
		self.negated=False
		if(self.tweakedPubkey.get_y()%2!=0):
			#print("New Not Even")
			self.tweakedPubkey.negate()
			self.tapTweak.negate()
			self.internalKey.pubKey.negate()
			#self.internalKey.privKey.negate()
			self.negated=True


		parents=None
		if(merkleRoot):parents=[internalKey,merkleRoot]
		else: parents=[internalKey]
		c_Container.__init__(self,x_pos,y_pos,"Taproot Address",self.TapRootAddress,parents,True)

		if(y_pos>gui.guiy-self.sizeY):y_pos=gui.guiy-self.sizeY

		self.label_label.config(text="Taproot Address")

		self.control_map=None
		if(self.taptree):self.control_map=self.taptree[2]

		self.utxoList=[]
		self.containerChooseUTXO=None
		gui.canvasUTXO=None
		self.scrollable_frame=None

		if(merkleRoot):print("Calculate Taproot Address from Internal Key: ",str(internalKey.pubKey)," and Tapbranch Merkle Hash ",merkleRoot.hash_.hex())
		else: print("Calculate Taproot Address from Internal Key: ",str(internalKey.pubKey))
		
		#print("TapTweak: "+((self.tapTweak_bytes.hex())))
		#if(internalKey.privKey):
		#	print("Tweaked Priv Key: ",hex(self.tweaked_privkey.secret))
		#	print("----- from internal priv: ",hex(internalKey.privKey.secret)," and taptweak: ",self.tapTweak_bytes.hex())
		print("Tweaked Pub Key: ",taproot_pubkey_b.hex(),"  :  ",ECPubKey().set(taproot_pubkey_b).get_y())
		print("----- from internal pub: ",str(internalKey.pubKey),"  :  ",str(hex(internalKey.pubKey.get_y())))
		print("-----------and taptweak: ",self.tapTweak_bytes.hex())


		if(mainnet==True):
			print('\nSegwit address:', self.TapRootAddress," from Tweaked Pub Key: ",taproot_pubkey_b.hex())
			console.printText(text="Your Mainnet Taproot Address: "+self.TapRootAddress)
		else:
			print('\nTestnet address:', self.TapRootAddress," from Tweaked Pub Key: ",taproot_pubkey_b.hex())
			console.printText(text="Your Testnet Taproot Address: "+self.TapRootAddress)

		print("###########\n")

		
		self.updateLine()
		self.removeUnusedContainer()
		
		

	def removeUnusedContainer(self):
		for i in range (0,len(gui.pubKeyContainerArray)):
			gui.pubKeyContainerArray[i].active=False
		for i in range (0,len(gui.scriptContainerArray)):
			gui.scriptContainerArray[i].active=False
		for i in range (0,len(gui.hashContainerArray)):
			gui.hashContainerArray[i].active=False

		self.internalKey.active=True
		self.internalKey.setParentActive()

		if(self.merkleRoot):
			self.merkleRoot.active=True
			self.merkleRoot.setParentActive()

		a=0
		for i in range (0,len(gui.pubKeyContainerArray)):
			if(a>=len(gui.pubKeyContainerArray)):break
			if(gui.pubKeyContainerArray[a]):
				if(gui.pubKeyContainerArray[a].active==False):
					container=gui.pubKeyContainerArray[a]
					gui.pubKeyContainerArray.remove(container)
					container.removeContainer()
				else:a+=1
		a=0
		for i in range (0,len(gui.scriptContainerArray)):
			if(a>=len(gui.scriptContainerArray)):break
			if(gui.scriptContainerArray[a]):
				if(gui.scriptContainerArray[a].active==False):
					container=gui.scriptContainerArray[a]
					gui.scriptContainerArray.remove(container)
					container.removeContainer()
				else:a+=1
		a=0
		for i in range (0,len(gui.hashContainerArray)):
			if(a>=len(gui.hashContainerArray)):break
			if(gui.hashContainerArray[a]):
				if(gui.hashContainerArray[a].active==False):
					container=gui.hashContainerArray[a]
					gui.hashContainerArray.remove(container)
					container.removeContainer()
				else:a+=1
		
	def removeContainer(self):
		
		super().removeContainer()
		gui.TapRootContainer=None
		guiTX.radio_spendpath.set(1)
		guiTX.initKeyPathSelection()
		guiTX.checkPathSelection()
		


class Console:
	def __init__(self,master):
		self.root=master

		self.textArea=tk.Text(self.root,font=('arial',11, 'italic'))
		self.textArea.pack()
		self.textArea.place(height=310,width=450, x=1015,y=52)
		self.textArea.delete(1.0, 'end')
		
		self.textArea.insert(1.0,"Console.\n")
		self.textArea.configure(state='disabled')

		self.clearChecked=IntVar(value=0)
		self.clearBox=tk.Checkbutton(self.root, text="Clear console before entering new text", variable=self.clearChecked)
		self.clearBox.pack()
		self.clearBox.place(x=1015,y=27)
			  

	def printText(self=None,text="",keepOld=False):
		self.textArea.configure(state='normal')
		if(self.clearChecked.get()==1 and keepOld==False):
			self.textArea.delete(1.0, 'end')
		
		self.textArea.insert(END,text+"\n")
		self.textArea.configure(state='disabled')
		self.textArea.see("end")
		
	def copyText(self=None,text=""):
		r = Tk()
		r.withdraw()
		r.clipboard_clear()
		r.clipboard_append(text)
		r.update() # now it stays on the clipboard after the window is closed
		r.destroy()

		self.printText(text="Copied to clipboard: "+text)


class GraphicalUserInterfaceCanvas:
	def __init__(self,master):
		self.root=master

		#self.containerArray=[]
		self.pubKeyContainerArray=[]
		self.scriptContainerArray=[]
		self.hashContainerArray=[]
		#self.taprootContainerArray=[]
		self.varCheckMultiSig = []
		self.TapRootContainer=None
		self.editLabel=StringVar() #label on second window 
		self.guix=1460
		self.guiy=500
		

		#Container for MultiSig Check
		self.container_Script = tk.LabelFrame(self.root)
		self.container_Script.pack()
		self.container_Script.place(height=self.guiy,width=self.guix, x=5,y=400)

		
		self.canvas = tk.Canvas(self.container_Script)
		self.canvas.pack(fill=BOTH, expand=1)

		


		root.bind('<KeyRelease>',self.checkKeyReleased)

		root.geometry("1470x900")


	def calcKeyReleasedTapRoot(self,key=0):

		if(self.TapRootContainer):
			console.printText("You must delete your taproot address before creating new scripts,keys or a new address")
			return#If a Taproot address already exists, stop creating other containers

		if(key!=0):
			selectedContainer.clear()
			selectedContainer.append(key)

		rootKey=None
		merkle=None

		parentArray=[]
		
		for a in range (0, len(selectedContainer)):
			parentArray.append(selectedContainer[a-1])


		
		if(len(selectedContainer)==1):#No scripts involved
			rootKey=selectedContainer[0]

		else:

			for i in range (0,len(self.pubKeyContainerArray)):
				if self.pubKeyContainerArray[i]==selectedContainer[0]:
					rootKey=selectedContainer[0]
					merkle=selectedContainer[1]
					break
			if(rootKey==None):
				rootKey=selectedContainer[1]
				merkle=selectedContainer[0]
		
		x=400
		y=300

		if(len(parentArray)==2):
			x=(parentArray[0].x_pos+parentArray[1].x_pos)/2
			y=parentArray[0].y_pos
			if(parentArray[1].y_pos>y):y=parentArray[1].y_pos
			y+=parentArray[0].sizeY+10


		self.TapRootContainer=c_Container_Taproot(x,y,rootKey,merkle)
		thread_balance()
		guiTX.selectSigningMethod()

		for a in range (0, len(selectedContainer)):
			selectedContainer[a-1].childList.append(self.TapRootContainer)
			selectedContainer[a-1].flag(event=None)
		

		if(key==0):self.scriptWindow.destroy()
		else: key.scriptWindow.destroy()


	def calcKeyReleasedMultiSig(self):
		#Get the selected PubKeys and create a MultiSig container

		pubKeyArray=[]
		parentArray=[]

		isMine=False
		

		for i in range (0,len(selectedContainer)):
			pubKeyArray.append(selectedContainer[i].pubKey)
			if(selectedContainer[i].isMine):isMine=True
			parentArray.append(selectedContainer[i])

		if(len(pubKeyArray)==0):
			print("ERROR in calcKeyReleasedMultiSig. pubkeyArray length 0")
		
		musig_c, aggregate_key=generate_musig_key(pubKeyArray)

		if(aggregate_key.get_y()%2!=0):
			aggregate_key.negate()
		


		print("Create MuSig: "+str(aggregate_key)," from keys ",pubKeyArray)
		child=self.addPubKeyContainer(self.editLabel.get(),None,aggregate_key,parentArray,isMine)

		for a in range (0, len(selectedContainer)):
			selectedContainer[0].childList.append(child)
			selectedContainer[0].flag(event=None)
				

		self.scriptWindow.destroy()

	def calcKeyReleasedTapBranch(self):
		tapBranch,hash_=tapTree.construct_TapBranch(selectedContainer[0].tapLeaf,selectedContainer[1].tapLeaf,selectedContainer[0].hash_,selectedContainer[1].hash_)
		parentArray=[]
		parentArray.append(selectedContainer[0])
		parentArray.append(selectedContainer[1])
		isMine=False
		if(selectedContainer[0].isMine):isMine=True
		if(selectedContainer[1].isMine):isMine=True
		#child=gui.addHashContainer(self.editLabel.get(),tapBranch,hash_,parentArray,isMine)
		child=gui.addHashContainer("TapBranch",tapBranch,hash_,parentArray,isMine)
		selectedContainer[0].childList.append(child)
		selectedContainer[1].childList.append(child)

		for a in range (0, len(selectedContainer)):
				selectedContainer[0].flag(event=None)

		self.scriptWindow.destroy()

	def checkKeyReleased(self,event,):
		#When several container are flagged and "control key" is released,
		#this function will check if it needs to create a new container

		if (event.keycode==17):#control key released

			if(self.TapRootContainer):
				console.printText("You must delete your taproot address before creating new scripts,keys or a new address")
				return#If a Taproot address already exists, stop creating other containers

			pubKeyCounter=0
			hashCounter=0
			
			#this loop counts how many pubkeys and/or hashes are selected
			for a in range (0, len(selectedContainer)):
				for i in range (0,len(self.pubKeyContainerArray)):
					if self.pubKeyContainerArray[i]==selectedContainer[a]:
						pubKeyCounter+=1
						break
				for i in range (0,len(self.hashContainerArray)):
					if self.hashContainerArray[i]==selectedContainer[a]:
						hashCounter+=1
						break
			
			#Possible scenarios are 
			# 2 pubKeys are selected -> create MultiSig
			# 2 hashes are selected  -> create another hash
			# one pubkey and one hash are selected -> create Taproot
			# All other combinations will be rejected

			if hashCounter>2 or (hashCounter==2 and pubKeyCounter>0) or (hashCounter>0 and pubKeyCounter>1):
				print("Choose either (1) multiple pubic keys, (2) one public key and one hash or (3) two hashes")
				console.printText(text="Choose one of the following methods:")
				console.printText(text="- Flag multiple pub keys to create a multisig key",keepOld=True)
				console.printText(text="- Flag two hashes to create a child hash",keepOld=True)
				console.printText(text="- Flag a pub key and a hash to create a taproot address",keepOld=True)
				console.printText(text="- Flag a pub key to create a taproot address",keepOld=True)
				for a in range (0, len(selectedContainer)):
					selectedContainer[0].flag(event=None)
				return

			if pubKeyCounter>1:
				for container in selectedContainer:
					if (len(container.parentArray)>0):
						console.printText(text="A MultiSig key can't be part of another MultiSig key")
						return

			if len(selectedContainer)==0:#return if nothing is selected
				return

			#init Pop Up Window
			self.scriptWindow = Toplevel(self.root)
			self.scriptWindow.geometry("600x400")

			labelLabel=tk.Label(self.scriptWindow,text="Add a label")
			labelLabel.pack()
			labelLabel.place(x=5,y=5)
		
			self.editLabel=tk.Entry(self.scriptWindow)
			self.editLabel.pack()
			self.editLabel.place(height=15,width=150,x=160,y=5)

			if (pubKeyCounter==1 and hashCounter==1)or pubKeyCounter==1:
				self.scriptWindow.title("Create Taproot Address")
				self.editLabel.destroy()
				self.scriptWindow.geometry("400x120")
				labelLabel.place(height=50,width=400,anchor="nw")
				labelLabel.config(text="You are going to create a Taproot Address now.                         \n"+
								       "All public keys, scripts and hashes which are not part of the address  \n"+
								       "will be removed to make clear what is part of the address and what not.")
				buttonScript=tk.Button(self.scriptWindow,text="Create TapRoot", command=self.calcKeyReleasedTapRoot,bg="#47C718")
				
			elif pubKeyCounter>1 and hashCounter==0:
				

				self.scriptWindow.title("Create MultiSig Address")
				self.editLabel.insert(0,"MultiSig")
				buttonScript=tk.Button(self.scriptWindow,text="Create MultiSig", command=self.calcKeyReleasedMultiSig)
			elif pubKeyCounter==0 and hashCounter==2:
				self.calcKeyReleasedTapBranch()
				return
				#self.scriptWindow.title("Create Tapbranch")
				#self.editLabel.insert(0,"TapBranch")
				#buttonScript=tk.Button(self.scriptWindow,text="Create TapBranch", command=self.calcKeyReleasedTapBranch)
			else: return

			buttonScript.pack()
			buttonScript.place(height=15,width=100,x=5,y=65)
				

			
		

	def addPubKeyContainer(self,label,privKey,pubKey,parentArray=[],isMine=False):
		x=None
		y=None

		if(len(parentArray)==2):
			x=(parentArray[0].x_pos+parentArray[1].x_pos)/2
			y=parentArray[0].y_pos
			if(parentArray[1].y_pos>y):y=parentArray[1].y_pos
			y+=parentArray[0].sizeY+10

		if(y==None):y=20
		pubContainer=c_Container_PubKey(x,y,privKey,pubKey,label,parentArray,isMine)
		self.pubKeyContainerArray.append(pubContainer)
		return pubContainer

	def removeKeyContainer(self,container):
		for i in range (0,len(self.pubKeyContainerArray)):
			if self.pubKeyContainerArray[i]==container:
				self.pubKeyContainerArray.remove(container)
				break

		for i in range (0,len(self.scriptContainerArray)):
			if self.scriptContainerArray[i]==container:
				self.scriptContainerArray.remove(container)
				break

		for i in range (0,len(self.hashContainerArray)):
			if self.hashContainerArray[i]==container:
				self.hashContainerArray.remove(container)
				break
		
	def addTapleafContainer(self,label,tapLeaf,timelockDelay,timelock,hash_,parentArray,x,isMine=False):
		container_=c_Container_Script(label,tapLeaf.script,timelockDelay,timelock,parentArray,isMine)
		#addHashContainer()
		parent=[]
		parent.append(container_)
		container2=c_Container_Hash(container_.x_pos,container_.y_pos+container_.sizeY,label,tapLeaf,hash_,parent,isMine)
		self.hashContainerArray.append(container2)
		self.scriptContainerArray.append(container_)
		return container_,container2
	
	def removeScriptContainer(self,container):
		self.scriptContainerArray.remove(container)
	
	def addHashContainer(self,label,tapBranch,hash_,parentArray,isMine=False):
		x=None
		y=None

		if(len(parentArray)==2):
			x=(parentArray[0].x_pos+parentArray[1].x_pos)/2
			y=parentArray[0].y_pos
			if(parentArray[1].y_pos>y):y=parentArray[1].y_pos
			y+=parentArray[0].sizeY+10

		if(y==None):y=200

		container_=c_Container_Hash(x,y,label,tapBranch,hash_,parentArray,isMine)
		self.hashContainerArray.append(container_)
		return container_


class GraphicalUserInterfaceTX:
	def __init__(self,master,script,privKey,pubKey,timelockDelay):
		self.root=master
		self.script=script
		self.privKey=privKey
		self.pubKey=pubKey
		self.timelockDelay=timelockDelay

		

		self.segwitaddressDisplay = StringVar()
		self.segwitaddressDisplay.set("Address: Please create a taproot address first")
		displayAddress=Entry(self.root,textvariable=self.segwitaddressDisplay,fg="black",bg="white",bd=0,state="readonly")
		displayAddress.pack()
		displayAddress.place(width=450,anchor="nw")


		self.containerChooseUTXO = tk.LabelFrame(self.root)
		self.containerChooseUTXO.pack()
		self.containerChooseUTXO.place(height=155,width=600, x=5,y=30)

		
		button_checkBalance=tk.Button(self.containerChooseUTXO,text="Check Balance",bg="#00469b",fg="#FFFFFF",command=thread_balance)
		button_checkBalance.pack()
		button_checkBalance.place(height=20, x=10, y=10)

		self.label_balance=tk.Label(self.containerChooseUTXO,text="Balance:---")
		self.label_balance.pack();
		self.label_balance.place(x=110,y=10)

		

		self.label_selected=tk.Label(self.containerChooseUTXO,text="Selected Coins:---")
		self.label_selected.pack();
		self.label_selected.place(x=350,y=10)

		#ScrollFrame
		container = tk.Frame(self.containerChooseUTXO,bg="#FF0000")
		container.pack()
		container.place(height=100,width=595,x=0,y=50)
		canvas = tk.Canvas(container)#,bg="#00FF00")
		canvas.place(height=100,width=100, x=0,y=50)
		scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
		self.scrollable_frame = tk.Frame(canvas,width=100,height=150)
		self.scrollable_frame.place(x=0,y=50)
		
		
		self.scrollable_frame.bind("<Configure>",lambda e: canvas.configure(	scrollregion=canvas.bbox("all")))

			

		canvas.create_window(0, 0, window=self.scrollable_frame, anchor="w")
		canvas.configure(yscrollcommand=scrollbar.set)


		

		
		canvas.pack(side="left", fill="both", expand=True)
		scrollbar.pack(side="right", fill="y")

		##########################

		self.containerCreateTX = tk.LabelFrame(self.root)
		self.containerCreateTX.pack()
		self.containerCreateTX.place(height=155,width=600, x=5,y=185)

		self.typedLabel = StringVar()#Entropy Textfield

		self.typedAddress=StringVar()#Address we want to send funds to
		
		self.typedAmount = StringVar()#Private Key Textfield
		self.typedFee = StringVar()#Public Key Textfield
		self.typedChange = StringVar()#Public Key Textfield


		##Static Key Information
		#self.label_label=tk.Label(self.containerCreateTX,text="Label:");         self.label_label.pack();   self.label_label.place(height=20,x=4,y=2)
		self.label_1=tk.Label(self.containerCreateTX,text="Bitcoin address  					Amount");     self.label_1.pack(); self.label_1.place(height=20,x=187,y=2)
		self.label_address=tk.Label(self.containerCreateTX,text="Send To:");     self.label_address.pack(); self.label_address.place(height=20,x=4,y=27)
		self.label_fee=tk.Label(self.containerCreateTX,text="Fee:");		     self.label_fee.pack();     self.label_fee.place(height=20,x=4,y=52)
		self.label_change=tk.Label(self.containerCreateTX,text="Change:");       self.label_change.pack();  self.label_change.place(height=20,x=4,y=77)
		
		
		##Editable Key Information

		#self.entry_Label=tk.Entry(self.containerCreateTX,textvariable=self.typedLabel);self.entry_Label.pack()
		#self.entry_Label.place(height=20,width=300, x=100, y=2);

		
		
		self.entry_Address = tk.Entry(self.containerCreateTX,textvariable=self.typedAddress,width=20,bg="#CCCCEE")
		self.entry_Address.pack();self.entry_Address.place(height=20,width=380, x=70, y=27)
		self.entry_Address.bind("<KeyRelease>", self.checkTxReady);
		
		self.entry_Amount=tk.Entry(self.containerCreateTX,textvariable=self.typedAmount,bg="#EECCCC")
		self.entry_Amount.pack();self.entry_Amount.place(height=20,width=100, x=460, y=27)
		self.entry_Amount.bind("<KeyRelease>", self.updateFee);
		#self.entry_Amount.bind("<KeyRelease>", self.checkTxReady);
		
		self.entry_Fee=tk.Entry(self.containerCreateTX,textvariable=self.typedFee)
		self.entry_Fee.pack();self.entry_Fee.place(height=20,width=100, x=70, y=52)
		self.entry_Fee.bind("<KeyRelease>", self.updateChange);

		self.entry_Change=tk.Entry(self.containerCreateTX,textvariable=self.typedChange,state=DISABLED)
		self.entry_Change.pack();self.entry_Change.place(height=20,width=100, x=70, y=77)
		
		



		self.button=tk.Button(self.containerCreateTX,text="Create Transaction",bg="#00469b",fg="#FFFFFF",command=self.createTX, state= DISABLED)
		self.button.pack()
		self.button.place(height=20, x=400, y=77)

		self.PathContainer=None
		self.PathValueArray=[]
		self.PathValueArray2=[]
		self.selectSigningMethod()#needs to be removed

		self.selected_balance=0

	def checkTxReady(self,event=None):
		if(event is not None):
			if (event.keycode==17 or event.keycode==16):return#Don't trigger when Shift or Control is released
		ret=False
		if(gui.TapRootContainer is None):self.button["state"]=DISABLED;ret=True
		if(self.selected_balance<=0):self.button["state"]=DISABLED;ret=True
		if(tapTree.address_to_scriptPubKey(self.typedAddress.get()) is None):
			self.button["state"]=DISABLED;
			ret=True
			self.entry_Address.configure(fg="#ff0000")
		else:
			self.entry_Address.configure(fg="#000000")
		
		if(len(self.typedAmount.get()) ==0):self.button["state"]=DISABLED;ret=True
		
		try:
			amt=(float)(self.typedAmount.get())
		except:
			self.entry_Amount.configure(fg="#ff0000")
			self.button["state"]=DISABLED;return
		else:self.entry_Amount.configure(fg="#000000")

		try:
			fee=(float)(self.typedFee.get())
		except:
			self.entry_Fee.configure(fg="#ff0000")
			self.button["state"]=DISABLED;return
		else:self.entry_Fee.configure(fg="#000000")
		
		if(self.selected_balance-amt<=0):self.button["state"]=DISABLED;return

		if(ret):return

		checked=False
		if(self.keyPathChosen):
			for i in range(0,len(self.PathValueArray)):
				if(self.PathValueArray[i][0].get()):checked=True
		else:
			for i in range(0,len(self.PathValueArray2)):
				if(self.PathValueArray2[i][0].get()):checked=True
		
		if(checked==False):self.button["state"]=DISABLED;print("No checkbox checked");return

		self.button["state"]=NORMAL
		
	def update(self,utxo_List):
		if(gui.TapRootContainer):
			self.segwitaddressDisplay.set("Address: "+str(gui.TapRootContainer.TapRootAddress))
			i=0
			balance=0
			self.label_selected.config(text="Selected Coins: 0 BTC")
			for child in self.scrollable_frame.winfo_children():
				child.destroy()
			del gui.TapRootContainer.utxoList[:]

			for utxo in utxo_List:
			
			
				txId=utxo['txid']
				outputIndex=utxo['output_n']
				value=utxo['value']/100000000

				var=IntVar(value=0)
				new_utxo=(var,utxo)
				
				gui.TapRootContainer.utxoList.append(new_utxo)
				#label_utxo=tk.Label(self.scrollable_frame,text=txId+" ["+str(outputIndex)+"]"+":"+"{:,.8f}".format(value)+" BTC");label_utxo.pack();#label_utxo.place(x=10,y=10+20*i)
				#ttk.Label(self.scrollable_frame, text="Sample scrolling label").pack()
				check_utxo=tk.Checkbutton(self.scrollable_frame, text=shortenHexString(txId)+" ["+str(outputIndex)+"]"+":"+"{:,.8f}".format(value)+" BTC", variable=var,command=guiTX.updateSelected)
				check_utxo.pack()#check_utxo.place(x=500,y=10+20*i)
				check_utxo.bind('<Button-3>',make_lambda(str(txId)))

				balance+=value
				i=i+1

			#for i in range(100):
			#	label_utxo=tk.Label(self.scrollable_frame,text="hallo"+str(i))
			#	label_utxo.pack()
			self.label_balance.config(text="Balance: "+"{:,.8f}".format(balance)+" BTC")
			self.updateSelected()

		else:
			self.segwitaddressDisplay.set("Address: Please create a taproot address first")
		
	def updateSelected(self):
		self.selected_balance=0
		for utxo in gui.TapRootContainer.utxoList:
			
			if(utxo[0].get()==1):
				self.selected_balance+=utxo[1]["value"]/100000000
		self.label_selected.config(text="Selected Coins: "+"{:,.8f}".format(self.selected_balance)+" BTC")

		self.updateFee(event=None)
		self.checkTxReady()

	def Container_setActive(self):
		if(self.radio_keypath.get()==1):

			for i in range (0,len(gui.scriptContainerArray)):
				gui.scriptContainerArray[i].active=False
				gui.scriptContainerArray[i].changeColor()
		else:
			for i in range (0,len(gui.scriptContainerArray)):
				gui.scriptContainerArray[i].active=True
				gui.scriptContainerArray[i].changeColor()
	
	def selectSigningMethod(self):
		
		self.containerChooseSigningMethod = tk.LabelFrame(self.root)
		self.containerChooseSigningMethod.pack()
		self.containerChooseSigningMethod.place(height=310,width=400, x=610,y=30)

		self.keyPathChosen=True

		self.radio_spendpath=IntVar()
		self.radio_scriptpath=IntVar()

		text="Spend via KeyPath: Most private and less expensive."
		self.radio_KeyPath=tk.Radiobutton(self.containerChooseSigningMethod,text=text,variable=self.radio_spendpath,value=1,command=self.initKeyPathSelection)
		self.radio_KeyPath.pack();self.radio_KeyPath.place(height=20, x=10, y=10)

		text="Spend via ScriptPath: Alternate way if keypath not possible"
		self.radio_ScriptPath=tk.Radiobutton(self.containerChooseSigningMethod,text=text,variable=self.radio_spendpath,value=2,command=self.initScriptPathSelection)
		self.radio_ScriptPath.pack();self.radio_ScriptPath.place(height=20, x=10, y=35)


		
	def initKeyPathSelection(self):
		self.keyPathChosen=True
		if(self.PathContainer):self.PathContainer.destroy()
		del self.PathValueArray[:]
		

		self.PathContainer = tk.LabelFrame(self.containerChooseSigningMethod)
		self.PathContainer.pack();self.PathContainer.place(height=245,width=394, x=1, y=60)
		self.PathValueArray=[]

		text=""
		if(gui.TapRootContainer==None):
			text="Please create a taproot address first"
			label=tk.Label(self.PathContainer,text=text);label.pack();label.place(height=20,x=4,y=2)
			return
		if(gui.TapRootContainer.internalKey.isMine==False):
			text="You do not own a KeyPath public key."
			label=tk.Label(self.PathContainer,text=text);label.pack();label.place(height=20,x=4,y=2)
			return

		if(len(gui.TapRootContainer.internalKey.parentArray)==0):
			var=IntVar(value=0)
			PathValue=[var,gui.TapRootContainer.internalKey]
			label_keys=tk.Checkbutton(self.PathContainer,text="Sign with: "+shortenHexString(str(gui.TapRootContainer.internalKey.pubKey)),variable=var,command=self.checkPathSelection)
			label_keys.pack();
			label_keys.place(height=20,x=4,y=2)
			label_keys.bind('<Button-3>',lambda x:console.copyText(str(gui.TapRootContainer.internalKey.pubKey)))
			self.PathValueArray.append(PathValue)
		
		if(len(gui.TapRootContainer.internalKey.parentArray)>0):
			text="Your Public Key is part of a multisig. You can create a signature,\nbut also need the signatures of the other keys"
			label=tk.Label(self.PathContainer,text=text);label.pack();label.place(height=45,x=4,y=2)
			
			var=IntVar()
			PathValue=[var,gui.TapRootContainer.internalKey]
			self.PathValueArray.append(PathValue)

			counter=0

			for i in range(0,len(gui.TapRootContainer.internalKey.parentArray)):
				var=IntVar()
				if(gui.TapRootContainer.internalKey.parentArray[i].isMine):
					text="Sign with "+gui.TapRootContainer.internalKey.parentArray[i].label+": "+shortenHexString(str(gui.TapRootContainer.internalKey.parentArray[i].pubKey))
					chkbutton=tk.Checkbutton(self.PathContainer,text=text,variable=var,command=self.checkPathSelection)
					chkbutton.bind('<Button-3>',make_lambda(str(gui.TapRootContainer.internalKey.parentArray[i].pubKey)))
				else:
					text="Key of "+gui.TapRootContainer.internalKey.parentArray[i].label+": "+shortenHexString(str(gui.TapRootContainer.internalKey.parentArray[i].pubKey))
					chkbutton=tk.Checkbutton(self.PathContainer,text=text,state=DISABLED)
					chkbutton.bind('<Button-3>',make_lambda(str(gui.TapRootContainer.internalKey.parentArray[i].pubKey)))
				
				PathValue=[var,gui.TapRootContainer.internalKey.parentArray[i]]
				chkbutton.pack();chkbutton.place(height=20,x=4,y=52+counter*25)
				self.PathValueArray.append(PathValue)
				counter+=1

		self.checkPathSelection()

	def initScriptPathSelection(self):
		self.keyPathChosen=False
		if(self.PathContainer):self.PathContainer.destroy()
		del self.PathValueArray[:]
		del self.PathValueArray2[:]

		self.PathContainer = tk.LabelFrame(self.containerChooseSigningMethod)
		self.PathContainer.pack();self.PathContainer.place(height=245,width=394, x=1, y=60)
		self.PathValueArray=[]
		self.PathValueArray2=[]

		text=""
		if(gui.TapRootContainer==None):
			text="Please create a taproot address first"
			label=tk.Label(self.PathContainer,text=text);label.pack();label.place(height=20,x=4,y=2)
			self.checkPathSelection()
			return
		if(gui.TapRootContainer.merkleRoot==None):
			text="This address has no script path scripts."
			label=tk.Label(self.PathContainer,text=text);label.pack();label.place(height=20,x=4,y=2)
			self.checkPathSelection()
			return

		counter=0
		counterY=-5

		self.radio_scriptpath=IntVar(value=0)
		for i in range(0,len(gui.scriptContainerArray)):
			if(gui.scriptContainerArray[i].isMine):
				
				text="Script "+gui.scriptContainerArray[i].label+": "+shortenHexString(str(gui.scriptContainerArray[i].script.hex()))
				#text+="\nSign with pubkey: "+str(gui.scriptContainerArray[i].parentArray[0].pubKey)
				
				var=IntVar()
				var2=IntVar(value=counter)
				PathValue1=[var,gui.scriptContainerArray[i]]
				PathValue2=[var,var2,gui.scriptContainerArray[i].parentArray[0]]
				radiobutton=tk.Radiobutton(self.PathContainer,text=text,variable=self.radio_scriptpath,value=counter,command=self.checkPathSelection)
				counterY+=5
				radiobutton.pack();radiobutton.place(height=40,x=4,y=counterY)
				#radiobutton.bind('<Button-3>',lambda x:console.copyText(str(gui.scriptContainerArray[i].script.hex())))
				radiobutton.bind('<Button-3>',make_lambda(str(gui.scriptContainerArray[i].script.hex())))
				counterY+=27
				self.PathValueArray.append(PathValue1)

				pubkeyContainer=gui.scriptContainerArray[i].parentArray[0]
				if(len(pubkeyContainer.parentArray)==0):
					text="Pubkey "+gui.scriptContainerArray[i].parentArray[0].label+": "+shortenHexString(str(gui.scriptContainerArray[i].parentArray[0].pubKey))
					chkbutton=tk.Checkbutton(self.PathContainer,text=text,variable=var,command=self.checkPathSelection)
					
					chkbutton.pack();chkbutton.place(height=40,x=14,y=counterY)
					#chkbutton.bind('<Button-3>',lambda x:console.copyText(str(gui.scriptContainerArray[i].parentArray[0].pubKey)))
					chkbutton.bind('<Button-3>',make_lambda(str(gui.scriptContainerArray[i].parentArray[0].pubKey)))
					counterY+=27
					self.PathValueArray2.append(PathValue2)
					

				else:
					counter2=0
					
						
					for o in range (0,len(pubkeyContainer.parentArray)):
						if(pubkeyContainer.parentArray[o].isMine):
							var=IntVar()
							PathValue2=[var,var2,pubkeyContainer.parentArray[o]]
							text="Pubkey "+pubkeyContainer.parentArray[o].label+": "+shortenHexString(str(pubkeyContainer.parentArray[o].pubKey))
							chkbutton=tk.Checkbutton(self.PathContainer,text=text,variable=var,command=self.checkPathSelection)
						
							chkbutton.pack();chkbutton.place(height=40,x=14,y=counterY)
							#chkbutton.bind('<Button-3>',lambda x:console.copyText(str(pubkeyContainer.parentArray[o].pubKey)))
							chkbutton.bind('<Button-3>',make_lambda(str(pubkeyContainer.parentArray[o].pubKey)))
							counterY+=27
							self.PathValueArray2.append(PathValue2)
							counter2+=1
						else:
							text="Key of "+gui.TapRootContainer.internalKey.parentArray[o].label+": "+shortenHexString(str(gui.TapRootContainer.internalKey.parentArray[o].pubKey))
					
							chkbutton=tk.Checkbutton(self.PathContainer,text=text,state=DISABLED)
							chkbutton.pack();chkbutton.place(height=40,x=14,y=counterY)
							#chkbutton.bind('<Button-3>',lambda x:console.copyText(str(gui.TapRootContainer.internalKey.parentArray[o].pubKey)))
							chkbutton.bind('<Button-3>',make_lambda(str(gui.TapRootContainer.internalKey.parentArray[o].pubKey)))
							counterY+=27
							counter2+=1
				
				counter+=1
				

		if(counter==0):
			text="You don't own keys that can spend via script path'"
			label=tk.Label(self.PathContainer,text=text);label.pack();label.place(height=20,x=4,y=2)

		self.checkPathSelection()

	def setHighlightContainer(self,container):
		container.highlightContainer.place(height=15, x=14, y=2)
		container.label_label.place_forget()
	def removeHighlightContainer(self,container):
		container.highlightContainer.place_forget()
		container.label_label.place(height=15, x=14, y=2)

	def checkPathSelection(self):
		for i in range(0,len(gui.pubKeyContainerArray)):
			self.removeHighlightContainer(gui.pubKeyContainerArray[i])
		for i in range(0,len(gui.scriptContainerArray)):
			self.removeHighlightContainer(gui.scriptContainerArray[i])

		if(self.radio_spendpath.get()==1 and len(self.PathValueArray)>0):#If KeyPath radio button is selected and keypath possible
			#If first key does not have parents, it is a single interal key. Check it automatically
			if(len(self.PathValueArray[0][1].parentArray)==0):
					self.PathValueArray[0][0].set(1)
					self.setHighlightContainer(self.PathValueArray[0][1])#hightlight multisig key
			
			else:#Search for selected checkboxes and hightlight the container + MultiSig
				self.setHighlightContainer(self.PathValueArray[0][1])#hightlight multisig key
				for i in range(0,len(self.PathValueArray)):
					if(self.PathValueArray[i][0].get()==1):
						self.setHighlightContainer(self.PathValueArray[i][1])
						
			#If just one key is available, check if it is a multisig
			
			#	if(len(self.PathValueArray[0][1].parentArray)==0):
			#		self.PathValueArray[0][0].select()
			#		self.PathValueArray[0][1].highlightContainer.place(height=15, x=105, y=2,width=85)#hightlight multisig key
			#	else: 
			#for i in range(0,len(self.PathValueArray)):
			#	if(self.PathValueArray[i][0].get()==1):
			#		self.PathValueArray[i][1].highlightContainer.place(height=15, x=105, y=2,width=85)
				

		if(self.radio_spendpath.get()==2):#If ScriptPath radio button is selected
			radio=self.radio_scriptpath.get()
			if(self.radio_scriptpath.get()>=len(self.PathValueArray)):
				guiTX.checkTxReady()
				return
			self.setHighlightContainer(self.PathValueArray[radio][1])#hightlight script container

			parent=self.PathValueArray[radio][1].parentArray[0]#get the pubkey that created the script
			if(len(parent.parentArray)==0):#if the pubkey has no parents, it can be checked
				for i in range(0,len(self.PathValueArray2)):
					if(self.PathValueArray2[i][1].get()==radio):
						self.PathValueArray2[i][0].set(1)
						self.setHighlightContainer(self.PathValueArray2[i][2])#hightlight multisig key
					else: self.PathValueArray2[i][0].set(0)
			else:#it is a multisig address
				self.setHighlightContainer(parent)#hightlight multisig address
				counter=0
				for i in range(0,len(self.PathValueArray2)):
					if(self.PathValueArray2[i][1].get()==radio):
						counter+=1
						if(self.PathValueArray2[i][0].get()==1):
							self.setHighlightContainer(self.PathValueArray2[i][2])#hightlight pubkey of MuSig
						
					else: self.PathValueArray2[i][0].set(0)
				if(counter==1):#You own one key of the MultiSig
					for i in range(0,len(self.PathValueArray2)):
						if(self.PathValueArray2[i][1].get()==radio):
							self.PathValueArray2[i][0].set(1)
							self.setHighlightContainer(self.PathValueArray2[i][2])#hightlight multisig key
				
				
		#self.highlightContainer.place_forget()
		#self.highlightContainer.place(height=15, x=105, y=2,width=85)
		guiTX.checkTxReady()

	def updateFee(self,event):
		self.entry_Fee.delete(0, 'end')
		self.entry_Change.configure(state='normal')
		self.entry_Change.delete(0, 'end')
		try:
			amt=(float)(self.typedAmount.get())
		except:
			self.entry_Amount.configure(fg="#ff0000")
			self.button["state"]=DISABLED;print("invalid amount");return False
		else:self.entry_Amount.configure(fg="#000000")

		if(amt==0):
			self.button["state"]=DISABLED;print("Fee 0");self.entry_Amount.configure(fg="#ff0000");return False
		else:self.entry_Amount.configure(fg="#000000")
		
		fee=(round(self.selected_balance-amt, 8))
		
		if((float)(fee)<0):
			self.entry_Amount.configure(fg="#ff0000")
			self.button["state"]=DISABLED;print("not enough funds");return False
			return False
		else:self.entry_Amount.configure(fg="#000000")

		suggested_fee=0.00001
		if((float)(fee)<=suggested_fee):
			self.entry_Fee.insert(0,"{:,.8f}".format(fee))
			self.entry_Change.insert(0,"0")
			self.entry_Change.configure(state='disabled')
			self.checkTxReady()
			return True
		change=(round(fee-suggested_fee, 8))
		self.entry_Fee.insert(0,"{:,.8f}".format(suggested_fee))
		self.entry_Change.insert(0,"{:,.8f}".format(change))
		self.entry_Change.configure(state='disabled')

		self.checkTxReady()
		return True
		

	def updateChange(self,event):
		self.entry_Change.configure(state='normal')
		self.entry_Change.delete(0, 'end')
		try:
			fee=(float)(self.typedFee.get())
		except:
			self.entry_Change.insert(0,"invalid input")
			self.entry_Change.configure(state='disabled')
			self.entry_Fee.configure(fg="#ff0000");self.button["state"]=DISABLED;ret=True;print("Fee invalid")
			return False
		else:self.entry_Fee.configure(fg="#000000")

		try:
			amt=(float)(self.typedAmount.get())
		except:
			self.entry_Fee.insert(0,"invalid input")
			return False

		suggested_fee=0.000001
		if((float)(fee)<suggested_fee):
			self.entry_Change.insert(0,"Fee too small")
			self.entry_Change.configure(state='disabled')
			self.entry_Fee.configure(fg="#ff0000");self.button["state"]=DISABLED;ret=True;print("Fee too small")
			return False
		else:self.entry_Fee.configure(fg="#000000")

		#if(self.typedAmount.get().isdecimal()==False):return
		#amt=(float)(self.typedAmount.get())

		change=(round(self.selected_balance-amt-fee, 8))

		if(change<0):
			self.entry_Change.insert(0,"not enough funds")
			self.entry_Change.configure(state='disabled')
			self.entry_Fee.configure(fg="#ff0000");self.button["state"]=DISABLED;ret=True;print("Fee invalid")
			return False
		else:self.entry_Fee.configure(fg="#000000")

		self.entry_Change.insert(0,"{:,.8f}".format(change))
		self.entry_Change.configure(state='disabled')

		self.checkTxReady()
		return True

	def get_destinationList(self):#creates a list of addresses that receive funds in the tx
		destination=[self.typedAddress.get(),(float)(self.typedAmount.get())]
		destination_list=[destination]

		if((float)(self.typedChange.get())>0):#Create Change Output
				destination_list.append([gui.TapRootContainer.TapRootAddress,(float)(self.typedChange.get())])

		return destination_list

	def broadcastWindow(self,tx):

		publishWindow = Toplevel(self.root)
		publishWindow.title("Publish Transaction")
		publishWindow.geometry("500x300")


		label=Label(publishWindow,text="Raw TX:")
		label.pack()
		label.place(x=5,y=10)

		textArea=tk.Text(publishWindow,font=('arial',11, 'italic'))
		textArea.pack()
		textArea.place(height=200,width=450, x=5,y=30)
		textArea.delete(1.0, 'end')
		
		textArea.insert(1.0,str(tx))
		textArea.configure(state='disabled')

		#label1=Label(publishWindow,text="Raw TX:    "+str(tx2))
		#label1.pack()
		#label1.place(height=200,width=500,x=5,y=15)

		button=tk.Button(publishWindow,text="Broadcast Transaction", command=lambda: self.broadcastTX(tx))
		button.pack()
		button.place(x=5,y=260)

	def broadcastTX(self,tx):
		
		

		if(mainnet):res=Service().sendrawtransaction(rawtx=tx)
		else: res=service_testnet.sendrawtransaction(rawtx=tx)

	    
		#console.printText(text="\nTried to send tx. It's'",keepOld=True)
		
		print(res)
		if(res==False):
			console.printText(text="\nError when broadcasting tx. No response",keepOld=True)
			return

		
		#a=res['response_dict']
		if "txid" in res:
			console.printText(text="\nTx ID: "+res['txid'],keepOld=True)
		else: console.printText(text="\nError when broadcasting tx. Unknown response",keepOld=True)
		

	def createTX(self):

		if(self.keyPathChosen):
			if(len(self.PathValueArray)==1):#KeyPath Single Key

				tx=tapTree.SpendTransactionViaKeyPath(gui.TapRootContainer,self.get_destinationList())
				console.printText(text="Signed Raw Transaction:\n"+str(tx))
				self.broadcastWindow(tx)

			if(len(self.PathValueArray)>1):#KeyPath MultiSig
				
				self.multisigContainer(multisig_key=gui.TapRootContainer.internalKey)
			return

		#ScriptPath chosen
		radio=self.radio_scriptpath.get()
		
		self.tx_scriptContainer=self.PathValueArray[radio][1]
		pubContainer=self.tx_scriptContainer.parentArray[0]

		if(len(pubContainer.parentArray)==0):#If Pubkey has no parent, it is not a multisig
			tx=tapTree.SpendTransactionViaScriptPath(gui.TapRootContainer,self.get_destinationList(),pubContainer.privKey,
							self.tx_scriptContainer.script,self.tx_scriptContainer.timelockDelay,self.tx_scriptContainer.timelock)
			console.printText(text="Signed Raw Transaction:\n"+str(tx))
			self.broadcastWindow(tx)
			return

		self.multisigContainer(multisig_key=pubContainer)

		return

	def multisigContainer(self,multisig_key):
		self.tx_multisigkey=multisig_key

		tweak_=None
		if(self.keyPathChosen):tweak_=gui.TapRootContainer.tapTweak_bytes

		self.cMultiSig=c_MultiSig(self.tx_multisigkey.pubKey,tweak=tweak_)
		

		allMine=True
		if(self.keyPathChosen):
			for i in range(1,len(self.PathValueArray)):
				if(self.PathValueArray[i][0].get()==0):
					allMine=False
		else:
			checked=[]
			for i in range(0,len(self.PathValueArray2)):
				if(self.PathValueArray2[i][0].get()):checked.append(self.PathValueArray2[i][2])
			
			for i in range(0,len(self.tx_multisigkey.parentArray)):
				key=self.tx_multisigkey.parentArray[i]
				mine=False
				for o in range(0,len(checked)):
					if(checked[o]==self.tx_multisigkey.parentArray[i]):
						#self.cMultiSig.addPrivKey(key.privKey)
						mine=True
				if(mine==False):
					allMine=False


		

		if(allMine==False):
			

			self.windowMultiSig = Toplevel(self.root)
			self.windowMultiSig.title("Create MultiSig Transaction")
			self.windowMultiSig.geometry("720x470")

			Label(self.windowMultiSig,text ="Create MultiSig Transaction").pack()

			self.page1=tk.LabelFrame(self.windowMultiSig)
			self.page1.pack()
			self.page1.place(height=800,width=700, x=10, y=50)

			label_noncehash=Label(self.page1,text ="Share nonce hash with partner")
			label_noncehash.pack()
			label_noncehash.place(height=20, x=200, y=5)

			self.entry_NonceHash=[]

			button_next=tk.Button(self.page1,text="Next", command=self.multisig_page2)
			button_next.pack()
			button_next.place(x=600,y=30)
		
		if(self.keyPathChosen):
			for i in range(1,len(self.PathValueArray)):
				if(self.PathValueArray[i][0].get()==1):
					self.cMultiSig.addPrivKey(self.PathValueArray[i][1].privKey)
				else:
					self.cMultiSig.addPubKey(self.PathValueArray[i][1].pubKey)

					
		
				if(allMine==False):
					label=Label(self.page1,text =self.PathValueArray[i][1].label)
					label.pack()
					label.place(height=20, x=10, y=30+i*30)

					entry_Label=tk.Entry(self.page1);entry_Label.pack()
					entry_Label.place(height=20,width=450, x=100, y=30+i*30);entry_Label.delete(0, 'end');
					nonce=self.cMultiSig.getNonce(self.PathValueArray[i][1].pubKey)
					if(nonce):entry_Label.insert(0,str(sha256(nonce.get_pubkey().get_bytes()).hex()))
					else:entry_Label.insert(0,"Enter nonce hash of your partner")
					self.entry_NonceHash.append(entry_Label)
		else:
			checked=[]
			for i in range(0,len(self.PathValueArray2)):
				if(self.PathValueArray2[i][0].get()):checked.append(self.PathValueArray2[i][2])
			
			for i in range(0,len(self.tx_multisigkey.parentArray)):
				key=self.tx_multisigkey.parentArray[i]

				mine=False
				for o in range(0,len(checked)):
					if(checked[o]==key):
						self.cMultiSig.addPrivKey(key.privKey)
						mine=True
				if(mine==False):
					self.cMultiSig.addPubKey(key.pubKey)

				if(allMine==False):
					label=Label(self.page1,text =key.label)
					label.pack()
					label.place(height=20, x=10, y=30+i*30)

					entry_Label=tk.Entry(self.page1);entry_Label.pack()
					entry_Label.place(height=20,width=450, x=100, y=30+i*30);entry_Label.delete(0, 'end');
					nonce=self.cMultiSig.getNonce(key.pubKey)
					if(nonce):entry_Label.insert(0,str(sha256(nonce.get_pubkey().get_bytes()).hex()))
					else:entry_Label.insert(0,"Enter nonce hash of your partner")
					self.entry_NonceHash.append(entry_Label)
				
		
		if(allMine):
			self.cMultiSig.genAggregateNonce()
			self.cMultiSig.genAggregatePubkey()
			priv=None
			if(self.keyPathChosen):
				priv=self.cMultiSig.getTweakedPrivateKey()
				gui.TapRootContainer.tweaked_privkey=priv
				tx=tapTree.SpendTransactionViaKeyPath(gui.TapRootContainer,self.get_destinationList())
				console.printText(text="Signed Raw Transaction:\n"+str(tx))
				self.broadcastWindow(tx)
			else:
				priv=self.cMultiSig.getInternalPrivateKey()
				tx=tapTree.SpendTransactionViaScriptPath(gui.TapRootContainer,self.get_destinationList(),priv,
							self.tx_scriptContainer.script,self.tx_scriptContainer.timelockDelay,self.tx_scriptContainer.timelock)
				console.printText(text="Signed Raw Transaction:\n"+str(tx))
				self.broadcastWindow(tx)
			return

		

	def multisig_page2(self):
		for i in range(0,len(self.entry_NonceHash)):
			try:int(self.entry_NonceHash[i].get(),16)
			except:
				console.printText("Enter all your partners nonce hashes before proceeding")
				return
			input_=self.entry_NonceHash[i].get()
			if(self.cMultiSig.getNonce(self.cMultiSig.keys[i][1]) is None):
				self.cMultiSig.addNonceHash(i,bytes.fromhex(input_))

		self.page1.place_forget()

		self.page2=tk.LabelFrame(self.windowMultiSig)
		self.page2.pack()
		self.page2.place(height=800,width=700, x=10, y=50)

		label_nonce=Label(self.page2,text ="Share nonce public key with partner")
		label_nonce.pack()
		label_nonce.place(height=20, x=200, y=5)

		self.entry_NoncePub=[]

		for i in range(0,len(self.cMultiSig.keys)):
			label=None
			if(self.keyPathChosen):label=Label(self.page2,text =self.PathValueArray[i+1][1].label)
			else:
				for o in range(0,len(self.tx_multisigkey.parentArray)):
					if(self.tx_multisigkey.parentArray[o].pubKey==self.cMultiSig.keys[i][1]):
						label=Label(self.page2,text =self.tx_multisigkey.parentArray[o].label)
			if(label is None):
				print("ERROR IN multisig_page2. LABEL IS NONE")
			label.pack()
			label.place(height=20, x=10, y=30+i*30)

			entry_Label=tk.Entry(self.page2);entry_Label.pack()
			entry_Label.place(height=20,width=450, x=100, y=30+i*30);entry_Label.delete(0, 'end');
			nonce=self.cMultiSig.getNonce(self.cMultiSig.keys[i][1])
			if(nonce):entry_Label.insert(0,str(nonce.get_pubkey()))
			else:entry_Label.insert(0,"Enter nonce public key of your partner")

			self.entry_NoncePub.append(entry_Label)

		button_next=tk.Button(self.page2,text="Next", command=self.button3)
		button_next.pack()
		button_next.place(x=600,y=30)

	def button3(self):
		self.multisig_page3(1)

	


	def multisig_page3(self,value):
		for i in range(0,len(self.entry_NoncePub)):
			try:int(self.entry_NoncePub[i].get(),16)
			except:
				console.printText("Enter all your partners nonce pubkeys before proceeding")
				return

		if(value==1):self.page2.place_forget()
		else:self.page3.destroy()
		
		for i in range(0,len(self.entry_NoncePub)):
			input_=self.entry_NoncePub[i].get()
			if(self.cMultiSig.getNonce(self.cMultiSig.keys[i][1])is None):
				val=self.cMultiSig.addNoncePub(i,bytes.fromhex(input_))
				if(val==1):
					#print(str(input_)+" and "+str(self.cMultiSig.keys[i][4])+" match")
					pass
				elif (val==2):
					console.printText("ERROR: "+str(input_)+" is no valid nonce")
					self.windowMultiSig.destroy()
					return
				elif (val==3):
					console.printText("ERROR: Hash of "+str(input_)+" does not match the hash you entered earlier")
					self.windowMultiSig.destroy()
					return

		self.cMultiSig.print()

		self.page3=tk.LabelFrame(self.windowMultiSig)
		self.page3.pack()
		self.page3.place(height=800,width=700, x=10, y=50)

		label_nonce=Label(self.page3,text ="Share partial signature with your partners")
		label_nonce.pack()
		label_nonce.place(height=20, x=200, y=5)

		self.cMultiSig.genAggregateNonce()
		self.cMultiSig.genAggregatePubkey()
		
		self.cMultiSig.print()
		if(self.keyPathChosen):self.spending_tx,input_tx=tapTree.createUnsignedTX(gui.TapRootContainer,self.get_destinationList())
		else: self.spending_tx,input_tx=tapTree.createUnsignedTX(gui.TapRootContainer,self.get_destinationList(),self.tx_scriptContainer.timelockDelay,self.tx_scriptContainer.timelock)
		#spending_tx,input_tx=tapTree.initMultiSigTX(gui.TapRootContainer,self.typedAddress.get(),(float)(self.typedAmount.get()),self.cMultiSig)
		print("SpendingTX :")
		print(self.spending_tx)
		print("\nInputTX :")
		print(input_tx)

		if(value==2):del self.signature_pool[:]
		self.signature_pool=[]
		self.signature_entry=[]
		self.sighash_list=None
		#self.witness_elements=None
		allsSigsAvailable=True

		for i in range(0,len(self.cMultiSig.keys)+1):
			if(i==len(self.cMultiSig.keys)):
				if(self.keyPathChosen):
					signature_list,self.sighash_list=tapTree.signMultiSig(gui.TapRootContainer,self.spending_tx,input_tx,self.cMultiSig,-1)
					print("SpendingTX :_____")
					print(signature_list)
					self.signature_pool.append(signature_list)

			elif (self.cMultiSig.keys[i][0] is None):
				allsSigsAvailable=False
				signature_list=None
			else:
				if(self.keyPathChosen):signature_list,self.sighash_list=tapTree.signMultiSig(gui.TapRootContainer,self.spending_tx,input_tx,self.cMultiSig,i)
				else:
					signature_list,self.sighash_list=tapTree.signMultiSig(gui.TapRootContainer,self.spending_tx,input_tx,self.cMultiSig,i,self.tx_scriptContainer.script)
					#self.witness_elements=signature_list[0][1],signature_list[0][2]
				print("SpendingTX :_____")
				print(signature_list)

			if(i<len(self.cMultiSig.keys)):
				label=None
				if(self.keyPathChosen):label=Label(self.page3,text =self.PathValueArray[i+1][1].label)
				else:
					#for o in range(0,len(self.tx_multisigkey.parentArray)):
					#	if(self.tx_multisigkey.parentArray[o].pubKey==self.cMultiSig.keys[i][1]):
					label=Label(self.page3,text =self.tx_multisigkey.parentArray[i].label)
				if(label is None):
					print("ERROR IN multisig_page3. LABEL IS NONE")
				label.pack()
				label.place(height=20, x=10, y=30+i*60)
				
				entry_Label=tk.Text(self.page3);entry_Label.pack()
				entry_Label.place(height=50,width=500, x=100, y=30+i*60);entry_Label.delete(1.0, 'end');

				if(signature_list is not None):
					string_=""
					for sig in signature_list:
						string_=string_+str(sig)+"\n"
					string_ = string_[:-1]

					#siglabel1=slice(0,len(str(signature[0]))//2)
					#siglabel2=slice(len(str(signature[0]))//2,len(str(signature[0])))
					#entry_Label.insert(1.0,str(signature[0])[siglabel1]+"\n"+str(signature[0])[siglabel2])
					entry_Label.insert(1.0,string_)
					self.signature_pool.append(signature_list)
				else: entry_Label.insert(1.0,"Copy signature of your partner here")

				self.signature_entry.append(entry_Label)
			

		if(allsSigsAvailable):
			

			self.combineSignatures()

		else:
			button_next=tk.Button(self.page3,text="Combine Signatures", command=self.combineSignatures)
			button_next.pack()
			button_next.place(x=100,y=30+len(self.cMultiSig.keys)*60)

	def combineSignatures(self):
	
			for i in  range(0,len(self.cMultiSig.keys)):
				if(self.cMultiSig.keys[i][0]is None):
					sig=self.signature_entry[i].get("1.0",'end-1c')
					try:
						int(sig,16)
					except:
						console.printText("Enter all your partners signatures before proceeding")
						return

					sig=sig.splitlines()
					for i in range(0,len(sig)):
						sig[i]=int(sig[i])
					print(sig)
					self.signature_pool.append(sig)
					print(self.signature_pool)
			
			num_utxos_spent=len(self.signature_pool[0])
			print(str(num_utxos_spent)+" UTXOs are going to be spent")

			for i in  range(0,num_utxos_spent):#length 2
				sig=[]
				for o in range(0,len(self.signature_pool)):#length 3
					sig.append(self.signature_pool[o][i])
				
				sig_agg = aggregate_musig_signatures(sig, self.cMultiSig.nonce_agg)
			
				if(self.keyPathChosen):self.spending_tx.wit.vtxinwit.append(CTxInWitness([sig_agg]))
				else:
					control_map=gui.TapRootContainer.taptree[2]
					script=self.tx_scriptContainer.script
					self.spending_tx.wit.vtxinwit.append(CTxInWitness([sig_agg,script,control_map[script]]))


			
				print(sig_agg.hex())
				print("Spending transaction New:\n{}".format(self.spending_tx))

				#if(self.cMultiSig.verifyTweaked(sig_agg,self.sighash_list[i])):
				#	print("Success")
				#else: print("Fail")

			num=len(self.cMultiSig.keys)

			spending_tx_str=self.spending_tx.serialize().hex()
			rawtxs=[spending_tx_str]

			label=Label(self.page3,text ="Final TX")
			label.pack()
			label.place(height=20, x=10, y=70+num*60)

			print(rawtxs[0])
			
			#siglabel1=slice(0,len(str(rawtxs[0]))//2)
			#siglabel2=slice(len(str(rawtxs[0]))//2,len(str(rawtxs[0])))
			#entry_Label=tk.Entry(self.page3);entry_Label.pack()
			#entry_Label.place(height=80,width=450, x=100, y=30+num*90);entry_Label.delete(0, 'end');
			#entry_Label.insert(0,str(rawtxs[0])[siglabel1]+"\n"+str(rawtxs[0])[siglabel2])

			entry_Label=tk.Text(self.page3);entry_Label.pack()
			entry_Label.place(height=80,width=500, x=100, y=70+num*60);entry_Label.delete(1.0, 'end');
			entry_Label.insert(1.0,str(rawtxs[0]))

			console.printText(text="Signed Raw Transaction\n"+str(rawtxs[0]))

			button_sendTX=tk.Button(self.page3,text="Send Transaction", command=lambda: self.broadcastTX(rawtxs[0]),bg="#00cc44",fg="#000000")
			button_sendTX.pack()
			button_sendTX.place(x=300,y=30+num*60)

"""
class TapRootWallet:

	def calcMuSig(self):
		pubKeyList=[]
		for i in range(0,4):
			if(self.varCheckMultiSig[i].get()==True):
				pubKeyList.append(self.containerArray[i].pubKey)

		#print("Pubkeys to include in MuSig: ",pubKeyList,self.varCheckMultiSig[0].get())
		
		c_map,pubKey_agg=getMuSigAddress(pubKeyList)
		#print(c_map)

		#print("Aggregated Public Key is {}\n".format(pubKey_agg.get_bytes().hex()))
		self.label_MuSig.config(text=pubKey_agg)

	def calScripts(self):
		pubKeyList=[]
		

		for i in range(0,4):
			if(self.varCheckMultiSig[i].get()==True):
				pubKeyList.append(self.containerArray[i].pubKey)
				self.labelScript[i].config(text="Public Key "+str(i)+": "+str(self.containerArray[i].pubKey))
		
		tapTree=TapTreeClass(pubKeys=pubKeyList)
		scriptList=tapTree.tapLeaf
		for i in range(0,len(pubKeyList)):
			pubKeyList.append(self.containerArray[i].pubKey)
			self.labelScript[i].config(text="Public Key "+str(i)+": "+str(self.containerArray[i].pubKey)+"- Script "+str(i)+": "+(scriptList[i].script.hex()))
	
		
	
	def main():
		init_window()
		#self.containerArray[0]
		
		root.mainloop()


	def loop(self):
		#self.getNewTaprootAddress()
		self.root.after(1000,self.loop())
"""
def init_some_addresses():
	"""MAINNET FUNDS key5 """
	"""privkey,pubkey,address=createTapRootFromPriv("112217362122113824384680233966774656903596854938195684801734534657064740212540")
	#privkey,pubkey,address=createTapRootFromPriv("76033175248883887326023636026588093639587144140395435720911304384488220219727")
	"""
	privkey,pubkey=generate_bip340_key_pair(secret=0xa01d47e364a61b51d22bb794580c66eb0272ddc063b0a457dcde548d9061be1)#createTapRootFromPriv("4526361905793704522839017442433689272896044907422408434527127994389357796321")
	gui.addPubKeyContainer("MainKey",privkey,pubkey,[],True)
	#gui.pubKeyContainerArray[0].doubleClick(event=None)
	#gui.pubKeyContainerArray[0].createScript()
	#selectedContainer.append(gui.hashContainerArray[0])

	privkey,pubkey=generate_bip340_key_pair(secret=0x90151935cc54da8d81b69b4e52acedfada49bc30dd95580b7fbdb994f67dd362)
	gui.addPubKeyContainer("Dad",privkey,pubkey,[],True)
	#gui.pubKeyContainerArray[1].doubleClick(event=None)
	#gui.pubKeyContainerArray[1].createScript()
	#selectedContainer.append(gui.hashContainerArray[1])

	privkey,pubkey=generate_bip340_key_pair(secret=0x8af8e1a2197e24a2a368d9efeb3aca7db40ce3810c98ea465b61c7981f3aa212)
	gui.addPubKeyContainer("Backup",privkey,pubkey,[],True)
	#gui.pubKeyContainerArray[2].doubleClick(event=None)
	#gui.pubKeyContainerArray[2].createScript()
	#selectedContainer.append(gui.hashContainerArray[2])

	#gui.calcKeyReleasedTapBranch()

	#selectedContainer.append(gui.hashContainerArray[2])
	#selectedContainer.append(gui.pubKeyContainerArray[0])

	#gui.calcKeyReleasedTapRoot()
	



def initService():
	global service_testnet
	service_testnet=Service(network="testnet")


	#print(Service())
	#print(Service().getinfo())
	
def startThread(function):
	thread=Thread(target=function)
	thread.start()

def getBalance():
	if(gui.TapRootContainer is None):
		console.printText("Create a taproot address first")
		return
	print("Check Balance")
	if(mainnet):utxo_List=Service().getutxos(address=gui.TapRootContainer.TapRootAddress)
	else: utxo_List=service_testnet.getutxos(address=gui.TapRootContainer.TapRootAddress)
	guiTX.update(utxo_List)
	print("Balance finished")

def thread_balance():
	t1=Thread(target=getBalance)
	t1.start()

#EXECUTION OF THIS WALLET BEGINS HERE

#Init some Objects
root = tk.Tk()
root.title("TapRoot Wallet by https://twitter.com/BR_Robin . Only testnet recommended")




tabControl=ttk.Notebook(root)


tab1=Frame(tabControl)#Create Address tab
tab2=Frame(tabControl)#Create Transaction tab

tabControl.add(tab1, text='Create Address')
tabControl.add(tab2, text='Create Transaction')
tabControl.pack(expand=1, fill="both")

#This method initiates the part in which addresses,hashes etc. get displayed
gui = GraphicalUserInterfaceCanvas(root)
console=Console(root)
tapTree=TapRootClass(console.printText)
guiTX=GraphicalUserInterfaceTX(tab2,None,None,None,None)

#Create the Key Creation Box in Create Address, set entropy to 'key0' and create public key (for demonstration)
keyCreation=keyCreationContainer(tab1,20,20)
keyCreation.entry_Entropy.insert(0,"key0")
keyCreation.getPubkeyFromEntropy()

text_=("Drag to reposition any window. Double Click to open and create script.\n"
		"Press Control + click multiple Public Keys to create MultiSig\n"
		"Press Control + click multiple Hashes to create a Child Hash\n"
		"Press Control + click one Public Key + One Hash to create a Taproot Address\n"
		"Right click on any container to copy to clipboard")

label_Info=tk.Label(tab1,text=text_, justify=LEFT)
label_Info.pack()
label_Info.place(height=80, x=20, y=200)

#To make debugging easier, this function creates some keys when starting
#Disabled for normal use
#init_some_addresses()




startThread(initService)#calls function in background, this establishes communication with blockchain providers


root.mainloop()#Start main thread
