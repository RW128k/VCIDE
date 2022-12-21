# OCR A Level Computer Science Programming Project
# Voice Control Integrated Development Environment - tree.py
# Created by Riordan Gunn, May 2021
#
# This file contains the 'FileTree' class which represents a Tkinter
# widget serving as the interactive directory tree at the side of the
# main window. This is a reusable module as there is no dependencies on
# other parts of the program meaning it can be imported and used in
# other solutions.
#
# Required Modules:
#   tkinter: GUI library used to create the widget by inheriting from
#     and using other widgets which are part of the library. Also for
#     displaying message boxes.
#   time: Time related functions to interpret and format last modified
#     date/time.
#   os: Provides access to the filesystem to remove files, get
#      directory listings and details about files used in tree
#      population.
#   shutil: Simply allows deleting of entire directories as the os
#     library does not provide ths functionality.

import tkinter as tk
from tkinter import ttk, messagebox
import time
import os
import shutil


class FileTree(tk.Frame):
    # File tree widget class which inherits from a Tkinter frame widget.
    #
    # An object of this class represents an interactive directory tree and
    # its toolbar. At the top of the widget is a frame which acts as the
    # toolbar containing buttons to open and delete the selected item as
    # well as to create a new file or directory and change the root node.
    # Below the toolbar is a TreeView widget and a vertical scrollbar on
    # the right hand side. The tree itself displays all files and
    # directories which are children of the root node (also a directory).
    # Each child is listed with its name, date modified, type and size.
    # Contains methods tree population, toolbar button actions and creating
    # dialogues.

    def __init__(self, root, onOpen=lambda path: None, initPath="/"):
        # Constructor method of file tree widget.
        #
        # Sets up image objects used for tree and toolbar button icons as
        # attributes so they are accessible by other methods. Also creates the
        # UI elements which form the widget (toolbar frame and buttons, tree
        # and scrollbar). Creates the drive (root node) using the initial path
        # provided and populates it.
        #
        # Parameters:
        #   root: The tkinter parent widget which the directory tree should be
        #     added to.
        #   onOpen: A function to be called when a file is opened from the tree
        #     that accepts the opened file path as a string parameter.
        #   initPath: A string containing the initial path of the root node.

        tk.Frame.__init__(self, root)

        self.onOpen = onOpen

        # Create toolbar button icon image objects
        self.openICO = tk.PhotoImage(file="resources/open.png")
        self.delICO = tk.PhotoImage(file="resources/del.png")
        self.newICO = tk.PhotoImage(file="resources/new.png")
        self.newdirICO = tk.PhotoImage(file="resources/newdir.png")
        self.cdICO = tk.PhotoImage(file="resources/cd.png")

        # Create tree item icon image objects
        self.driveICO = tk.PhotoImage(file="resources/drive.png")
        self.dirICO = tk.PhotoImage(file="resources/folder.png")
        self.pyICO = tk.PhotoImage(file="resources/py.png")
        self.fileICO = tk.PhotoImage(file="resources/file.png")
        self.imgICO = tk.PhotoImage(file="resources/img.png")
        self.jsonICO = tk.PhotoImage(file="resources/json.png")
        self.csvICO = tk.PhotoImage(file="resources/csv.png")

        # Define tree element with its last modified date, type, size and path
        # columns for each node. Hide path column as only used internally
        self.tree = ttk.Treeview(self, columns=("date", "type", "size", "path"), displaycolumns=("date", "type", "size"))

        # Set initial width of visible columns
        self.tree.column("#0", width=100)
        self.tree.column("date", width=75)
        self.tree.column("type", width=75)
        self.tree.column("size", width=50)

        # Set displayed names of visible columns
        self.tree.heading("#0", text="Name", anchor="w")
        self.tree.heading("date", text="Date modified", anchor="w")
        self.tree.heading("type", text="Type", anchor="w")
        self.tree.heading("size", text="Size", anchor="w")

        # Define vertical scrollbar element and link to tree object
        scrollbar = ttk.Scrollbar(self, command=self.tree.yview)
        self.tree["yscrollcommand"] = scrollbar.set

        # Define toolbar frame element for holding buttons
        toolbar = tk.Frame(self)

        # Define each of the toolbar buttons with their appropriate icon and
        # function
        openButton = tk.Button(toolbar, image=self.openICO, relief="groove", command=self.nodeOpen)
        delButton = tk.Button(toolbar, image=self.delICO, relief="groove", command=self.delItem)
        newButton = tk.Button(toolbar, image=self.newICO, relief="groove", command=lambda: self.dialogue(0))
        newdirButton = tk.Button(toolbar, image=self.newdirICO, relief="groove", command=lambda: self.dialogue(1))
        cdButton = tk.Button(toolbar, image=self.cdICO, relief="groove", command=lambda: self.dialogue(2))

        # Add and position toolbar buttons on the toolbar frame
        openButton.pack(side="left", padx=5, pady=2)
        delButton.pack(side="left", padx=5, pady=2)
        newButton.pack(side="left", padx=5, pady=2)
        newdirButton.pack(side="left", padx=5, pady=2)
        cdButton.pack(side="left", padx=5, pady=2)

        # Add and position the toolbar frame, tree and scrollbar on the widget
        toolbar.pack(side="top", fill="x")
        scrollbar.pack(side="right", fill="y", padx=(4, 0))
        self.tree.pack(side="left", expand=1, fill="both")

        # Bind the open node event to the node open method
        self.tree.bind("<<TreeviewOpen>>", lambda e: self.nodeOpen())

        # Create the root node as a drive with the path provided as a parameter
        # and date modified obtained from the filesystem. Insert a placeholder
        # child removed in population to mark the drive as an expandable node
        date = time.strftime("%d/%m/%Y %H:%M", time.localtime(os.path.getmtime(initPath)))
        drive = self.tree.insert("", 1, text=os.path.abspath(initPath), values=(date, "Drive", "", initPath), image=self.driveICO)
        self.tree.insert(drive, 1)

        # Perform initial population of the drive/root node
        self.nodePopulate(drive)

    def nodePopulate(self, selected):
        # Node Populate method used to insert directory's contents in the tree.
        #
        # Expands the node with the provided ID and deletes all of its
        # children. Attempts to iterate over the contents of the directory at
        # the path associated with the node and inserts each item with the
        # appropriate icon based on directory/file type as children of the
        # specified node alongside their details (date modified, size, type and
        # full path). Should an error occur, a message box is shown and
        # population halted.
        #
        # Parameters:
        #   selected: A string representing the ID of the directory node to
        #     populate within the tree.

        # Expand the specified node
        self.tree.item(selected, open=True)

        # Delete the specified node's contents (can be placeholder contents)
        for i in self.tree.get_children(selected):
            self.tree.delete(i)

        nodePath = self.tree.item(selected)["values"][3]

        try:
            # Attempt to iterate over directory contents of node's path
            for num, name in enumerate(os.listdir(nodePath)):
                # Add path of selected node to name of item to form new path
                path = nodePath + name

                # Get the date last modified of item from the filesystem and
                # format
                date = time.strftime("%d/%m/%Y %H:%M", time.localtime(os.path.getmtime(path)))

                # Get the size of item from the filesystem and convert to
                # gigabytes, megabytes, kilobytes or leave as bytes if small
                size = os.path.getsize(path)
                if size >= 1000000000:
                    size = str(round(size / 1000000000, 2)) + "GB"
                elif size >= 1000000:
                    size = str(round(size / 1000000, 2)) + "MB"
                elif size >= 1000:
                    size = str(round(size / 1000, 2)) + "KB"
                else:
                    size = str(size) + "B"

                if os.path.isdir(path):
                    # If the item is a directory, insert a node with the values
                    # found above into the specified node and insert a placeholder
                    # child to it to mark it as expandable
                    directory = self.tree.insert(selected, num + 1, text=name, values=(date, "Directory", size, path + "/"), image=self.dirICO)
                    self.tree.insert(directory, 1)
                else:
                    # If the item is a file, first find the file type and icon
                    # to use based of its extension
                    ftype = (name.split(".")[1].upper() + " File") if "." in name else "File"
                    if ftype in ["PY File", "PYW File"]:
                        img = self.pyICO
                    elif ftype == "JSON File":
                        img = self.jsonICO
                    elif ftype == "CSV File":
                        img = self.csvICO
                    elif ftype in ["JPEG File", "JPG File", "PNG File", "GIF File", "TIFF File"]:
                        img = self.imgICO
                    else:
                        img = self.fileICO

                    # Then insert a node with the values found above into the
                    # specified node
                    self.tree.insert(selected, num + 1, text=name, values=(date, ftype, size, path), image=img)
        except:
            # Display messagebox if an error occurs then halt population
            messagebox.showerror("Error Opening Directory", "An error occurred when opening the directory \"" + self.tree.item(selected)["text"] + "\". Ensure the directory exists and you have permission.")

    def nodeOpen(self):
        # Node open method used the open or expand the currently selected node.
        #
        # Calls the above populate function to expand the selected node if it
        # represents a directory/drive or calls the open file function passed
        # to the constructor with the selected node's path as a parameter if it
        # represents a file.
        #
        # Accepts no parameters.

        # Return from function if node is selected
        if len(self.tree.selection()) == 0:
            return

        # Get the ID of the first selected node
        selected = self.tree.selection()[0]

        if self.tree.item(selected)["values"][1] in ["Directory", "Drive"]:
            # Expand and populate the node if it is a directory or drive
            self.nodePopulate(selected)
        else:
            # Pass the node's path to the function provided in the constructor
            # if it is a file of any type
            self.onOpen(self.tree.item(selected)["values"][3])

    def delItem(self):
        # Delete item method used to delete the selected file or directory.
        #
        # Displays a message box asking the user to confirm deletion and if yes
        # is pressed, the file or directory the currently selected node
        # represents is deleted and the node removed. Should an error occur,
        # another message box is shown and deletion cancelled.
        #
        # Accepts no parameters.

        # Return from function if node is selected
        if len(self.tree.selection()) == 0:
            return

        # Get the ID of the first selected node
        selected = self.tree.item(self.tree.selection()[0])

        try:
            if selected["values"][1] == "Directory":
                # If the selected node represents a directory ask the user to
                # confirm deletion via message box
                conf = messagebox.askquestion("Confirm Delete", "Are you sure you want to delete the entire directory \"" + selected["text"] + "\"? This action cannot be undone!", icon="warning")
                if conf == "yes":
                    # If user presses yes, attempt to delete entire directory
                    # and remove node
                    shutil.rmtree(selected["values"][3])
                    self.tree.delete(self.tree.selection()[0])
            else:
                # If the selected node represents a file ask the user to
                # confirm deletion via message box
                conf = messagebox.askquestion("Confirm Delete", "Are you sure you want to delete the file \"" + selected["text"] + "\"? This action cannot be undone!", icon="warning")
                if conf == "yes":
                    # If user presses yes, attempt to delete file and remove
                    # node
                    os.remove(selected["values"][3])
                    self.tree.delete(self.tree.selection()[0])
        except:
            # Display messagebox if an error occurs then cancel deletion
            messagebox.showerror("Error Deleting Item", "An error occurred when deleting the item \"" + selected["text"] + "\". Ensure that it exists and you have permission.")

    def dialogue(self, dType):
        # Dialogue method used to create a window for toolbar button actions.
        #
        # Constructs a dialogue box requesting input for file creation,
        # directory creation or drive change based the parameter. The dialogue
        # is very simple with a brief description, path and name text fields
        # as well as submit and cancel buttons. For each purpose the window
        # title, description and submit button text and function changes. The
        # name field is also not shown for the change drive dialogue.
        #
        # Parameters:
        #   dType: An integer representing the dialogue type to create. 0 for
        #     file creation, 1 for directory creation and 2 for drive changing.

        # Setup variables for path and name fields, setting path equal to the
        # path of the selected node
        path = tk.StringVar()
        name = tk.StringVar()
        path.set(self.tree.item(self.tree.selection()[0])["values"][3] if len(self.tree.selection()) > 0 else "/")

        # Create dialogue and set options
        dialogue = tk.Toplevel()
        dialogue.resizable(False, False)
        dialogue.grab_set()

        # Define path text field, its container and cancel button elements
        uiFrame = tk.Frame(dialogue)
        pathLabel = tk.Label(uiFrame, text="Path:")
        pathEntry = tk.Entry(uiFrame, width=48, textvariable=path)
        closeButton = tk.Button(dialogue, text="Cancel", command=dialogue.destroy)

        # Set the window title and create description label and submit button
        # with text based on dialogue purpose specified via parameter
        if dType == 0:
            # FILE CREATION
            showName = True
            dialogue.title("Create new file")
            infoLabel = tk.Label(dialogue, text="Please specify the path, name and type of file you wish to create:")
            createButton = tk.Button(dialogue, text="Create", command=lambda: self.createFile(path.get(), name.get(), dialogue))
        elif dType == 1:
            # DIRECTORY CREATION
            showName = True
            dialogue.title("Create new directory")
            infoLabel = tk.Label(dialogue, text="Please specify the path and name of the directory you wish to create:")
            createButton = tk.Button(dialogue, text="Create", command=lambda: self.createFolder(path.get(), name.get(), dialogue))
        else:
            # DRIVE CHANGING
            showName = False
            dialogue.title("Change root directory")
            infoLabel = tk.Label(dialogue, text="Please specify the path of the root directory you would like to change to:")
            createButton = tk.Button(dialogue, text="Change", command=lambda: self.changeDrive(path.get(), dialogue))

        # Add and position description label, path text entry and buttons on
        # the dialogue
        infoLabel.pack(padx=10, pady=10)
        pathLabel.grid(row=0, column=0, padx=10, sticky="w")
        pathEntry.grid(row=0, column=1, padx=(0, 10), sticky="e")
        uiFrame.pack(padx=10)
        closeButton.pack(padx=(10, 20), pady=10, side="right")
        createButton.pack(pady=10, side="right")

        # Create, add and position name text entry on the dialogue if its
        # purpose is for file or directory creation. Focus on the name field if
        # applicable otherwise on the path field
        if showName:
            nameLabel = tk.Label(uiFrame, text="Name:")
            nameEntry = tk.Entry(uiFrame, width=48, textvariable=name)
            nameLabel.grid(row=1, column=0, padx=10, pady=10, sticky="w")
            nameEntry.grid(row=1, column=1, padx=(0, 10), pady=(10, 0), sticky="e")
            nameEntry.focus()
        else:
            pathEntry.focus()

    def createFile(self, path, name, dialogue=None):
        # Create file method used to create a file with provided name and path.
        #
        # Checks if the provided path and name are valid and displays a message
        # box if validation fails. If they are valid, attempts to write an
        # empty string to a file with the name and path, closes the passed
        # dialogue (if applicable) and calls the open function passed to the
        # constructor with the new file's path as a parameter. Should an error
        # occur, a message box is shown and creation cancelled.
        #
        # Parameters:
        #   path: A string containing the path of the parent directory to
        #     create the file under.
        #   name: A string containing the filename of the file to create,
        #     including the file extension.
        #   dialogue: An optional tkinter window object (toplevel/tk) to be
        #     closed upon successful creation of the file.

        # Validate path and filename parameters
        if path == "" or name == "":
            # Cancel if either provided path or name is empty
            messagebox.showwarning("Provide a path and name", "You must provide a valid path and Filename before creating a new file")
        elif not os.path.isdir(path):
            # Cancel if provided path is not a real directory
            messagebox.showwarning("Invalid path", "The path you have provided is invalid. Please change it to a valid one.")
        elif "." not in name or name[-1] == ".":
            # Cancel if the filename contains no extension
            messagebox.showwarning("Provide a file extension", "You have not provided a file extension. Please provide one.")
        elif os.path.exists(path + ("/" if path[-1] != "/" else "") + name):
            # Cancel if a file with proved name exists at provided path
            messagebox.showwarning("File exists", "You have provided the name and path of a file that already exists. Please amend.")
        else:
            try:
                # If path and filename pass validation, attempt to write an
                # empty string to a file with filename at path
                with open(path + ("/" if path[-1] != "/" else "") + name, "w") as file:
                    file.write("")

                # Close the dialogue if one is passed as a parameter
                if dialogue:
                    dialogue.destroy()

                # Pass the new file's path to the function provided in the
                # constructor
                self.onOpen(path + ("/" if path[-1] != "/" else "") + name)
            except:
                # Display messagebox if an error occurs then cancel creation
                messagebox.showerror("An error occurred while creating file", "Could not create file. Please check you have permission.")

    def createFolder(self, path, name, dialogue=None):
        # Create folder method used to create a directory with provided name.
        #
        # Checks if the provided path and name are valid and displays a message
        # box if validation fails. If they are valid, attempts to create a
        # directory with the name and path then closes the passed dialogue (if
        # applicable). Should an error occur, a message box is shown and
        # creation cancelled.
        #
        # Parameters:
        #   path: A string containing the path of the parent directory to
        #     create the new directory under.
        #   name: A string containing the name of the directory to create.
        #   dialogue: An optional tkinter window object (toplevel/tk) to be
        #     closed upon successful creation of the directory.

        # Validate path and directory name parameters
        if path == "" or name == "":
            # Cancel if either provided path or name is empty
            messagebox.showwarning("Provide a path and name", "You must provide a valid path and name before creating a new directory")
        elif not os.path.isdir(path):
            # Cancel if provided path is not a real directory
            messagebox.showwarning("Invalid path", "The path you have provided is invalid. Please change it to a valid one.")
        elif os.path.isdir(path + ("/" if path[-1] != "/" else "") + name):
            # Cancel if a directory with proved name exists at provided path
            messagebox.showwarning("Directory exists", "You have provided the name and path of a directory that already exists. Please amend.")
        else:
            try:
                # If path and directory name pass validation, attempt to create
                # a directory with name at path
                os.mkdir(path + ("/" if path[-1] != "/" else "") + name)

                # Close the dialogue if one is passed as a parameter
                if dialogue:
                    dialogue.destroy()
            except:
                # Display messagebox if an error occurs then cancel creation
                messagebox.showerror("An error occurred while creating directory", "Could not create directory. Please check you have permission.")

    def changeDrive(self, path, dialogue=None):
        # Change drive method used to update the root node's path in the tree.
        #
        # Checks if the provided path is valid and displays a message box if
        # validation fails. If it is valid, attempts to make a directory
        # listing of the path to check for permission errors. Should an error
        # occur, a message box is shown and drive changing cancelled. Deletes
        # the root node in the tree (and also all of its children), creates the
        # new drive (root node) using the path provided, closes the passed
        # dialogue (if applicable) then populates the drive.
        #
        # Parameters:
        #   path: A string containing the path of the parent directory to
        #     create the new directory under.
        #   name: A string containing the name of the directory to create.
        #   dialogue: An optional tkinter window object (toplevel/tk) to be
        #     closed upon successful creation of the directory.

        # Validate path parameter
        if not os.path.isdir(path):
            # Cancel if provided path is not a real directory
            messagebox.showwarning("Directory does not exist", "You have provided the path of a directory that does not exist. Please provide a valid directory path.")
        else:
            # Attempt to create a directory listing for the provided path and
            # display a message box then return if an exception is thrown
            try:
                os.listdir(path)
            except:
                messagebox.showwarning("Directory is inaccessible", "You have provided the path of a directory that is not accessible. Please ensure you have permission.")
                return

            # Delete the root node in the tree and its contents
            self.tree.delete(self.tree.get_children("")[0])

            # Create the root node as a drive with the path provided and date
            # modified obtained from the filesystem. Insert a placeholder child
            # removed in population to mark the drive as an expandable node
            date = time.strftime("%d/%m/%Y %H:%M", time.localtime(os.path.getmtime(path)))
            drive = self.tree.insert("", 1, text=os.path.abspath(path), values=(date, "Drive", "", os.path.abspath(path).replace("\\", "/") + ("" if os.path.abspath(path).replace("\\", "/")[-1] == "/" else "/")), image=self.driveICO)
            self.tree.insert(drive, 1)

            # Close the dialogue if one is passed as a parameter
            if dialogue:
                dialogue.destroy()

            # Populate the contents of the new drive
            self.nodePopulate(drive)
