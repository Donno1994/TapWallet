import copy
import tkinter as tk
from tkinter import ttk
import global_ 
import bitcoinlib
import test_framework
import container
import console
import taproot
import blockchain
from helperFunctions import *
from musig1 import c_MultiSig

var=0
def make_lambda(a):
	return lambda event:global_.gl_gui_build_address.count_up(a)

class class_gui():
	#Graphical User Interface - Main
	#initiate the outer window and definde window size

	def __init__(self):
		self.root = tk.Tk()
		self.root.title("TapRoot Wallet by https://twitter.com/BR_Robin . Only testnet recommended")
		self.root.geometry("600x400")

		global_.gl_gui=self
		

		self.guix=1470
		self.guiy=900

		self.guix=1470
		self.guiy=900

		self.root.geometry("1470x900")
		self.window_main_gui= tk.LabelFrame(self.root)
		self.window_main_gui.pack()
		self.window_main_gui.place(x=5,y=5,height=self.guiy-10,width=self.guix-10)

		tab_control=ttk.Notebook(self.window_main_gui)


		self.tab_key=tk.Frame(tab_control)#Create Keys tab
		self.tab_address=tk.Frame(tab_control)#Create Address tab
		self.tab_transaction=tk.Frame(tab_control)#Create Transaction tab

		tab_control.add(self.tab_key, text='Create Keys and Addresses')
		tab_control.add(self.tab_address, text='See Addresses')
		tab_control.add(self.tab_transaction, text='Create Transaction')
		tab_control.pack(expand=1, fill="both")

		#init different classes for the window tabs
		global_.gl_gui_key=gui_key_tab(self.tab_key)
		global_.gl_gui_address_tab=gui_address_tab(self.tab_address)
		global_.gl_gui_build_address=gui_build_address_canvas()
		global_.gl_gui_transaction_tab=gui_transaction_tab(self.tab_transaction)

		blockchain.startThread(blockchain.initService)#calls function in background, this establishes communication with blockchain providers

class gui_key_tab:
	#window tab 'Create Keys and Addresses'
	#here we create/import all keys that will be needed for the taproot address

	def __init__(self,tab_key_creation):
		global_.gl_gui
		self.root=tab_key_creation
		self.var_is_mine=tk.IntVar(value=True)
		
		self.ext_key=None
		self.priv_key=[]
		self.pub_key=[]

		self.init_page_1()


	def init_page_1(self):
		#First window that is shown on wallet startup

		self.del_old_vars()
		try:self.page_new_seed.place_forget()
		except:pass
		try:self.page_new_extended.place_forget()
		except:pass
		try:self.page_single_key.place_forget()
		except:pass

		self.page_1= tk.LabelFrame(self.root)
		self.page_1.pack()
		self.page_1.place(x=5,y=5,height=400,width=600)

		info_text=("You have to create keys for your taproot address\n"
					"You can create or import a seed phrase (mnemonic phrase), extended keys (xpubs) or single keys\n"
					"")
		label_info = tk.Label(self.page_1, justify=tk.LEFT,text=info_text);
		label_info.pack()
		label_info.place(x=4,y=10)

		self.radio_key=tk.IntVar(value=1)
		radio_new_seed=tk.Radiobutton(self.page_1,text="Create or import mnemonic seed",variable=self.radio_key,value=1)
		radio_new_seed.pack()
		radio_new_seed.place(x=5,y=60)

		radio_extended_key=tk.Radiobutton(self.page_1,text="Import an extended master key (xpub)",variable=self.radio_key,value=2)
		radio_extended_key.pack()
		radio_extended_key.place(x=5,y=85)
		#radio_extended_key.configure(state = tk.DISABLED)#Not yet implemented

		radio_single_key=tk.Radiobutton(self.page_1,text="Create or import a single private or public key",variable=self.radio_key,value=3)
		radio_single_key.pack()
		radio_single_key.place(x=5,y=110)

		#radio_single_key=tk.Radiobutton(self.page_1,text="Import a single public key (usually a key of someone else)",variable=self.radio_key,value=5)
		#radio_single_key.pack()
		#radio_single_key.place(x=5,y=160)

		self.button_continue=tk.Button(self.page_1,text="Next",command=self.show_page_2)
		self.button_continue.pack()
		self.button_continue.place(x=5,y=185)

	def show_page_2(self):
		#Init second window page depending on radio button state

		radio_var=self.radio_key.get()

		if(radio_var==1):self.show_seed_generation();
		if(radio_var==2):self.show_extended_generation();
		if(radio_var==3):self.show_single_priv();

	def show_seed_generation(self):
		#Init window that lets you enter or create a mnemonic seed
		#It is not yet possible to add a passphrase

		self.page_1.place_forget()
		
		self.page_new_seed= tk.LabelFrame(self.root)
		self.page_new_seed.pack()
		self.page_new_seed.place(x=5,y=5,height=400,width=850)

		seed_words=""

		text_label=tk.Label(self.page_new_seed,text="Enter a short label:");text_label.pack();text_label.place(x=5,y=5)
		self.entry_Label=tk.Entry(self.page_new_seed);self.entry_Label.pack();self.entry_Label.place(height=20, x=120, y=5);

		stringvar = tk.StringVar()
		stringvar.set("")

		stringvar2 = tk.StringVar()
		stringvar2.set("")

		stringvar3 = tk.StringVar()
		stringvar3.set("")

		stringvar4 = tk.StringVar()
		stringvar4.set("")

		text_seed=tk.Label(self.page_new_seed,text="BIP 32 Seed: Create a new random seed, or enter your own 12 word seed");text_seed.pack();text_seed.place(x=5,y=40)
		self.entry_seed = tk.Entry(self.page_new_seed,textvariable=stringvar,fg="black",bg="white",bd=0)
		self.entry_seed.pack()
		self.entry_seed.place(x=5,y=60,width=550,height=25)
		self.entry_seed.bind("<KeyRelease>", self.read_user_seed)

		button_random_seed=tk.Button(self.page_new_seed,text="Create random seed",command=self.create_random_seed)
		button_random_seed.pack()
		button_random_seed.place(x=570,y=60)

		self.text_seed_error=tk.Label(self.page_new_seed,text="error",fg="#FF0000");self.text_seed_error.pack();self.text_seed_error.place(x=140,y=90)

		text_root_key=tk.Label(self.page_new_seed,text="BIP32 root key");text_root_key.pack();text_root_key.place(x=5,y=100)
		self.entry_root_key=tk.Entry(self.page_new_seed,textvariable=stringvar2,fg="black",bg="white",bd=0,state="readonly")
		self.entry_root_key.pack()
		self.entry_root_key.place(x=5,y=120,width=780)
		

		text_xpub=tk.Label(self.page_new_seed,text="Extended Priv Key (m/86'/0'/0')");text_xpub.pack();text_xpub.place(x=5,y=160)
		self.entry_extended_priv=tk.Entry(self.page_new_seed,textvariable=stringvar3,fg="black",bg="white",bd=0,state="readonly")
		self.entry_extended_priv.pack()
		self.entry_extended_priv.place(x=5,y=180,width=780)
		self.entry_extended_pub=tk.Entry(self.page_new_seed,textvariable=stringvar4,fg="black",bg="white",bd=0,state="readonly")
		self.entry_extended_pub.pack()
		self.entry_extended_pub.place(x=5,y=200,width=780)
		#network earn direct noodle course into purity stick alcohol screen update choose

		
			
		text_key_pairs=tk.Label(self.page_new_seed,text="First public keys  (x-only pubkey, first byte is dropped)");text_key_pairs.pack();text_key_pairs.place(x=5,y=240)
		self.text_pub_1=tk.Label(self.page_new_seed,text="m/86'/0'/0'/0/0: ");self.text_pub_1.pack();self.text_pub_1.place(x=5,y=260)
		self.text_pub_2=tk.Label(self.page_new_seed,text="m/86'/0'/0'/0/1: ");self.text_pub_2.pack();self.text_pub_2.place(x=5,y=280)
		self.text_pub_3=tk.Label(self.page_new_seed,text="m/86'/0'/0'/0/2: ");self.text_pub_3.pack();self.text_pub_3.place(x=5,y=300)

		button_back=tk.Button(self.page_new_seed,text="Back",command=self.init_page_1)
		button_back.pack()
		button_back.place(x=5,y=330)

		self.button_continue=tk.Button(self.page_new_seed,text="Add extended key to key pool",command=self.add_pubkey_container)
		self.button_continue.pack()
		self.button_continue.place(x=105,y=330)

		self.read_user_seed(None)

	def create_random_seed(self):
		#Creates a random 128 bit mnemonic phrase

		seed_words = bitcoinlib.mnemonic.Mnemonic('english').generate(128)
		self.enter_seed_details(seed_words)

	def read_user_seed(self,event):
		#When the user is typing a seed, this function will check if it valid after each input

		seed_words=self.entry_seed.get()
		if(len(seed_words)==0):
			self.text_seed_error.configure(text="")
			return

		try:
			root_key=bitcoinlib.keys.HDKey().from_passphrase(seed_words)
			self.enter_seed_details(seed_words)
			
		except Exception as e:
			#If the typed input is not a valid seed, display the error
			self.text_seed_error.configure(text=str(e))
			self.enter_seed_details()
			
			

	def enter_seed_details(self,seed_words=None):
		#Use seed words to calculate and display the following data
		#	- seed
		#	- BIP32 root key
		#	- xprv and xpub (derivation path m/86'/0'/0' )
		#	- first three generated public keys (derivation path m/86'/0'/0'/0/0 - m/86'/0'/0'/0/2)

		stringvar = tk.StringVar()
		stringvar2 = tk.StringVar()
		stringvar3 = tk.StringVar()
		stringvar4 = tk.StringVar()

		if(seed_words):
			root_key=bitcoinlib.keys.HDKey().from_passphrase(seed_words)
			account_0=root_key.subkey_for_path("m/86'/0'/0'")
			self.ext_key=account_0
			#self.ext_pub=account_0.wif_public()

			stringvar.set(seed_words)
			stringvar2.set(root_key.wif(is_private=True))
			stringvar3.set(account_0.wif(is_private=True))
			stringvar4.set(account_0.wif_public())
			self.entry_seed.configure(text=stringvar)

			self.button_continue.configure(state=tk.NORMAL)
			self.text_seed_error.configure(text="")
		else:
			self.ext_key=None
			#self.ext_pub=None
			#stringvar.set("")
			stringvar2.set("")
			stringvar3.set("")
			stringvar4.set("")
			self.button_continue.configure(state=tk.DISABLED)

		#text_seed=tk.Label(self.page_new_seed,text="Write down your seed. This will not be shown again.");text_seed.pack();text_seed.place(x=5,y=40)
		text_seed=tk.Label(self.page_new_seed,text="BIP 32 Seed: Create a new random seed, or enter your own 12 or 24 word seed");text_seed.pack();text_seed.place(x=5,y=40)
		

		button_random_seed=tk.Button(self.page_new_seed,text="Create random seed",command=self.create_random_seed)
		button_random_seed.pack()
		button_random_seed.place(x=570,y=60)

		text_root_key=tk.Label(self.page_new_seed,text="BIP32 root key");text_root_key.pack();text_root_key.place(x=5,y=100)
		self.entry_root_key.configure(text=stringvar2)
		

		text_xpub=tk.Label(self.page_new_seed,text="Extended Priv Key");text_xpub.pack();text_xpub.place(x=5,y=160)
		self.entry_extended_priv.configure(text=stringvar3)
		self.entry_extended_pub.configure(text=stringvar4)


		example_keys=[]

		if(seed_words):
			for a in range(0,3):
				ck = account_0.child_private(0).child_private(a)
				child_key=test_framework.ECKey().set(bytes.fromhex(ck.private_hex))
				if(child_key.get_pubkey().get_y()%2!=0):
					child_key.negate()

				example_keys.append(child_key)
			
		text_key_pairs=tk.Label(self.page_new_seed,text="First public keys (x-only pubkey, first byte is dropped):");text_key_pairs.pack();text_key_pairs.place(x=5,y=240)
		self.text_pub_1.configure(text="m/86'/0'/0'/0/0: "+str(example_keys[0].get_pubkey())) if seed_words else self.text_pub_1.configure(text="m/86'/0'/0'/0/0:")
		self.text_pub_2.configure(text="m/86'/0'/0'/0/1: "+str(example_keys[1].get_pubkey())) if seed_words else self.text_pub_2.configure(text="m/86'/0'/0'/0/1:")
		self.text_pub_3.configure(text="m/86'/0'/0'/0/2: "+str(example_keys[2].get_pubkey())) if seed_words else self.text_pub_3.configure(text="m/86'/0'/0'/0/2:")

	def show_extended_generation(self):
		#init window that lets your import a xprv or xpub

		self.page_1.place_forget()
		
		self.page_new_extended= tk.LabelFrame(self.root)
		self.page_new_extended.pack()
		self.page_new_extended.place(x=5,y=5,height=400,width=850)
		
		text_label=tk.Label(self.page_new_extended,text="Enter a short label:");text_label.pack();text_label.place(x=5,y=5)
		self.entry_Label=tk.Entry(self.page_new_extended);self.entry_Label.pack();self.entry_Label.place(height=20, x=120, y=5);


		self.stringvar3 = tk.StringVar()
		self.stringvar3.set("Extended Priv Key: <None>")

		self.stringvar4 = tk.StringVar()
		self.stringvar4.set("Extended  Pub Key: <None>")

		
		text_extended=tk.Label(self.page_new_extended,text="Enter an extended private or public key (xprv/xpub)");text_extended.pack();text_extended.place(x=5,y=40)
		self.entry_extended = tk.Entry(self.page_new_extended,fg="black",bg="white",bd=0)
		self.entry_extended.pack()
		self.entry_extended.place(x=5,y=60,width=550,height=25)
		self.entry_extended.bind("<KeyRelease>", self.read_user_extended)

		self.text_seed_error=tk.Label(self.page_new_extended,text="error",fg="#FF0000");self.text_seed_error.pack();self.text_seed_error.place(x=140,y=90)


		#text_xpub=tk.Label(self.page_new_extended,text="Extended Priv Key");text_xpub.pack();text_xpub.place(x=5,y=160)
		self.entry_extended_priv=tk.Entry(self.page_new_extended,textvariable=self.stringvar3,fg="black",bg="white",bd=0,state="readonly")
		self.entry_extended_priv.pack()
		self.entry_extended_priv.place(x=5,y=180,width=780)
		self.entry_extended_pub=tk.Entry(self.page_new_extended,textvariable=self.stringvar4,fg="black",bg="white",bd=0,state="readonly")
		self.entry_extended_pub.pack()
		self.entry_extended_pub.place(x=5,y=200,width=780)
		#network earn direct noodle course into purity stick alcohol screen update choose

		
			
		text_key_pairs=tk.Label(self.page_new_extended,text="First public keys  (x-only pubkey, first byte is dropped)");text_key_pairs.pack();text_key_pairs.place(x=5,y=240)
		self.text_pub_1=tk.Label(self.page_new_extended,text="m/.../0/0: ");self.text_pub_1.pack();self.text_pub_1.place(x=5,y=260)
		self.text_pub_2=tk.Label(self.page_new_extended,text="m/.../0/1: ");self.text_pub_2.pack();self.text_pub_2.place(x=5,y=280)
		self.text_pub_3=tk.Label(self.page_new_extended,text="m/.../0/2: ");self.text_pub_3.pack();self.text_pub_3.place(x=5,y=300)

		button_back=tk.Button(self.page_new_extended,text="Back",command=self.init_page_1)
		button_back.pack()
		button_back.place(x=5,y=330)

		self.button_continue=tk.Button(self.page_new_extended,text="Add extended key to key pool",command=self.add_pubkey_container)
		self.button_continue.pack()
		self.button_continue.place(x=105,y=330)

		self.read_user_extended(None)

	def read_user_extended(self,event):
		#when typing into the edit field, this function is called after input and checks if it is a valid xprv/xpub
		#if it is valid, it displays the derived keys
		#otherwise it displays an error

		extended_key=self.entry_extended.get()
		
		try:
			hd_key=bitcoinlib.keys.HDKey().from_wif(extended_key)
			self.enter_extended_details(hd_key=hd_key)
			
		except Exception as e:
			self.text_seed_error.configure(text=str(e)) if len(extended_key)>0 else self.text_seed_error.configure(text="")
				
			self.enter_extended_details(hd_key=None)

	def enter_extended_details(self,hd_key=None):
		#fill in all the derived data
		#	- xprv/xpub
		#	- first three derived public keys
		
		if(hd_key):
			
			self.ext_key=hd_key

			self.stringvar3.set("Extended Priv Key: "+hd_key.wif(is_private=True)) if hd_key.secret else self.stringvar3.set("Extended Priv Key: <None>")
			self.stringvar4.set("Extended  Pub Key: "+hd_key.wif_public())

			self.button_continue.configure(state=tk.NORMAL)
			self.text_seed_error.configure(text="")
		else:
			self.stringvar3.set("Extended Priv Key: <None>")
			self.stringvar4.set("Extended  Pub Key: <None>")
			self.button_continue.configure(state=tk.DISABLED)


		example_keys=[]

		if(hd_key):
			for a in range(0,3):
				ck = hd_key.child_public(0).child_public(a)
				child_key=test_framework.ECPubKey().set(bytes.fromhex(ck.public_hex))

				example_keys.append(child_key)
			
		text_key_pairs=tk.Label(self.page_new_extended,text="First public keys (x-only pubkey, first byte is dropped):");text_key_pairs.pack();text_key_pairs.place(x=5,y=240)
		self.text_pub_1.configure(text="m/.../0/0: "+str(example_keys[0])) if hd_key else self.text_pub_1.configure(text="m/.../0/0:")
		self.text_pub_2.configure(text="m/.../0/1: "+str(example_keys[1])) if hd_key else self.text_pub_2.configure(text="m/.../0/1:")
		self.text_pub_3.configure(text="m/.../0/2: "+str(example_keys[2])) if hd_key else self.text_pub_3.configure(text="m/.../0/2:")

	def show_single_priv(self):
		#init window that lets you create a single private/public key

		self.page_1.place_forget()

		self.page_single_key = tk.LabelFrame(self.root)
		self.page_single_key.pack()
		self.page_single_key.place(height=127,width=590, x=20,y=20)

		self.entropy="key"
		del self.priv_key [:]
		del self.pub_key [:]
		self.pub_key.append("0x00")
		self.typedLabel="Alice"#Give the Pubkey a label
		self.typedEntropy = tk.StringVar()#Entropy Textfield
		self.typedEntropy.set("key0")
		self.typedPrivKey = tk.StringVar()#Private Key Textfield
		self.typedPubKey = tk.StringVar()#Public Key Textfield

		##Static Key Information
		self.label_label=tk.Label(self.page_single_key,text="Label:");         self.label_label.pack();   self.label_label.place(height=20,x=4,y=2)
		self.label_entropy=tk.Label(self.page_single_key,text="Entropy:");     self.label_entropy.pack(); self.label_entropy.place(height=20,x=4,y=27)
		self.label_privKey=tk.Label(self.page_single_key,text="Private Key:"); self.label_privKey.pack(); self.label_privKey.place(height=20,x=4,y=52)
		self.label_pubKey=tk.Label(self.page_single_key,text="Public Key:");   self.label_pubKey.pack();  self.label_pubKey.place(height=20,x=4,y=77)

			

		##Editable Key Information

		self.entry_Label=tk.Entry(self.page_single_key);self.entry_Label.pack()
		self.entry_Label.place(height=20, x=100, y=2);self.entry_Label.delete(0, 'end');self.entry_Label.insert(0,self.typedLabel)

		
		self.entry_Entropy = tk.Entry(self.page_single_key,textvariable=self.typedEntropy,bg="#CCCCEE")
		self.entry_Entropy.pack();self.entry_Entropy.bind("<KeyRelease>", self.create_single_key_from_entropy);self.entry_Entropy.place(height=20, x=100, y=27)

		self.create_rnd_key=tk.Button(self.page_single_key,text="Create a random key pair",command=self.create_single_key_from_random)
		self.create_rnd_key.pack()
		self.create_rnd_key.place(height=20, x=300, y=27)
		
		self.entry_PrivKey=tk.Entry(self.page_single_key,textvariable=self.typedPrivKey,bg="#EECCCC")
		self.entry_PrivKey.pack();self.entry_PrivKey.bind("<KeyRelease>", self.create_single_key_from_priv);self.entry_PrivKey.place(height=20,width=430, x=100, y=52)

		
		self.entry_PubKey=tk.Entry(self.page_single_key,textvariable=self.typedPubKey)
		self.entry_PubKey.pack();self.entry_PubKey.bind("<KeyRelease>", self.create_single_key_from_pub);self.entry_PubKey.place(height=20,width=430, x=100, y=77)

		

		button_back=tk.Button(self.page_single_key,text="Back",command=self.init_page_1)
		button_back.pack()
		button_back.place(x=5,y=102,height=20)

		self.button=tk.Button(self.page_single_key,text="Add Key to pool",bg="#00469b",fg="#FFFFFF",command=self.add_pubkey_container)
		self.button.pack()
		self.button.place(height=20, x=200, y=102)

	def create_single_key_from_random(self):
		#create a random private/public key pair
		#entropy is deleted, since it can't be known
		
		self.del_old_vars()
		prv,pub=test_framework.generate_bip340_key_pair()
		self.priv_key.append(prv)
		self.pub_key.append(pub)
		self.entry_PrivKey.configure(fg="#000000")
		self.entry_PubKey.configure(fg="#000000")
		self.entropy=""
		self.update_text()

	def create_single_key_from_entropy(self,event=None):
		#the typed entropy is hashed and used as a private key
		#this should only be used for testing, because brain wallets are dangerous if entropy is short and not random

		if(self.typedEntropy.get()==self.entropy):
			return;
		self.del_old_vars()
		self.entropy=self.entry_Entropy.get()
		self.entry_PrivKey.configure(fg="#000000")
		self.entry_PubKey.configure(fg="#000000")
		sha=test_framework.sha256(self.entropy.encode("utf-8"))
		prv,pub=test_framework.generate_bip340_key_pair(sha)
		self.priv_key.append(prv)
		self.pub_key.append(pub)
		#self.check_is_mine.select()
		self.update_text()

	def create_single_key_from_priv(self,event=None):
		#create a public key from a private key
		#called when a key is pressed inside private key entry field
		#if the pubkey has an uneven y coordinate, the key pair is negated to conform to BIP340
		
		if(event.keycode==17):return #return when control key is released
		typedKey=self.typedPrivKey.get()
		if(typedKey==str(self.priv_key[0])):return #return when privkey has not changed
		if(len(typedKey)>64):self.entry_PrivKey.configure(fg="#ff0000");return #return if privkey has more than 64 characters

		if(len(typedKey)<64):
			for i in range(0,64-len(typedKey)):typedKey="0"+typedKey #fill privkey with zeros at the beginning if too small

		
		#else:self.entry_PrivKey.configure(fg="#000000")

		try:
			priv=bytes.fromhex(typedKey)
		except:
			self.entry_PrivKey.configure(fg="#ff0000")
			return
		else:
			self.entry_PrivKey.configure(fg="#000000")

		self.del_old_vars()
		prv,pub=test_framework.generate_bip340_key_pair(priv)
		self.priv_key.append(prv)
		self.pub_key.append(pub)
		self.entry_PubKey.configure(fg="#000000")
		self.entropy=""
		#self.check_is_mine.select()
		self.update_text(noPriv=True)
		

	def create_single_key_from_pub(self,event=None):
		#imports a public key
		#this is used to import public keys from other people that you create a taproot address with

		if(event.keycode==17):return
		typedKey=self.typedPubKey.get()
		if(len(self.pub_key)>0):
			if(str(typedKey)==str(self.pub_key[0])):
				self.entry_PubKey.configure(fg="#000000")
				return; #return when pubkey has not changed
		#del self.priv_key [:]

		if(len(typedKey)>64):self.entry_PubKey.configure(fg="#ff0000");return #return if pubkey has more than 64 characters

		if(len(typedKey)<64):self.entry_PubKey.configure(fg="#ff0000");return

		try:
			pub_bytes=bytes.fromhex(typedKey)
		except:
			self.entry_PubKey.configure(fg="#ff0000")
			return
		else:
			self.entry_PubKey.configure(fg="#000000")

		
		try:
			pubkey=test_framework.ECPubKey().set(pub_bytes)
		except:
			self.entry_PubKey.configure(fg="#ff0000");return

		if(pubkey.valid==False):self.entry_PubKey.configure(fg="#ff0000");return

		self.entropy=""
		self.del_old_vars()
		self.pub_key.append(pubkey)
		self.update_text()

	def update_text(self,noPriv=False):
		#update entropy, single private and public key after certain events

		self.label_privKey.config(text="Private Key:")
		self.label_pubKey.config(text="Public Key:")
		self.label_label.config(text="Label:")

		self.entry_Entropy.delete(0, 'end')
		self.entry_Entropy.insert(0,self.entropy)
		if(len(self.priv_key)==0):self.entry_PrivKey.delete(0, 'end')
		if(len(self.priv_key)>0 and noPriv==False):
			self.entry_PrivKey.delete(0, 'end')
			hexPriv=str(hex(self.priv_key[0].secret))[2:]
			self.entry_PrivKey.insert(0,hexPriv)
		self.entry_PubKey.delete(0, 'end')
		self.entry_PubKey.insert(0,self.pub_key)

	def del_old_vars(self):
		del self.priv_key [:]
		del self.pub_key [:]
		self.typedLabel=None
		self.ext_key=None

	def add_pubkey_container(self):
		#when a key is created (doesn't matter if from seed or single keys), you can add it to the container field
		#a container is a rectangular field, that shows some information about your Keys
		#you can drag&drop them and create scripts and multisig keys from them
		#this method is called when clicking the 'add key to pool' buttons

		if(global_.gl_gui_build_address.taproot_container):
			global_.gl_console.printText("Can't add more public keys when taproot address was already created")
			return
		
		global_.gl_gui_build_address.add_pubkey_container(self.entry_Label.get(),self.ext_key,self.priv_key,self.pub_key,[])
		self.init_page_1()

class gui_address_tab:
	#window tab 'See Addresses'
	#after generating a taproot address, your wallet creates 10 different addresses (or just 1 if no extended keys are used)
	#and shows the balance under this tab
	#you can click on an address to see how all the key containers change and display the data corresponding to this address

	def __init__(self,tab_address_creation):
		self.root=tab_address_creation

	def init_window_after_taproot_generated(self,delay=0):
		self.delay=delay
		blockchain.startThread(global_.gl_gui_address_tab.init_window_after_taproot_generated_thread)

	def init_window_after_taproot_generated_thread(self):
		
		balance_list,utxo_list=blockchain.get_utxos_from_address_list()
		
		t = self.Table(self.root,balance_list)
		global_.gl_gui_transaction_tab.update(utxo_list)
		#global_.gl_gui_build_address.taproot_container.utxoList=utxo_list

	class Table: 
		#init 10 rows to display 10 taproot addresses

		def __init__(self,root,lst): 
			total_rows=len(lst)
			total_columns=len(lst[0]) 

			for i in range(0,total_rows): 
				for j in range(total_columns):
					width=5
					readonly=True
					if(j==0):width=10
					elif(j==1):width=5
					elif(j==2):width=30
					elif(j==3):
						width=20
						if(i>0):readonly=False
					elif(j==4):width=15
				
					self.e = tk.Entry(root, width=width, fg='black',font=('Arial',8,'bold')) 
                
					self.e.grid(row=i, column=j) 
					self.e.insert(tk.END, lst[i][j])
					if(readonly):self.e.configure(state="readonly")
					if(j==2 and i>0):self.e.bind('<Button-1>', make_lambda(a=i-1))

class gui_build_address_canvas:
	#this part of the window is always shown
	#it draws the canvas on the bottom part of the window which displays all the container
	#here you create scripts, multisig keys and your taproot address

	def __init__(self):

		self.pubkey_container_array=[]
		self.script_container_array=[]
		self.hash_container_array=[]

		self.varCheckMultiSig = []
		self.taproot_container=None
		self.editLabel=tk.StringVar() #label on second window 
		

		self.container_Script = tk.LabelFrame(global_.gl_gui.root)
		self.container_Script.pack()
		self.container_Script.place(height=global_.gl_gui.guiy,width=global_.gl_gui.guix, x=5,y=400)

		
		self.canvas = tk.Canvas(self.container_Script)
		self.canvas.pack(fill=tk.BOTH, expand=1)
		global_.gl_gui.root.bind('<KeyRelease>',self.check_key_released)


		
	def count_up(self,val=None):
		global_.gl_current_child_index=val
		for container in self.pubkey_container_array:
			container.update_index()

		for container in self.script_container_array:
			container.update_index()

		for container in self.hash_container_array:
			container.update_index()

		if(self.taproot_container is not None):
			self.taproot_container.update_index()



	def calc_key_released_taproot(self,key=0):

		if(self.taproot_container):
			global_.gl_console.printText("You must delete your taproot address before creating new scripts,keys or a new address")
			return#If a Taproot address already exists, stop creating other containers

		if(key!=0):
			global_.gl_selected_container.clear()
			global_.gl_selected_container.append(key)

		root_key=None
		merkle=None

		parent_array=[]
		
		for a in range (0, len(global_.gl_selected_container)):
			parent_array.append(global_.gl_selected_container[a-1])


		
		if(len(global_.gl_selected_container)==1):#No scripts involved
			root_key=global_.gl_selected_container[0]

		else:

			for i in range (0,len(self.pubkey_container_array)):
				if self.pubkey_container_array[i]==global_.gl_selected_container[0]:
					root_key=global_.gl_selected_container[0]
					merkle=global_.gl_selected_container[1]
					break
			if(root_key==None):
				root_key=global_.gl_selected_container[1]
				merkle=global_.gl_selected_container[0]
		
		x=400
		y=300

		if(len(parent_array)==2):
			x=(parent_array[0].x_pos+parent_array[1].x_pos)/2
			y=parent_array[0].y_pos
			if(parent_array[1].y_pos>y):y=parent_array[1].y_pos
			y+=parent_array[0].sizeY+10


		self.taproot_container=container.c_Container_Taproot(x,y,root_key,merkle)
		
		global_.gl_gui_address_tab.init_window_after_taproot_generated()
		#thread_balance()
		#guiTX.selectSigningMethod()

		for a in range (0, len(global_.gl_selected_container)):
			global_.gl_selected_container[a-1].childList.append(self.taproot_container)
			global_.gl_selected_container[a-1].flag(event=None)
		

		if(key==0):self.scriptWindow.destroy()
		else: key.scriptWindow.destroy()


	def calc_key_released_multisig(self):
		#Get the selected PubKeys and create a MultiSig container

		pubkey_array=[]
		parent_array=[]
		aggregate_key=None

		is_mine=False
		has_extended_parent=False

		for i in range (0,len(global_.gl_selected_container)):
			pubkey_array.append(global_.gl_selected_container[i].pubkey)
			if(len(global_.gl_selected_container[i].pubkey)>1):
				has_extended_parent=True
		
		if(len(pubkey_array)==0):
			print("ERROR in calc_key_released_multisig. pubkey_array length 0")
		
		aggregate_key_list=[]
		for a in range(0,global_.gl_address_generation_max):
			del pubkey_array [:]
			for i in range (0,len(global_.gl_selected_container)):
				
				key=global_.gl_selected_container[i].pubkey[0] if len(global_.gl_selected_container[i].pubkey)==1 else global_.gl_selected_container[i].pubkey[a]
				pubkey_array.append(key)
				if(global_.gl_selected_container[i].is_mine):is_mine=True
				if(a==0):parent_array.append(global_.gl_selected_container[i])

			musig_c, aggregate_key=test_framework.generate_musig_key(pubkey_array)

			if(aggregate_key.get_y()%2!=0):
				aggregate_key.negate()
			aggregate_key_list.append(aggregate_key)

		child=self.add_pubkey_container(self.editLabel.get(),None,None,aggregate_key_list,parent_array,is_mine,has_extended_parent)

		for a in range (0, len(global_.gl_selected_container)):
			global_.gl_selected_container[0].childList.append(child)
			global_.gl_selected_container[0].flag(event=None)
				

		self.scriptWindow.destroy()

	def calc_key_released_tapbranch(self):
		tapbranch=[]
		hash_=[]

		con0=global_.gl_selected_container[0]
		con1=global_.gl_selected_container[1]
		
		for i in range(max(len(con0.tapLeaf),len(con1.tapLeaf))):
			tapb,h=taproot.construct_TapBranch(con0.tapLeaf[min(len(con0.tapLeaf)-1,i)],con1.tapLeaf[min(len(con1.tapLeaf)-1,i)],con0.hash_[min(len(con0.tapLeaf)-1,i)],con1.hash_[min(len(con1.tapLeaf)-1,i)])
			tapbranch.append(tapb)
			hash_.append(h)

		parent_array=[]
		parent_array.append(global_.gl_selected_container[0])
		parent_array.append(global_.gl_selected_container[1])
		is_mine=False
		if(global_.gl_selected_container[0].is_mine):is_mine=True
		if(global_.gl_selected_container[1].is_mine):is_mine=True
		#child=gui.add_hash_container(self.editLabel.get(),tapBranch,hash_,parent_array,is_mine)
		child=self.add_hash_container("TapBranch",tapbranch,hash_,parent_array,is_mine)
		global_.gl_selected_container[0].childList.append(child)
		global_.gl_selected_container[1].childList.append(child)

		for a in range (0, len(global_.gl_selected_container)):
				global_.gl_selected_container[0].flag(event=None)

		self.scriptWindow.destroy()

		
	def check_key_released(self,event):
		#When several container are flagged and "control key" is released,
		#this function will check if it needs to create a new container
		if len(global_.gl_selected_container)==0:
			return

		if (event.keycode==17):#control key released

			if(self.taproot_container):
				global_.gl_console.printText("You must delete your taproot address before creating new scripts,keys or a new address")
				for a in range (0, len(global_.gl_selected_container)):global_.gl_selected_container[0].flag(event=None)
				return#If a Taproot address already exists, stop creating other containers

			pubkey_counter=0
			hash_counter=0
			
			#this loop counts how many pubkeys and/or hashes are selected
			for a in range (0, len(global_.gl_selected_container)):
				for i in range (0,len(self.pubkey_container_array)):
					if self.pubkey_container_array[i]==global_.gl_selected_container[a]:
						pubkey_counter+=1
						break
				for i in range (0,len(self.hash_container_array)):
					if self.hash_container_array[i]==global_.gl_selected_container[a]:
						hash_counter+=1
						break
				for i in range (0,len(self.script_container_array)):
					if self.script_container_array[i]==global_.gl_selected_container[a]:
						hash_counter+=1
						break
			#Possible scenarios are 
			# 2 pubKeys are selected -> create MultiSig
			# 2 hashes are selected  -> create another hash
			# one pubkey and one hash are selected -> create Taproot
			# All other combinations will be rejected

			if hash_counter>2 or (hash_counter==2 and pubkey_counter>0) or (hash_counter>0 and pubkey_counter>1) or (hash_counter==1 and pubkey_counter!=1):
				global_.gl_console.printText(text="Choose one of the following methods:")
				global_.gl_console.printText(text="- Flag multiple pub keys to create a multisig key",keepOld=True)
				global_.gl_console.printText(text="- Flag two hashes to create a child hash",keepOld=True)
				global_.gl_console.printText(text="- Flag a pub key and a hash to create a taproot address",keepOld=True)
				global_.gl_console.printText(text="- Flag a pub key to create a taproot address",keepOld=True)
				for a in range (0, len(global_.gl_selected_container)):global_.gl_selected_container[0].flag(event=None)
				return

			if pubkey_counter>1:
				for container in global_.gl_selected_container:
					if (len(container.parent_array)>0):
						global_.gl_console.printText(text="A MultiSig key can't be part of another MultiSig key")
						for a in range (0, len(global_.gl_selected_container)):global_.gl_selected_container[0].flag(event=None)
						return

			if len(global_.gl_selected_container)==0:#return if nothing is selected
				return

			#init Pop Up Window
			self.scriptWindow = tk.Toplevel(global_.gl_gui.root)
			self.scriptWindow.geometry("600x400")

			labelLabel=tk.Label(self.scriptWindow,text="Add a label")
			labelLabel.pack()
			labelLabel.place(x=5,y=5)
		
			self.editLabel=tk.Entry(self.scriptWindow)
			self.editLabel.pack()
			self.editLabel.place(height=15,width=150,x=160,y=5)

			if (pubkey_counter==1 and hash_counter==1)or pubkey_counter==1:
				self.scriptWindow.title("Create Taproot Address")
				self.editLabel.destroy()
				self.scriptWindow.geometry("400x120")
				labelLabel.place(height=50,width=400,anchor="nw")
				labelLabel.config(text="You are going to create a Taproot Address now.                         \n"+
								       "All public keys, scripts and hashes which are not part of the address  \n"+
								       "will be removed to make clear what is part of the address and what not.")
				buttonScript=tk.Button(self.scriptWindow,text="Create TapRoot", command=self.calc_key_released_taproot,bg="#47C718")

				
			elif pubkey_counter>1 and hash_counter==0:
				

				self.scriptWindow.title("Create MultiSig Address")
				self.editLabel.insert(0,"MultiSig")
				buttonScript=tk.Button(self.scriptWindow,text="Create MultiSig", command=self.calc_key_released_multisig)
			elif pubkey_counter==0 and hash_counter==2:
				self.calc_key_released_tapbranch()
				return
				#self.scriptWindow.title("Create Tapbranch")
				#self.editLabel.insert(0,"TapBranch")
				#buttonScript=tk.Button(self.scriptWindow,text="Create TapBranch", command=self.calc_key_released_tapbranch)
			else: return

			buttonScript.pack()
			buttonScript.place(height=15,width=100,x=5,y=65)

	def add_pubkey_container(self,label,ext_key=None,privKey=None,pubKey=None,parent_array=[],is_mine=None,has_extended_parent=False):
		pubkey_copy=copy.deepcopy(pubKey)
		privkey_copy=copy.deepcopy(privKey)
		x=None
		y=None

		#if(isinstance(privKey,bitcoinlib.keys.Key)):has_extended_parent=True

		if(len(parent_array)==2):
			x=(parent_array[0].x_pos+parent_array[1].x_pos)/2
			y=parent_array[0].y_pos
			if(parent_array[1].y_pos>y):y=parent_array[1].y_pos
			y+=parent_array[0].sizeY+10

		if(y==None):y=20
		pubContainer=container.c_Container_PubKey(x,y,ext_key,privkey_copy,pubkey_copy,label,parent_array,is_mine,has_extended_parent)
		self.pubkey_container_array.append(pubContainer)
		return pubContainer

	def removeKeyContainer(self,container):
		for i in range (0,len(self.pubkey_container_array)):
			if self.pubkey_container_array[i]==container:
				self.pubkey_container_array.remove(container)
				break

		for i in range (0,len(self.script_container_array)):
			if self.script_container_array[i]==container:
				self.script_container_array.remove(container)
				break

		for i in range (0,len(self.hash_container_array)):
			if self.hash_container_array[i]==container:
				self.hash_container_array.remove(container)
				break
		
	def add_tapleaf_container(self,label,tapLeaf,timelockDelay,timelock,hash_,parent_array,x,is_mine=False,has_extended_parent=False):
		container_=container.c_Container_Script(label,tapLeaf,hash_,timelockDelay,timelock,parent_array,is_mine,has_extended_parent)
		#add_hash_container()
		parent=[]
		parent.append(container_)
		#container2=c_Container_Hash(container_.x_pos,container_.y_pos+container_.sizeY,label,tapLeaf,hash_,parent,is_mine)
		#self.hash_container_array.append(container2)
		self.script_container_array.append(container_)
		return container_#,container2
	
	def remove_script_container(self,container):
		self.script_container_array.remove(container)
	
	def add_hash_container(self,label,tapBranch,hash_,parent_array,is_mine=False):
		x=None
		y=None

		if(len(parent_array)==2):
			x=(parent_array[0].x_pos+parent_array[1].x_pos)/2
			y=parent_array[0].y_pos
			if(parent_array[1].y_pos>y):y=parent_array[1].y_pos
			y+=parent_array[0].sizeY+10

		if(y==None):y=200

		container_=container.c_Container_Hash(x,y,label,tapBranch,hash_,parent_array,is_mine)
		self.hash_container_array.append(container_)
		return container_







class gui_transaction_tab:
	def __init__(self,master,script=None,privKey=None,pubKey=None,timelockDelay=0):
		self.root=master
		self.script=script
		self.privkey=privKey
		self.pubkey=pubKey
		self.timelockDelay=timelockDelay

		

		self.segwitaddressDisplay =tk.StringVar()
		self.segwitaddressDisplay.set("Address: Please create a taproot address first")
		displayAddress=tk.Entry(self.root,textvariable=self.segwitaddressDisplay,fg="black",bg="white",bd=0,state="readonly")
		displayAddress.pack()
		displayAddress.place(width=450,anchor="nw")


		self.containerChooseUTXO = tk.LabelFrame(self.root)
		self.containerChooseUTXO.pack()
		self.containerChooseUTXO.place(height=155,width=600, x=5,y=30)

		
		button_checkBalance=tk.Button(self.containerChooseUTXO,text="Check Balance",bg="#00469b",fg="#FFFFFF",command=global_.gl_gui_address_tab.init_window_after_taproot_generated)
		button_checkBalance.pack()
		button_checkBalance.place(height=20, x=10, y=10)

		self.label_balance=tk.Label(self.containerChooseUTXO,text="Balance:---")
		self.label_balance.pack();
		self.label_balance.place(x=110,y=10)

		

		self.label_selected=tk.Label(self.containerChooseUTXO,text="Selected Coins:---")
		self.label_selected.pack();
		self.label_selected.place(x=350,y=10)

		#ScrollFrame
		container = tk.Frame(self.containerChooseUTXO)
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

		self.typedLabel =tk.StringVar()#Entropy Textfield

		self.typedAddress=tk.StringVar()#Address we want to send funds to
		self.typedAddress.set("")
		self.typedAmount =tk.StringVar()#Private Key Textfield
		self.typedAmount.set("")
		self.typedFee =tk.StringVar()#Public Key Textfield
		self.typedChange =tk.StringVar()#Public Key Textfield


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

		self.entry_Change=tk.Entry(self.containerCreateTX,textvariable=self.typedChange,state=tk.DISABLED)
		self.entry_Change.pack();self.entry_Change.place(height=20,width=100, x=70, y=77)
		
		



		self.button=tk.Button(self.containerCreateTX,text="Create Transaction",bg="#00469b",fg="#FFFFFF",command=self.createTX, state=tk.DISABLED)
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
		if(global_.gl_gui_build_address.taproot_container is None):self.button["state"]=tk.DISABLED;ret=True
		if(self.selected_balance<=0):self.button["state"]=tk.DISABLED;ret=True
		if(taproot.address_to_scriptPubKey(self.typedAddress.get()) is None):
			self.button["state"]=tk.DISABLED;
			ret=True
			self.entry_Address.configure(fg="#ff0000")
		else:
			self.entry_Address.configure(fg="#000000")
		
		if(len(self.typedAmount.get()) ==0):self.button["state"]=tk.DISABLED;ret=True
		
		try:
			amt=(float)(self.typedAmount.get())
		except:
			self.entry_Amount.configure(fg="#ff0000")
			self.button["state"]=tk.DISABLED;return
		else:self.entry_Amount.configure(fg="#000000")

		try:
			fee=(float)(self.typedFee.get())
		except:
			self.entry_Fee.configure(fg="#ff0000")
			self.button["state"]=tk.DISABLED;return
		else:self.entry_Fee.configure(fg="#000000")
		
		if(self.selected_balance-amt<=0):self.button["state"]=tk.DISABLED;return

		if(ret):return

		checked=False
		if(self.keyPathChosen):
			for i in range(0,len(self.PathValueArray)):
				if(self.PathValueArray[i][0].get()):checked=True
		else:
			for i in range(0,len(self.PathValueArray2)):
				if(self.PathValueArray2[i][0].get()):checked=True
		
		if(checked==False):self.button["state"]=tk.DISABLED;return

		self.button["state"]=tk.NORMAL
		
	def update(self,utxo_List):
		if(global_.gl_gui_build_address.taproot_container):
			self.segwitaddressDisplay.set("Address: "+str(global_.gl_gui_build_address.taproot_container.TapRootAddress[0]))
			i=0
			balance=0
			self.label_selected.config(text="Selected Coins: 0 BTC")
			for child in self.scrollable_frame.winfo_children():
				child.destroy()
			del global_.gl_gui_build_address.taproot_container.utxoList[:]

			for utxo in utxo_List:
			
				address=utxo['address']
				txId=utxo['txid']
				outputIndex=utxo['output_n']
				value=utxo['value']/100000000

				var=tk.IntVar(value=0)
				new_utxo=(var,utxo)
				
				global_.gl_gui_build_address.taproot_container.utxoList.append(new_utxo)
				
				#label_utxo=tk.Label(self.scrollable_frame,text=txId+" ["+str(outputIndex)+"]"+":"+"{:,.8f}".format(value)+" BTC");label_utxo.pack();#label_utxo.place(x=10,y=10+20*i)
				#ttk.Label(self.scrollable_frame, text="Sample scrolling label").pack()
				check_utxo=tk.Checkbutton(self.scrollable_frame, text=shortenHexString(address)+" : "+shortenHexString(txId)+" ["+str(outputIndex)+"]"+":"+"{:,.8f}".format(value)+" BTC", variable=var,command=self.updateSelected)
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
		del global_.gl_gui_build_address.taproot_container.utxoSelected[:]
		for utxo in global_.gl_gui_build_address.taproot_container.utxoList:
			if(utxo[0].get()==1):
				self.selected_balance+=utxo[1]["value"]/100000000
				global_.gl_gui_build_address.taproot_container.utxoSelected.append(utxo)
		self.label_selected.config(text="Selected Coins: "+"{:,.8f}".format(self.selected_balance)+" BTC")

		self.updateFee(event=None)
		self.checkTxReady()

	def Container_setActive(self):
		if(self.radio_keypath.get()==1):

			for i in range (0,len(global_.gl_gui_build_address.script_container_array)):
				global_.gl_gui_build_address.script_container_array[i].active=False
				global_.gl_gui_build_address.script_container_array[i].changeColor()
		else:
			for i in range (0,len(global_.gl_gui_build_address.script_container_array)):
				global_.gl_gui_build_address.script_container_array[i].active=True
				global_.gl_gui_build_address.script_container_array[i].changeColor()
	
	def selectSigningMethod(self):
		
		self.containerChooseSigningMethod = tk.LabelFrame(self.root)
		self.containerChooseSigningMethod.pack()
		self.containerChooseSigningMethod.place(height=310,width=400, x=610,y=30)

		self.keyPathChosen=True

		self.radio_spendpath=tk.IntVar()
		self.radio_scriptpath=tk.IntVar()

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
		if(global_.gl_gui_build_address.taproot_container==None):
			text="Please create a taproot address first"
			label=tk.Label(self.PathContainer,text=text);label.pack();label.place(height=20,x=4,y=2)
			return
		if(global_.gl_gui_build_address.taproot_container.internalKey.is_mine==False):
			text="You do not own a KeyPath public key."
			label=tk.Label(self.PathContainer,text=text);label.pack();label.place(height=20,x=4,y=2)
			return

		if(len(global_.gl_gui_build_address.taproot_container.internalKey.parent_array)==0):
			var=tk.IntVar(value=0)
			PathValue=[var,global_.gl_gui_build_address.taproot_container.internalKey]
			label_keys=tk.Checkbutton(self.PathContainer,text="Sign with: "+shortenHexString(str(global_.gl_gui_build_address.taproot_container.internalKey.pubkey)),variable=var,command=self.checkPathSelection)
			label_keys.pack();
			label_keys.place(height=20,x=4,y=2)
			label_keys.bind('<Button-3>',lambda x:console.copyText(str(global_.gl_gui_build_address.taproot_container.internalKey.pubkey)))
			self.PathValueArray.append(PathValue)
		
		if(len(global_.gl_gui_build_address.taproot_container.internalKey.parent_array)>0):
			text="Your Public Key is part of a multisig. You can create a signature,\nbut also need the signatures of the other keys"
			label=tk.Label(self.PathContainer,text=text);label.pack();label.place(height=45,x=4,y=2)
			
			var=tk.IntVar()
			PathValue=[var,global_.gl_gui_build_address.taproot_container.internalKey]
			self.PathValueArray.append(PathValue)

			counter=0
			for i in range(0,len(global_.gl_gui_build_address.taproot_container.internalKey.parent_array)):
				var=tk.IntVar()
				if(global_.gl_gui_build_address.taproot_container.internalKey.parent_array[i].is_mine):
					text="Sign with "+global_.gl_gui_build_address.taproot_container.internalKey.parent_array[i].label0+": "+shortenHexString(str(global_.gl_gui_build_address.taproot_container.internalKey.parent_array[i].pubkey))
					chkbutton=tk.Checkbutton(self.PathContainer,text=text,variable=var,command=self.checkPathSelection)
					chkbutton.bind('<Button-3>',make_lambda(str(global_.gl_gui_build_address.taproot_container.internalKey.parent_array[i].pubkey)))
				else:
					text="Key of "+global_.gl_gui_build_address.taproot_container.internalKey.parent_array[i].label0+": "+shortenHexString(str(global_.gl_gui_build_address.taproot_container.internalKey.parent_array[i].pubkey))
					chkbutton=tk.Checkbutton(self.PathContainer,text=text,state=tk.DISABLED)
					chkbutton.bind('<Button-3>',make_lambda(str(global_.gl_gui_build_address.taproot_container.internalKey.parent_array[i].pubkey)))
				
				PathValue=[var,global_.gl_gui_build_address.taproot_container.internalKey.parent_array[i]]
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
		if(global_.gl_gui_build_address.taproot_container==None):
			text="Please create a taproot address first"
			label=tk.Label(self.PathContainer,text=text);label.pack();label.place(height=20,x=4,y=2)
			self.checkPathSelection()
			return
		if(global_.gl_gui_build_address.taproot_container.merkleRoot==None):
			text="This address has no script path scripts."
			label=tk.Label(self.PathContainer,text=text);label.pack();label.place(height=20,x=4,y=2)
			self.checkPathSelection()
			return

		counter=0
		counterY=-5

		self.radio_scriptpath=tk.IntVar(value=0)
		for i in range(0,len(global_.gl_gui_build_address.script_container_array)):
			if(global_.gl_gui_build_address.script_container_array[i].is_mine):
				
				text="Script "+global_.gl_gui_build_address.script_container_array[i].label0#+": "+shortenHexString(str(global_.gl_gui_build_address.script_container_array[i].script.hex()))
				#text+="\nSign with pubkey: "+str(global_.gl_gui_build_address.script_container_array[i].parent_array[0].pubkey)
				
				var=tk.IntVar()
				var2=tk.IntVar(value=counter)
				PathValue1=[var,global_.gl_gui_build_address.script_container_array[i]]
				PathValue2=[var,var2,global_.gl_gui_build_address.script_container_array[i].parent_array[0]]
				radiobutton=tk.Radiobutton(self.PathContainer,text=text,variable=self.radio_scriptpath,value=counter,command=self.checkPathSelection)
				counterY+=5
				radiobutton.pack();radiobutton.place(height=40,x=4,y=counterY)
				#radiobutton.bind('<Button-3>',lambda x:console.copyText(str(global_.gl_gui_build_address.script_container_array[i].script.hex())))
				#radiobutton.bind('<Button-3>',make_lambda(str(global_.gl_gui_build_address.script_container_array[i].script.hex())))
				counterY+=27
				self.PathValueArray.append(PathValue1)

				pubkeyContainer=global_.gl_gui_build_address.script_container_array[i].parent_array[0]
				if(len(pubkeyContainer.parent_array)==0):
					text="Pubkey "+global_.gl_gui_build_address.script_container_array[i].parent_array[0].label0#+": "+shortenHexString(str(global_.gl_gui_build_address.script_container_array[i].parent_array[0].pubkey))
					chkbutton=tk.Checkbutton(self.PathContainer,text=text,variable=var,command=self.checkPathSelection)
					
					chkbutton.pack();chkbutton.place(height=40,x=14,y=counterY)
					#chkbutton.bind('<Button-3>',lambda x:console.copyText(str(global_.gl_gui_build_address.script_container_array[i].parent_array[0].pubkey)))
					#chkbutton.bind('<Button-3>',make_lambda(str(global_.gl_gui_build_address.script_container_array[i].parent_array[0].pubkey)))
					counterY+=27
					self.PathValueArray2.append(PathValue2)
					

				else:
					counter2=0
					
						
					for o in range (0,len(pubkeyContainer.parent_array)):
						if(pubkeyContainer.parent_array[o].is_mine):
							var=tk.IntVar()
							PathValue2=[var,var2,pubkeyContainer.parent_array[o]]
							text="Pubkey "+pubkeyContainer.parent_array[o].label0+": "+shortenHexString(str(pubkeyContainer.parent_array[o].pubkey))
							chkbutton=tk.Checkbutton(self.PathContainer,text=text,variable=var,command=self.checkPathSelection)
						
							chkbutton.pack();chkbutton.place(height=40,x=14,y=counterY)
							#chkbutton.bind('<Button-3>',lambda x:console.copyText(str(pubkeyContainer.parent_array[o].pubkey)))
							chkbutton.bind('<Button-3>',make_lambda(str(pubkeyContainer.parent_array[o].pubkey)))
							counterY+=27
							self.PathValueArray2.append(PathValue2)
							counter2+=1
						else:
							text="Key of "+pubkeyContainer.parent_array[o].label0+": "+shortenHexString(str(pubkeyContainer.parent_array[o].pubkey))
					
							chkbutton=tk.Checkbutton(self.PathContainer,text=text,state=tk.DISABLED)
							chkbutton.pack();chkbutton.place(height=40,x=14,y=counterY)
							#chkbutton.bind('<Button-3>',lambda x:console.copyText(str(global_.gl_gui_build_address.taproot_container.internalKey.parent_array[o].pubkey)))
							chkbutton.bind('<Button-3>',make_lambda(str(pubkeyContainer.parent_array[o].pubkey)))
							counterY+=27
							counter2+=1
				
				counter+=1
				

		if(counter==0):
			text="You don't own keys that can spend via script path'"
			label=tk.Label(self.PathContainer,text=text);label.pack();label.place(height=20,x=4,y=2)

		self.checkPathSelection()

	def setHighlightContainer(self,container):
		container.highlightContainer.place(height=15, x=14, y=2)
		container.label_label0.place_forget()
	def removeHighlightContainer(self,container):
		container.highlightContainer.place_forget()
		container.label_label0.place(height=15, x=14, y=2)

	def checkPathSelection(self):
		for i in range(0,len(global_.gl_gui_build_address.pubkey_container_array)):
			self.removeHighlightContainer(global_.gl_gui_build_address.pubkey_container_array[i])
		for i in range(0,len(global_.gl_gui_build_address.script_container_array)):
			self.removeHighlightContainer(global_.gl_gui_build_address.script_container_array[i])

		if(self.radio_spendpath.get()==1 and len(self.PathValueArray)>0):#If KeyPath radio button is selected and keypath possible
			#If first key does not have parents, it is a single interal key. Check it automatically
			if(len(self.PathValueArray[0][1].parent_array)==0):
					self.PathValueArray[0][0].set(1)
					self.setHighlightContainer(self.PathValueArray[0][1])#hightlight multisig key
			
			else:#Search for selected checkboxes and hightlight the container + MultiSig
				self.setHighlightContainer(self.PathValueArray[0][1])#hightlight multisig key
				for i in range(0,len(self.PathValueArray)):
					if(self.PathValueArray[i][0].get()==1):
						self.setHighlightContainer(self.PathValueArray[i][1])
						
			#If just one key is available, check if it is a multisig
			
			#	if(len(self.PathValueArray[0][1].parent_array)==0):
			#		self.PathValueArray[0][0].select()
			#		self.PathValueArray[0][1].highlightContainer.place(height=15, x=105, y=2,width=85)#hightlight multisig key
			#	else: 
			#for i in range(0,len(self.PathValueArray)):
			#	if(self.PathValueArray[i][0].get()==1):
			#		self.PathValueArray[i][1].highlightContainer.place(height=15, x=105, y=2,width=85)
				

		if(self.radio_spendpath.get()==2):#If ScriptPath radio button is selected
			radio=self.radio_scriptpath.get()
			if(self.radio_scriptpath.get()>=len(self.PathValueArray)):
				self.checkTxReady()
				return
			self.setHighlightContainer(self.PathValueArray[radio][1])#hightlight script container

			parent=self.PathValueArray[radio][1].parent_array[0]#get the pubkey that created the script
			if(len(parent.parent_array)==0):#if the pubkey has no parents, it can be checked
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
		self.checkTxReady()

	def updateFee(self,event):
		self.entry_Fee.delete(0, 'end')
		self.entry_Change.configure(state='normal')
		self.entry_Change.delete(0, 'end')
		try:
			amt=(float)(self.typedAmount.get())
		except:
			self.entry_Amount.configure(fg="#ff0000")
			self.button["state"]=tk.DISABLED;return False
		else:self.entry_Amount.configure(fg="#000000")

		if(amt==0):
			self.button["state"]=tk.DISABLED;self.entry_Amount.configure(fg="#ff0000");return False
		else:self.entry_Amount.configure(fg="#000000")
		
		fee=(round(self.selected_balance-amt, 8))
		
		if((float)(fee)<0):
			self.entry_Amount.configure(fg="#ff0000")
			self.button["state"]=tk.DISABLED;return False
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
			self.entry_Fee.configure(fg="#ff0000");self.button["state"]=tk.DISABLED;ret=True;
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
			self.entry_Fee.configure(fg="#ff0000");self.button["state"]=tk.DISABLED;ret=True;
			return False
		else:self.entry_Fee.configure(fg="#000000")

		#if(self.typedAmount.get().isdecimal()==False):return
		#amt=(float)(self.typedAmount.get())

		change=(round(self.selected_balance-amt-fee, 8))

		if(change<0):
			self.entry_Change.insert(0,"not enough funds")
			self.entry_Change.configure(state='disabled')
			self.entry_Fee.configure(fg="#ff0000");self.button["state"]=tk.DISABLED;ret=True;
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
				destination_list.append([global_.gl_gui_build_address.taproot_container.TapRootAddress[0],(float)(self.typedChange.get())])

		return destination_list

	def broadcastWindow(self,tx):

		publishWindow = tk.Toplevel(self.root)
		publishWindow.title("Publish Transaction")
		publishWindow.geometry("500x300")


		label=tk.Label(publishWindow,text="Raw TX:")
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
		
		

		res=global_.gl_gui_service.sendrawtransaction(rawtx=tx)
		if(res==False):
			global_.gl_console.printText(text="\nError when broadcasting tx. No response",keepOld=True)
			return

		
		#a=res['response_dict']
		if "txid" in res:
			global_.gl_console.printText(text="\nTx ID: "+res['txid'],keepOld=True)
		else: global_.gl_console.printText(text="\nError when broadcasting tx. Unknown response",keepOld=True)
		

	def createTX(self):

		if(self.keyPathChosen):
			if(len(self.PathValueArray)==1):#KeyPath Single Key

				tx=taproot.SpendTransactionViaKeyPath(global_.gl_gui_build_address.taproot_container,self.get_destinationList())
				global_.gl_console.printText(text="Signed Raw Transaction:\n"+str(tx))
				self.broadcastWindow(tx)

			if(len(self.PathValueArray)>1):#KeyPath MultiSig
				
				self.multisigContainer(multisig_key=global_.gl_gui_build_address.taproot_container.internalKey)
			return

		#ScriptPath chosen
		radio=self.radio_scriptpath.get()
		
		self.tx_scriptContainer=self.PathValueArray[radio][1]
		pubContainer=self.tx_scriptContainer.parent_array[0]
		print("pubcon")
		print(pubContainer.privkey)
		if(len(pubContainer.parent_array)==0):#If Pubkey has no parent, it is not a multisig
			privkey_list=[]
			script_list=[]
			for utxo in global_.gl_gui_build_address.taproot_container.utxoList:
				if(utxo[0].get()==1):
					address_index=global_.gl_gui_build_address.taproot_container.get_index_of_address(utxo[1]['address'])
					privkey_list.append(pubContainer.privkey[address_index])
					script_list.append(self.tx_scriptContainer.script[address_index])
			tx=taproot.SpendTransactionViaScriptPath(global_.gl_gui_build_address.taproot_container,self.get_destinationList(),privkey_list,
							script_list,self.tx_scriptContainer.timelockDelay,self.tx_scriptContainer.timelock)
			global_.gl_console.printText(text="Signed Raw Transaction:\n"+str(tx))
			self.broadcastWindow(tx)
			return

		self.multisigContainer(multisig_key=pubContainer)

		return

	def multisigContainer(self,multisig_key):
		self.tx_multisigkey=multisig_key

		tx_inputs=len(global_.gl_gui_build_address.taproot_container.utxoSelected)
		self.cMultiSig=[]
		del self.cMultiSig[:]

		for utxo in global_.gl_gui_build_address.taproot_container.utxoSelected:
			tweak_=None
			address_index=global_.gl_gui_build_address.taproot_container.get_index_of_address(utxo[1]['address'])
			if(self.keyPathChosen):tweak_=global_.gl_gui_build_address.taproot_container.tapTweak_bytes[address_index]
			
			self.cMultiSig.append(c_MultiSig(self.tx_multisigkey.pubkey[address_index],tweak=tweak_))
		

		allMine=True
		if(self.keyPathChosen):
			for i in range(1,len(self.PathValueArray)):
				if(self.PathValueArray[i][0].get()==0):
					allMine=False
		else:
			checked=[]
			for i in range(0,len(self.PathValueArray2)):
				if(self.PathValueArray2[i][0].get()):checked.append(self.PathValueArray2[i][2])
			
			for i in range(0,len(self.tx_multisigkey.parent_array)):
				key=self.tx_multisigkey.parent_array[i]
				mine=False
				for o in range(0,len(checked)):
					if(checked[o]==self.tx_multisigkey.parent_array[i]):
						#self.cMultiSig.addPrivKey(key.privkey)
						mine=True
				if(mine==False):
					allMine=False


		

		if(allMine==False):
			

			self.windowMultiSig = tk.Toplevel(self.root)
			self.windowMultiSig.title("Create MultiSig Transaction")
			self.windowMultiSig.geometry("720x470")

			tk.Label(self.windowMultiSig,text ="Create MultiSig Transaction").pack()

			self.page1=tk.LabelFrame(self.windowMultiSig)
			self.page1.pack()
			self.page1.place(height=800,width=700, x=10, y=50)

			label_noncehash=tk.Label(self.page1,text ="Share nonce hash with partner")
			label_noncehash.pack()
			label_noncehash.place(height=20, x=200, y=5)

			self.entry_NonceHash=[]

			button_next=tk.Button(self.page1,text="Next", command=self.multisig_page2)
			button_next.pack()
			button_next.place(x=600,y=30)
		
		if(self.keyPathChosen):
			if(allMine==False):
				for i in range(1,len(self.PathValueArray)):
					label=tk.Label(self.page1,text =self.PathValueArray[i][1].label0)
					label.pack()
					label.place(height=20, x=10, y=30+i*30)

					entry_Label=tk.Entry(self.page1);entry_Label.pack()
					entry_Label.place(height=20,width=450, x=100, y=30+i*30);entry_Label.delete(0, 'end');
					self.entry_NonceHash.append(entry_Label)

			for a in range(0,tx_inputs):
				utxo=global_.gl_gui_build_address.taproot_container.utxoSelected[a]
				address_index=global_.gl_gui_build_address.taproot_container.get_index_of_address(utxo[1]['address'])

				for i in range(1,len(self.PathValueArray)):
					
					
					if(self.PathValueArray[i][0].get()==1):
						
						
						if(len(self.PathValueArray[i][1].privkey)>1):
							self.cMultiSig[a].addPrivKey(self.PathValueArray[i][1].privkey[address_index])
						else:
							self.cMultiSig[a].addPrivKey(self.PathValueArray[i][1].privkey[0])
					else:
						if(len(self.PathValueArray[i][1].pubkey)>1):self.cMultiSig[a].addPubKey(self.PathValueArray[i][1].pubkey[address_index])
						else:self.cMultiSig[a].addPubKey(self.PathValueArray[i][1].pubkey[0])
					
		
					if(allMine==False):
						
						if(len(self.PathValueArray[i][1].pubkey)>1):nonce=self.cMultiSig[a].getNonce(self.PathValueArray[i][1].pubkey[address_index])
						else: nonce=self.cMultiSig[a].getNonce(self.PathValueArray[i][1].pubkey[0])
						if(nonce):self.entry_NonceHash[i-1].insert(tk.END,str(test_framework.sha256(nonce.get_pubkey().get_bytes()).hex()))
						elif(a==0):self.entry_NonceHash[i-1].insert(tk.END,"Enter nonce hash of your partner")
			
				#if(allMine==False):self.entry_NonceHash.append(entry_Label_list[i-1])
		else:
			checked=[]
			for i in range(0,len(self.PathValueArray2)):
				if(self.PathValueArray2[i][0].get()):checked.append(self.PathValueArray2[i][2])
			
			for i in range(0,len(self.tx_multisigkey.parent_array)):
				key=self.tx_multisigkey.parent_array[i]

				mine=False
				for o in range(0,len(checked)):
					if(checked[o]==key):
						for a in range(0,tx_inputs):
							if(len(key.privkey)>1):
								address_index=global_.gl_gui_build_address.taproot_container.get_index_of_address(global_.gl_gui_build_address.taproot_container.utxoSelected[a][1]['address'])
								self.cMultiSig[a].addPrivKey(key.privkey[address_index])
							else: self.cMultiSig[a].addPrivKey(key.privkey[0])
						mine=True
				if(mine==False):
					for a in range(0,tx_inputs):
						
						if(len(key.pubkey)>1):
							address_index=global_.gl_gui_build_address.taproot_container.get_index_of_address(global_.gl_gui_build_address.taproot_container.utxoSelected[a][1]['address'])
							self.cMultiSig[a].addPubKey(key.pubkey[address_index])
						else: self.cMultiSig[a].addPubKey(key.pubkey[0])

				if(allMine==False):
					label=tk.Label(self.page1,text =key.label0)
					label.pack()
					label.place(height=20, x=10, y=30+i*30)

					entry_Label=tk.Entry(self.page1);entry_Label.pack()
					entry_Label.place(height=20,width=450, x=100, y=30+i*30);entry_Label.delete(0, 'end');
					for a in range(0,tx_inputs):
						if(len(key.pubkey)>1):
							address_index=global_.gl_gui_build_address.taproot_container.get_index_of_address(global_.gl_gui_build_address.taproot_container.utxoSelected[a][1]['address'])
							nonce=self.cMultiSig[a].getNonce(key.pubkey[address_index])
						else: nonce=self.cMultiSig[a].getNonce(key.pubkey[0])
						if(nonce):entry_Label.insert(tk.END,str(test_framework.sha256(nonce.get_pubkey().get_bytes()).hex()))
						else:
							entry_Label.insert(tk.END,"Enter nonce hash of your partner")
							break
					self.entry_NonceHash.append(entry_Label)
				
		
		if(allMine):
			priv_list=[]
			for a in range(0,tx_inputs):
				self.cMultiSig[a].genAggregateNonce()
				self.cMultiSig[a].genAggregatePubkey()
				
			if(self.keyPathChosen):
				for a in range(0,tx_inputs):
					priv_list.append(self.cMultiSig[a].getTweakedPrivateKey())
				global_.gl_gui_build_address.taproot_container.tweaked_privkey=priv_list
				tx=taproot.SpendTransactionViaKeyPath(global_.gl_gui_build_address.taproot_container,self.get_destinationList(),address_index_from_short_list=True)
				global_.gl_console.printText(text="Signed Raw Transaction:\n"+str(tx))
				self.broadcastWindow(tx)
			else:
				for a in range(0,tx_inputs):
					priv_list.append(self.cMultiSig[a].getInternalPrivateKey())
				script_list=[]
				for utxo in global_.gl_gui_build_address.taproot_container.utxoList:
					if(utxo[0].get()==1):
						address_index=global_.gl_gui_build_address.taproot_container.get_index_of_address(utxo[1]['address'])
						script_list.append(self.tx_scriptContainer.script[address_index])
				tx=taproot.SpendTransactionViaScriptPath(global_.gl_gui_build_address.taproot_container,self.get_destinationList(),priv_list,
							script_list,self.tx_scriptContainer.timelockDelay,self.tx_scriptContainer.timelock)
				global_.gl_console.printText(text="Signed Raw Transaction:\n"+str(tx))
				self.broadcastWindow(tx)
			return

		
	def multisig_page2(self):
		tx_inputs=len(global_.gl_gui_build_address.taproot_container.utxoSelected)

		for i in range(0,len(self.entry_NonceHash)):
			if(self.cMultiSig[0].getNonce(self.cMultiSig[0].keys[i][1]) is not None):
				continue


			try:int(self.entry_NonceHash[i].get(),16)
			except:
				global_.gl_console.printText("Enter all your partners nonce hashes before proceeding")
				return
			input_=self.entry_NonceHash[i].get()
			input_length=len(input_)
			if(input_length!=tx_inputs*64):
				global_.gl_console.printText("You must insert "+str(tx_inputs)+" hashes of 64 hex chars each without spaces")
				return

			for a in range(tx_inputs):
				input_a=input_[:64]
				input_=input_[64:]
				self.cMultiSig[a].addNonceHash(i,bytes.fromhex(input_a))
				

		self.page1.place_forget()

		self.page2=tk.LabelFrame(self.windowMultiSig)
		self.page2.pack()
		self.page2.place(height=800,width=700, x=10, y=50)

		label_nonce=tk.Label(self.page2,text ="Share nonce public key with partner")
		label_nonce.pack()
		label_nonce.place(height=20, x=200, y=5)

		self.entry_NoncePub=[]

		

		for i in range(0,len(self.cMultiSig[0].keys)):
			label=None
			if(self.keyPathChosen):label=tk.Label(self.page2,text =self.PathValueArray[i+1][1].label0)
			else:
				for o in range(0,len(self.tx_multisigkey.parent_array)):
					for a in range(tx_inputs):
						if(len(self.tx_multisigkey.parent_array[o].pubkey)>1):
							address_index=global_.gl_gui_build_address.taproot_container.get_index_of_address(global_.gl_gui_build_address.taproot_container.utxoSelected[a][1]['address'])
						else: address_index=0
						if(self.tx_multisigkey.parent_array[o].pubkey[address_index]==self.cMultiSig[a].keys[i][1]):
							label=tk.Label(self.page2,text =self.tx_multisigkey.parent_array[o].label0)
			if(label is None):
				print("ERROR IN multisig_page2. LABEL IS NONE")
			label.pack()
			label.place(height=20, x=10, y=30+i*30)

			entry_Label=tk.Entry(self.page2);entry_Label.pack()
			entry_Label.place(height=20,width=450, x=100, y=30+i*30);entry_Label.delete(0, 'end');

			nonce=self.cMultiSig[0].getNonce(self.cMultiSig[0].keys[i][1])
			if(nonce):
				entry_Label.insert(tk.END,str(nonce.get_pubkey()))
				for a in range(1,tx_inputs):
					nonce=self.cMultiSig[a].getNonce(self.cMultiSig[a].keys[i][1])
					entry_Label.insert(tk.END,str(nonce.get_pubkey()))
			else:entry_Label.insert(tk.END,"Enter nonce public keys of your partner")
			
				
				

			self.entry_NoncePub.append(entry_Label)

		button_next=tk.Button(self.page2,text="Next", command=self.button3)
		button_next.pack()
		button_next.place(x=600,y=30)

	def button3(self):
		self.multisig_page3(1)
	#hash cbf76bb7c511d3135e180d66a6a2d5e9d00a33e313fdf78465a675ff05c31f6d
	 #    19aae63e2ab99af3dccc80cd5d3d59ee6d37694971c9ac42c81c57586b8492fc

	#Alice hash	
	#	 9d4fd5c8826b822b2b5cf69cc5581cef136c4ec2baaba8a0be18080492848a0e
	#	 c0e8238c6e141f408d7cab6a397d25dec8b0dd513b7dee010386365fee9c9cb0
	     
	def multisig_page3(self,value):
		tx_inputs=len(global_.gl_gui_build_address.taproot_container.utxoSelected)
		
		for i in range(0,len(self.entry_NoncePub)):
			try:int(self.entry_NoncePub[i].get(),16)
			except:
				global_.gl_console.printText("Enter all your partners nonce pubkeys before proceeding")
				return

		if(value==1):self.page2.place_forget()
		else:self.page3.destroy()
		
		for i in range(0,len(self.entry_NoncePub)):
			input_=self.entry_NoncePub[i].get()

			if(len(input_)!=tx_inputs*64):
				global_.gl_console.printText("You must insert "+str(tx_inputs)+" hashes of 64 hex chars each without spaces")
				return

			for a in range(tx_inputs):
				if(self.cMultiSig[a].getNonce(self.cMultiSig[a].keys[i][1])is None):
					val=self.cMultiSig[a].addNoncePub(i,bytes.fromhex(input_[a*64:(a+1)*64]))
					if(val==1):
						pass
					elif (val==2):
						global_.gl_console.printText("ERROR: "+str(input_[a*64:(a+1)*64])+" is no valid nonce")
						self.windowMultiSig.destroy()
						return
					elif (val==3):
						global_.gl_console.printText("ERROR: Hash of "+str(input_[a*64:(a+1)*64])+" does not match the hash you entered earlier")
						self.windowMultiSig.destroy()
						return

		

		self.page3=tk.LabelFrame(self.windowMultiSig)
		self.page3.pack()
		self.page3.place(height=800,width=700, x=10, y=50)

		label_nonce=tk.Label(self.page3,text ="Share partial signature with your partners")
		label_nonce.pack()
		label_nonce.place(height=20, x=200, y=5)

		for a in range(tx_inputs):
			self.cMultiSig[a].genAggregateNonce()
			self.cMultiSig[a].genAggregatePubkey()
		
		if(self.keyPathChosen):self.spending_tx,input_tx=taproot.createUnsignedTX(global_.gl_gui_build_address.taproot_container,self.get_destinationList())
		else: self.spending_tx,input_tx=taproot.createUnsignedTX(global_.gl_gui_build_address.taproot_container,self.get_destinationList(),self.tx_scriptContainer.timelockDelay,self.tx_scriptContainer.timelock)


		if(value==2):del self.signature_pool[:]
		self.signature_pool=[]
		self.signature_entry=[]
		self.sighash_list=None
		#self.witness_elements=None
		allsSigsAvailable=True
		for i in range(0,len(self.cMultiSig[0].keys)+1):
			if(i==len(self.cMultiSig[0].keys)):
				if(self.keyPathChosen):
					signature_list=[]
					for a in range(tx_inputs):
						sig,self.sighash_list=taproot.signMultiSig(global_.gl_gui_build_address.taproot_container,self.spending_tx,input_tx,self.cMultiSig[a],-1,input_tx_counter=a)
						signature_list.append(sig)
					self.signature_pool.append(signature_list)

			elif (self.cMultiSig[0].keys[i][0] is None):
				allsSigsAvailable=False
				signature_list=None
			else:
					signature_list=[]
					for a in range(tx_inputs):
						if(self.keyPathChosen):sig,self.sighash_list=taproot.signMultiSig(global_.gl_gui_build_address.taproot_container,self.spending_tx,input_tx,self.cMultiSig[a],i,input_tx_counter=a)
						else:
							if(len(self.tx_scriptContainer.script)>1):
								address_index=global_.gl_gui_build_address.taproot_container.get_index_of_address(global_.gl_gui_build_address.taproot_container.utxoSelected[a][1]['address'])
							else:address_index=0
							sig,self.sighash_list=taproot.signMultiSig(global_.gl_gui_build_address.taproot_container,self.spending_tx,input_tx,self.cMultiSig[a],i,self.tx_scriptContainer.script[address_index],input_tx_counter=a)
						
						signature_list.append(sig)
						print("SpendingTX :_____")
						print(signature_list)

			if(i<len(self.cMultiSig[0].keys)):
				label=None
				if(self.keyPathChosen):label=tk.Label(self.page3,text =self.PathValueArray[i+1][1].label0)
				else:
					#for o in range(0,len(self.tx_multisigkey.parent_array)):
					#	if(self.tx_multisigkey.parent_array[o].pubkey==self.cMultiSig.keys[i][1]):
					label=tk.Label(self.page3,text =self.tx_multisigkey.parent_array[i].label0)
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
					entry_Label.insert(tk.END,string_)
					self.signature_pool.append(signature_list)
				else: entry_Label.insert(tk.END,"Copy signature of your partner here")

				self.signature_entry.append(entry_Label)
			

		if(allsSigsAvailable):
			

			self.combineSignatures()

		else:
			button_next=tk.Button(self.page3,text="Combine Signatures", command=self.combineSignatures)
			button_next.pack()
			button_next.place(x=100,y=30+len(self.cMultiSig[0].keys)*60)

	def combineSignatures(self):
		#tx_inputs=len(global_.gl_gui_build_address.taproot_container.utxoSelected)

		#for a in range(tx_inputs):
			for i in  range(0,len(self.cMultiSig[0].keys)):
				
				if(self.cMultiSig[0].keys[i][0]is None):
					sig=self.signature_entry[i].get("1.0",'end-1c')
					

					sig=sig.splitlines()
					for i in range(0,len(sig)):
						try:
							int(sig[i],16)
						except:
							global_.gl_console.printText("Enter all your partners signatures before proceeding")
							return
						sig[i]=int(sig[i])
					self.signature_pool.append(sig)
			
			num_utxos_spent=len(self.signature_pool[0])
			print(str(num_utxos_spent)+" UTXOs are going to be spent")

			for i in  range(0,num_utxos_spent):#length 2
				sig=[]
				for o in range(0,len(self.signature_pool)):#length 3
					sig.append(self.signature_pool[o][i])
				sig_agg = test_framework.aggregate_musig_signatures(sig, self.cMultiSig[i].nonce_agg)
			
				if(self.keyPathChosen):self.spending_tx.wit.vtxinwit.append(test_framework.CTxInWitness([sig_agg]))
				else:
					
					if(len(self.tx_scriptContainer.script)>1):
						address_index=global_.gl_gui_build_address.taproot_container.get_index_of_address(global_.gl_gui_build_address.taproot_container.utxoSelected[i][1]['address'])
					else: address_index=0
					control_map=global_.gl_gui_build_address.taproot_container.taptree[address_index][2]
					script=self.tx_scriptContainer.script[address_index]
					self.spending_tx.wit.vtxinwit.append(test_framework.CTxInWitness([sig_agg,script,control_map[script]]))


			
				print("Spending transaction New:\n{}".format(self.spending_tx))


			num=len(self.cMultiSig[0].keys)

			spending_tx_str=self.spending_tx.serialize().hex()
			rawtxs=[spending_tx_str]

			label=tk.Label(self.page3,text ="Final TX")
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

			global_.gl_console.printText(text="Signed Raw Transaction\n"+str(rawtxs[0]))

			button_sendTX=tk.Button(self.page3,text="Send Transaction", command=lambda: self.broadcastTX(rawtxs[0]),bg="#00cc44",fg="#000000")
			button_sendTX.pack()
			button_sendTX.place(x=300,y=30+num*60)
