##Import Modules to gui.py

import tkinter as tk
from tkinter import ttk

import global_
import encryption
import wallet
import bitcoinlib
import window
import container
import console
import blockchain
##Defining global variables


##Define helper functions

def make_lambda(a):
	return lambda x:console.copyText((a)) # helper function to pass a variable on mouseclick



## Define main functions

class class_gui():
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

		#self.window_key=window.window_key(self,self.tab_key)
		#self.window_address=window.window_address(self,self.tab_address)

		global_.gl_gui_key=window.gui_key_tab(self.tab_key)
		global_.gl_gui_address=window.gui_address_tab(self.tab_address)
		global_.gl_gui_build_address=window.gui_build_address_canvas()
		global_.gl_gui_create_tx=window.gui_create_tx(self.tab_transaction)

		blockchain.startThread(blockchain.initService)#calls function in background, this establishes communication with blockchain providers



		
		



def init_gui():
	gui=class_gui()
	global_.gl_console=console.Console()
	#global_.init_globals()
	global_.gl_gui.root.mainloop()

	