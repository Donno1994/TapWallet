from threading import Thread
import global_
import bitcoinlib

def initService():
	print("Connecting to blockchain explorer to check for available UTXOs")
	global_.gl_gui_service=bitcoinlib.services.services.Service(network="testnet",providers=["blockstream"])

def startThread(function):
	thread=Thread(target=function)
	thread.start()
	
def getBalance(address):
	if(global_.gl_gui_build_address.taproot_container is None):
		return False

	#if(mainnet):utxo_List=Service().getutxos(address=global_.gl_gui_build_address.taproot_container.TapRootAddress)
	balance_list=global_.gl_gui_service.getbalance(address=address)
	
	return balance_list

def thread_balance():
	t1=Thread(target=getBalance)
	t1.start()

def get_utxos_from_address_list():
	balance_list=[["Type","Index","Address","Label","Balance"]]
	utxo_list=[]
	
	if(global_.gl_gui_build_address.taproot_container is not None):
		index=0
		for taproot_address in global_.gl_gui_build_address.taproot_container.TapRootAddress:
			balance=0
			if(global_.gl_gui_service is not None):
				utxos=global_.gl_gui_service.getutxos(taproot_address)
				for utxo in utxos:
					balance=balance+utxo['value']
					utxo_list.append(utxo)

			balance_list.append(["receive",index,taproot_address,"label",balance])
			index=index+1

	print("List of availale UTXOs below:")
	print(utxo_list)if(len(utxo_list)>0) else print("no UTXOs available")

	return balance_list,utxo_list