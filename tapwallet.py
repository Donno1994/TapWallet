import window
import config

def main():
    print("Running TapWallet.py")

    config.gl_gui=window.class_gui()
    config.gl_gui.root.mainloop()
    


if __name__ == '__main__':
    main()