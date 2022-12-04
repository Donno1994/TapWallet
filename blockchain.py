from threading import Thread
import os
import config
import bitcoinlib
import tkinter as tk
import time
import bitcoinlib.transactions
import tx_history

continue_endless_loop=True
connected_to_service=False
block_height=0
last_updated_blockheight=0
timelock_script_array=[]
timelockDelay_script_array=[]
transaction_list=[]
#last_known_tx={"tx_id":"","block":0,"force_update":False}

#database=None
loop_is_running=False
last_blockheight_check_time=0 # updated when new blockheight is fetched to prevent unnecessary calls
last_full_check_time=0 # updated when a full balance check was made
bool_syncing=False

def init_service_loop():

	# Every 'gl_auto_update_time' seconds this thread calls get_blockheight_from_service() to check if a new block was found.
	# 'gl_auto_update_time' can be set in the config settings and is either 0, 60, 120, 300 or 600.
	# 'gl_auto_update_time' == 0 means that no auto updates occur.

	# get_blockheight_from_service() does not load any transactions, if no new block was found.
	# If you receive an unconfirmed transaction, you should update with "Check Balance" button.

	global connected_to_service
	global continue_endless_loop
	global loop_is_running
	global last_blockheight_check_time
	global bool_syncing

	while(continue_endless_loop): #continue_endless_loop is set to False when the whole wallet is closed
		if(config.gl_auto_update_time==0):#Don't update anything. Sleep 1 sec and check again
			time.sleep(1)
			continue

			
		current_time=int(time.time())
		delta_time=current_time-last_blockheight_check_time
		c_time=time.strftime("%H:%M:%S", time.localtime(current_time))
		b_time=time.strftime("%H:%M:%S", time.localtime(last_blockheight_check_time))
		#if(delta_time%10==0):print("Next Interval Check: comparing ",c_time," with ",b_time,"   Delta: ",delta_time)

		if(delta_time>config.gl_auto_update_time and not bool_syncing):

			new_block=get_blockheight_from_service(force_fetch=True)

			if(config.gl_wallet is not None):
			
				thread=Thread(target=check_gap_limit) # if no new block -> only check next receive and change address
				thread.start()

		time.sleep(1)
			


connection_positive=True

def get_blockheight_from_service(force_fetch=False):
	
	# This method is called by init_service_loop every 'gl_auto_update_time' seconds.
	# This method tries to connect to a service provider and fetch the highest blockheight.
	# If a new block was found, check_all_addresses is called to update balances and utxos.
	# If no new block was found, nothing happens. Unconfirmed transactions will not be loaded.
	# If you expected a payment that might be unconfirmed, user should press "Check Balance" button.

	global connected_to_service
	global block_height
	global last_blockheight_check_time
	global connection_positive
	
	# check if this method was called within last 3 seconds
	# if yes, return to avoid duplicate calls

	current_time=int(time.time())
	delta_time=current_time-last_blockheight_check_time

	if(delta_time>10):
		last_blockheight_check_time=current_time
	else:
		return False

	srv=None
	
	print(time.strftime("%H:%M:%S", time.localtime(current_time))," : fetch latest block height from provider")

	network="bitcoin" if config.gl_mainnet else "testnet"
	height=0
	try:
		srv=bitcoinlib.services.services.Service(network=network)#,cache_uri=url)#"D:/Robin/Programmieren/Taproot/GitHub/bitcoinlib/data/database.txt")
		height=srv.blockcount(force_fetch)
	except:
		
		if(connection_positive==True):
			if(config.gl_console is not None):config.gl_console.printText("Lost connection to service provider")
			print("Lost connection to service provider")
			connection_positive=False
		update_connection_status()
		return False

	
	connected_to_service=bitcoinlib.services.services.connected
	t = time.localtime()
		
	current_time = time.strftime("%H:%M:%S", t)

	if(connection_positive==False):
		if(config.gl_console is not None):config.gl_console.printText("Connected to service provider: ")
		connection_positive=True

	update_connection_status()

		
	if(height>block_height):
		# new block was found, print new blockheight

		block_height=height
		if(config.gl_console is not None):config.gl_console.printText(str(current_time)+" New Blockheight: "+str(height))
		print("New Blockheight: ",height)
		return True
			
	else:
		print("Blockheight: ",height)
				
		
	return False
	#startThread(self.checkBalanceThread)

def check_hot_addresses(full_check=False):

	# just checks for next receive and next change address

	# full_check is set to True when this method is called via check_all_addresses()
	# used for enabling and disabling Check Balance button

	global connected_to_service
	global continue_endless_loop
	global bool_syncing

	if(full_check==False):
		counter=0
		while(bool_syncing):
			print("Wallet already syncing somewhere else. Sleep 5 seconds and check hot addresses again")
			time.sleep(5)
			counter+=1
			if(counter==20 or continue_endless_loop):
				return
		bool_syncing=True
		config.gl_gui.button_checkBalance.configure(state="disabled")

	print("Checking balance of next receive and change address.")
	
	
	receive_address=config.gl_gui_transaction_tab.next_receive_address
	receive_key=config.gl_wallet.key(receive_address)
	change_address=config.gl_gui_transaction_tab.next_change_address
	change_key=config.gl_wallet.key(change_address)

	config.gl_wallet.transactions_update(key_id=receive_key.key_id)
	if(receive_address!=change_address):
		config.gl_wallet.transactions_update(key_id=change_key.key_id)

	#except:
	#	print("Could not load transactions")
	#	connected_to_service=False
	#	return

	print("End checking receive and change address")

	if(continue_endless_loop == False): return

	update_connection_status()
	tx_history.show_transactions()
	if(full_check==False):
		bool_syncing=False
		config.gl_gui.button_checkBalance.configure(state="normal")


def check_gap_limit():

	# Similiar to check_all_addresses() but only checks for unused gap limit addresses.

	if(len(config.gl_gui_build_address.taproot_container.TapRootAddress)<=1):return
	
	global bool_syncing
	global continue_endless_loop
	global connected_to_service

	counter=0
	while(bool_syncing):
		print("Wallet already syncing somewhere else. Sleep 5 seconds and check gap limit addresses")
		time.sleep(5)
		counter+=1
		if(counter==20 or continue_endless_loop):
			return


	config.gl_gui.button_checkBalance.configure(state="disabled")
	bool_syncing=True

	config.gl_console.printText("Checking for new tx within gap limit of "+str(config.gl_gap_limit))
	print("Checking gap limit addresses. Gap limit: ",config.gl_gap_limit)

	check_hot_addresses(full_check=True)

	try:
		# Get indexes of desired receive addresses and check for tx updates with service provider.
		# Change addresses are not updated. Next change address already updated in check_hot_addresses()
		
		
		last_index=config.gl_gui_transaction_tab.next_receive_index+config.gl_gap_limit
		if(last_index>=config.gl_address_generation_max/2):
			last_index=int(config.gl_address_generation_max/2)-1

		for index in range(0,last_index+1):

			if(index==config.gl_gui_transaction_tab.next_receive_index):
				continue #already checked in check_hot_addresses()
			address=config.gl_gui_build_address.taproot_container.TapRootAddress[index]
			key=config.gl_wallet.key(address)
			config.gl_wallet.transactions_update(key_id=key.key_id)


		

	except:
		print("Could not load gap limit transactions.")
		connected_to_service=False
		return

	if(continue_endless_loop == False): return

	update_connection_status()
	tx_history.show_transactions()

	config.gl_console.printText("Gap limit addresses should be loaded now.")
	print("End checking gap limit addresses")
	bool_syncing=False
	config.gl_gui.button_checkBalance.configure(state="normal")

def check_all_addresses():

	# Calls an extern function that handles some wallet logic.
	# Then update the green/red bar in the top right of the wallet and display all transactions again.
	# 'delay' can be set after a transaction is sent. We then wait a few seconds to give
	# service providers some time to get the transaction

	global bool_syncing
	global continue_endless_loop
	global connected_to_service

	counter=0
	while(bool_syncing):
		print("Wallet already syncing somewhere else. Sleep 5 seconds and check all addresses")
		time.sleep(5)
		counter+=1
		if(counter==20 or continue_endless_loop):
			return


	config.gl_gui.button_checkBalance.configure(state="disabled")
	bool_syncing=True

	print("Checking all addresses")
	config.gl_console.printText("Checking for transactions.")

	if(len(config.gl_gui_build_address.taproot_container.TapRootAddress)>1):
		check_hot_addresses(full_check=True)

	


	
	

	try:
		print("Checking for transactions. 2")
		num_new_tx=config.gl_wallet.transactions_update(limit=400)
	except:
		print("Could not load transactions. Shutdown connection to service")
		connected_to_service=False
		return

	
	if(continue_endless_loop == False): return

	update_connection_status()
	tx_history.show_transactions()

	config.gl_console.printText("Transactions should be loaded now.")
	print("End checking all addresses")
	bool_syncing=False
	config.gl_gui.button_checkBalance.configure(state="normal")


def check_blockheight_and_balance():
	
	print("Check Blockheight and Balance")
	get_blockheight_from_service(force_fetch=True)
	check_gap_limit()
	print("End   Blockheight and Balance")

def update_balance_by_txid(txid=None):

	# Only update specific txid after tx was published

	global connected_to_service
	global continue_endless_loop
	global bool_syncing

	delay=10 

	print("txid is ",txid);
	if(txid is None):return
	
	if(delay>0):
		print("Check balance in ",delay," seconds")
		time.sleep(delay)

	counter=0
	while(bool_syncing):
		print("Wallet already syncing somewhere else. Sleep 5 seconds and check again")
		time.sleep(5)
		counter+=1
		if(counter==20 or continue_endless_loop==False):
			return

	config.gl_gui.button_checkBalance.configure(state="disabled")
	bool_syncing=True

	print("Checking transaction ",txid)
	config.gl_console.printText("Checking for transaction "+str(txid))

	try:
		num_new_tx=config.gl_wallet.transactions_update_by_txids(txid)
	except:
		print("Could not load transaction by txid. Shutdown connection to service")
		connected_to_service=False
		return

	
	if(continue_endless_loop == False): return

	update_connection_status()
	tx_history.show_transactions()

	bool_syncing=False
	config.gl_gui.button_checkBalance.configure(state="normal")

	
def update_connection_status():

	# In the top right corner of the wallet the server status is diplayed.
	# Connection status and blockheight are updated here.

	global block_height
	global connected_to_service

	if(connected_to_service):
		if(config.gl_gui.label_show_server_status is not None):
			config.gl_gui.label_show_server_status.configure(text="Server: connected - Blockheight: "+str(block_height),bg="#36c936")

	else:
		if(config.gl_gui.label_show_server_status is not None):
			config.gl_gui.label_show_server_status.configure(text="Server: not connected - Blockheight: "+str(block_height),bg="#ff1a1a")



def startThread(function,args=()):
	thread=Thread(target=function,args=args)

	
	thread.start()
	

def add_timelock_script(script_container,radio_button,radio_index):
	timelock_script_array.append([script_container,radio_button,radio_index])

def add_timelockDelay_script(script_container,radio_button,radio_index):
	timelockDelay_script_array.append([script_container,radio_button,radio_index])
	
def del_timelock_scripts():
	del timelock_script_array[:]
	del timelockDelay_script_array[:]


last_script_locktime=0
def update_script_locktimes():
	global last_script_locktime
	global block_height

	#if(last_script_locktime>=block_height):return

	last_script_locktime=block_height

	

	for timelock_script,radio_button,radio_index in timelock_script_array:
		text=timelock_script.label0
		if(timelock_script.hash160 is not None):text+=" - Hashlock"
		text+=" - Abs Timelock: "+str(timelock_script.timelock)
		if(timelock_script.timelock<=block_height):
			text+=" -> Ready";
			radio_button.configure(text=text,fg="#000000")
			
		else:
			text+=" -> Not Ready";
			radio_button.configure(text=text,fg="#A00000")

		

	
	for timelock_script,radio_button,radio_index in timelockDelay_script_array:
		text=timelock_script.label0
		if(timelock_script.hash160 is not None):text+=" - Hashlock"
		text+=" - Rel Timelock: "+str(timelock_script.timelockDelay)
		if(config.gl_gui_transaction_tab.largest_selected_blockheight is None):
			text+=" - Not all UTXOs confirmed -> not ready"
			radio_button.configure(text=text,fg="#A00000")
		elif(config.gl_gui_transaction_tab.largest_selected_blockheight==0):
			radio_button.configure(text=text,fg="#000000")
		else:
			text+=" - youngest UTXO: "+str(block_height-config.gl_gui_transaction_tab.largest_selected_blockheight+1)
			if(timelock_script.timelockDelay<=block_height-config.gl_gui_transaction_tab.largest_selected_blockheight+1):
				text+=" -> Ready";
				radio_button.configure(text=text,fg="#000000")
			
			else:
				text+=" -> Not Ready";
				radio_button.configure(text=text,fg="#A00000")
		
	
