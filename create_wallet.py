#import copy
import tkinter as tk
from tkinter import ttk
from tkinter.simpledialog import askstring

import bitcoinlib
import test_framework

import window
import config 
import blockchain
import encryption

class create_wallet_page:
	
	
	def __init__(self):
		self.root= tk.LabelFrame(config.gl_gui.root)
		self.root.pack()

		info_text=("You have to create keys for your taproot address\n"
					"You can create or import a seed phrase (mnemonic phrase), extended keys (xpubs) or single keys\n"
					"")
		label_info = tk.Label(self.root,text=info_text);
		label_info.pack()


	def load_wallet_create(self):
	
		root=config.gl_gui.root
		guix=1470
		guiy=900


		my_menu=tk.Menu(root) # for creating the menu bar
		m1=tk.Menu(my_menu,tearoff=0)
		m1.add_command(label="Save",command=encryption.save_wallet)
		

		my_menu.add_cascade(label="Wallet",menu=m1)

		m2=tk.Menu(my_menu,tearoff=0)
		m2.add_command(label="Configurations")
		my_menu.add_cascade(label="Options",menu=m2)


		root.config(menu=my_menu)

		root.geometry("1470x900")
		window_main_gui= tk.LabelFrame(root)
		window_main_gui.pack()
		window_main_gui.place(x=0,y=0,height=guiy,width=guix)

		tab_control=ttk.Notebook(window_main_gui)


		tab_key=tk.Frame(tab_control)#Create Keys tab
		tab_history=tk.Frame(tab_control)#Create History tab
		tab_address=tk.Frame(tab_control)#Create Address tab
		tab_transaction=tk.Frame(tab_control)#Create Transaction tab

		tab_control.add(tab_key, text='Create Keys and Addresses')
		tab_control.add(tab_history, text='Tx History')
		tab_control.add(tab_address, text='See Addresses')
		tab_control.add(tab_transaction, text='Create Transaction')
		tab_control.pack(expand=1, fill="both")

		config.gl_gui_key=gui_key_tab(tab_key)

		blockchain.get_blockheight_from_service()


class gui_key_tab:
	#window tab 'Create Keys and Addresses'
	#here we create/import all keys that will be needed for the taproot address

	def __init__(self,tab_key_creation):
		config.gl_gui
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

		#If a taproot address was already created, just show an info text. Otherwise show buttons to create keys.
		if(config.gl_gui_build_address is not None):
			if(config.gl_gui_build_address.taproot_container is not None):
				info_text=("You have already created a taproot address.\n"
							"If you want to add any more keys, you have to delete the green taproot container in the window below.\n\n"
							"ATTENTION:\nIf you change any of your keys, you will get a new taproot address with probably no funds.\n"
							"Be careful to not override any existing wallet with funds!")
				label_info = tk.Label(self.page_1, justify=tk.LEFT,text=info_text);
				label_info.pack()

				return

		info_text=("You have to create keys for your taproot address\n"
					"You can create or import a seed phrase (mnemonic phrase), extended keys (xpubs) or single keys\n"
					"")
		label_info = tk.Label(self.page_1,text=info_text);
		label_info.pack()

		self.radio_key=tk.IntVar(value=1)
		radio_new_seed=tk.Radiobutton(self.page_1,text="Create or import mnemonic seed  (spice report eye sick knife fork dawn other ...)",variable=self.radio_key,value=1)
		radio_new_seed.pack()

		radio_extended_key=tk.Radiobutton(self.page_1,text="Import an extended master key/ xpub  (xprv9xhWQW6gkX5JfDfLceirkZtwoPK2cZpv ...)",variable=self.radio_key,value=2)
		radio_extended_key.pack()

		radio_single_key=tk.Radiobutton(self.page_1,text="Create or import a single private or public key  (a819408ce5010ca2e09ef59ac3d89f5ff8595d02b5 ...)",variable=self.radio_key,value=3)
		radio_single_key.pack()

		self.button_continue=tk.Button(self.page_1,text="Next",bg="#0099ff",command=self.show_page_2)
		self.button_continue.pack()

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

		text_seed=tk.Label(self.page_new_seed,text="BIP 32 Seed: Create a new random seed, or enter your own 12 or 24 word seed");text_seed.pack();text_seed.place(x=5,y=40)
		self.entry_seed = tk.Entry(self.page_new_seed,textvariable=stringvar,fg="black",bg="white",bd=0)
		self.entry_seed.pack()
		self.entry_seed.place(x=5,y=60,width=550,height=25)
		self.entry_seed.bind("<KeyRelease>", self.read_user_seed)

		button_random_seed=tk.Button(self.page_new_seed,text="Create random seed",bg="#ffcc80",command=self.create_random_seed)
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

		
			
		text_key_pairs=tk.Label(self.page_new_seed,text="First public keys  (x-only pubkey, first byte is dropped)");text_key_pairs.pack();text_key_pairs.place(x=5,y=240)
		self.text_pub_1=tk.Label(self.page_new_seed,text="m/86'/0'/0'/0/0: ");self.text_pub_1.pack();self.text_pub_1.place(x=5,y=260)
		self.text_pub_2=tk.Label(self.page_new_seed,text="m/86'/0'/0'/0/1: ");self.text_pub_2.pack();self.text_pub_2.place(x=5,y=280)
		self.text_pub_3=tk.Label(self.page_new_seed,text="m/86'/0'/0'/0/2: ");self.text_pub_3.pack();self.text_pub_3.place(x=5,y=300)

		button_back=tk.Button(self.page_new_seed,text="Back",bg="#DC7A7A",command=self.init_page_1)
		button_back.pack()
		button_back.place(x=5,y=330)

		self.button_continue=tk.Button(self.page_new_seed,text="Add extended key to key pool",bg="#0099FF",state=tk.DISABLED,command=self.add_pubkey_container)
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
			stringvar2.set("")
			stringvar3.set("")
			stringvar4.set("")
			self.button_continue.configure(state=tk.DISABLED)

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

		button_back=tk.Button(self.page_new_extended,text="Back",bg="#DC7A7A",command=self.init_page_1)
		button_back.pack()
		button_back.place(x=5,y=330)

		self.button_continue=tk.Button(self.page_new_extended,text="Add extended key to key pool",bg="#0099FF",command=self.add_pubkey_container)
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
		self.page_single_key.place(height=200,width=590, x=20,y=20)

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
		self.label_privKey=tk.Label(self.page_single_key,text="Private Key (hex only):"); self.label_privKey.pack(); self.label_privKey.place(height=20,x=4,y=52)
		self.label_pubKey=tk.Label(self.page_single_key,text="Public Key (hex only):");   self.label_pubKey.pack();  self.label_pubKey.place(height=20,x=4,y=77)

			

		##Editable Key Information

		self.entry_Label=tk.Entry(self.page_single_key);self.entry_Label.pack()
		self.entry_Label.place(height=20, x=130, y=2);self.entry_Label.delete(0, 'end');self.entry_Label.insert(0,self.typedLabel)

		
		self.entry_Entropy = tk.Entry(self.page_single_key,textvariable=self.typedEntropy,bg="#CCCCEE")
		self.entry_Entropy.pack();self.entry_Entropy.bind("<KeyRelease>", self.create_single_key_from_entropy);self.entry_Entropy.place(height=20, x=130, y=27)

		self.create_rnd_key=tk.Button(self.page_single_key,text="Create a random key pair",bg="#ffcc80",command=self.create_single_key_from_random)
		self.create_rnd_key.pack()
		self.create_rnd_key.place(height=20, x=300, y=27)
		
		self.entry_PrivKey=tk.Entry(self.page_single_key,textvariable=self.typedPrivKey,bg="#EECCCC")
		self.entry_PrivKey.pack();self.entry_PrivKey.bind("<KeyRelease>", self.create_single_key_from_priv);self.entry_PrivKey.place(height=20,width=430, x=130, y=52)

		
		self.entry_PubKey=tk.Entry(self.page_single_key,textvariable=self.typedPubKey)
		self.entry_PubKey.pack();self.entry_PubKey.bind("<KeyRelease>", self.create_single_key_from_pub);self.entry_PubKey.place(height=20,width=430, x=130, y=77)

		

		button_back=tk.Button(self.page_single_key,text="Back",bg="#DC7A7A",command=self.init_page_1)
		button_back.pack()
		button_back.place(x=5,y=120)

		self.button=tk.Button(self.page_single_key,text="Add Key to key pool",state=tk.DISABLED,bg="#0099FF",command=self.add_pubkey_container)
		self.button.pack()
		self.button.place(x=130, y=120)

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
		if(len(typedKey)>64):
			self.entry_PrivKey.configure(fg="#ff0000");
			del self.pub_key [:]
			self.entry_PubKey.delete(0, 'end')
			self.button.configure(state=tk.DISABLED)
			return #return if privkey has more than 64 characters

		if(len(typedKey)<64):
			for i in range(0,64-len(typedKey)):typedKey="0"+typedKey #fill privkey with zeros at the beginning if too small

		
		#else:self.entry_PrivKey.configure(fg="#000000")

		try:
			priv=bytes.fromhex(typedKey)
		except:
			self.entry_PrivKey.configure(fg="#ff0000")
			del self.pub_key [:]
			self.entry_PubKey.delete(0, 'end')
			self.button.configure(state=tk.DISABLED)
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
				self.button.configure(state=tk.NORMAL)
				return; #return when pubkey has not changed

		if(len(typedKey)>64 or len(typedKey)<64):
			self.entry_PubKey.configure(fg="#ff0000");
			self.button.configure(state=tk.DISABLED)
			return #return if pubkey has more or less than 64 characters


		try:
			pub_bytes=bytes.fromhex(typedKey)
		except:
			self.entry_PubKey.configure(fg="#ff0000")
			self.button.configure(state=tk.DISABLED)
			return
		else:
			self.entry_PubKey.configure(fg="#000000")

		
		try:
			pubkey=test_framework.ECPubKey().set(pub_bytes)
		except:
			self.entry_PubKey.configure(fg="#ff0000");
			self.button.configure(state=tk.DISABLED)
			return

		if(pubkey.valid==False):
			self.entry_PubKey.configure(fg="#ff0000");
			self.button.configure(state=tk.DISABLED)
			return

		self.entropy=""
		self.del_old_vars()
		self.pub_key.append(pubkey)
		self.update_text()

	def update_text(self,noPriv=False):
		#update entropy, single private and public key after certain events

		self.entry_Entropy.delete(0, 'end')
		self.entry_Entropy.insert(0,self.entropy)
		if(len(self.priv_key)==0):self.entry_PrivKey.delete(0, 'end')
		if(len(self.priv_key)>0 and noPriv==False):
			self.entry_PrivKey.delete(0, 'end')
			hexPriv=str(hex(self.priv_key[0].secret))[2:]
			self.entry_PrivKey.insert(0,hexPriv)
		self.entry_PubKey.delete(0, 'end')
		self.entry_PubKey.insert(0,self.pub_key)

		if(self.pub_key[0].valid):
			self.button.configure(state=tk.NORMAL)
		else:
			self.button.configure(state=tk.DISABLED)

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

		if(config.gl_gui_build_address.taproot_container):
			config.gl_console.printText("Can't add more public keys when taproot address was already created")
			return
		
		config.gl_gui_build_address.add_pubkey_container(self.entry_Label.get(),self.ext_key,self.priv_key,self.pub_key,[])
		self.init_page_1()