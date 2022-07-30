import tkinter as tk
import global_

class Console:
	def __init__(self):
		self.root=global_.gl_gui.root
		self.textArea=tk.Text(self.root,font=('arial',11, 'italic'))
		self.textArea.pack()
		self.textArea.place(height=310,width=450, x=1015,y=52)
		self.textArea.delete(1.0, 'end')
		
		self.textArea.insert(1.0,"Console.\n")
		self.textArea.configure(state='disabled')

		self.clearChecked=tk.IntVar(value=0)
		self.clearBox=tk.Checkbutton(self.root, text="Clear console before entering new text", variable=self.clearChecked)
		self.clearBox.pack()
		self.clearBox.place(x=1015,y=27)
			  

	def printText(self=None,text="",keepOld=False):
		self.textArea.configure(state='normal')
		if(self.clearChecked.get()==1 and keepOld==False):
			self.textArea.delete(1.0, 'end')
		
		self.textArea.insert(tk.END,text+"\n")
		self.textArea.configure(state='disabled')
		self.textArea.see("end")
		
	def copyText(self=None,text=""):
		r = tk.Tk()
		r.withdraw()
		r.clipboard_clear()
		r.clipboard_append(text)
		r.update() # now it stays on the clipboard after the window is closed
		r.destroy()

		self.printText(text="Copied to clipboard: "+text)