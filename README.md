![Taproot Twitter](https://user-images.githubusercontent.com/30496048/156334114-51db784d-f341-4280-8b33-e2454e1aa1b9.png)


# TapWallet
A taproot dedicated wallet. It can spend via keypath and scriptpath.
You can select one (single/Multisig) key as your primary spend key and create as many backup scripts as you want.
Timelock and hashlock script are supported.

# What can you do with this?
Have you ever thought "What happens if I lose my keys?
What happens if I pass away?"
Before taproot, you had to keep all sensible keys somewhere safe or share all necessary information with your relatives.

With this wallet you can say:
"I can always spend my money.
My mum, dad and sister can also always spend via Multisig.
My mum alone can spend after a timelock of 3 years. 
My wife can spend if she knows a secret she got from the lawyer.
If I lose my main key, I have a backup key that can spend together with any of my family members as Multisig."

You can now store your main key save and IF something happens, you pull your backups.

# Be careful
This wallet is still under development and is risky to use.
Although mainnet is possible, I recommend using testnet only.
There are still several bugs. 
If you want to help, you can test this wallet (on testnet) and tell me your experience.

To use this wallet, download this repository, enter TapWallet directory and run "python tapwallet.py"
For further information read my medium article https://medium.com/@BR_Robin/basic-taproot-wallet-with-script-path-spend-c41f3f648a5a
