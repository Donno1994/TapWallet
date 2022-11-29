import tkinter as tk

import bitcoinlib
import test_framework
import bitcoinlib.transactions

import config 
import container
import console
import taproot
import blockchain
import encryption
from helperFunctions import *

tx_list=[["Tx Hash","Confirmations","Date","Description","Amount","Wallet Balance"]]
balance_list=[["Type","Index","Address","Label","Balance"]]

history_table=None
balance_table=None
tx_history=None


def make_lambda(a):
	return lambda event:config.gl_gui_build_address.count_up(a)


class HistoryTable: 

		def __init__(self,root,lst):
		
			self.entry=[]

			container = tk.Frame(root,borderwidth=4)
			self.root=container
			self.tx_history=None

			container.pack()
			container.place(height=370,width=1050,x=0,y=0)
			self.canvas = tk.Canvas(container)
			self.canvas.place(height=0,width=0, x=0,y=0)
			scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
			self.scrollable_frame = tk.Frame(self.canvas)
			self.scrollable_frame.place(x=0,y=50)
		
		
			self.scrollable_frame.bind("<Configure>",lambda e: self.canvas.configure(	scrollregion=self.canvas.bbox("all")))
			self.scrollable_frame.bind('<Enter>', self._bind_canvas_to_mousewheel)
			self.scrollable_frame.bind('<Leave>', self._unbound_to_mousewheel)
			
			
			self.canvas.create_window(0, 0, window=self.scrollable_frame, anchor="w")
			self.canvas.configure(yscrollcommand=scrollbar.set)
			self.canvas.pack(side="left", fill="both", expand=True)
			scrollbar.pack(side="right", fill="y")
			
			self.total_rows=0
			self.total_columns=0

			self.update_table(lst)
			

		def update_table(self,lst):

			total_rows=self.total_rows
			total_columns=len(lst[0])


			def change_entry_content(e,i,j):

				e.configure(state="normal")
				e.delete(0, 'end')
				if(j==0):
					e.insert(tk.END, shortenHexString(lst[i][j]))
				else:
					e.insert(tk.END, lst[i][j])
				if(not(i>0 and j==3)):e.configure(state="readonly")
				if((j==1 or j>=4) and i>0):e.configure(justify="right")#confirmations amount and wallet balance is displayed on right edge
				e.bind('<Double-Button-1>', self.make_lambda_transaction(lst[i][j]))

			# update old rows
			counter=0
			for i in range(0,total_rows): 
				for j in range(total_columns):

					change_entry_content(self.entry[counter],i,j)

					counter+=1

			# update new rows
			for i in range(total_rows,len(lst)): 
				for j in range(total_columns):
					width=5
					if(j==0):width=20
					elif(j==1):width=20
					elif(j==2):width=20
					elif(j==3):width=40
					elif(j==4):width=20
					elif(j==5):width=20
				
					e=tk.Entry(self.scrollable_frame, width=width, fg='black',font=('Arial',8,'bold'))
					e.grid(row=i, column=j) 
					change_entry_content(e,i,j)
					self.entry.append(e)
                

			self.total_rows=len(lst)
			self.total_columns=len(lst[0])


		def open_transaction_in_window(self,tx):

			self.transactionWindow = tk.Toplevel(self.root)
			self.transactionWindow.title("Tx "+str(tx.txid))
			self.transactionWindow.geometry("1000x600")
		
			window_top=tk.Label(self.transactionWindow)
			window_top.pack(fill=tk.X, expand=1)
			window_top.place(x=5,y=5)

			window_top.columnconfigure(0, weight=1)
			window_top.columnconfigure(1, weight=4)

			label_txid=tk.Label(window_top,text="TxID: ",)
			label_txid.grid(column=0, row=0, sticky=tk.W, padx=5)

			entry_txid=tk.Entry(window_top,width=70)
			entry_txid.grid(column=1, row=0, sticky=tk.W, padx=5)
			entry_txid.insert(0,str(tx.txid))
			entry_txid.configure(state="readonly",readonlybackground="#FFFFFF")

			

			label_confirmations=tk.Label(window_top,text="Confirmations: ")
			label_confirmations.grid(column=0, row=1, sticky=tk.W, padx=5)

			label_confirmations=tk.Label(window_top,text=str(tx.confirmations))
			label_confirmations.grid(column=1, row=1, sticky=tk.W, padx=5)

			label_date=tk.Label(window_top,text="Date")
			label_date.grid(column=0, row=2, sticky=tk.W, padx=5)

			label_date=tk.Label(window_top,text=tx.date)
			label_date.grid(column=1, row=2, sticky=tk.W, padx=5)

			label_fee=tk.Label(window_top,text="Fee")
			label_fee.grid(column=0, row=3, sticky=tk.W, padx=5)

			label_fee=tk.Label(window_top,text=tx.fee)
			label_fee.grid(column=1, row=3, sticky=tk.W, padx=5)

			label_size=tk.Label(window_top,text="Size")
			label_size.grid(column=0, row=4, sticky=tk.W, padx=5)

			label_size=tk.Label(window_top,text=tx.size)
			label_size.grid(column=1, row=4, sticky=tk.W, padx=5)


			window_bottom=tk.Label(self.transactionWindow)
			window_bottom.pack(fill=tk.X, expand=1)
			window_bottom.place(x=5,y=200,width=990,height=400)
			
			announcement_inputs=tk.Label(window_bottom,text="Inputs: "+str(len(tx.inputs)))
			announcement_inputs.pack()
			announcement_inputs.place(x=5,y=5)

			field_inputs=tk.Label(window_bottom,relief=tk.GROOVE)
			field_inputs.pack()
			field_inputs.place(x=5,y=30,width=980,height=140)

			label_inputs=tk.Entry(field_inputs,width=70, justify='center')
			label_inputs.insert(0,"Tx Hash of Spent Input")
			label_inputs.grid(column=0, row=0, sticky=tk.W)
			label_inputs.configure(state="readonly")

			label_inputs=tk.Entry(field_inputs,width=70, justify='center')
			label_inputs.insert(0,"Spent Address")
			label_inputs.grid(column=1, row=0, sticky=tk.W)
			label_inputs.configure(state="readonly")

			
			total_value_in=0
			row=1

			for tx_input in tx.inputs:

				bg_color="#FFFFFF"
				is_my_address=config.gl_gui_transaction_tab.is_my_address(tx_input.address)
				if(is_my_address==1):bg_color="#D6F5D6"
				if(is_my_address==2):bg_color="#FFFFCC"
					

				label_input_id=tk.Entry(field_inputs,width=70)
				label_input_id.insert(0,str(tx_input.prev_txid.hex())+":"+str(tx_input.output_n_int))
				label_input_id.grid(column=0, row=row, sticky=tk.W)
				label_input_id.configure(state="readonly",readonlybackground="#FFFFFF")

				label_input_address=tk.Entry(field_inputs,width=70)
				label_input_address.insert(0,str(tx_input.address))
				label_input_address.grid(column=1, row=row, sticky=tk.W)
				label_input_address.configure(state="readonly",readonlybackground=bg_color)

				label_input_value=tk.Entry(field_inputs,width=22)
				if(config.gl_base_unit=="BTC"):label_input_value.insert(0,"{:,.8f}".format(tx_input.value/100_000_000))
				else: label_input_value.insert(0,str(tx_input.value))
				total_value_in+=tx_input.value
				
				label_input_value.grid(column=2, row=row, sticky=tk.W)
				label_input_value.configure(state="readonly",readonlybackground="#FFFFFF")

				row+=1

			label_inputs=tk.Entry(field_inputs,width=22)
			if(config.gl_base_unit=="BTC"):label_inputs.insert(0,"Total BTC: "+"{:,.8f}".format(total_value_in/100_000_000))
			else: label_inputs.insert(0,"Total Sats: "+str(total_value_in))
			label_inputs.grid(column=2, row=0, sticky=tk.W)
			label_inputs.configure(state="readonly")

			

			announcement_outputs=tk.Label(window_bottom,text="Outputs: "+str(len(tx.outputs)))
			announcement_outputs.pack()
			announcement_outputs.place(x=5,y=200)

			field_outputs=tk.Label(window_bottom,relief=tk.GROOVE)
			field_outputs.pack()
			field_outputs.place(x=5,y=225,width=980,height=140)

			

			row=0

			label_output_utxo=tk.Entry(field_outputs,width=70, justify='center')
			label_output_utxo.insert(0,"Hash of new UTXO")
			label_output_utxo.grid(column=0, row=row, sticky=tk.W)
			label_output_utxo.configure(state="readonly")

			label_output_address=tk.Entry(field_outputs,width=70, justify='center')
			label_output_address.insert(0,"Receiving Address")
			label_output_address.grid(column=1, row=row, sticky=tk.W)
			label_output_address.configure(state="readonly")

			
			total_value_out=0
			row=1
			for tx_output in tx.outputs:
				
				bg_color="#FFFFFF"
				is_my_address=config.gl_gui_transaction_tab.is_my_address(tx_output.address)
				if(is_my_address==1):bg_color="#D6F5D6"
				if(is_my_address==2):bg_color="#FFFFCC"

				label_new_utxo=tk.Entry(field_outputs,width=70)
				label_new_utxo.insert(0,str(tx.txid)+":"+str(row-1))
				label_new_utxo.grid(column=0, row=row, sticky=tk.W)
				label_new_utxo.configure(state="readonly",readonlybackground="#FFFFFF")

				label_output_address=tk.Entry(field_outputs,width=70)
				label_output_address.insert(0,str(tx_output.address))
				label_output_address.grid(column=1, row=row, sticky=tk.W)
				label_output_address.configure(state="readonly",readonlybackground=bg_color)

				label_output_value=tk.Entry(field_outputs,width=22)
				if(config.gl_base_unit=="BTC"):label_output_value.insert(0,"{:,.8f}".format(tx_output.value/100_000_000))
				else: label_output_value.insert(0,str(tx_output.value))
				total_value_out+=tx_output.value
				label_output_value.grid(column=2, row=row, sticky=tk.W)
				label_output_value.configure(state="readonly",readonlybackground="#FFFFFF")

				row+=1

			label_output_value=tk.Entry(field_outputs,width=22)
			if(config.gl_base_unit=="BTC"):label_output_value.insert(0,"Total BTC: "+"{:,.8f}".format(total_value_out/100_000_000))
			else: label_output_value.insert(0,"Total Sats: "+str(total_value_out))
			label_output_value.grid(column=2, row=0, sticky=tk.W)
			label_output_value.configure(state="readonly")



		def find_transaction(self,tx_id):

			global tx

			for tx in self.tx_history:
				if(tx.txid==tx_id):
					self.open_transaction_in_window(tx)

		def make_lambda_transaction(self,tx_id):
			return lambda event:self.find_transaction(tx_id)

		def _bind_canvas_to_mousewheel(self, event):
			self.canvas.bind_all("<MouseWheel>", self._canvas_tx_mousewheel)

		def _unbound_to_mousewheel(self, event):
			self.canvas.unbind_all("<MouseWheel>")

		def _canvas_tx_mousewheel(self, event):
			self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")


class Table_Balance_List: 

		def __init__(self,root,lst): 

			self.entry=[]

			container = tk.Frame(root,borderwidth=4)
			self.root=container

			container.pack()
			container.place(height=370,width=950,x=0,y=0)
			self.canvas = tk.Canvas(container)#,bg="#00FF00")
			self.canvas.place(height=0,width=0, x=0,y=0)
			scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
			self.scrollable_frame = tk.Frame(self.canvas)
			self.scrollable_frame.place(x=0,y=50)
		
		
			self.scrollable_frame.bind("<Configure>",lambda e: self.canvas.configure(	scrollregion=self.canvas.bbox("all")))
			self.scrollable_frame.bind('<Enter>', self._bind_canvas_to_mousewheel)
			self.scrollable_frame.bind('<Leave>', self._unbound_to_mousewheel)
			
			
			self.canvas.create_window(0, 0, window=self.scrollable_frame, anchor="w")
			self.canvas.configure(yscrollcommand=scrollbar.set)
			self.canvas.pack(side="left", fill="both", expand=True)
			scrollbar.pack(side="right", fill="y")
			
			self.total_rows=0
			self.total_columns=0


		def update_table(self,lst,inputs_per_address=[],outputs_per_address=[]):
			print("Update Table")

			total_rows=self.total_rows
			total_columns=len(lst[0])

			self.total_columns=total_columns

			

			def change_entry_content(e,i,j):
				e.configure(state="normal")
				e.delete(0, 'end')
				try:
					e.insert(0, lst[i][j])
				except:
					print("ERROR IN change_entry_content ")
					print("Entry: ",e)
					print("i: ",i)
					print("j: ",j)
					print("lst: ",lst)

				if(total_rows>2 and i>0):
					
					if(j==0):
						if(i<total_rows/2):e.configure(readonlybackground="#d6f5d6")
						else: e.configure(readonlybackground="#ffffcc")

					if(inputs_per_address[i-1]>0):
						if(i<=total_rows/2 ):
							if(inputs_per_address[i-1]==outputs_per_address[i-1]):e.configure(readonlybackground="#d6f5d6")
							else: e.configure(readonlybackground="#84e184")
						else:
							if(inputs_per_address[i-1]==outputs_per_address[i-1]):e.configure(readonlybackground="#ffffcc")
							else: e.configure(readonlybackground="#ffff4d")

						
				if(j!=3 or i==0):e.configure(state="readonly")
				if((j==1 or j==4) and i>0):e.configure(justify="right")#index and balance is displayed on right edge
				if(j==5):e.configure(justify="center")#Inputs/Ouputs is displayed in center

				if(i>0):e.bind('<Button-1>', make_lambda(a=i-1))


			# update old rows
			counter=0
			for i in range(0,total_rows): 
				for j in range(total_columns):

					change_entry_content(self.entry[counter],i,j)

					counter+=1

			# check if new rows were added, if yes add new rows

			for i in range(total_rows,len(lst)): 
				for j in range(total_columns):

					width=5

					if(j==0):width=10
					elif(j==1):width=5
					elif(j==2):width=80
					elif(j==3):width=20
					elif(j==4):width=15
					elif(j==5):width=15
				
					e=tk.Entry(self.scrollable_frame, width=width, fg='black',font=('Arial',8,'bold'))
					e.grid(row=i, column=j) 
					
					
					change_entry_content(e,i,j)

					self.entry.append(e)

			self.total_rows=len(lst)
			self.total_columns=len(lst[0])


		


		def _bind_canvas_to_mousewheel(self, event):
			self.canvas.bind_all("<MouseWheel>", self._canvas_tx_mousewheel)

		def _unbound_to_mousewheel(self, event):
			self.canvas.unbind_all("<MouseWheel>")

		def _canvas_tx_mousewheel(self, event):
			self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")


def init(root):

	label_info = tk.Label(root, justify=tk.LEFT,text="hi");
	label_info.pack()
	label_info.place(x=4,y=10)

	global tx_list
	global balance_list
	global history_table
	global balance_table


	history_table = HistoryTable(root,tx_list)
	balance_table=Table_Balance_List(config.gl_gui.tab_address,balance_list)


def show_transactions(parse_database=True):
	global tx_list
	global balance_list
	global balance_table
	
	del tx_list[:]
	del balance_list[:]
	
	
	
	if(parse_database):
		inputs_per_address,outputs_per_address=parse_transaction_list()
		utxo_list=config.gl_wallet.utxos()
	else:
		inputs_per_address = [0 for element in range(len(config.gl_gui_build_address.taproot_container.TapRootAddress))]
		outputs_per_address=inputs_per_address
		utxo_list=[]

	index=0

	balance_list=[["Type","Index","Address","Label","Balance","Inputs/Outputs"]]

	
	
	

	for taproot_add in config.gl_gui_build_address.taproot_container.TapRootAddress:

		address_balance=0
		for utxo in utxo_list:
			if(utxo["address"]==taproot_add):
				address_balance+=utxo["value"]

		if(config.gl_base_unit=="BTC"):
			balance_string="0 BTC" if(address_balance==0) else "{:,.8f}".format(address_balance/100_000_000)+" BTC"
			
		else:
			balance_string="0 Sats" if (address_balance==0) else str(address_balance)+" Sats"

		displayed_purpose="receive"
		displayed_index=index
		displayed_IO=str(inputs_per_address[index])+"    /    "+str(outputs_per_address[index])
		if(index >= (config.gl_address_generation_max/2)):
			displayed_purpose="change"
			displayed_index = int(index % (config.gl_address_generation_max/2)) # start counting change addresses from 0 again
			

		balance_list.append([displayed_purpose,displayed_index,taproot_add,"label",balance_string,displayed_IO])
		index=index+1

	balance_table.update_table(balance_list,inputs_per_address,outputs_per_address)
	config.gl_gui_transaction_tab.update(utxo_list)


def parse_transaction_list():
	global history_table

	print("Show transactions up to block: ",blockchain.block_height)

	try:
		transaction_list=config.gl_wallet.transactions()
		history_table.tx_history=transaction_list
	except:
		print("TODO - Trying to fetch history when database is being changed. Return.")
		return

	# Stores how many inputs each address has. Initialised with 0.
	inputs_per_address=[0]*len(config.gl_gui_build_address.taproot_container.TapRootAddress)
	outputs_per_address=[0]*len(config.gl_gui_build_address.taproot_container.TapRootAddress)

	
	total_balance=0
	for tx in transaction_list:

		balance=0

		for tx_input in tx.inputs:
			
			index=0
			for taproot_add in config.gl_gui_build_address.taproot_container.TapRootAddress:

				if(tx_input.address==taproot_add):
					
					balance-=tx_input.value
					total_balance-=tx_input.value

					outputs_per_address[index]+=1

				index+=1


		for output in tx.outputs:
			
			index=0
			for taproot_add in config.gl_gui_build_address.taproot_container.TapRootAddress:
				
				if(output.address==taproot_add):
					total_balance+=output.value
					balance+=output.value

					inputs_per_address[index]+=1

				index+=1

				
		confirms="0" if(tx.block_height is None) else str(blockchain.block_height-tx.block_height+1)
		if(config.gl_base_unit=="BTC"):
			balance_string="0 BTC" if(balance==0) else "{:,.8f}".format(balance/100_000_000)+" BTC"
			total_balance_string="0 BTC" if(total_balance==0) else"{:,.8f}".format(total_balance/100_000_000)+" BTC"
			
		else:
			balance_string="0 Sats" if (balance==0) else str(balance)+" Sats"
			total_balance_string="0 Sats" if (total_balance==0) else str(total_balance)+" Sats"

		date=str(tx.date).split(".")[0] # unconfirmed txs have a decimal in date format -> Cut before decimal point
		tx_list.append([str(tx.txid),confirms,date,"Labels not ready yet.",balance_string,total_balance_string])
	#del tx_list[:]
	total_num_addresses=len(config.gl_gui_build_address.taproot_container.TapRootAddress)

	if(total_num_addresses>1):
		
		for index in range(int(total_num_addresses/2)):
			if(inputs_per_address[index]==0):
				config.gl_gui_transaction_tab.update_receive_address(index)
				break

		for index in range(int(total_num_addresses/2),total_num_addresses):
			if(inputs_per_address[index]==0):
				config.gl_gui_transaction_tab.update_change_address(index)
				break
	else:
		config.gl_gui_transaction_tab.update_change_address(0)
		
	tx_list.append(["Tx Hash","Confirmations","Date","Description","Amount","Wallet Balance"])
	tx_list.reverse()
	history_table.update_table(tx_list)
	

	return inputs_per_address,outputs_per_address
