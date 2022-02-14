# TapWallet
A taproot dedicated wallet. It can spend via keypath and scriptpath

## Motivation
This wallet was made after the taproot softfork in November 2021.
With taproot it is possible to define two spending paths, a keypath and a scriptpath.
The keypath can be seen as the default way to spend bitcoin, whereas the scriptpath could be seen as a kind of backup procedure.

After the taproot upgrade some wallets integrated taproot, however in most cases this just included "spend via keypath"
All the script logic (which is the reason why taproot is so amazing) could not be used.

With this wallet you can create a taproot address and spend funds using keypath and/or scriptpath.

## Security and missing features
This wallet is my first wallet release and lacks of many important features that a user would expect. This wallet is not secure (yet) and expects some advanced knowledge of the user and is not beginner friendly. A detailed list of what you need to consider can be found later. It probably contains bugs and is not yet intended to be used for mainnet.
Although it is already possible to use this wallet for mainnet, it was almost only tested on testnet, so I recommend only using is on testnet for "testing".

Here is a list of missing features:
- no mnemonic seeds
- no passwords possible
- the wallet can't be saved (If you close the wallet, it will forget all private keys)
- no backups
- no BIP32 wallet -> just one address possible, which means you reuse the address
- no MuSig2 -> multisig is already integrated, but only MuSig1, so 3 rounds of communications are needed
- no PSBT -> when using multisig, you can not share a PSBT, so all users need to create an identical tx.


# How to use the wallet

## 1. step: Create a taproot address
1.  Dowload this reposity
2.  Open your command terminal (cmd), go to the folder of this project and open TapWallet.py with "python tapwallet.py"
3.  In the top right you can create a keypair and attach a label (name) to it.
    For testing, it is easy to create private keys from entropy, because you can easily recreate the keys. Don't do that on mainnet!
    You can also create a random key pair or enter a hex private key.
    You can also paste in a public key of someone else (for multisig).
    The checkbox "Do you own this public key?" is used to attach different colours to the keys if they are not yours.
    Press "Add key" to create a key container
![keyCreation](https://user-images.githubusercontent.com/30496048/153785530-8870dee2-46ba-49ee-b776-d9ed82854f46.png)

4.  You will see a blue container which says "PubKey: Alice" and the public key. You can create several container and drag them whereever you want.
    
    
![key1](https://user-images.githubusercontent.com/30496048/153786307-ba784133-0f87-43e4-b29d-889dacd7ef81.png)

5.  If you want to create a taproot address from a key, press the "control key" and click on the public key container. This flags the container. If you release "control" you will be asked if you want to create a taproot address. Thereafter you have already created a single keypath taproot address which is what most of the taproot wallets do. All unused key will be deleted and no more keys can be created as long as you don't delete the taproot address container.

![firsttaproot](https://user-images.githubusercontent.com/30496048/153786679-349c631b-1de2-4227-9fed-dcd7a0f67cf4.png)

6.  Let's delete the taproot container by pressing the red X and create a second key "Bob" with entropy set to "key1"
    Place Alice and Bob next to each other, press "control", click on both public key containers and release "control" to create a MultiSig key. You can give it a new label like "Alice and Bob"
    
![multisig1](https://user-images.githubusercontent.com/30496048/153787047-599aff36-c3fe-4efe-86f9-a0e51636e76d.png)

7.  You could flag the multisig container and release "control" to create a multisig taproot address.
    However, we will now double click the multisig container to open our "script window".
    Here you see the label and public key of the container and can create a bitcoin script.
    This will be our first script that we want to use as a backup. If we can satisfy the script, we can spend the bitcoin on the bitcoin address. In this example we want to say "If Alice and Bob both agree, they can spend the bitcoin anytime". For that we can just click "Create Script". We could add a timelock, but we don't want to.
    
![script1](https://user-images.githubusercontent.com/30496048/153787228-192d2eb0-b0a1-44af-8b60-2b50409a300c.png)

The additional window will now close and you see the script and the corresponding script hash

![script2](https://user-images.githubusercontent.com/30496048/153787728-def19e3d-f4e3-439d-a90b-cf82318d0f75.png)

8.  We will now create a script for Bob which let's him spend the bitcoin after 100 blocks. Double click Bob, select "Relative timelock" and create the script.
    You now have to scripts (red) and two hashes (green)
    
    ![script3](https://user-images.githubusercontent.com/30496048/153788029-4b91c237-a4fe-47d9-bfd8-14b6a4fb439a.png)
    
9.  Now we want to hash the two hashes together to create a mekle hash. Press "control" and click bot green hashes, release "control" and you see a third green container. You could continue to hash these hashes with other hashes, but we don't want anymore scripts.

![merkle](https://user-images.githubusercontent.com/30496048/153788268-fa51c62e-3b75-4172-9c09-6d081a2efafb.png)

10. Finally we want to create our taproot address
    At the beginning we just created a taproot address from Alice's pubkey. We still want to use that as our main signing key, but we want to add our new backup scripts. Press "control", click on Alice pubkey and the green hash that was created from the other hashes and release "control". You will now see our final taproot address.
    
 ![secondtaproot](https://user-images.githubusercontent.com/30496048/153788555-373fccda-90fd-4d80-a26f-3734fd84dc34.png)
 
 ## 2nd step: Spend from taproot address by keypath
 
 


