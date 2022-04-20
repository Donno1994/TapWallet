
from test_framework import *

from bitcoin_core_framework.script_util import *
from bitcoin_core_framework.address import *
from bitcoin_core_framework.segwit_addr import *
from bitcoin_core_framework.script import *
from bitcoinlib.services.services import *
from helperFunctions import *
import global_
import console

TAPSCRIPT_VER = bytes([0xc0])

def construct_Tapleaf(pubKey,timeLockdelay=0,timeLock=0,password=None):
    tapLeaf_=0
    if(timeLockdelay==0 and timeLock==0):tapLeaf_=TapLeaf().construct_pk(pubKey)
    elif (timeLockdelay>0):
        tapLeaf_=TapLeaf().construct_pk(pubKey)
        tapLeaf_.script=bytes.fromhex(tapLeaf_.script.hex()+getTimelockDelayBytesForScript(timeLockdelay).hex())
    else:
        tapLeaf_=TapLeaf().construct_pk(pubKey)
        tapLeaf_.script=bytes.fromhex(tapLeaf_.script.hex()+getTimelockBytesForScript(timeLock).hex())
    tapleaf_hash=tagged_hash("TapLeaf", TAPSCRIPT_VER + ser_string(tapLeaf_.script))
    return tapLeaf_, tapleaf_hash

def construct_TapBranch(TapleafA,TapleafB,hashA,hashB):
    tapBranch=Tapbranch(TapleafA, TapleafB)
    tapbranch_hash_=tapbranch_hash(hashA, hashB)
    return tapBranch, tapbranch_hash_

def tapbranch_hash(l, r):
    return tagged_hash("TapBranch", b''.join(sorted([l,r])))

def construct_TapTweak(internalKey,merkleRoot):
    return tagged_hash("TapTweak", internalKey.get_bytes() + merkleRoot)

def createUnsignedTX(taprootObject,destination_list,timeLockDelay=0,timeLock=0):
    #creates an unsigned transaction from the taproot container and all the recipients
    #taprootObject - the taproot container which contains all information about the utxoSelected
    #destination_list - list of receiving addressess with amount

    spending_tx = CTransaction()
    spending_tx.nVersion = 2
    spending_tx.nLockTime = timeLock
    spending_tx.vin = []
    input_tx = CTransaction()
    input_tx.vout =[]
    utxo_list=taprootObject.utxoList


    input_tx_counter=0
    for utxo in utxo_list:
        if(utxo[0].get()==1):
            input_tx_counter+=1
            txId=utxo[1]['txid']
            outputIndex=utxo[1]['output_n']
            inputAmount=utxo[1]['value']/100000000

            outpoint = COutPoint(int(txId, 16), outputIndex)
            nSequence=0
            if(timeLockDelay>0):nSequence=timeLockDelay
            if(timeLock>0):nSequence=0xFFFFFFFE
            spending_tx_in = CTxIn(outpoint=outpoint,nSequence=nSequence)
            spending_tx.vin.append(spending_tx_in)
            address_index=taprootObject.get_index_of_address(utxo[1]['address'])
            dest_input=CTxOut(nValue=int(inputAmount * 100_000_000),scriptPubKey=bytes.fromhex(address_to_scriptPubKey(taprootObject.TapRootAddress[address_index])))
            input_tx.vout.append(dest_input)
              
    if(input_tx_counter==0):
        print("Error: No UTXO selected")
        return None

    spending_tx.vout = []
    for destination in destination_list:
        scriptpubkey = bytes.fromhex(address_to_scriptPubKey(destination[0]))
        amount_sat = int(destination[1] * 100_000_000)
        dest_output = CTxOut(nValue=amount_sat, scriptPubKey=scriptpubkey)
        spending_tx.vout.append(dest_output)

    return spending_tx,input_tx

def sign_output_with_single_key(spending_tx,input_tx,input_index,privkey,script):
    if(script is None):
        sighash = TaprootSignatureHash(spending_tx,input_tx.vout,SIGHASH_ALL_TAPROOT,input_index=input_tx_counter,scriptpath= False)
    else:
        sighash = TaprootSignatureHash(spending_tx,input_tx.vout,SIGHASH_ALL_TAPROOT,input_index=input_tx_counter,scriptpath= True,script= script)


    signature=privkey.sign_schnorr(sighash)

    return signature

def sign_output_with_all_keys(taprootObject,privkey_list,spending_tx,input_tx,script_list=None):
    input_tx_counter=0
    print("SignTX")
    print(privkey_list)
    print(script_list)
    for utxo in taprootObject.utxoList:
        if(utxo[0].get()==1):
                
            priv_key_index=input_tx_counter
            if(len(privkey_list)==1):
                priv_key_index=0
            print("Priv Index: "+str(priv_key_index)+"  "+str(input_tx_counter))
            if(script_list is None):#Spend via keypath
                sighash = TaprootSignatureHash(spending_tx,
                                        input_tx.vout,
                                        SIGHASH_ALL_TAPROOT,
                                        input_index=input_tx_counter,
                                        scriptpath= False)
            else:
                sighash = TaprootSignatureHash(spending_tx,
                                    input_tx.vout,
                                    SIGHASH_ALL_TAPROOT,
                                    input_index=input_tx_counter,
                                    scriptpath= True,
                                    script= script_list[priv_key_index])
                

            signature = privkey_list[priv_key_index].sign_schnorr(sighash)

            if(script_list is None):
                spending_tx.wit.vtxinwit.append(CTxInWitness([signature]))
            else:
                address_index=taprootObject.get_index_of_address(utxo[1]['address'])
                print("Address Index "+str(address_index))
                controlMap=taprootObject.control_map[address_index]
                witness_elements = [signature, script_list[priv_key_index], controlMap[script_list[priv_key_index]]]
                spending_tx.wit.vtxinwit.append(CTxInWitness(witness_elements))

            input_tx_counter+=1

    spending_tx_str = spending_tx.serialize().hex()
    rawtxs=[spending_tx_str]
        
    return rawtxs[0]

def signTX(taprootObject,privkey_list,spending_tx,input_tx,script_list=None,address_index_from_short_list=False):
    input_tx_counter=0
    print("SignTX")
    print(privkey_list)
    print(script_list)
    for utxo in taprootObject.utxoList:
        if(utxo[0].get()==1):
                
            if(address_index_from_short_list):address_index=input_tx_counter
            else: address_index=taprootObject.get_index_of_address(utxo[1]['address'])
            print("Address Index "+str(address_index))
            priv_key_index=input_tx_counter
            print("Privkey Index "+str(priv_key_index))
            if(len(privkey_list)==1):
                priv_key_index=0
            if(script_list is None):#Spend via keypath
                sighash = TaprootSignatureHash(spending_tx,
                                        input_tx.vout,
                                        SIGHASH_ALL_TAPROOT,
                                        input_index=input_tx_counter,
                                        scriptpath= False)
            else:
                sighash = TaprootSignatureHash(spending_tx,
                                    input_tx.vout,
                                    SIGHASH_ALL_TAPROOT,
                                    input_index=input_tx_counter,
                                    scriptpath= True,
                                    script= script_list[priv_key_index])
                

            signature = privkey_list[priv_key_index].sign_schnorr(sighash)

            if(script_list is None):
                spending_tx.wit.vtxinwit.append(CTxInWitness([signature]))
            else:
                controlMap=taprootObject.control_map[address_index]
                witness_elements = [signature, script_list[priv_key_index], controlMap[script_list[priv_key_index]]]
                spending_tx.wit.vtxinwit.append(CTxInWitness(witness_elements))

            input_tx_counter+=1

    spending_tx_str = spending_tx.serialize().hex()
    rawtxs=[spending_tx_str]
        
    return rawtxs[0]


def SpendTransactionViaKeyPath(taprootObject,destination_list,change_amount=0,address_index_from_short_list=False):

    spending_tx,input_tx=createUnsignedTX(taprootObject,destination_list)
    signedTX=signTX(taprootObject,taprootObject.tweaked_privkey,spending_tx,input_tx,None,address_index_from_short_list)

    return signedTX

def SpendTransactionViaScriptPath(taprootObject,destination_list,privkey,script,timelockDelay,timeLock,address_index_from_short_list=False):
        
    spending_tx,input_tx=createUnsignedTX(taprootObject,destination_list,timelockDelay,timeLock)
    signedTX=sign_output_with_all_keys(taprootObject,privkey,spending_tx,input_tx,script)

    return signedTX


def signMultiSig(taprootObject,spending_tx,input_tx,cMultiSig,index,script=None,input_tx_counter=0):

    utxo_list=taprootObject.utxoSelected

        

    if(index==-1):
        privkey=cMultiSig.tweak[0]
    else:
        privkey=cMultiSig.keys[index][0]

    signature_list=[]
    sighash_list=[]

    #for utxo in utxo_list:
        #   if(utxo[0].get()==1):
                
    if(script):
        sighash = TaprootSignatureHash(spending_tx,
                            input_tx.vout,
                            SIGHASH_ALL_TAPROOT,
                            input_index=input_tx_counter,
                            scriptpath= True,
                            script=script)

    else:
        sighash = TaprootSignatureHash(spending_tx,
                            input_tx.vout,
                            SIGHASH_ALL_TAPROOT,
                            input_index=input_tx_counter,
                            scriptpath= False)
    #sighash=sha256(b'transaction')
    sig = privkey.sign_schnorr(sighash)
    nonce_priv=None
    if(index==-1):nonce_priv=cMultiSig.tweak[2]
    else: nonce_priv=cMultiSig.keys[index][2]
    sig=sign_musig(privkey,nonce_priv,cMultiSig.nonce_agg,cMultiSig.getTweakedPublicKey(),sighash)
                
    print("PubKey: "+str(privkey.get_pubkey())+" Nonce: "+str(nonce_priv.get_pubkey()))
    print("Signature: "+str(sig))
    input_tx_counter+=1
                
    signature_list.append(sig)
    sighash_list.append(sighash)

    return sig,sighash

    

def address_to_scriptPubKey(address):
    if len(address)<10:return None
    script=None
        
    #Check if mainnet bech32 or bech32m
    if(address[0:3]=='bc1' or address[0:3]=='BC1'):
        if(global_.gl_mainnet==False):
            global_.gl_console(text="This is a mainnet address. You are using testnet.")
            return None
        version,program=decode_segwit_address("bc", address)
        if(version is None):return None
        if(version==0):
            if(len(program)==20 or len(program)==32):
                script=program_to_witness_script(version,bytes(program)).hex()
                #print("Segwit mainnet P2WPKH: ",script)
                return script
            else:
                global_.gl_console(text="Segwit Address has wrong length")
                return None

        if(version>0):
            script=program_to_witness_script(version,bytes(program)).hex()
            #print("TapRoot mainnet P2WPKH: ",script)
            return script

    #Check if testnet bech32 or bech32m
    if(address[0:3]=='tb1' or address[0:3]=='TB1'):
        if(global_.gl_mainnet==True):
            global_.gl_console(text="This is a testnet address. You are using mainnet.")
            return None
        version,program=decode_segwit_address("tb", address)
        if(version is None):return None
        if(version==0):
            if(len(program)==20 or len(program)==32):
                script=program_to_witness_script(version,bytes(program)).hex()
                #print("Segwit testnet P2WPKH: ",script)
                return script
            else:
                global_.gl_console(text="Segwit Address has wrong length")
                return None
            
        if(version>0):
            script=program_to_witness_script(version,bytes(program)).hex()
            #print("TapRoot testnet P2WPKH: ",script)
            return script
        
    #If it's not bech32/bech32m, check for P2PKH and P2SH
    try:result,version=base58_to_byte(address)
    except:version=None

    if(version is None):return None
    if(version==0):#mainnet P2PKH
        if(global_.gl_mainnet==False):
            global_.gl_console(text="This is a mainnet address. You are using testnet.")
            return None
        script=keyhash_to_p2pkh_script(result).hex()
        #print("P2PKH: ",script)
        return script
    if(version==5):#main P2SH
        if(global_.gl_mainnet==False):
            global_.gl_console(text="This is a mainnet address. You are using testnet.")
            return None
        script=scripthash_to_p2sh_script(result).hex()
        #print("P2SH: ",script)
        return script

    if(version==111):#testnet P2PKH
        if(global_.gl_mainnet==True):
            global_.gl_console(text="This is a testnet address. You are using mainnet.")
            return None
        script=keyhash_to_p2pkh_script(result).hex()
        #print("P2PKH: ",script)
        return script
    if(version==196):#testnet P2SH
        if(global_.gl_mainnet==True):
            global_.gl_console(text="This is a testnet address. You are using mainnet.")
            return None
        script=scripthash_to_p2sh_script(result).hex()
        #print("P2SH: ",script)
        return script
        
    global_.gl_console(text="Can't decode address properly'")

    return None

def getTimelockDelayBytesForScript(timeLock):
    if(timeLock>=65536):return None

    timeLockBytes =  bytearray()
    if(timeLock<=16):
        timeLockBytes.append(0x50+timeLock)
    else:
        lockBytes=bn2vch(timeLock)
        for byte in lockBytes:
            
            timeLockBytes.append(byte)

    timeLockBytes.append(0xb2)#OP_CSV
    timeLockBytes.append(0x75)#OP_DROP
    #print(timeLockBytes.hex())
    return timeLockBytes

def getTimelockBytesForScript(timeLock):
    if(timeLock>=16777216):return None

    timeLockBytes =  bytearray()
    if(timeLock<=16):
        timeLockBytes.append(0x50+timeLock)
    else:
        lockBytes=bn2vch(timeLock)
        timeLockBytes.append(len(lockBytes))
        for byte in lockBytes:
            
            timeLockBytes.append(byte)
        
    timeLockBytes.append(0xb1)#OP_CLTV
    timeLockBytes.append(0x75)#OP_DROP
    if(timeLockBytes[-3]>=0x80):print("ERROR in TapTreeClass: getTimelockBytesForScript - signed integer would be negative")

    return timeLockBytes
