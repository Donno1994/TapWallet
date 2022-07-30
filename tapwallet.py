##Import Modules to tapwallet.py
import window
import taproot
import console
import global_

def main():
    print("Running TapWallet.py")


    global_.gl_gui=window.class_gui()

    
    global_.gl_gui.root.mainloop()
    


if __name__ == '__main__':
    main()