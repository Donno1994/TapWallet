import tkinter as tk
from tkinter import ttk
import global_ 
import bitcoinlib
import test_framework
import random
import taproot
from helperFunctions import *
import console
from musig1 import *

guix=1460
guiy=560

class c_Container: #Moveable Parent Container, can be a public key, script, hash or taproot container
	def __init__(self,x_pos,y_pos,label0="Alice",label1="xpub123",label2="0:123",parent_array=[],is_mine=True,has_extended_parent=False):
		self.x_pos=x_pos

		if(self.x_pos==None):
			random_=random.randrange(0,guix-100)
			self.x_pos=20+random_

		if(y_pos>guiy-60):y_pos=guiy-60
		self.y_pos=y_pos
		
		self.sizeX=225
		self.sizeY=40
		if(isinstance(self,c_Container_PubKey)):self.sizeY=60
		if(isinstance(self,c_Container_Script)):self.sizeY=75

		self.parent_array=parent_array
		self.childList=[]
		
		self.label0=label0
		
		self.active=True
		self.is_mine=is_mine

		self.root=global_.gl_gui_build_address.container_Script
		self.mouseDown=False
		self.mouseX=x_pos
		self.mouseY=y_pos
		self.isMini=False
		

		self.has_extended_parent=has_extended_parent # True, if at least one parent is an extended key. Then this key can't be calculated until a child key is derived

		

		self.container = tk.LabelFrame(self.root)
		self.container.pack()
		self.container.place(height=self.sizeY,width=self.sizeX, x=self.x_pos,y=self.y_pos)
		self.container.bind('<Button-1>', self.onClick)
		self.container.bind('<B1-Motion>', self.onMove)
		self.container.bind('<Control-Button-1>', self.flag)
		self.container.bind('<Double-Button-1>', self.doubleClick)
		self.container.bind('<Button-3>',self.copy_on_right_click)

		self.highlightContainer=tk.Label(self.container,bg="#00FFFF")
		self.highlightContainer.pack()
		self.highlightContainer.place(height=15, x=14, y=2)
		self.highlightContainer.bind('<Button-1>', self.onClick)
		self.highlightContainer.bind('<B1-Motion>', self.onMove)
		self.highlightContainer.bind('<Control-Button-1>', self.flag)
		self.highlightContainer.bind('<Double-Button-1>', self.doubleClick)
		self.highlightContainer.bind('<Button-3>',self.copy_on_right_click)

		#text_l=tk.Label(self.highlightContainer,text="Selected",bg="#00FFFF")
		#text_l.pack()
		self.highlightContainer.place_forget()

		#text.place(height=15, x=1, y=2)

		self.label_label0=tk.Label(self.container)#Example: PubKey: Alice
		self.label_label0.pack()
		self.label_label0.place(height=15, x=14, y=2)
		self.label_label0.bind('<Button-1>', self.onClick)
		self.label_label0.bind('<B1-Motion>', self.onMove)
		self.label_label0.bind('<Control-Button-1>', self.flag)
		self.label_label0.bind('<Double-Button-1>', self.doubleClick)
		self.label_label0.bind('<Button-3>',self.copy_on_right_click)
		
		self.label_label1=tk.Label(self.container)#Example: xpub123
		self.label_label1.pack()
		self.label_label1.place(x=4, y=17,width=self.sizeX-5)
		self.label_label1.bind('<Button-1>', self.onClick)
		self.label_label1.bind('<B1-Motion>', self.onMove)
		self.label_label1.bind('<Control-Button-1>', self.flag)
		self.label_label1.bind('<Double-Button-1>', self.doubleClick)
		self.label_label1.bind('<Button-3>',self.copy_on_right_click)
		self.changeColor()
		self.line=[]
		if(parent_array!=None):
			for i in range(0, len(parent_array)):
				middleX=self.x_pos+(self.sizeX/2)
				middleY=self.y_pos+(self.sizeY/2)
				self.line.append(global_.gl_gui_build_address.canvas.create_line(middleX,middleY,parent_array[i].x_pos+(self.sizeX/2),parent_array[i].y_pos++(self.sizeY/2)))

		self.buttonMinimize=tk.Button(self.container,bg="#FF8080", text="-", command=self.minimizeContainer)
		self.buttonMinimize.pack()
		self.buttonMinimize.place(height=15,width=15,x=2,y=0)

		self.buttonExit=tk.Button(self.container,bg="#FF8080", text="X", command=self.remove_container)
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

		if self.parent_array!=None:
			middleX=self.x_pos+(self.sizeX/2)
			middleY=self.y_pos+(self.sizeY/2)

			for i in range (0,len(self.parent_array)):
				global_.gl_gui_build_address.canvas.coords(self.line[i],middleX,middleY,self.parent_array[i].x_pos+(self.sizeX/2),self.parent_array[i].y_pos+(self.sizeY/2))

	def changeColor(self):

		color="#000000"

		if(self.is_mine):
			if(isinstance(self,c_Container_PubKey)):color="#0099FF"
			if(isinstance(self,c_Container_Script)):color="#DC7A7A"
			if(isinstance(self,c_Container_Hash)):color="#16e971"
			if hasattr(self, 'label_label3'):
				if(self.label_label3):self.label_label3.config(bg="#16e971")
			if(isinstance(self,c_Container_Taproot)):color="#47C718"
			#pub "#0099FF","#CCEBFF"
			#script "#DC7A7A","#F5D6D6"
			#Hash "#16e971","E8FDF1"

			#self.container.config(bg=self.color)
			#self.label_label0.config(bg=self.color)
			#self.label_label1.config(bg=self.color)
		else:
			if(isinstance(self,c_Container_PubKey)):color="#CCEBFF"
			if(isinstance(self,c_Container_Script)):color="#F5D6D6"
			if(isinstance(self,c_Container_Hash)):color="#E8FDF1"
			if hasattr(self, 'label_label3'):
				if(self.label_label3 is not None):self.label_label3.config(bg="#E8FDF1")
			#self.container.config(bg=self.inactiveColor)
			#self.label_label0.config(bg=self.inactiveColor)
			#self.label_label1.config(bg=self.inactiveColor)
		
		
		
		self.container.config(bg=color)
		self.label_label0.config(bg=color)
		self.label_label1.config(bg=color)
		
		
	def flag(self,event):
		
		
		for i in range(0,len(global_.gl_selected_container)):
			if(global_.gl_selected_container[i]==self):
				self.changeColor()
				global_.gl_selected_container.remove(self)
				return

		#if(gui.taproot_container==None):#Don't flag when Taproot Address exists
		
		self.container.config(bg="#ffcc00")
		self.label_label0.config(bg="#ffcc00")
		self.label_label1.config(bg="#ffcc00")
		if(isinstance(self,c_Container_Script)):self.label_label3.config(bg="#ffcc00")
		global_.gl_selected_container.append(self)

	def minimizeContainer(self):
		if(self.isMini):
			self.isMini=False
			self.sizeY=60
			self.sizeX=225

			if(isinstance(self,c_Container_PubKey)):
				self.label_label0.config(text="PubKey: "+str(self.label0))
				self.highlightContainer.config(text="PubKey: "+str(self.label0))
			if(isinstance(self,c_Container_Script)):
				self.sizeY=self.sizeY+20
				self.label_label0.config(text=str(self.label0))
				self.highlightContainer.config(text=str(self.label0))

		else:
			self.isMini=True
			self.sizeY=25
			self.sizeX=120

			if(isinstance(self,c_Container_PubKey) or isinstance(self,c_Container_Script)):
				self.label_label0.config(text=str(self.label0))
				self.highlightContainer.config(text=str(self.label0))

		self.container.place(height=self.sizeY,width=self.sizeX, x=self.x_pos,y=self.y_pos)

	def remove_container(self):

		for i in range(0,len(self.parent_array)):
			global_.gl_gui_build_address.canvas.delete(self.line[i])

		for i in range(0,len(self.childList)):
			self.childList[i].remove_container()

		for i in range(0,len(global_.gl_selected_container)):
			if(global_.gl_selected_container[i]==self):
				global_.gl_selected_container.remove(self)

		global_.gl_gui_build_address.removeKeyContainer(self)
		self.container.destroy()

	def updateLine(self):
		if(self.parent_array==None):
			return


		tempX=self.x_pos
		tempY=self.y_pos
		if(tempX<0):tempX=0
		if(tempY<0):tempY=0
		if(tempX>guix-self.sizeX):tempX=guix-self.sizeX
		if(tempY>guiy-self.sizeY):tempY=guiy-self.sizeY
		middleX=tempX+(self.sizeX/2)
		middleY=tempY+(self.sizeY/2)

		for i in range(0,len(self.parent_array)):
			global_.gl_gui_build_address.canvas.coords(self.line[i],middleX,middleY,self.parent_array[i].x_pos+(self.parent_array[i].sizeX/2),self.parent_array[i].y_pos+(self.parent_array[i].sizeY/2))
	
	def doubleClick(self,event):
		return

	def setParentActive(self):
		for a in range(0,len(self.parent_array)):
			container=self.parent_array[a]
			container.active=True
			container.setParentActive()

	def copy_on_right_click(self,event):
		index=global_.gl_current_child_index

		if(isinstance(self,c_Container_PubKey)):
			if(len(self.pubkey)==1):index=0
			global_.gl_console.copyText(str(self.pubkey[index]))
		if(isinstance(self,c_Container_Script)):
			if(len(self.script)==1):index=0
			global_.gl_console.copyText(str(self.script[index].hex()))
		if(isinstance(self,c_Container_Hash)):
			if(len(self.hash_)==1):index=0
			global_.gl_console.copyText(self.hash_[index].hex())
		if(isinstance(self,c_Container_Taproot)):
			if(len(self.TapRootAddress)==1):index=0
			global_.gl_console.copyText(self.TapRootAddress[index])

	def copy_hash_on_right_click(self,event):
		index=global_.gl_current_child_index
		if(len(self.hash_)==1):index=0
		global_.gl_console.copyText(self.hash_[index].hex())
		

class c_Container_PubKey (c_Container):
	def __init__(self,x_pos,y_pos,ext_key=None,privKey=None,pubKey=None,label="Label",parent_array=[],is_mine=None,has_extended_parent=False):
		
		
		self.ext_key=ext_key
		self.privkey=privKey
		self.pubkey=pubKey
		
		if(self.ext_key is not None):
			if(is_mine is None):is_mine=self.ext_key.secret
			label1=self.ext_key.wif_public()
		else:
			if(is_mine is None):
				if(self.privkey is None):is_mine=False
				elif(len(self.privkey)==0):is_mine=False
				else: is_mine=True
			label1=str(self.pubkey)
				
		for parent in parent_array:
			if(parent.ext_key is not None):
				has_extended_parent=True

		c_Container.__init__(self,x_pos=x_pos,y_pos=y_pos,label0=label,label1=label1,label2=self.pubkey,parent_array=parent_array,is_mine=is_mine,has_extended_parent=False)
		

		self.label_label0.config(text="PubKey: "+str(label))
		self.highlightContainer.config(text="PubKey: "+str(label))
		
		
		self.lastTimelock=0

		if(x_pos==None):
			random_=random.randrange(0,1000)
			self.x_pos=20+random_

		if(self.y_pos>guiy-self.sizeY):self.y_pos=guiy-self.sizeY

		self.container.place(height=self.sizeY,width=self.sizeX, x=self.x_pos,y=self.y_pos)
		
		self.updateLine()

		self.editTimelock=0
		self.tab1=0
		self.tab2=0
		self.editLabel=0

		if(isinstance(privKey,test_framework.ECKey)):
			if(len(str(privKey))>5):
				print("Adding KeyPair: ",str(hex(privKey.secret))[2:]," - ",str(privKey.get_pubkey()))
			elif(len(parent_array)==0):
				print("Adding Pubkey: ",str(privKey.get_pubkey()))


		if(isinstance(privKey,bitcoinlib.keys.Key)):
			if(len(str(privKey))>5):
				print("Addig KeyPair: ",str(privKey)," - ",str(privKey.wif_public()))

		if(self.ext_key is not None):
			for i in range (0,global_.gl_address_generation_max):
				if(self.ext_key.secret is not None):
					prv=test_framework.ECKey().set(self.ext_key.child_private(0).child_private(i).secret)
				else:prv=None
				#print("hex")
				#print(self.ext_key.child_public(0).child_public(i).public_byte)
				pub=test_framework.ECPubKey().set(self.ext_key.child_public(0).child_public(i).public_byte)
				if(pub.get_y()%2!=0):
					if(prv is not None):prv.negate()
					pub.negate()
				if(prv is not None):self.privkey.append(prv)
				self.pubkey.append(pub)

		self.update_index()

	def doubleClick(self,event):
		if(event.state==12):return#Control key is pressed -> flag function is called

		self.scriptWindow = tk.Toplevel(self.root)
		self.scriptWindow.title("Info about your key")
		self.scriptWindow.geometry("600x400")
		

		label1=tk.Label(self.scriptWindow,text="Label: "+str(self.label0))
		label1.pack()
		label1.place(x=5,y=5)
		#Label(self.scriptWindow,text =str(self.label)).pack()
		#Label(self.scriptWindow,text ="PubKey: "+str(self.pubkey)).pack()
		data_string_ext = tk.StringVar()
		if(self.ext_key is not None):data_string_ext.set("Extended Key: "+str(self.ext_key.wif_public()))
		else: data_string_ext.set(str("Extended Key: not available"))
		e=tk.Entry(self.scriptWindow,textvariable=data_string_ext,fg="black",bg="white",bd=0,state="readonly")
		e.pack()
		e.place(x=5,y=25,width=590)

		data_string_pub = tk.StringVar()
		if(len(self.pubkey)> global_.gl_current_child_index):data_string_pub.set("Public Key "+str(global_.gl_current_child_index)+": "+str(self.pubkey[global_.gl_current_child_index]))
		else: data_string_pub.set(str("Public Key  : not available"))
		e2=tk.Entry(self.scriptWindow,textvariable=data_string_pub,fg="black",bg="white",bd=0,state="readonly")
		e2.pack()
		e2.place(x=5,y=45,width=590)

		scriptFrame = tk.LabelFrame(self.scriptWindow)
		scriptFrame.pack()
		scriptFrame.place(height=265,width=590, x=5,y=70)

		label=tk.Label(scriptFrame,text="Create a script of the above key to specify spending conditions")
		label.pack()
		label.place(x=5,y=0,anchor="nw")
		labelLabel=tk.Label(scriptFrame,text="Add a label to script:")
		labelLabel.pack()
		labelLabel.place(height=15,x=5,y=30)
		

		self.editLabel=tk.Entry(scriptFrame)
		self.editLabel.pack()
		self.editLabel.place(height=15,width=80,x=150,y=30)
		self.editLabel.insert(0,str(self.label0))

		labelTimelock=tk.Label(scriptFrame,text="Add a timelock to script:")
		labelTimelock.pack()
		labelTimelock.place(height=15,x=5,y=55)

		self.radioTimelockVar=tk.IntVar(value=1)
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
		
		labelPassword=tk.Label(scriptFrame,text="Add a hashlock to script: <<Not supported yet>>")
		labelPassword.pack()
		labelPassword.place(height=15,x=5,y=160)

		buttonScript=tk.Button(scriptFrame,text="Create Script", command=self.createScript,bg="#DC7A7A")
		buttonScript.pack()
		buttonScript.place(height=20,width=100,x=5,y=235)

		taprootFrame = tk.LabelFrame(self.scriptWindow)
		taprootFrame.pack()
		taprootFrame.place(height=60,width=590, x=5,y=340)

		buttonTaprootAddress=tk.Button(taprootFrame,text="Create Taproot", command=lambda:global_.gl_gui_build_address.calc_key_released_taproot(key=self),bg="#47C718")
		buttonTaprootAddress.pack()
		buttonTaprootAddress.place(height=20,width=100,x=5,y=20)

		labelInfo=tk.Label(taprootFrame,text="Creating a taproot address from this key\nwill delete all other scripts and keys\napart from parent keys")
		labelInfo.pack()
		labelInfo.place(x=120,y=5)

		

	
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

		if(global_.gl_gui_build_address.taproot_container):
			global_.gl_console.printText("Can't create a script when taproot address is already created")
			return

		if(len(self.editRelTimelock.get())>0):
			if(self.editRelTimelock.get().isnumeric()==False):
				global_.gl_console.printText("TimeLock must be a positive number or empty")
				return
			if(int (self.editRelTimelock.get())>65535 or int (self.editRelTimelock.get())<=0):
				global_.gl_console.printText("Rel TimeLock must be between 1 and 65535")
				return

		elif(len(self.editAbsTimelock.get())>0):
			if(self.editAbsTimelock.get().isnumeric()==False):
				global_.gl_console.printText("TimeLock must be a positive number or empty")
				return
			if(int (self.editAbsTimelock.get())>16777216 or int(self.editAbsTimelock.get())<=0):
				global_.gl_console.printText("Abs TimeLock must be bewteen 1 and 16777216")
				return


		

		timelockdelay=0
		timelock=0

		if(len(self.editRelTimelock.get())>0):
			timelockdelay=int(self.editRelTimelock.get())
		elif(len(self.editAbsTimelock.get())>0):
			timelock=int(self.editAbsTimelock.get())

		tapLeaf=[]
		tapleaf_hash=[]

		for i in range(0,len(self.pubkey)):
			
			tapL,tapleaf_h=taproot.construct_Tapleaf(self.pubkey[i],timelockdelay,timelock)
			print("Adding Script: "+tapL.script.hex()+" for Pubkey: "+str(self.pubkey)+"  TimeLockRel: "+str(timelockdelay)+"  TimeLockAbs: "+str(timelock))
			print("Adding TapBranch: "+tapleaf_h.hex()+" for Script: ",tapL.script.hex())
			tapLeaf.append(tapL)
			tapleaf_hash.append(tapleaf_h)
		else:
			print("Adding Script for extended key")

		parent_array=[]
		parent_array.append(self)
		
		child=c_Container_Script(self.editLabel.get(),tapLeaf,tapleaf_hash,timelockdelay,timelock,parent_array,self.is_mine,self.has_extended_parent)
		global_.gl_gui_build_address.script_container_array.append(child)
		
		
		self.childList.append(child)
		child.onMove(None)

		self.scriptWindow.destroy()

	
	def update_index(self):
		if len(self.pubkey)==1:txt="\n"+str(shortenHexString(str(self.pubkey[0]),True))
		else:
			if(len(self.parent_array)>0):
				txt=("Extended Key not available"+"\nIndex:"+
					str(global_.gl_current_child_index)+":"+
					str(shortenHexString(str(self.pubkey[global_.gl_current_child_index]),True)))
			else:
				txt=(str(shortenHexString(str(self.ext_key.wif_public()),True))+"\nIndex:"+
					str(global_.gl_current_child_index)+":"+
					str(shortenHexString(str(self.pubkey[global_.gl_current_child_index]),True)))
		self.label_label1.config(text=txt)

class c_Container_Script(c_Container):
	def __init__(self,label,tapleaf,hash_,timelockDelay,timelock,parent_array,is_mine=False,has_extended_parent=False):
		x=parent_array[0].x_pos
		y=parent_array[0].y_pos+parent_array[0].sizeY+10

		self.timelockDelay=timelockDelay
		self.timelock=timelock
		self.tapLeaf=tapleaf
		self.script=[]
		self.hash_=hash_
		for tapL in tapleaf:
			self.script.append(tapL.script)

		maximum_index=len(self.tapLeaf)-1
		index=min(maximum_index,global_.gl_current_child_index)
		c_Container.__init__(self,x,y,label0=label,label1=str(tapleaf[index].script.hex()),parent_array=parent_array,is_mine=is_mine,has_extended_parent=has_extended_parent)
		
		

		#self.label_label1.config(text=txt, justify=tk.LEFT)

		#self.label_label0.config(text=str(label))
		self.highlightContainer.config(text=str(label))
		
		
		self.label_label3=tk.Label(self.container,text="Hash "+str(index)+": "+str(shortenHexString(str(hash_[index].hex()),True)),bg="#16e971")
		self.label_label3.pack()
		self.label_label3.place(x=0, y=52,height=20,width=self.sizeX-5)
		self.label_label3.bind('<Button-1>', self.onClick)
		self.label_label3.bind('<B1-Motion>', self.onMove)
		self.label_label3.bind('<Control-Button-1>', self.flag)
		self.label_label3.bind('<Double-Button-1>', self.doubleClick)
		self.label_label3.bind('<Button-3>',self.copy_hash_on_right_click)


		self.container.place(height=self.sizeY,width=self.sizeX, x=self.x_pos,y=self.y_pos)

		self.updateLine()
		txt="Script: "+str(shortenHexString(str(self.script[index].hex()),True))
			
		if(self.timelockDelay>0):txt=txt+"\nRelative Timelock: "+str(self.timelockDelay)
		elif(self.timelock>0):txt=txt+"\nAbsolute Timelock: "+str(self.timelock)
		else:txt=txt+"\nNo Timelock"
		self.label_label1.config(text=txt)
		self.label_label3.config(text="Hash "+str(index)+": "+str(shortenHexString(str(self.hash_[index].hex()),True)))

	def doubleClick(self,event):
		if(event.state==12):return#Control key is pressed -> flag function is called

		self.scriptWindow = tk.Toplevel(self.root)
		self.scriptWindow.title("See Script Details")
		self.scriptWindow.geometry("650x120")

		label=tk.Label(self.scriptWindow,text="Script:    "+str(self.label0)+":")
		label.pack()
		label.place(x=5,y=15)
		data_string = tk.StringVar()
		data_string.set(str(self.script[index].hex()))
		e=tk.Entry(self.scriptWindow,textvariable=data_string,fg="black",bg="white",bd=0,state="readonly")
		e.pack()
		e.place(x=150,y=17,width=500)

		label=tk.Label(self.scriptWindow,text="PubKey:    "+str(self.parent_array[0].label0)+":")
		label.pack()
		label.place(x=5,y=40)
		data_string = tk.StringVar()
		data_string.set(str(self.parent_array[0].pubkey[index]))
		e=tk.Entry(self.scriptWindow,textvariable=data_string,fg="black",bg="white",bd=0,state="readonly")
		e.pack()
		e.place(x=150,y=42,width=400)

		if(self.timelockDelay>0):
			label=tk.Label(self.scriptWindow,text="Relative TimeLock: ")
			data_string = tk.StringVar()
			data_string.set(str(self.timelockDelay))
		if(self.timelock>0):
			label=tk.Label(self.scriptWindow,text="Absolute TimeLock: ")
			data_string = tk.StringVar()
			data_string.set(str(self.timelock))
		if(self.timelockDelay>0 or self.timelock>0):
			label.pack()
			label.place(x=5,y=65)
			e=tk.Entry(self.scriptWindow,textvariable=data_string,fg="black",bg="white",bd=0,state="readonly")
			e.pack()
			e.place(x=150,y=67,width=400)

	def createTapbranch(self):
		tapBranch,hash_=tapTree.construct_Tapbranch(self.script)
		parent_array=[]
		parent_array.append(self)
		child=global_.gl_gui_build_address.add_hash_container(self.editLabel.get(),tapBranch,hash_,parent_array)
		self.childList.append(child)

	
	def update_index(self):
		if(len(self.tapLeaf)<2):return
		txt="Script: "+str(shortenHexString(str(self.script[global_.gl_current_child_index].hex()),True))
			
		if(self.timelockDelay>0):txt=txt+"\nRelative Timelock: "+str(self.timelockDelay)
		elif(self.timelock>0):txt=txt+"\nAbsolute Timelock: "+str(self.timelock)
		else:txt=txt+"\nNo Timelock"
		self.label_label1.config(text=txt)
		self.label_label3.config(text="Hash "+str(global_.gl_current_child_index)+": "+str(shortenHexString(str(self.hash_[global_.gl_current_child_index].hex()),True)))



class c_Container_Hash(c_Container):
	def __init__(self,x_pos,y_pos,label,tapLeaf,hash_,parent_array,is_mine=False,has_extended_parent=False):

		#if(hash_ is not None):
		c_Container.__init__(self,x_pos,y_pos,label,None,str(hash_[global_.gl_current_child_index].hex()),parent_array=parent_array,is_mine=is_mine,has_extended_parent=has_extended_parent)
		#else:
		#	c_Container.__init__(self,x_pos,y_pos,label,None,parent_array=parent_array,is_mine=is_mine,has_extended_parent=True)

		if(len(self.parent_array)==1):self.label_label0.config(text="TapLeaf")
		else: self.label_label0.config(text="TapBranch")
		self.tapLeaf=tapLeaf
		self.hash_=hash_
		self.label_balance=None
		self.label_label1.place(x=4, y=17,height=15,width=self.sizeX-10)

		if(self.x_pos==None):
			random_=randrange(0,100)
			self.x_pos=20+random_*10

		if(self.y_pos>global_.gl_gui.guiy-self.sizeY):self.y_pos=global_.gl_gui.guiy-self.sizeY

		


		if(self.y_pos>global_.gl_gui.guiy-self.sizeY):self.y_pos=global_.gl_gui.guiy-self.sizeY

		self.container.place(height=self.sizeY,width=self.sizeX, x=self.x_pos,y=self.y_pos)

		self.updateLine()
		if(len(self.parent_array)==1):self.buttonExit.destroy()

		txt="Hash "+str(global_.gl_current_child_index)+": "+str(shortenHexString(str(self.hash_[global_.gl_current_child_index].hex()),True))
		self.label_label1.config(text=txt)


	

	def update_index(self):
		txt="Hash "+str(global_.gl_current_child_index)+": "+str(shortenHexString(str(self.hash_[global_.gl_current_child_index].hex()),True))
		self.label_label1.config(text=txt)

class c_Container_Taproot(c_Container):
	def __init__(self,x_pos,y_pos,internalKey,merkleRoot,show=True):
		
		self.internalKey=internalKey
		self.merkleRoot=merkleRoot
		self.show=show
		self.taptree=[]
		self.tapTweak=[]
		self.tapTweak_bytes=[]
		self.TapRootAddress=[]
		self.tweaked_privkey=[]
		self.tweakedPubkey=[]
		#self.label_label1.place(x=4, y=17,height=15,width=self.sizeX-10)

		has_extended_parent=False
		#if(self.internalKey.ext_pubkey is not None):has_extended_parent=True
		#if(self.merkleRoot is not None):
		#	if(self.merkleRoot.tapLeaf is None):
		#		has_extended_parent=True
		#if(self.internalKey.pubkey is None):has_extended_parent=True
		#if(self.merkleRoot is not None):
		#	if(self.merkleRoot.tapLeaf is None):has_extended_parent=True

		for i in range(0,global_.gl_address_generation_max):    #if(has_extended_parent==False):
			a=0 if(len(self.internalKey.pubkey)==1) else i
			#b=0 if(len(self.merkleRoot.tapLeaf)==1) else i

			if(self.merkleRoot==None):#No scripts involved
				self.tapTweak_bytes.append( test_framework.tagged_hash("TapTweak", self.internalKey.pubkey[a].get_bytes()))
		
			else:#With scriptTree
				a=0 if(len(self.internalKey.pubkey)==1) else i
				b=0 if(len(self.merkleRoot.tapLeaf)==1) else i
				taptree = taproot.TapTree(key=self.internalKey.pubkey[a], root=merkleRoot.tapLeaf[b])
				taptree = taptree.construct()
				self.tapTweak_bytes.append(taptree[1])
				self.taptree.append(taptree)

			#print([taprootObject])
			taproot_pubkey_b = self.internalKey.pubkey[a].tweak_add(self.tapTweak_bytes[i]).get_bytes()
			self.TapRootAddress.append(test_framework.program_to_witness(1, taproot_pubkey_b,main=global_.gl_mainnet))
			self.tapTweak.append(test_framework.ECKey().set(self.tapTweak_bytes[i]))
			self.tweakedPubkey.append(test_framework.ECPubKey().set(taproot_pubkey_b))


			if(self.internalKey.privkey is not None):
				if(len(self.internalKey.privkey)>i):
					tweak_p=self.internalKey.privkey[i].add(self.tapTweak_bytes[i])
					tweak_p,pub=test_framework.generate_bip340_key_pair(tweak_p.secret)#createTapRootFromPriv(str(self.tweaked_privkey.secret))[0]
					self.tweaked_privkey.append(tweak_p)
			
			#print("NEW: "+str(self.tweakedPubkey)+" : "+str(self.tweakedPubkey.get_y()))
			#self.negated=False
			if(self.tweakedPubkey[i].get_y()%2!=0):
				#print("New Not Even")
				self.tweakedPubkey[i].negate()
				self.tapTweak[i].negate()
				self.internalKey.pubkey[i].negate()
				#self.internalKey.privkey.negate()
				#self.negated=True

			if(len(self.internalKey.pubkey)==1 and self.merkleRoot==None):break
			if(len(self.internalKey.pubkey)==1 and len(self.merkleRoot.tapLeaf)==1):break

		parents=None
		if(merkleRoot):parents=[internalKey,merkleRoot]
		else: parents=[internalKey]

		if(len(self.TapRootAddress)>global_.gl_current_child_index):
			global_.gl_current_child_index=len(self.TapRootAddress)-1
		c_Container.__init__(self,x_pos,y_pos,label0="Taproot Address",label1=self.TapRootAddress[global_.gl_current_child_index],parent_array=parents,is_mine=True,has_extended_parent=has_extended_parent)
		self.label_label0.config(text="Taproot Address")
		if(y_pos>global_.gl_gui.guiy-self.sizeY):y_pos=global_.gl_gui.guiy-self.sizeY

		#self.label0="Taproot Address"
		#self.label_label0.config(text=self.label0)

		self.control_map=[]
		for taptree in self.taptree:
			self.control_map.append(taptree[2])

		self.utxoList=[]
		self.utxoSelected=[]
		self.containerChooseUTXO=None
		global_.gl_gui_build_address.canvasUTXO=None
		self.scrollable_frame=None

		txt=str(global_.gl_current_child_index)+": "+str(shortenHexString(str(self.TapRootAddress[global_.gl_current_child_index]),True))
		self.label_label1.config(text=txt)

		
		self.updateLine()
		self.remove_unused_container()

		
		
		

	def remove_unused_container(self):
		for i in range (0,len(global_.gl_gui_build_address.pubkey_container_array)):
			global_.gl_gui_build_address.pubkey_container_array[i].active=False
		for i in range (0,len(global_.gl_gui_build_address.script_container_array)):
			global_.gl_gui_build_address.script_container_array[i].active=False
		for i in range (0,len(global_.gl_gui_build_address.hash_container_array)):
			global_.gl_gui_build_address.hash_container_array[i].active=False

		self.internalKey.active=True
		self.internalKey.setParentActive()

		if(self.merkleRoot):
			self.merkleRoot.active=True
			self.merkleRoot.setParentActive()

		a=0
		for i in range (0,len(global_.gl_gui_build_address.pubkey_container_array)):
			if(a>=len(global_.gl_gui_build_address.pubkey_container_array)):break
			if(global_.gl_gui_build_address.pubkey_container_array[a]):
				if(global_.gl_gui_build_address.pubkey_container_array[a].active==False):
					container=global_.gl_gui_build_address.pubkey_container_array[a]
					global_.gl_gui_build_address.pubkey_container_array.remove(container)
					container.remove_container()
				else:a+=1
		a=0
		for i in range (0,len(global_.gl_gui_build_address.script_container_array)):
			if(a>=len(global_.gl_gui_build_address.script_container_array)):break
			if(global_.gl_gui_build_address.script_container_array[a]):
				if(global_.gl_gui_build_address.script_container_array[a].active==False):
					container=global_.gl_gui_build_address.script_container_array[a]
					global_.gl_gui_build_address.script_container_array.remove(container)
					container.remove_container()
				else:a+=1
		a=0
		for i in range (0,len(global_.gl_gui_build_address.hash_container_array)):
			if(a>=len(global_.gl_gui_build_address.hash_container_array)):break
			if(global_.gl_gui_build_address.hash_container_array[a]):
				if(global_.gl_gui_build_address.hash_container_array[a].active==False):
					container=global_.gl_gui_build_address.hash_container_array[a]
					global_.gl_gui_build_address.hash_container_array.remove(container)
					container.remove_container()
				else:a+=1
		
	def remove_container(self):
		
		super().remove_container()
		global_.gl_gui_build_address.taproot_container=None

	def update_index(self):
		
		txt=str(global_.gl_current_child_index)+": "+str(shortenHexString(str(self.TapRootAddress[global_.gl_current_child_index]),True))
		self.label_label1.config(text=txt)

	def get_index_of_address(self,address):

		for i in range(0,len(self.TapRootAddress)):
			if(address==self.TapRootAddress[i]):
				return i
		return None