#import util
from test_framework.key import ECKey, ECPubKey, generate_key_pair, generate_bip340_key_pair, generate_schnorr_nonce,SECP256K1_FIELD_SIZE, SECP256K1_ORDER
from test_framework.messages import sha256
from test_framework.musig import aggregate_musig_signatures, aggregate_schnorr_nonces, generate_musig_key, sign_musig
from test_framework.script import tagged_hash
from test_framework.wallet_util import test_address
import inspect


class c_MultiSig:
    def __init__(self,publicKey,tweak=None,keys=[]):
        
        self.publicKey=ECPubKey().set(publicKey.get_bytes())
        self.keys=[]
        self.nonces=None
        self.nonce_agg=None
        self.tweak=None
        if(tweak is not None):
            t=ECKey().set(tweak)
            tweakNonce=ECKey().set(111)
            self.tweak=[t,t.get_pubkey(),tweakNonce,tweakNonce.get_pubkey(),sha256(tweakNonce.get_pubkey().get_bytes())]
        
    
    def addPrivKey(self,privKey,nonce=None):
        nonce=generate_schnorr_nonce()
        #nonce=ECKey().set(111)
        nonce_hash=sha256(nonce.get_pubkey().get_bytes())
        self.keys.append([privKey,privKey.get_pubkey(),nonce,nonce.get_pubkey(),nonce_hash])

    

    def addPubKey(self,pubKey):
        self.keys.append([None,pubKey,None,None,None])
       
    def print(self):
        print("Print MultiSig")
        for i in range(0,len(self.keys)):
            if(self.keys[i][0]):
                #print("Yours: "+str(self.keys[i][0])+" : "+str(self.keys[i][1])+" Y: "+str(self.keys[i][1].get_y()))
                print("Yours: "+str(self.keys[i][1])+" Y: "+str(self.keys[i][1].get_y()))
                #print("Nonce: "+str(self.keys[i][2])+" : "+str(self.keys[i][3])+" Y: "+str(self.keys[i][3].get_y()))
                print("Nonce: "+str(self.keys[i][3])+" Hash: "+str(self.keys[i][4].hex()))
                #print("Nonce Hash:"+str(self.keys[i][4].hex()))
            else:
                
                print("Not yours: "+str(self.keys[i][1])+" Y: "+str(self.keys[i][1].get_y()))
                if(self.keys[i][3] is not None):
                    print("Nonce Pub: "+str(self.keys[i][3]))
                if(self.keys[i][4] is not None):
                    print("Nonce Hash: "+str(self.keys[i][4].hex()))
        if(self.nonce_agg is not None):
            print("Agg Nonce: "+str(self.nonce_agg)+"  Y: "+str(self.nonce_agg.get_y()))
    
    def getNonce(self,pubKey):
        for i in range(0,len(self.keys)):
            if(self.keys[i][1]==pubKey):
                return self.keys[i][2]
        return None

    def addNonceHash(self,index,nonce_hash):
        
        self.keys[index][4]=nonce_hash

    def addNoncePub(self,index,nonce):
        nonce_pub=ECPubKey().set(nonce)
        try:nonce_hash=sha256(nonce_pub.get_bytes())
        except:return 2
        hash_=sha256(nonce)

        if(hash_==self.keys[index][4]):
            self.keys[index][3]=nonce_pub
            return 1
        else:
            return 3

    def genAggregatePubkey(self):
        pubkeys=[]

        for i in range(0,len(self.keys)):
            pubkeys.append(self.keys[i][1])
        c_map, pubkey_agg=generate_musig_key(pubkeys)

        for key in self.keys:
            if(key[0]is not None):key[0]=key[0]*c_map[key[1]]
            key[1]=key[1]*c_map[key[1]]
        

        if(pubkey_agg.get_y()%2!=0):
            for key in self.keys:
                key[1].negate()
                if(key[0]is not None):
                    key[0].negate()
                
                
            pubkey_agg.negate()


        if(self.tweak is not None):
            
            taprootPub=pubkey_agg+self.tweak[1]

            if(taprootPub.get_y()%2!=0):
                for key in self.keys:
                    key[1].negate()
                    if(key[0]is not None):
                        key[0].negate()

                self.tweak[0].negate()
                self.tweak[1].negate()
                self.publicKey.negate()

    
        
    def genAggregateNonce(self):
        pubkeys=[]

        for i in range(0,len(self.keys)):
            pubkeys.append(self.keys[i][3])
        self.nonce_agg, negated =aggregate_schnorr_nonces(pubkeys)
        
        if(self.tweak is not None):
            self.gen_tweak_nonce(self.nonce_agg)
            pubkeys.append(self.tweak[3])
            self.nonce_agg, negated =aggregate_schnorr_nonces(pubkeys)

        if negated:
            for key in self.keys:
                if(key[2]is not None):
                    key[2].negate()
                key[3].negate()

            if(self.tweak is not None):self.tweak[2].negate();self.tweak[3].negate()
                

    def gen_tweak_nonce(self,agg):
        #Everyone who sign needs to generate a random nonce.
        #The tweak however is not owned by a single person, but is known to everybody.
        #This method creates a deterministic tweak nonce which is derived from all the other nonces

        hash_=sha256(agg.get_bytes())
        tweakNonce=ECKey().set(hash_)
        self.tweak[2]=tweakNonce
        self.tweak[3]=tweakNonce.get_pubkey()
        self.tweak[4]=sha256(tweakNonce.get_pubkey().get_bytes())

    def init_tx():
        
        self.nonces=[]
        for i in range(0,len(self.keys)):
            self.nonces=generate_schnorr_nonce()

    def verify(self,Sig,Msg):
        return self.publicKey.verify_schnorr(Sig, Msg)

    def getTweakedPublicKey(self):
        if(self.tweak is None):
            return self.publicKey
        tweakedPub=self.publicKey+self.tweak[1]
        return tweakedPub

    def verifyTweaked(self,Sig,Msg):
        
        tweaked=self.getTweakedPublicKey()
        return tweaked.verify_schnorr(Sig, Msg)

    def getInternalPrivateKey(self):
        priv_agg=None
        for i in range(0,len(self.keys)):
            if(self.keys[i][0] is None):return None
            if(priv_agg is None):priv_agg=self.keys[i][0]
            else: priv_agg=priv_agg+self.keys[i][0]
        
        pub=priv_agg.get_pubkey()
        if(pub.get_y()%2!=0):
            priv_agg.negate()
            pub.negate()
        return priv_agg

    def getTweakedPrivateKey(self):
        if(self.tweak[0] is None):return None

        priv_agg=self.tweak[0]
        for i in range(0,len(self.keys)):
            if(self.keys[i][0] is None):return None
            if(priv_agg is None):priv_agg=self.keys[i][0]
            else: priv_agg=priv_agg+self.keys[i][0]


        pub=priv_agg.get_pubkey()
        if(pub.get_y()%2!=0):
            priv_agg.negate()
            pub.negate()
        return priv_agg
        
