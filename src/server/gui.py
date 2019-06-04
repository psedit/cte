import tkinter as tk


class MainWindow(object):
    """
    GUI window with a prompt.
    """
    def __init__(self, root=None):
        """
        Constructor.
        """
        # set initial state
        self._root = root or tk.Tk()
        self._quitstate = False
        self._line = ''
        # make frame
        frame = tk.Frame(self._root)
        frame.pack(fill=tk.BOTH)
        # make textbox with scrollbar
        scrolly = tk.Scrollbar(frame)
        scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        self._txtlog = tk.Text(frame, font=("TkDefaultFont", 10))
        self._txtlog.config(width=80, height=24)
        self._txtlog.config(state='disabled')
        self._txtlog.pack(fill=tk.BOTH)
        scrolly.config(command=self._txtlog.yview)
        self._txtlog.config(yscrollcommand=scrolly.set)
        # make buttons
        self._prompt = tk.Entry(frame)
        self._prompt.pack(expand=1, fill=tk.X)
        self._prompt.focus_set()
        btnok = tk.Button(frame, text='OK', command=self.submit)
        btnclear = tk.Button(frame, text='CLEAR', command=self.clear)
        btnquit = tk.Button(frame, text='QUIT', fg='red', command=self.quit)
        btnok.pack(side=tk.RIGHT)
        btnclear.pack(side=tk.RIGHT)
        btnquit.pack(side=tk.LEFT)
        # assign key shortcuts
        self._root.bind('<Return>', lambda e, b=btnok: b.invoke())
        self._root.bind('<Escape>', lambda e, b=btnquit: b.invoke())

    def quit(self):
        """
        Disables updates.
        """
        self._quitstate = True

    def submit(self):
        """
        Submits the prompt text and clears the prompt.
        """
        self._line = self._prompt.get()
        self._prompt.delete(0, tk.END)

    def getline(self):
        """
        Get the prompt text.
        Returns an empty string if the prompt is empty.
        """
        line, self._line = self._line, ''
        return line

    def write(self, text):
        """
        Writes a string to the text box.
        """
        self._txtlog.config(state='normal')
        self._txtlog.insert(tk.END, text)
        self._txtlog.yview(tk.END)
        self._txtlog.config(state='disabled')

    def writeln(self, text):
        """
        Writes a string to the text box followed by a newline.
        """
        self.write('%s\n' % text)

    def clear(self):
        """
        Clears the text box.
        """
        self._txtlog.config(state='normal')
        self._txtlog.delete(0.0, tk.END)
        self._txtlog.config(state='disabled')

    def update(self):
        """
        Updates the window state.
        Returns True on success or False to indicate
        the application should quit.
        """
        if self._quitstate:
            return False
        self._root.update()
        return True


# For testing only.
if __name__ == '__main__':
    w = MainWindow()
    while w.update():
        line = w.getline()
        if line:
            w.writeln(line)
