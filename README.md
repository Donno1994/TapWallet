![Taproot Twitter](https://user-images.githubusercontent.com/30496048/156334114-51db784d-f341-4280-8b33-e2454e1aa1b9.png)

## Don't use on mainnet.
I found a bug which leaks your private key if you use multiple transaction inputs when doing Multisig (nonce reuse).
This will be fixed in the next update.

# TapWallet
A taproot dedicated wallet. It can spend via keypath and scriptpath.
This wallet is still under development and is risky to use.
Although mainnet is possible, I recommend using testnet only.
With this wallet you can create timelock scripts which I have not heavily tested.
There are still several bugs. 
If you want to help, you can test this wallet (on testnet) and tell me your experience.

To use this wallet, download this repository, enter TapWallet directory and run "python tapwallet.py"
For further information read my medium article https://medium.com/@BR_Robin/basic-taproot-wallet-with-script-path-spend-c41f3f648a5a
