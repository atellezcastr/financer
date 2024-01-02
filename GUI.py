import tkinter as tk
from tkinter import ttk

class GUIapp(object):
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Finance App Alpha V0.1")
        self.set_geometry()
        options = [
            'Add gain',
            'Add expense',
            ''
        ]
        self.set_top_data()


        self.root.mainloop()

    def set_geometry(self):
        WINDOW_WIDTH = 800
        WINDOW_HEIGHT = 600

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        center_x = int(screen_width/2 - WINDOW_WIDTH / 2)
        center_y = int(screen_height/2 - WINDOW_HEIGHT / 2)
        self.root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{center_x}+{center_y}')

    def set_top_data(self):
        display_info = [
            'Current holdings:',
            'Expenses(Monthly):',
            'Savings:'
        ]
        self.fields = {}
        for label in display_info:
            self.fields[label] = ttk.Label(text=label).pack(anchor=tk.N, padx=10, pady=5, fill=tk.X)
if __name__ == "__main__":
    GUIapp()
