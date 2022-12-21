# OCR A Level Computer Science Programming Project
# Voice Control Integrated Development Environment - page.py
# Created by Riordan Gunn, May 2021
#
# This file contains the 'Page' class which represents a Tkinter widget
# serving as the code editor within each tab. This is a reusable module
# as there is no dependencies on other parts of the program meaning it
# can be imported and used in other solutions.
#
# Required Modules:
#   tkinter: GUI library used to create the widget by inheriting from
#     and using other widgets which are part of the library. Also for
#     displaying on screen dialogues like save file and message boxes.
#   os: Allows command line access used to execute the python program
#     currently being edited.
#   json: Handles the reading of the JSON file containing the keywords
#     and builtin functions to be syntax highlighted into a dictionary.

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json


class Page(tk.Frame):
    # Code editor widget class which inherits from a Tkinter frame widget.
    #
    # Objects of this class represent tabs in a notebook widget that hold a
    # code editor. The widget is very simple and consists of a text field
    # with horizontal and vertical scrollbars. The text field widget can be
    # accessed easily as it is a public attribute of the class, allowing
    # for updating contents or positioning the cursor. The code residing in
    # the text field can be executed with the run method and can be colored
    # to match the python syntax using the syntaxHighlight method. Includes
    # other file and tab related methods such as save and close. The path
    # and contents of the open file at the last save (if applicable) can be
    # obtained from the object as attributes.

    # List of characters that cannot be used in identifiers so will not
    # prevent syntax highlighting
    illegals = ["`", "¬", "¦", "!", "\"", "%", "^", "&", "*", "(", ")", "-", " ", "+", "=", "[", "]", "{", "}", "'", "@", ":", ";", "#", "~", "/", "?", ",", "<", ".", ">", "\\", "|"]

    # Read lists of keywords and built in functions to highlight from file
    with open("resources/syntax.json", "r") as syntaxFile:
        syntax = json.loads(syntaxFile.read())

    def __init__(self, notebook, cont=None, title="Untitled", path=None, textFont=("Courier New", 12)):
        # Constructor method of code editor widget.
        #
        # Sets up public attributes (path, text widget and saved contents) with
        # values from parameters. Also creates the UI elements which form the
        # widget (scrollbars and text). Automatically performs initial syntax
        # highlighting, adds tab to notebook and selects it.
        #
        # Parameters:
        #   notebook: The tkinter Notebook object which the tab should be added
        #     to.
        #   cont: A string containing the initial contents to be inserted into
        #     the editor.
        #   title: A string holding the title of the tab.
        #   path: A string holding the filesystem path to the current file.
        #     Used in saving and execution. Can also be None if file is new.
        #   textFont: The font family and size that the editor should use for
        #     displaying code. Can be any type interpreted by Tkinter as a font
        #     such as a tuple or font object.

        tk.Frame.__init__(self, notebook)

        # Set up attributes
        self.notebook = notebook
        self.textFont = textFont
        self.path = path

        # Define text field element and its scrollbars
        self.text = tk.Text(self, font=textFont, wrap="none", undo=1)
        ysb = ttk.Scrollbar(self, command=self.text.yview)
        xsb = ttk.Scrollbar(self, orient="horizontal", command=self.text.xview)

        # Link scrollbars to text field
        self.text["yscrollcommand"] = ysb.set
        self.text["xscrollcommand"] = xsb.set

        # Create color tags belonging to the text field for syntax highlighting
        #
        # Keywords
        self.text.tag_configure("kw", foreground="#FFA500")
        # Built in Functions
        self.text.tag_configure("bi", foreground="#6A0DAD")
        # Strings
        self.text.tag_configure("str", foreground="#0B6623")
        # Comments
        self.text.tag_configure("comment", foreground="#FF0000")

        # Insert the initial contents to the text field if it was provided as a
        # parameter, and set the last saved contents attribute accordingly.
        if cont is not None:
            self.text.insert("end", cont)
            self.saved = cont
        else:
            self.saved = ""

        # Add the tab to the notebook object specified
        self.notebook.add(self, text=title)

        # Add and position the text field and scrollbars on the tab
        xsb.pack(side="bottom", fill="x")
        ysb.pack(side="right", fill="y")
        self.text.pack(fill="both", expand=1, side="left")

        # Select the tab in the notebook and perform initial syntax highlight
        self.notebook.select(self)
        self.syntaxHighlight()

    def save(self, saveAs=False):
        # Save method used to write/update the contents of the current file.
        #
        # Displays a save file dialogue which updates the path if the current
        # tab has no associated path or if Save As is specified via the
        # parameter. The contents of the tab's text field will attempt to be
        # written to the associated path (or that provided by the Save As
        # dialogue if applicable) and stored as the last save contents. Should
        # an error occur, a messagebox is shown, the path removed and the
        # process repeated again with the dialogue.
        #
        # Parameters:
        #   saveAs: Boolean that when true forces the save file dialogue to be
        #     shown regardless of whether the opened file already has a path.

        if self.path is None or saveAs:
            # Create Save As dialogue and store path if tab has no associated
            # path or if saveAs parameter is true
            path = filedialog.asksaveasfilename(filetypes=[("Python File", ".py"), ("Text File", ".txt"), ("JSON File", ".json"), ("CSV File", ".csv"), ("All Files", "*")], defaultextension="*.*")
            if path == "":
                # Return from function if no filename was provided
                return True
            else:
                # Update path associated with the tab and set its title to the
                # new filename
                self.path = path
                self.notebook.tab(self, text=path.split("/")[-1] if "/" in path else path)

        try:
            # Attempt to write text field contents to path and update last save
            # contents variable
            with open(self.path, "w") as file:
                file.write(self.text.get("1.0", "end-1c"))
                self.saved = self.text.get("1.0", "end-1c")
        except:
            # Display messagebox if an error occurs, remove path and redo save
            messagebox.showerror("An error occurred while saving the file", "Could not save file. Please check you have permission and the path exists.")
            self.path = None
            self.save()

    def close(self):
        # Close method used to close and destroy the tab.
        #
        # Prompts the user to save the file if it is not already saved then
        # removes the tab from it's notebook object. If it was the only open
        # tab, a new one is created with an new untitled file.
        #
        # Accepts no parameters.

        if self.text.get("1.0", "end-1c") != self.saved:
            # Ask to user if they want to save the file if text field contents
            # does not match last save contents (not already saved)
            res = messagebox.askyesnocancel("Save file before closing?", "Do you want to save the file before closing?")
            # Attempt file save if yes is chosen and/or return true if
            # operation is cancelled
            if res:
                if self.save():
                    return True
            elif res is None:
                return True

        # Remove the tab from the notebook
        self.notebook.forget(self)

        # Insert a new tab with an new untitled file if the notebook is empty
        if len(self.notebook.tabs()) == 0:
            Page(self.notebook, textFont=self.textFont)

    def run(self):
        # Run method used to execute the python file opened in the tab.
        #
        # Prompts the user to save the file if it is not already saved then
        # executes the file at the path associated with the tab using the
        # python interpreter.
        #
        # Accepts no parameters.

        if self.text.get("1.0", "end-1c") != self.saved or self.path is None:
            # Ask to user if they want to save the file if text field contents
            # does not match last save contents (not already saved)
            res = messagebox.askyesno("File must be saved before being run", "File Must be saved in order to be run. Save?")
            # Attempt file save if yes is chosen or return from function if no
            # is chosen  or if save dialogue is closed after pressing yes.
            if res:
                if self.save():
                    return
            elif not res:
                return

        # Run file at the tab's path with python interpreter using command line
        os.system("start cmd /K py \"" + self.path + "\"")

    def undoRedo(self, undo):
        # Undo/redo method used to undo or redo changes made in the text field.
        #
        # Attempts to undo or redo changes made to the code editor's text
        # field one step at a time. Whether an undo or redo command is issued
        # depends on the below boolean parameter. Ignores any TclErrors which
        # will usually be thrown if there are no more steps to undo/redo.
        #
        # Parameters:
        #   undo: Boolean for specifying undo or redo. True for undo, false for
        #     redo.

        try:
            if undo:
                self.text.edit_undo()
            else:
                self.text.edit_redo()
        except tk.TclError:
            pass

    def syntaxHighlight(self, event=None):
        # Syntax highlight method used to color code and automatically indent.
        #
        # If a key press event is passed to this method and the key pressed is
        # enter, inserts the same amount of whitespace to automatically indent
        # and adds a further four spaces if the previous line ends in a colon.
        # Removes all previous syntax highlighting color tags then iterates
        # over every keyword and builtin function identifier to apply the
        # appropriate color tag to each match in the text field. Also searches
        # for string quotes and comment hash signs then colors the text for the
        # remainder of the line or up to another quotation mark on the same
        # line.
        #
        # Parameters:
        #   event: A Tkinter event object holding the key that triggered it or
        #     None if the method should be called independently of an event.

        t = self.text

        if event is not None and event.keysym == "Return":
            # If the method was called with an event and the triggering key was
            # enter, insert the same number of indents as the previous line
            prevln = t.get(t.index("insert" + "-1c linestart"), t.index("insert" + "-1c lineend"))
            t.insert("insert", " " * 4 * ((len(prevln) - len(prevln.lstrip())) // 4))

            # Insert an extra 4 spaces if the previous line ends in a colon (:)
            if t.get(t.index("insert" + "-1l lineend -1c")) == ":":
                t.insert("insert", "    ")

        # Remove all color tags from the text field
        t.tag_remove("kw", "1.0", "end")
        t.tag_remove("bi", "1.0", "end")
        t.tag_remove("str", "1.0", "end")
        t.tag_remove("comment", "1.0", "end")

        # KEYWORD HIGHLIGHTING

        # Iterate over all python keywords
        for kw in Page.syntax["keywords"]:
            # Create variable for storing match length and create text pointers
            # (marks) with their initial position at the start of text field
            length = tk.IntVar()
            t.mark_set("a", "1.0")
            t.mark_set("b", "1.0")

            # Repeat until no more of matches of the current keyword are found
            while True:
                # Search for keyword in text field and break if none found
                index = t.search(kw, "b", "end", count=length)

                if index == "":
                    break

                line = t.get(index + " linestart", index + "lineend")

                # Move pointers/marks around keyword
                t.mark_set("a", index)
                t.mark_set("b", "%s+%sc" % (index, length.get()))

                # Add tag around keyword if below conditions are satisfied
                if (
                    # Line contains only the keyword
                    (index.split(".")[1] == "0" and len(line) == int(index.split(".")[1]) + length.get()) or
                    # Keyword at start of line and ends in illegal
                    (index.split(".")[1] == "0" and line[int(index.split(".")[1]) + length.get()] in Page.illegals) or
                    # Keyword at end of line and starts with illegal
                    (len(line) == int(index.split(".")[1]) + length.get() and line[int(index.split(".")[1]) - 1] in Page.illegals) or
                    # Keyword in midst of line but starts and ends with illegal
                    (
                        (index.split(".")[1] != "0" and len(line) > int(index.split(".")[1]) + length.get()) and
                        (line[int(index.split(".")[1]) - 1] in Page.illegals and line[int(index.split(".")[1]) + length.get()] in Page.illegals)
                    )
                ):
                    t.tag_add("kw", "a", "b")

        # BUILT IN FUNCTION HIGHLIGHTING

        # Iterate over all python built in function identifiers
        for bi in Page.syntax["builtins"]:
            # Create variable for storing match length and create text pointers
            # (marks) with their initial position at the start of text field
            length = tk.IntVar()
            t.mark_set("a", "1.0")
            t.mark_set("b", "1.0")

            # Repeat until no more of matches of the current function are found
            while True:
                # Search for function in text field and break if none found
                index = t.search(bi, "b", "end", count=length)

                if index == "":
                    break

                line = t.get(index + " linestart", index + "lineend")

                # Move pointers/marks around function identifier
                t.mark_set("a", index)
                t.mark_set("b", "%s+%sc" % (index, length.get()))

                # Add tag around identifier if below conditions are satisfied
                if (
                    # Line contains only the function identifier
                    (index.split(".")[1] == "0" and len(line) == int(index.split(".")[1]) + length.get()) or
                    # Function identifier at start of line and ends in illegal
                    (index.split(".")[1] == "0" and line[int(index.split(".")[1]) + length.get()] in Page.illegals) or
                    # Function identifier at end of line and starts with
                    # illegal
                    (len(line) == int(index.split(".")[1]) + length.get() and line[int(index.split(".")[1]) - 1] in Page.illegals) or
                    # Function identifier in midst of line but starts and ends
                    # with illegal
                    (
                        (index.split(".")[1] != "0" and len(line) > int(index.split(".")[1]) + length.get()) and
                        (line[int(index.split(".")[1]) - 1] in Page.illegals and line[int(index.split(".")[1]) + length.get()] in Page.illegals)
                    )
                ):
                    t.tag_add("bi", "a", "b")

        # STRING HIGHLIGHTING (DOUBLE QUOTES)

        # Create text pointers (marks) with their initial position at the start
        # of text field
        t.mark_set("a", "1.0")
        t.mark_set("b", "1.0")

        # Repeat until no more of matches of double quotes are found
        while True:
            # Search for double quotes in text field and break if none found
            index = t.search("\"", "b", "end")

            if index == "":
                break
            else:
                # If double quotes are found search again from their position
                # to the end of the same line
                t.mark_set("a", index)
                t.mark_set("b", index + " lineend")

                index = t.search("\"", "a+1c", "b")

                # If no more double quotes are found on the same line highlight
                # the remainder of the line otherwise highlight between the
                # pair of double quotes
                if index == "":
                    t.tag_add("str", "a", "a lineend")
                else:
                    t.mark_set("b", index)
                    t.tag_add("str", "a", "b+1c")
                    t.mark_set("b", index + "+1c")

        # STRING HIGHLIGHTING (SINGLE QUOTES)

        # Create text pointers (marks) with their initial position at the start
        # of text field
        t.mark_set("a", "1.0")
        t.mark_set("b", "1.0")

        # Repeat until no more of matches of single quotes are found
        while True:
            # Search for single quotes in text field and break if none found
            index = t.search("'", "b", "end")

            if index == "":
                break
            else:
                # If a single quote is found search again from its position to
                # the end of the same line
                t.mark_set("a", index)
                t.mark_set("b", index + " lineend")

                index = t.search("'", "a+1c", "b")

                # If no more single quotes are found on the same line highlight
                # the remainder of the line otherwise highlight between the
                # pair of single quotes
                if index == "":
                    t.tag_add("str", "a", "a lineend")

                else:
                    t.mark_set("b", index)
                    t.tag_add("str", "a", "b+1c")
                    t.mark_set("b", index + "+1c")

        # COMMENT HIGHLIGHTING

        # Create text pointers (marks) with their initial position at the start
        # of text field
        t.mark_set("a", "1.0")
        t.mark_set("b", "1.0")

        # Repeat until no more of matches of hash signs are found
        while True:
            # Search for hash signs in text field and break if none found
            index = t.search("#", "b", "end")

            if index == "":
                break

            # Highlight the entire line from the hash symbol if there is an
            # even number of double/single quotes (or none) before it implying
            # the hash symbol is not part of a string and is in fact a comment
            if t.get(index + " linestart", index).count("\"") % 2 == 0 and t.get(index + " linestart", index).count("'") % 2 == 0:
                t.mark_set("a", index)
                t.mark_set("b", index + " lineend")
                t.tag_remove("str", "a", "b")
                t.tag_add("comment", "a", "b")
            else:
                t.mark_set("b", index + "+1c")
