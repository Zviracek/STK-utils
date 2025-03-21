import tkinter as tk
import conf

window = tk.Tk()
window.title('Los configuration')


window.rowconfigure([0, 1], weight = 1, minsize=50)
window.columnconfigure(0, weight = 3, minsize=50)
window.columnconfigure(1, weight = 1, minsize=50)

#at first, let's say what we need these settings to do
#selection between WU/MU or U + F/M
#weight in tollerance
#selection of which categories to draw
#enablation of debug mode

#and we also need buttons to cancel and apply

deb = tk.BooleanVar()
check1 = tk.Checkbutton(window, variable = deb)
label1 = tk.Label(text = "Enable Debug mode")

label1.grid(row = 0, column = 0, sticky = "w", padx = 5)
check1.grid(row = 0, column = 1, sticky = "e", padx = 5)

def apply():
    #export to config 
    i = 0
    
def exit():
    #exit the window
    i = 0

window.mainloop()


