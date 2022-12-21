# OCR A Level Computer Science Programming Project
# Voice Control Integrated Development Environment - settings.py
# Created by Riordan Gunn, May 2021
#
# This file contains the 'Settings' class which provides a means to
# view and update settings used by the software via a GUI.
#
# Required Modules:
#   tkinter: GUI library used to construct the settings user interface
#     and display warning message boxes.
#   os: Provides access to the filesystem so the directory tree path
#     entered can be validated.
#   json: Handles the formatting and writing of the JSON file which the
#     settings are stored in.

import tkinter as tk
from tkinter import ttk, messagebox
import os
import json


class Settings(tk.Toplevel):
    # Settings window class which inherits from a tkinter toplevel widget.
    #
    # An object of this class is created each time the settings window is
    # opened from within the main app. Represents the window itself and
    # handles the input and saving of configuration values. Contains
    # sections for formatting, microphone and directory tree settings.

    def __init__(self, root):
        # Constructor method of settings window class.
        #
        # Sets up user interface components and populates them with current
        # settings obtained from the main window's BoolVars and config
        # attribute (A dictionary storing user preferences in memory).
        #
        # Parameters:
        #   root: The tkinter Tk object of the main window containing the
        #     config and other essential attributes.

        tk.Toplevel.__init__(self, root)

        self.root = root

        # Set window options
        self.title("Preferences")
        self.iconbitmap("resources/icon.ico")
        self.resizable(False, False)
        self.grab_set()

        # Define UI elements related to formatting settings (font and size)
        formatPrefFrame = tk.LabelFrame(self, text="Formatting:", padx=5, pady=5)
        fontLabel = tk.Label(formatPrefFrame, text="Font:")
        self.fontBox = ttk.Combobox(formatPrefFrame, values=["Arial", "Courier New", "Times New Roman", "Fixedsys", "Comic Sans MS"], state="readonly")
        self.fontBox.current(self.root.prefs["fontNum"])
        sizeLabel = tk.Label(formatPrefFrame, text="Size:")
        self.sizeBox = ttk.Combobox(formatPrefFrame, values=["2", "4", "6", "8", "10", "12", "14", "20", "24", "30", "40", "50", "60", "72"], state="readonly")
        self.sizeBox.current(self.root.prefs["sizeNum"])
        exampleLabel = tk.Label(formatPrefFrame, text="Example", font=self.root.prefs["font"])
        self.fontBox.bind("<<ComboboxSelected>>", lambda e: exampleLabel.config(font=(self.fontBox.get(), int(self.sizeBox.get()))))
        self.sizeBox.bind("<<ComboboxSelected>>", lambda e: exampleLabel.config(font=(self.fontBox.get(), int(self.sizeBox.get()))))

        # Define UI elements related to microphone settings (enable / disable)
        micPrefFrame = tk.LabelFrame(self, text="Microphone:", padx=5, pady=5)
        defaultLabel = tk.Label(micPrefFrame, text="Default Setting:")
        onRb = tk.Radiobutton(micPrefFrame, text="Enabled", value=False, variable=self.root.micKilled, command=lambda: self.root.killMic(True))
        offRb = tk.Radiobutton(micPrefFrame, text="Disabled", value=True, variable=self.root.micKilled, command=lambda: self.root.killMic(True))

        # Define UI elements related to the directory tree (path, visibility)
        treePrefFrame = tk.LabelFrame(self, text="File Browser:", padx=5, pady=5)
        dirLabel = tk.Label(treePrefFrame, text="Default DIR:")
        self.dirEntry = tk.Entry(treePrefFrame)
        self.dirEntry.insert("end", self.root.prefs["treePath"])
        stateLabel = tk.Label(treePrefFrame, text="Default State:")
        shownRb = tk.Radiobutton(treePrefFrame, text="Shown", value=False, variable=self.root.treeHidden, command=lambda: self.root.mainPane.paneconfigure(self.root.mainPane.panes()[0], hide=self.root.treeHidden.get()))
        hiddenRb = tk.Radiobutton(treePrefFrame, text="Hidden", value=True, variable=self.root.treeHidden, command=lambda: self.root.mainPane.paneconfigure(self.root.mainPane.panes()[0], hide=self.root.treeHidden.get()))

        # Define UI buttons to save or discard settings
        applyButton = tk.Button(self, text="Apply", command=self.write)
        cancelButton = tk.Button(self, text="Cancel", command=self.destroy)

        # Add and position formatting settings elements on the window
        formatPrefFrame.pack(padx=10, pady=10, fill="x")
        fontLabel.grid(row=0, column=0, sticky="w")
        self.fontBox.grid(row=0, column=1, sticky="w")
        sizeLabel.grid(row=1, column=0, pady=10, sticky="w")
        self.sizeBox.grid(row=1, column=1, pady=10, sticky="w")
        exampleLabel.grid(row=2, column=0, columnspan=10)

        # Add and position microphone settings elements on the window
        micPrefFrame.pack(padx=10, pady=10, fill="x")
        defaultLabel.grid(row=0, column=0)
        onRb.grid(row=0, column=1, sticky="w")
        offRb.grid(row=1, column=1, sticky="w")

        # Add and position directory tree settings elements on the window
        treePrefFrame.pack(padx=10, pady=10, fill="x")
        dirLabel.grid(row=0, column=0)
        self.dirEntry.grid(row=0, column=1)
        stateLabel.grid(row=1, column=0)
        shownRb.grid(row=1, column=1, sticky="w")
        hiddenRb.grid(row=2, column=1, sticky="w")

        # Add and position apply/cancel buttons on the window
        applyButton.pack(side="right", padx=(0, 20), pady=(0, 10))
        cancelButton.pack(side="right", padx=(0, 10), pady=(0, 10))

    def write(self):
        # Save settings method used to update and write preferences to file.
        #
        # Validates inputs entered in the settings window (self) and updates
        # the main window's attributes accordingly if they are correct or
        # displays a message box if not.
        #
        # Accepts no parameters.

        # Check if the entered default directory tree path is valid and if not
        # display an error then return
        if not os.path.isdir(self.dirEntry.get()):
            messagebox.showwarning("Directory does not exist", "You have provided the path of a directory that does not exist. Please provide a valid directory path.")
            return

        # Attempt to create a directory listing for the entered default
        # directory tree path and display a message box then return if an
        # exception is thrown
        try:
            os.listdir(self.dirEntry.get())
        except:
            messagebox.showwarning("Directory is inaccessible", "You have provided the path of a directory that is not accessible. Please ensure you have permission.")
            return

        # Change the root node in the main window's directory tree
        self.root.tree.changeDrive(self.dirEntry.get())

        # Update the local settings stored in the prefs dictionary
        self.root.prefs["fontNum"] = self.fontBox.current()
        self.root.prefs["sizeNum"] = self.sizeBox.current()
        self.root.prefs["font"] = [self.fontBox.get(), int(self.sizeBox.get())]
        self.root.prefs["micKilled"] = self.root.micKilled.get()
        self.root.prefs["treePath"] = os.path.abspath(self.dirEntry.get()) + "/"
        self.root.prefs["treeHidden"] = self.root.treeHidden.get()

        self.root.pageFont.config(family=self.root.prefs["font"][0], size=self.root.prefs["font"][1])

        # Write the new settings to the preferences JSON file
        with open("prefs.json", "w") as prefsFile:
            json.dump(self.root.prefs, prefsFile)

        # Close the settings window and return the focus to the main window
        self.destroy()
