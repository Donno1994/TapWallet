import tkinter as tk
from tkinter import ttk
import config 
import bitcoinlib
from bitcoin_core_framework.script import hash160,hash256,sha256,ripemd160

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

		self.root=config.gl_gui_build_address.container_Script
		self.mouseDown=False
		self.mouseX=x_pos
		self.mouseY=y_pos
		self.isMini=False
		

		self.has_extended_parent=has_extended_parent # True, if at least one parent is an extended key. Then this key can't be calculated until a child key is derived

		#config.gl_gui.bool_ask_for_save=True
		

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

		self.label_label0=tk.Label(self.container,text="Script: "+str(self.label0))#Example: PubKey: Alice
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
				self.line.append(config.gl_gui_build_address.canvas.create_line(middleX,middleY,parent_array[i].x_pos+(self.sizeX/2),parent_array[i].y_pos++(self.sizeY/2)))

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
				config.gl_gui_build_address.canvas.coords(self.line[i],middleX,middleY,self.parent_array[i].x_pos+(self.sizeX/2),self.parent_array[i].y_pos+(self.sizeY/2))

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
		
		
		for i in range(0,len(config.gl_selected_container)):
			if(config.gl_selected_container[i]==self):
				self.changeColor()
				config.gl_selected_container.remove(self)
				return

		#if(gui.taproot_container==None):#Don't flag when Taproot Address exists
		
		self.container.config(bg="#ffcc00")
		self.label_label0.config(bg="#ffcc00")
		self.label_label1.config(bg="#ffcc00")
		if(isinstance(self,c_Container_Script)):self.label_label3.config(bg="#ffcc00")
		config.gl_selected_container.append(self)

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
				self.label_label0.config(text="Script: "+str(self.label0))
				self.highlightContainer.config(text="Script: "+str(self.label0))

		else:
			self.isMini=True
			self.sizeY=25
			self.sizeX=120

			if(isinstance(self,c_Container_PubKey) or isinstance(self,c_Container_Script)):
				self.label_label0.config(text=str(self.label0))
				self.highlightContainer.config(text=str(self.label0))

		self.container.place(height=self.sizeY,width=self.sizeX, x=self.x_pos,y=self.y_pos)
		self.updateLine()
		for i in range (0,len(self.childList)):
			self.childList[i].updateLine()

	def remove_container(self,ask_for_confirmation=True):
		
		if(ask_for_confirmation):
			answer = tk.messagebox.askyesno(title='Sure to delete container?',
						message=("If you delete this container, all child containers will be deleted as well, including your taproot address.\n"
								"If you have funds on your addresses, you must know how to recreate your taproot address, or you lose your money.\n\n"
								"Are you sure you want to delete this container?"))
	
			if(answer==False):
				return
		for i in range(0,len(self.parent_array)):
			config.gl_gui_build_address.canvas.delete(self.line[i])

		for i in range(0,len(self.childList)):
			self.childList[i].remove_container(False)

		for i in range(0,len(config.gl_selected_container)):
			if(config.gl_selected_container[i]==self):
				config.gl_selected_container.remove(self)

		config.gl_gui_build_address.removeKeyContainer(self)
		config.gl_gui.bool_ask_for_save=True
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
			config.gl_gui_build_address.canvas.coords(self.line[i],middleX,middleY,self.parent_array[i].x_pos+(self.parent_array[i].sizeX/2),self.parent_array[i].y_pos+(self.parent_array[i].sizeY/2))
	
	def doubleClick(self,event):
		return

	def setParentActive(self):
		for a in range(0,len(self.parent_array)):
			container=self.parent_array[a]
			container.active=True
			container.setParentActive()

	def copy_on_right_click(self,event):
		index=config.gl_current_child_index

		if(isinstance(self,c_Container_PubKey)):
			if(len(self.pubkey)==1):index=0
			config.gl_console.copyText(str(self.pubkey[index]))
		if(isinstance(self,c_Container_Script)):
			if(len(self.script)==1):index=0
			config.gl_console.copyText(str(self.script[index].hex()))
		if(isinstance(self,c_Container_Hash)):
			if(len(self.hash_)==1):index=0
			config.gl_console.copyText(self.hash_[index].hex())
		if(isinstance(self,c_Container_Taproot)):
			if(len(self.TapRootAddress)==1):index=0
			config.gl_console.copyText(self.TapRootAddress[index])

	def copy_hash_on_right_click(self,event):
		index=config.gl_current_child_index
		if(len(self.hash_)==1):index=0
		config.gl_console.copyText(self.hash_[index].hex())
		

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

		self.hash160=None

		if(isinstance(privKey,test_framework.ECKey)):
			if(len(str(privKey))>5):
				print("Adding KeyPair: ",str(hex(privKey.secret))[2:]," - ",str(privKey.get_pubkey()))
			elif(len(parent_array)==0):
				print("Adding Pubkey: ",str(privKey.get_pubkey()))


		if(isinstance(privKey,bitcoinlib.keys.Key)):
			if(len(str(privKey))>5):
				print("Addig KeyPair: ",str(privKey)," - ",str(privKey.wif_public()))

		
		if(self.ext_key is not None):
			
			for change_index in range(2):

				priv_parent = self.ext_key.child_private(change_index) if(self.ext_key.secret is not None) else None
				pub_parent = self.ext_key.child_public(change_index)

				for address_index in range (0,int(config.gl_address_generation_max/2)):
					print("Address Index ",address_index ,"")
					if(self.ext_key.secret is not None):
						prv=test_framework.ECKey().set(priv_parent.child_private(address_index).secret)
					else:prv=None
					pub=test_framework.ECPubKey().set(pub_parent.child_public(address_index).public_byte)
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
		if(len(self.pubkey)> config.gl_current_child_index):data_string_pub.set("Public Key "+str(config.gl_current_child_index)+": "+str(self.pubkey[config.gl_current_child_index]))
		else: data_string_pub.set(str("Public Key  : not available"))
		e2=tk.Entry(self.scriptWindow,textvariable=data_string_pub,fg="black",bg="white",bd=0,state="readonly")
		e2.pack()
		e2.place(x=5,y=45,width=590)

		scriptFrame = tk.LabelFrame(self.scriptWindow)
		scriptFrame.pack()
		scriptFrame.place(height=280,width=590, x=5,y=70)

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
		
		label_hashlock=tk.Label(scriptFrame,text="Add a hashlock to script:")
		label_hashlock.pack()
		label_hashlock.place(height=15,x=5,y=160)

		self.radioHashlockVar=tk.IntVar(value=1)
		radioTimelock0=tk.Radiobutton(scriptFrame,text="No Hashlock",variable=self.radioHashlockVar,value=1,command=self.showNoHashlock)
		radioTimelock0.pack()
		radioTimelock0.place(x=150,y=158)
		radioTimelock1=tk.Radiobutton(scriptFrame,text="Add Hashlock",variable=self.radioHashlockVar,value=2,command=self.showHashlock)
		radioTimelock1.pack()
		radioTimelock1.place(x=250,y=158)

		self.label_preimage_value=tk.Label(scriptFrame,text="Enter Preimage:")
		self.label_preimage_value.pack()
		self.label_preimage_value.place(height=15,x=5,y=185)

		self.editHashlock=tk.Entry(scriptFrame)
		self.editHashlock.pack()
		self.editHashlock.place(height=15,width=450,x=100,y=185)
		self.editHashlock.bind("<KeyRelease>", self.calc_hashlock)

		self.label_hash_value=tk.Label(scriptFrame,text="Hash160 Value:")
		self.label_hash_value.pack()
		self.label_hash_value.place(height=15,x=5,y=210)

		self.typed_hash = tk.StringVar()
		self.edit_show_hash160=tk.Entry(scriptFrame,textvariable=self.typed_hash)
		self.edit_show_hash160.pack()
		self.edit_show_hash160.place(height=15,width=300,x=100,y=210)
		self.edit_show_hash160.bind("<KeyRelease>", self.use_custom_hashlock);

		self.label_hash_info=tk.Label(scriptFrame,text="Enter a preimage, generate a random preimage, or enter a friend's hash")
		self.label_hash_info.pack()
		self.label_hash_info.place(height=15,x=100,y=235)

		self.button_random_preimage=tk.Button(scriptFrame,text="Create random Preimage", command=self.create_random_preimage,bg="#ffcc80")
		self.button_random_preimage.pack()
		self.button_random_preimage.place(height=15,x=510,y=185)
		

		self.buttonScript=tk.Button(scriptFrame,text="Create Script", command=self.createScript,bg="#DC7A7A")
		self.buttonScript.pack()
		self.buttonScript.place(height=20,width=90,x=5,y=250)

		self.showNoHashlock()

		taprootFrame = tk.LabelFrame(self.scriptWindow)
		taprootFrame.pack()
		taprootFrame.place(height=40,width=600, x=5,y=350)

		buttonTaprootAddress=tk.Button(taprootFrame,text="Create Taproot", command=lambda:config.gl_gui_build_address.calc_key_released_taproot(key=self),bg="#47C718")
		buttonTaprootAddress.pack()
		buttonTaprootAddress.place(height=20,width=90,x=5,y=5)

		labelInfo=tk.Label(taprootFrame,text="If you don't want to use scripts, you can create a taproot address straight away.\n"
											"This will delete all other scripts and keys apart from parent keys.")
		labelInfo.pack()
		labelInfo.place(x=120,y=5)

		
	def create_random_preimage(self):
		prv,pub=test_framework.generate_bip340_key_pair()
		prv=str(hex(prv.secret))[2:]

		self.editHashlock.delete(0, 'end')
		self.editHashlock.insert(0,prv)
		self.calc_hashlock()
	
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

	def showNoHashlock(self):
		self.label_preimage_value.place_forget()
		self.editHashlock.place_forget()
		self.button_random_preimage.place_forget()
		self.label_hash_value.place_forget()
		self.edit_show_hash160.place_forget()
		self.label_hash_info.place_forget()

		self.editHashlock.delete(0, 'end')
		self.edit_show_hash160.configure(state='normal',fg="#000000")
		self.edit_show_hash160.delete(0, 'end')


		self.buttonScript.configure(state='normal')

		self.hash160=None

	def showHashlock(self):
		self.label_preimage_value.place(height=15,x=5,y=185)
		self.editHashlock.place(height=15,width=400,x=100,y=185)
		self.button_random_preimage.place(height=15,x=420,y=210)
		self.label_hash_value.place(height=15,x=5,y=210)
		self.edit_show_hash160.place(height=15,width=300,x=100,y=210)
		self.label_hash_info.place(height=15,x=100,y=235)

		self.calc_hashlock()

	def calc_hashlock(self,event=None):
		#preimage=bytes.fromhex(self.editHashlock.get())  interpret input as hex number
		preimage=self.editHashlock.get().encode()        #interpret input as string

		if(len(preimage)==0):
			self.label_hash_info.configure(text="Enter a preimage, generate a random preimage, or just enter the hash")
			self.edit_show_hash160.configure(fg="#ff0000")
			self.edit_show_hash160.delete(0, 'end')
			self.buttonScript.configure(state='disabled')
			return
		elif(len(preimage)<10):
			self.label_hash_info.configure(text="Your input is too short. This can be brute forced easily.")
			self.edit_show_hash160.configure(fg="#ff0000")
			self.buttonScript.configure(state='disabled')
		else:
			self.label_hash_info.configure(text="Enter a preimage, generate a random preimage, or just enter the hash")
			self.edit_show_hash160.configure(fg="#000000")
			self.buttonScript.configure(state='normal')

		
		hash_160=hash160(preimage)

		self.edit_show_hash160.delete(0, 'end')
		self.edit_show_hash160.insert(0,str(hash_160.hex()))
		#self.edit_show_hash160.configure(state='disabled')

		self.hash160=hash_160

	def use_custom_hashlock(self,event=None):
		if(event.keycode==17):return
		self.editHashlock.delete(0, 'end')
		typed_hash_string=self.typed_hash.get()


		if(len(typed_hash_string)==40):
			try:
				self.hash160=bytes.fromhex(self.typed_hash.get())
				self.edit_show_hash160.configure(fg="#000000")
				self.buttonScript.configure(state='normal')
				self.label_hash_info.configure(text="Enter a preimage, generate a random preimage, or just enter the hash")
			except:
				self.label_hash_info.configure(text="Your hash is not valid. Only hexadecimal characters allowed")
		else:
			self.label_hash_info.configure(text="The hash must have 40 hexadecimal characters")
			self.hash160=None
			self.edit_show_hash160.configure(fg="#ff0000")
			self.buttonScript.configure(state='disabled')
			return

		

	def createScript(self,label=None,x_pos=None,y_pos=None,timelockdelay=None,timelock=None,hash160=None):

		if(config.gl_gui_build_address.taproot_container):
			config.gl_console.printText("Can't create a script when taproot address is already created")
			return

		if(label is None):label=self.editLabel.get()

		if(timelockdelay is None and timelock is None):
			timelockdelay=0
			timelock=0

			if(len(self.editRelTimelock.get())>0):
				if(self.editRelTimelock.get().isnumeric()==False):
					config.gl_console.printText("TimeLock must be a positive number or empty")
					return
				if(int (self.editRelTimelock.get())>65535 or int (self.editRelTimelock.get())<=0):
					config.gl_console.printText("Rel TimeLock must be between 1 and 65535")
					return

			elif(len(self.editAbsTimelock.get())>0):
				if(self.editAbsTimelock.get().isnumeric()==False):
					config.gl_console.printText("TimeLock must be a positive number or empty")
					return
				if(int (self.editAbsTimelock.get())>16777216 or int(self.editAbsTimelock.get())<=0):
					config.gl_console.printText("Abs TimeLock must be bewteen 1 and 16777216")
					return

			if(len(self.editRelTimelock.get())>0):
				timelockdelay=int(self.editRelTimelock.get())
			elif(len(self.editAbsTimelock.get())>0):
				timelock=int(self.editAbsTimelock.get())

		if(hash160 is None and self.hash160 is not None):hash160=self.hash160

		tapLeaf=[]
		tapleaf_hash=[]

		for i in range(0,len(self.pubkey)):
			
			tapL,tapleaf_h=taproot.construct_Tapleaf(self.pubkey[i],timelockdelay,timelock,hash160)
			if(tapL is None or tapleaf_h is None):
				return
			tapLeaf.append(tapL)
			tapleaf_hash.append(tapleaf_h)

		parent_array=[]
		parent_array.append(self)
		
		child=c_Container_Script(label,tapLeaf,tapleaf_hash,x_pos,y_pos,timelockdelay,timelock,hash160,parent_array,self.is_mine,self.has_extended_parent)
		config.gl_gui_build_address.script_container_array.append(child)
		
		
		self.childList.append(child)
		child.onMove(None)

		try:
			self.scriptWindow.destroy()
		except:
			pass

	
	def update_index(self):
		if len(self.pubkey)==1:txt="\n"+str(shortenHexString(str(self.pubkey[0]),14,11))
		else:
			if(len(self.parent_array)>0):
				txt=("Extended Key not available"+"\nIndex:"+
					str(config.gl_current_child_index)+":"+
					str(shortenHexString(str(self.pubkey[config.gl_current_child_index]),14,11)))
			else:
				txt=(str(shortenHexString(str(self.ext_key.wif_public()),14,11))+"\nIndex:"+
					str(config.gl_current_child_index)+":"+
					str(shortenHexString(str(self.pubkey[config.gl_current_child_index]),14,11)))
		self.label_label1.config(text=txt)

class c_Container_Script(c_Container):
	def __init__(self,label,tapleaf,hash_,x=None,y=None,timelockDelay=0,timelock=0,hash160=None,parent_array=[],is_mine=False,has_extended_parent=False):
		
		if(x is None):x=parent_array[0].x_pos
		if(y is None):y=parent_array[0].y_pos+parent_array[0].sizeY+10

		self.timelockDelay=timelockDelay
		self.timelock=timelock
		self.hash160=hash160
		self.hash160_preimage=None
		self.tapLeaf=tapleaf
		self.script=[]
		self.hash_=hash_
		for tapL in tapleaf:
			self.script.append(tapL.script)

		maximum_index=len(self.tapLeaf)-1
		index=min(maximum_index,config.gl_current_child_index)
		c_Container.__init__(self,x,y,label0=label,label1=str(tapleaf[index].script.hex()),parent_array=parent_array,is_mine=is_mine,has_extended_parent=has_extended_parent)
		
		

		#self.label_label1.config(text=txt, justify=tk.LEFT)

		#self.label_label0.config(text=str(label))
		self.highlightContainer.config(text=str(label))
		
		
		self.label_label3=tk.Label(self.container,text="Hash "+str(index)+": "+str(shortenHexString(str(hash_[index].hex()),14,11)),bg="#16e971")
		self.label_label3.pack()
		self.label_label3.place(x=0, y=52,height=20,width=self.sizeX-5)
		self.label_label3.bind('<Button-1>', self.onClick)
		self.label_label3.bind('<B1-Motion>', self.onMove)
		self.label_label3.bind('<Control-Button-1>', self.flag)
		self.label_label3.bind('<Double-Button-1>', self.doubleClick)
		self.label_label3.bind('<Button-3>',self.copy_hash_on_right_click)


		self.container.place(height=self.sizeY,width=self.sizeX, x=self.x_pos,y=self.y_pos)

		self.updateLine()
		txt="Script: "+str(shortenHexString(str(self.script[index].hex()),14,11)+"\n")
		
		if(self.timelockDelay>0):txt=txt+"Rel Timelock: "+str(self.timelockDelay)
		elif(self.timelock>0):txt=txt+"Abs Timelock: "+str(self.timelock)


		if(self.hash160 is not None):
			if(self.timelockDelay>0 or self.timelock>0):
				txt+=" Hashlock: "+str(shortenHexString(self.hash160.hex(),3,3))
			else:
				txt+=" Hashlock: "+str(shortenHexString(self.hash160.hex(),14,11))

		self.label_label1.config(text=txt)
		self.label_label3.config(text="Hash "+str(index)+": "+str(shortenHexString(str(self.hash_[index].hex()),14,11)))

	def doubleClick(self,event):
		if(event.state==12):return#Control key is pressed -> flag function is called

		self.scriptWindow = tk.Toplevel(self.root)
		self.scriptWindow.title("See Script Details")
		self.scriptWindow.geometry("650x120")

		maximum_index=len(self.tapLeaf)-1
		index=min(maximum_index,config.gl_current_child_index)

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
		elif(self.timelock>0):
			label=tk.Label(self.scriptWindow,text="Absolute TimeLock: ")
			data_string = tk.StringVar()
			data_string.set(str(self.timelock))
		else:
			label=tk.Label(self.scriptWindow,text="TimeLock:")
			data_string = tk.StringVar()
			data_string.set("None")
		
		label.pack()
		label.place(x=5,y=65)

		#if(self.timelockDelay>0 or self.timelock>0):
		e=tk.Entry(self.scriptWindow,textvariable=data_string,fg="black",bg="white",bd=0,state="readonly")
		e.pack()
		e.place(x=150,y=67,width=400)

		label=tk.Label(self.scriptWindow,text="Hashlock (HASH160):")
		label.pack()
		label.place(x=5,y=90)

		if(self.hash160 is not None):
			
			data_string = tk.StringVar()
			data_string.set(str(self.hash160.hex()))
			#e=tk.Entry(self.scriptWindow,textvariable=data_string,fg="black",bg="white",bd=0,state="readonly")
			#e.pack()
			#e.place(x=150,y=92,width=400)

		else:
			data_string = tk.StringVar()
			data_string.set("None")
		e=tk.Entry(self.scriptWindow,textvariable=data_string,fg="black",bg="white",bd=0,state="readonly")
		e.pack()
		e.place(x=150,y=92,width=400)

	
	def update_index(self):
		len_=len(self.tapLeaf)
		if(len(self.tapLeaf)<2):return

		index=config.gl_current_child_index
		if(len_-1<config.gl_current_child_index):index=len_-1

		txt="Script: "+str(shortenHexString(str(self.script[index].hex()),14,11)+"\n")
		if(self.timelockDelay>0):txt=txt+"Rel Timelock: "+str(self.timelockDelay)
		elif(self.timelock>0):txt=txt+"Abs Timelock: "+str(self.timelock)
		if(self.hash160 is not None):
			if(self.timelockDelay>0 or self.timelock>0):
				txt+=" Hashlock: "+str(shortenHexString(self.hash160.hex(),3,3))
			else:
				txt+=" Hashlock: "+str(shortenHexString(self.hash160.hex(),14,11))

		self.label_label1.config(text=txt)

		len_=len(self.hash_)
		
		index=config.gl_current_child_index
		if(len_-1<config.gl_current_child_index):index=len_-1

		txt="Hash "+str(index)+": "+str(shortenHexString(str(self.hash_[index].hex()),14,11))
		self.label_label3.config(text=txt)


class c_Container_Hash(c_Container):
	def __init__(self,x_pos,y_pos,label,tapLeaf,hash_,parent_array,is_mine=False,has_extended_parent=False):

		#if(hash_ is not None):
		c_Container.__init__(self,x_pos,y_pos,label,None,str(hash_[config.gl_current_child_index].hex()),parent_array=parent_array,is_mine=is_mine,has_extended_parent=has_extended_parent)
		#else:
		#	c_Container.__init__(self,x_pos,y_pos,label,None,parent_array=parent_array,is_mine=is_mine,has_extended_parent=True)

		if(len(self.parent_array)==1):self.label_label0.config(text="TapLeaf")
		else: self.label_label0.config(text="TapBranch")
		self.tapLeaf=tapLeaf
		self.hash_=hash_
		self.label_balance=None
		self.label_label1.place(x=4, y=17,height=15,width=self.sizeX-10)

		if(self.x_pos==None):
			random_=random.randrange(0,100)
			self.x_pos=20+random_*10

		if(self.y_pos>config.gl_gui.guiy-self.sizeY):self.y_pos=config.gl_gui.guiy-self.sizeY

		


		if(self.y_pos>config.gl_gui.guiy-self.sizeY):self.y_pos=config.gl_gui.guiy-self.sizeY

		self.container.place(height=self.sizeY,width=self.sizeX, x=self.x_pos,y=self.y_pos)

		self.updateLine()
		if(len(self.parent_array)==1):self.buttonExit.destroy()

		txt="Hash "+str(config.gl_current_child_index)+": "+str(shortenHexString(str(self.hash_[config.gl_current_child_index].hex()),14,11))
		self.label_label1.config(text=txt)


	

	def update_index(self):
		len_=len(self.hash_)
		
		index=config.gl_current_child_index
		if(len_-1<config.gl_current_child_index):index=len_-1

		txt="Hash "+str(index)+": "+str(shortenHexString(str(self.hash_[index].hex()),14,11))
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

		for address_index in range(0,config.gl_address_generation_max):    #if(has_extended_parent==False):
			a=0 if(len(self.internalKey.pubkey)==1) else address_index
			#b=0 if(len(self.merkleRoot.tapLeaf)==1) else i

			if(self.merkleRoot==None):#No scripts involved
				self.tapTweak_bytes.append( test_framework.tagged_hash("TapTweak", self.internalKey.pubkey[a].get_bytes()))
		
			else:#With scriptTree
				a=0 if(len(self.internalKey.pubkey)==1) else address_index
				b=0 if(len(self.merkleRoot.tapLeaf)==1) else address_index
				taptree = taproot.TapTree(key=self.internalKey.pubkey[a], root=merkleRoot.tapLeaf[b])
				taptree = taptree.construct()
				self.tapTweak_bytes.append(taptree[1])
				self.taptree.append(taptree)

			taproot_pubkey_b = self.internalKey.pubkey[a].tweak_add(self.tapTweak_bytes[address_index]).get_bytes()
			self.TapRootAddress.append(test_framework.program_to_witness(1, taproot_pubkey_b,main=config.gl_mainnet))
			self.tapTweak.append(test_framework.ECKey().set(self.tapTweak_bytes[address_index]))
			self.tweakedPubkey.append(test_framework.ECPubKey().set(taproot_pubkey_b))


			if(self.internalKey.privkey is not None):
				if(len(self.internalKey.privkey)>address_index):
					tweak_p=self.internalKey.privkey[address_index].add(self.tapTweak_bytes[address_index])
					tweak_p,pub=test_framework.generate_bip340_key_pair(tweak_p.secret)
					self.tweaked_privkey.append(tweak_p)
			
			if(self.tweakedPubkey[address_index].get_y()%2!=0):
				self.tweakedPubkey[address_index].negate()
				self.tapTweak[address_index].negate()
				self.internalKey.pubkey[address_index].negate()

			if(len(self.internalKey.pubkey)==1 and self.merkleRoot==None):break
			if(len(self.internalKey.pubkey)==1 and len(self.merkleRoot.tapLeaf)==1):break

		parents=None
		if(merkleRoot):parents=[internalKey,merkleRoot]
		else: parents=[internalKey]

		if(len(self.TapRootAddress)>config.gl_current_child_index):
			config.gl_current_child_index=len(self.TapRootAddress)-1
		c_Container.__init__(self,x_pos,y_pos,label0="Taproot Address",label1=self.TapRootAddress[config.gl_current_child_index],parent_array=parents,is_mine=True,has_extended_parent=has_extended_parent)
		self.label_label0.config(text="Taproot Address")
		if(y_pos>config.gl_gui.guiy-self.sizeY):y_pos=config.gl_gui.guiy-self.sizeY

		#self.label0="Taproot Address"
		#self.label_label0.config(text=self.label0)

		self.control_map=[]
		for taptree in self.taptree:
			self.control_map.append(taptree[2])

		self.utxoList=[]
		self.utxoSelected=[]
		self.containerChooseUTXO=None
		config.gl_gui_build_address.canvasUTXO=None
		self.scrollable_frame=None

		txt=str(config.gl_current_child_index)+": "+str(shortenHexString(str(self.TapRootAddress[config.gl_current_child_index]),14,11))
		self.label_label1.config(text=txt)

		
		self.updateLine()
		self.remove_unused_container()
		
		
		
		

	def remove_unused_container(self):
		for i in range (0,len(config.gl_gui_build_address.pubkey_container_array)):
			config.gl_gui_build_address.pubkey_container_array[i].active=False
		for i in range (0,len(config.gl_gui_build_address.script_container_array)):
			config.gl_gui_build_address.script_container_array[i].active=False
		for i in range (0,len(config.gl_gui_build_address.hash_container_array)):
			config.gl_gui_build_address.hash_container_array[i].active=False

		self.internalKey.active=True
		self.internalKey.setParentActive()

		if(self.merkleRoot):
			self.merkleRoot.active=True
			self.merkleRoot.setParentActive()

		a=0
		for i in range (0,len(config.gl_gui_build_address.pubkey_container_array)):
			if(a>=len(config.gl_gui_build_address.pubkey_container_array)):break
			if(config.gl_gui_build_address.pubkey_container_array[a]):
				if(config.gl_gui_build_address.pubkey_container_array[a].active==False):
					container=config.gl_gui_build_address.pubkey_container_array[a]
					config.gl_gui_build_address.pubkey_container_array.remove(container)
					container.remove_container()
				else:a+=1
		a=0
		for i in range (0,len(config.gl_gui_build_address.script_container_array)):
			if(a>=len(config.gl_gui_build_address.script_container_array)):break
			if(config.gl_gui_build_address.script_container_array[a]):
				if(config.gl_gui_build_address.script_container_array[a].active==False):
					container=config.gl_gui_build_address.script_container_array[a]
					config.gl_gui_build_address.script_container_array.remove(container)
					container.remove_container()
				else:a+=1
		a=0
		for i in range (0,len(config.gl_gui_build_address.hash_container_array)):
			if(a>=len(config.gl_gui_build_address.hash_container_array)):break
			if(config.gl_gui_build_address.hash_container_array[a]):
				if(config.gl_gui_build_address.hash_container_array[a].active==False):
					container=config.gl_gui_build_address.hash_container_array[a]
					config.gl_gui_build_address.hash_container_array.remove(container)
					container.remove_container()
				else:a+=1
		
	def remove_container(self,ask_for_confirmation=True):
		
		if(ask_for_confirmation):
			answer = tk.messagebox.askyesno(title='Sure to delete container?',
						message=("If you delete this container, all child containers will be deleted as well, including your taproot address.\n"
								"If you have funds on your addresses, you must know how to recreate your taproot address, or you lose your money.\n\n"
								"Are you sure you want to delete this container?"))
	
			if(answer==False):
				return
		
		super().remove_container(False)
		try:
			del config.gl_gui_build_address.taproot_container.utxoList[:]
		except:
			pass
		config.gl_gui_build_address.taproot_container=None
		config.gl_gui.button_checkBalance.place_forget()
		config.gl_gui_key.init_page_1()

		config.gl_gui_transaction_tab.label_selected.config(text="Selected Coins: 0 BTC")
		for child in config.gl_gui_transaction_tab.scrollable_frame_utxo.winfo_children():
			child.destroy()
		

	def update_index(self):
		
		txt=str(config.gl_current_child_index)+": "+str(shortenHexString(str(self.TapRootAddress[config.gl_current_child_index]),14,11))
		self.label_label1.config(text=txt)

	def get_index_of_address(self,address):

		for i in range(0,len(self.TapRootAddress)):
			if(address==self.TapRootAddress[i]):
				return i
		return None
