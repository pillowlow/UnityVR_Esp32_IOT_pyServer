from tkinter import Tk
from server_app import ServerApp

if __name__ == "__main__":
    root = Tk()
    app = ServerApp(root)
    root.mainloop()
