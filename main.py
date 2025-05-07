from database import init_db
from database.base import delete_db_file
import tkinter as tk
from gui import EncryptionManagerGUI

if __name__ == "__main__":
    #delete_db_file()
    init_db()
    root = tk.Tk()
    app = EncryptionManagerGUI(root)
    root.mainloop()
