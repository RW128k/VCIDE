# OCR A Level Computer Science Programming Project
# Voice Control Integrated Development Environment - app.py
# Created by Riordan Gunn, May 2021
#
# This file contains the 'App' class which represents a Tkinter Tk
# object serving as the main window for the IDE that houses the
# directory tree and editor tab widgets as well as the voice control
# object and settings.
#
# Required Modules:
#   page: Code editor file used to create tabs in the notebook as
#     'Page' objects for both new and existing files.
#   settings: Settings window file used to create the preferences
#     dialogue that allows for viewing and updating IDE settings.
#   speech: Voice control file used to create the object that handles
#     speech recognition and processing.
#   tree: Directory tree file used to create the tree widget that can
#     be shown at the side of the window.
#   tkinter: GUI library used to create the main window by inheriting
#     from and using other widgets which are part of the library. Also
#     for displaying on screen dialogues like open file and message
#     boxes as well as creating font objects.
#   speech_recognition: Speech recognition library used to check if a
#     working microphone can be found.
#   json: Handles the reading and writing of the JSON file which the
#     settings are stored in to/from a dictionary.

from IDE.page import Page
from IDE.settings import Settings
from IDE.speech import Speech
from IDE.tree import FileTree
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font
import speech_recognition as sr
import json


class App(tk.Tk):
    # Main window/app class which inherits from a Tkinter Tk widget.
    #
    # An object of this class represents the main window of the IDE. It
    # contains a menu bar at the top of the screen, a status bar at the
    # bottom and and a paned window widget in the middle. Two panes are
    # shown by default, one with the directory tree widget and another with
    # a notebook holding code editor tab objects and it's toolbar. The
    # directory tree can be disabled or swapped sides. The microphone can
    # also be enabled/disabled using a button in the toolbar above the
    # notebook. This window stores the current font object and IDE settings
    # as public attributes, providing a means to modify them by creating a
    # settings dialogue. Starts voice control by interfacing with a
    # 'Speech' object also created as an attribute. Provides methods to
    # safely close the window and to show an 'about' dialogue. Includes
    # other helper functions.

    def __init__(self):
        # Constructor method of main window class.
        #
        # Attempts to read preferences from json file into an attribute or uses
        # default settings then creates a preferences file and writes them to
        # it if one is not found. Creates the UI elements used in the main
        # window, such as the menubar, status bar, directory tree, notebook,
        # toolbar and the panes that house them. Sets up important attributes
        # including the image objects used for toolbar buttons and the about
        # window, the voice control object and Tkinter variables for disabling
        # the mic and hiding the directory tree. Also configures binds for
        # keyboard shortcuts, key to start listening and for syntax
        # highlighting.
        #
        # Accepts no parameters.

        try:
            with open("prefs.json", "r") as prefsFile:
                self.prefs = json.loads(prefsFile.read())
        except:
            self.prefs = {"fontNum": 1, "sizeNum": 5, "font": ["Courier New", 12], "micKilled": False, "treePath": "/", "treeHidden": False}
            with open("prefs.json", "w") as prefsFile:
                json.dump(self.prefs, prefsFile)

        tk.Tk.__init__(self)

        # Create Tkinter boolean variables as attributes for the microphone and
        # directory tree enabled status
        self.treeHidden = tk.BooleanVar(value=self.prefs["treeHidden"])
        self.micKilled = tk.BooleanVar(value=self.prefs["micKilled"])

        # Instantiate a speech object for interacting with voice control
        speechRec = Speech(self)

        # Define menubar UI element
        menuBar = tk.Menu(self)

        # Create the file menu and its commands
        fileMb = tk.Menu(menuBar, tearoff=0)
        fileMb.add_command(label="New Untitled File", accelerator="Ctrl+N", command=lambda: Page(self.notebook, textFont=self.pageFont))
        fileMb.add_command(label="New Titled File", accelerator="Ctrl+Shift+N", command=lambda: self.tree.dialogue(0))
        fileMb.add_separator()
        fileMb.add_command(label="Open File", accelerator="Ctrl+O", command=self.openFileDialogue)
        fileMb.add_separator()
        fileMb.add_command(label="Save File", accelerator="Ctrl+S", command=lambda: self.notebook.nametowidget(self.notebook.select()).save())
        fileMb.add_command(label="Save File As", accelerator="Ctrl+Shift+S", command=lambda: self.notebook.nametowidget(self.notebook.select()).save(True))
        fileMb.add_separator()
        fileMb.add_command(label="Close File", accelerator="Ctrl+W", command=lambda: self.notebook.nametowidget(self.notebook.select()).close())
        fileMb.add_command(label="Quit", accelerator="Ctrl+Q", command=self.exit)

        # Create the edit menu and its commands
        editMb = tk.Menu(menuBar, tearoff=0)
        editMb.add_command(label="Undo", accelerator="Ctrl+Z", command=lambda: self.notebook.nametowidget(self.notebook.select()).undoRedo(True))
        editMb.add_command(label="Redo", accelerator="Ctrl+Y", command=lambda: self.notebook.nametowidget(self.notebook.select()).undoRedo(False))
        editMb.add_separator()
        editMb.add_command(label="Select All", accelerator="Ctrl+A", command=lambda: self.notebook.nametowidget(self.notebook.select()).text.tag_add("sel", "1.0", "end"))
        editMb.add_separator()
        editMb.add_command(label="Cut", accelerator="Ctrl+X", command=lambda: self.notebook.nametowidget(self.notebook.select()).text.event_generate("<<Cut>>"))
        editMb.add_command(label="Copy", accelerator="Ctrl+C", command=lambda: self.notebook.nametowidget(self.notebook.select()).text.event_generate("<<Copy>>"))
        editMb.add_command(label="Paste", accelerator="Ctrl+V", command=lambda: self.notebook.nametowidget(self.notebook.select()).text.event_generate("<<Paste>>"))
        editMb.add_separator()
        editMb.add_command(label="Preferences", command=lambda: Settings(self))

        # Create the view menu and its commands
        viewMb = tk.Menu(menuBar, tearoff=0)
        viewMb.add_command(label="Increase Font Size", accelerator="Ctrl++", command=lambda: self.fontSize(1))
        viewMb.add_command(label="Decrease Font Size", accelerator="Ctrl+-", command=lambda: self.fontSize(-1))
        viewMb.add_separator()
        viewMb.add_checkbutton(label="Hide File Browser", variable=self.treeHidden, command=lambda: self.mainPane.paneconfigure(self.mainPane.panes()[0], hide=self.treeHidden.get()))
        viewMb.add_command(label="Swap File Browser Side", command=lambda: self.mainPane.paneconfigure(self.mainPane.panes()[0], after=self.mainPane.panes()[1]))

        # Create the microphone menu and its commands
        self.micMb = tk.Menu(menuBar, tearoff=0)
        self.micMb.add_command(label="Start Listening", command=lambda: speechRec.start())
        self.micMb.add_checkbutton(label="Disable Microphone", command=lambda: self.killMic())

        # Create the help menu and its command
        helpMb = tk.Menu(menuBar, tearoff=0)
        helpMb.add_command(label="About", command=self.aboutWindow)

        # Add all of the menus to the menubar with their appropriate name
        menuBar.add_cascade(label="File", menu=fileMb)
        menuBar.add_cascade(label="Edit", menu=editMb)
        menuBar.add_cascade(label="View", menu=viewMb)
        menuBar.add_cascade(label="Microphone", menu=self.micMb)
        menuBar.add_cascade(label="Help", menu=helpMb)

        # Add the menubar to window, set it's title and bind the close event to
        # the exit method
        self.config(menu=menuBar)
        self.title("Voice Control IDE")
        self.protocol("WM_DELETE_WINDOW", self.exit)

        # Define statusbar UI element with initial text
        self.statusbar = tk.Label(self, text="Waiting Command...", bd=1, relief="sunken", anchor="nw")

        # Define panedwindow UI element to create resizable split screen
        # between the directory tree and code editor notebook
        self.mainPane = tk.PanedWindow(self)

        # Define directory tree UI element with initial directory from settings
        self.tree = FileTree(self, self.openFile, self.prefs["treePath"])

        # Create a Tkinter font object to use in each code editor tab with font
        # from settings
        self.pageFont = font.Font(font=self.prefs["font"])

        # Define code editor tab controller (notebook) UI element and its frame
        notebookFrame = tk.Frame(self)
        self.notebook = ttk.Notebook(notebookFrame)

        # Create an empty code editor tab in the notebook with the above font
        Page(self.notebook, textFont=self.pageFont)

        # Define code editor toolbar frame UI element for holding buttons
        notebookToolbar = tk.Frame(notebookFrame)

        # Create toolbar button icon image objects
        self.saveICO = tk.PhotoImage(file="resources/save.png")
        self.closeICO = tk.PhotoImage(file="resources/close.png")
        self.addICO = tk.PhotoImage(file="resources/add.png")
        self.opendirICO = tk.PhotoImage(file="resources/opendir.png")
        self.runICO = tk.PhotoImage(file="resources/run.png")

        # Create different microphone button icon image objects
        self.micICO = tk.PhotoImage(file="resources/mic.png")
        self.nomicICO = tk.PhotoImage(file="resources/nomic.png")
        self.listenICO = tk.PhotoImage(file="resources/listen.png")
        self.internetICO = tk.PhotoImage(file="resources/internet.png")
        self.nointernetICO = tk.PhotoImage(file="resources/nointernet.png")

        # Create about window image object
        self.bgImg = tk.PhotoImage(file="resources/about.png")

        # Define each of the toolbar buttons with their appropriate icon and
        # function
        saveButton = tk.Button(notebookToolbar, image=self.saveICO, relief="groove", command=lambda: self.notebook.nametowidget(self.notebook.select()).save())
        addButton = tk.Button(notebookToolbar, image=self.addICO, relief="groove", command=lambda: Page(self.notebook, textFont=self.pageFont))
        closeButton = tk.Button(notebookToolbar, image=self.closeICO, relief="groove", command=lambda: self.notebook.nametowidget(self.notebook.select()).close())
        opendirButton = tk.Button(notebookToolbar, image=self.opendirICO, relief="groove", command=lambda: self.openFileDialogue())
        runButton = tk.Button(notebookToolbar, image=self.runICO, relief="groove", command=lambda: self.notebook.nametowidget(self.notebook.select()).run())

        # Set appropriate statusbar and microphone button text/icon depending
        # on whether the microphone is disabled or if isn't, whether one is
        # available or not
        if not self.micKilled.get():
            try:
                # Working microphone found and enabled
                sr.Microphone()
                micText = "Microphone Ready"
                micImg = self.micICO
            except OSError:
                # No working microphone found but enabled
                micText = "Microphone Offline"
                self.statusbar.config(text=micText)
                micImg = self.nomicICO
        else:
            # Microphone disabled
            self.micMb.entryconfig(0, state="disabled")
            micText = "Microphone Disabled"
            self.statusbar.config(text="Microphone Disabled by User")
            micImg = self.nomicICO

        # Define microphone toolbar button with above text and icon used to
        # display voice control status or toggle microphone on or off
        self.micButton = tk.Button(notebookToolbar, image=micImg, text=micText, relief="groove", compound="left", command=lambda: self.killMic())

        # Add and position toolbar buttons on the toolbar frame
        saveButton.pack(side="left", padx=5, pady=2)
        addButton.pack(side="left", padx=5, pady=2)
        closeButton.pack(side="left", padx=5, pady=2)
        opendirButton.pack(side="left", padx=5, pady=2)
        runButton.pack(side="left", padx=5, pady=2)
        self.micButton.pack(side="right", padx=5, pady=2)

        # Add and position the code editor notebook and its toolbar on the
        # frame
        notebookToolbar.pack(side="top", fill="x")
        self.notebook.pack(side="bottom", fill="both", expand=1)

        # Add the directory tree and notebook frame as panes to the panedwindow
        self.mainPane.add(self.tree)
        self.mainPane.add(notebookFrame)

        # Set the directory tree's disabled status to the current setting
        self.mainPane.paneconfigure(self.mainPane.panes()[0], hide=self.treeHidden.get())

        # Add and position the panedwindow and statusbar on the window
        self.statusbar.pack(side="bottom", fill="x")
        self.mainPane.pack(fill="both", expand=1)

        # Setup bind for all key releases to trigger syntax highlighting of
        # current code editor tab
        self.bind_all("<KeyRelease>", lambda event: self.notebook.nametowidget(self.notebook.select()).syntaxHighlight(event))

        # Setup bind to start voice control listening when right shift is
        # pressed
        self.bind_all("<Shift_R>", lambda event: speechRec.start())

        # Setup binds for keyboard shortcuts to their appropriate functions
        self.bind_all("<Control-n>", lambda event: Page(self.notebook, textFont=self.pageFont))
        self.bind_all("<Control-N>", lambda event: self.tree.dialogue(0))
        self.bind_all("<Control-o>", lambda event: self.openFileDialogue())
        self.bind_all("<Control-s>", lambda event: self.notebook.nametowidget(self.notebook.select()).save())
        self.bind_all("<Control-S>", lambda event: self.notebook.nametowidget(self.notebook.select()).save(True))
        self.bind_all("<Control-w>", lambda event: self.notebook.nametowidget(self.notebook.select()).close())
        self.bind_all("<Control-q>", lambda event: self.exit())
        self.bind_all("<Control-plus>", lambda event: self.fontSize(1))
        self.bind_all("<Control-minus>", lambda event: self.fontSize(-1))

        # Set the window's icon
        self.iconbitmap("resources/icon.ico")

    def killMic(self, override=False):
        # Kill Mic method used to toggle the microphone on or off.
        #
        # Modifies the Tkinter boolean variable which determines whether voice
        # control should be started or not. This method toggles the boolean so
        # if it is already true it becomes false and vice versa. The icon and
        # text of the microphone toolbar button, the statusbar and the
        # microphone menu are updated to reflect the new status.
        #
        # Parameters:
        #   override: A boolean which when true does not change the mic status
        #     but updates the user interface to reflect the current status.
        #     Used if status is changed externally of this function.

        # Toggle mic killed status if override is not specified
        if not override:
            self.micKilled.set(not self.micKilled.get())

        # Set appropriate microphone button text/icon, statusbar text and
        # microphone menu status depending on whether the microphone is
        # disabled or if isn't, whether one is available or not
        if not self.micKilled.get():
            # Microphone enabled
            self.micMb.entryconfig(0, state="normal")
            try:
                # Working microphone found
                sr.Microphone()
                self.statusbar.config(text="Waiting Command...")
                self.micButton.config(image=self.micICO, text="Microphone Ready")
            except OSError:
                # No working microphone
                self.statusbar.config(text="Microphone Offline")
                self.micButton.config(image=self.nomicICO, text="Microphone Offline")

        else:
            # Microphone disabled
            self.micMb.entryconfig(0, state="disabled")
            self.micButton.config(image=self.nomicICO, text="Microphone Disabled")
            self.statusbar.config(text="Microphone Disabled by User")

    def openFile(self, path):
        # Open File method used to open a file in a new notebook tab.
        #
        # Iterates over all tabs in the notebook and if a tab has the same path
        # as the one provided, switches the focus to it and returns. If no tab
        # is found (file is not already open) then attempts to read the
        # contents of the file at the provided path and creates a new code
        # editor tab with it in. If the first tab is an empty and new, it is
        # removed. Should an error occur, a message box is shown and opening of
        # the file cancelled.
        #
        # Parameters:
        #   path: A string containing the path of the file to open.

        # If one exists, set focus on first tab with the same path as provided
        # then return
        for pageName in self.notebook.tabs():
            if path == self.notebook.nametowidget(pageName).path:
                self.notebook.select(pageName)
                return

        try:
            with open(path, "r") as file:
                try:
                    # Attempt to create a new code editor tab in the notebook
                    # with the contents read from the file at provided path
                    Page(self.notebook, file.read(), path.split("/")[-1] if "/" in path else path, path, self.pageFont)
                except UnicodeDecodeError:
                    # Display messagebox if an unreadable character prevents
                    # the file contents from being read and return
                    messagebox.showerror("Unreadable File", "The File \"" + (path.split("/")[-1] if "/" in path else path) + "\" contains a character that is unreadable by this software. It cannot be opened.")
                    return

            # If the first tab in the notebook has an empty contents and no
            # path (it is new), remove it
            if self.notebook.nametowidget(self.notebook.tabs()[0]).text.get("1.0", "end") == "\n" and self.notebook.nametowidget(self.notebook.tabs()[0]).path is None:
                self.notebook.forget(self.notebook.tabs()[0])
        except:
            # Display messagebox if an error occurs then stop opening
            messagebox.showerror("Error Opening Item", "An error occurred when opening the item \"" + path.split("/")[-1] if "/" in path else path + "\". Ensure the file exists and you have permission.")

    def openFileDialogue(self):
        # Open File Dialogue method used to open an 'open file' dialogue.
        #
        # Creates an 'open file' dialogue prompting the user to select a file
        # to be opened in the notebook as a tab. Calls the open file method
        # passing the path of the file as a parameter when one is selected.
        #
        # Accepts no parameters.

        path = filedialog.askopenfilename(filetypes=[("Python File", ".py"), ("Text File", ".txt"), ("JSON File", ".json"), ("CSV File", ".csv"), ("All Files", "*")], defaultextension="*.*")

        if path != "":
            self.openFile(path)

    def fontSize(self, toAdd):
        # Font Size method used increase or decrease the code editor font size.
        #
        # Calculates the new font size by adding the parameter to the existing
        # size. If it is at least 1, the font object used by all code editor
        # tabs is updated alongside the preferences (Used by settings window).
        #
        # Parameters:
        #   toAdd: An integer of the amount to add to the font size. Can be
        #     negative if the font size is to be decreased.

        newSize = self.pageFont.cget("size") + toAdd
        if newSize >= 1:
            self.pageFont.config(size=newSize)
            self.prefs["font"][1] = newSize

    def aboutWindow(self):
        # About Window method used to show an information window.
        #
        # Constructs a borderless toplevel window in the middle of the screen
        # which displays an image giving information about the program and a
        # close button to destroy the window.
        #
        # Accepts no parameters.

        dialogue = tk.Toplevel(self)

        # Set window options
        dialogue.title("About")
        dialogue.resizable(False, False)
        dialogue.geometry("800x500+" + str(int((self.winfo_screenwidth() - 800) / 2)) + "+" + str(int((self.winfo_screenheight() - 500) / 2)))
        dialogue.overrideredirect(True)
        dialogue.grab_set()

        # Define the label which holds the image and the close button UI
        # elements
        bgLabel = tk.Label(dialogue, image=self.bgImg)
        closeButton = tk.Button(dialogue, text="Close", font=(None, 12), command=dialogue.destroy)

        # Add and position label and button UI elements on the window
        bgLabel.pack()
        closeButton.place(x=790, y=490, anchor="se")

    def exit(self):
        # Exit method used to close the main window safely.
        #
        # Iterates over all currently open code editor notebook tabs and calls
        # their close method. If any are unsaved new the method will prompt the
        # user to save them. Once all are successfully closed the main window
        # is destroyed and the program quit. Exiting will be halted if the user
        # chooses to press 'Cancel' when asked to save a file.
        #
        # Accepts no parameters.

        for pageName in self.notebook.tabs():
            if self.notebook.nametowidget(pageName).close():
                # Return from method if saving is cancelled
                return
        self.destroy()
