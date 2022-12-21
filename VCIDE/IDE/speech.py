# OCR A Level Computer Science Programming Project
# Voice Control Integrated Development Environment - speech.py
# Created by Riordan Gunn, May 2021
#
# This file contains the 'Speech' class which comprises all of the
# voice control handling functions.
#
# Required Modules:
#   page: Code editor file used to create a new tab in the main
#     window's notebook as a 'Page' object.
#   tkinter: GUI library used to display an error messagebox.
#   playsound: Simple Library which provides functionality to play
#     audio files such as the mic listening sound.
#   threading: Adds multithreading support so speech recognition can
#     run in its own thread to prevent the software from hanging.
#   speech_recognition: Library that uses the Google API to convert
#     microphone input to a string which can be processed.

from IDE.page import Page
from tkinter import messagebox
from playsound import playsound
from threading import Thread
import speech_recognition as sr


class Speech:
    # Voice control class which does not inherit from any class.
    #
    # The main window instantiates an object of this class upon
    # construction. The object stores a thread which runs the voice control
    # method concurrently with the main window and can be used to tell if
    # the software is undergoing voice control at any time. Can interpret
    # voice commands to interact with the code editor as it is a attribute
    # of the main window.

    def __init__(self, root):
        # Constructor method of voice control class.
        #
        # Makes the main window passed as a parameter an attribute so that
        # other methods of the class can access it. Also creates an empty
        # thread to be replaced as the start method must check if the thread is
        # alive (must be a Thread object as it contains the is_alive method).
        #
        # Parameters:
        #   root: The tkinter Tk object of the main window containing the UI
        #     elements to update and mic status attribute (micKilled).

        self.root = root
        self.thread = Thread()

    def recognize(self):
        # Speech capture and processing method used to perform voice commands.
        #
        # Captures input from the user's default microphone until silence is
        # detected, then attempts to convert to a string. Various exceptions
        # are handled and string is parsed to identify a command. Appropriate
        # action is taken and status is updated in the main window. This method
        # is executed in a new thread (by the start method) as it contains
        # blocking functions which will cause the main window to hang and be
        # unresponsive until listening and processing is complete.
        #
        # Accepts no parameters.

        recog = sr.Recognizer()

        # Attempt to create microphone object. Update status and return if no
        # microphone hardware is found
        try:
            mic = sr.Microphone()
        except OSError:
            messagebox.showerror("An error occurred during speech recognition", "Could not find a working microphone. Please connect one and try again.")
            self.root.micButton.config(image=self.root.nomicICO, text="Microphone Offline")
            self.root.statusbar.config(text="Microphone Offline")
            return

        # Update UI and play a sound to show the software is listening
        self.root.micButton.config(image=self.root.listenICO, text="Listening...")
        self.root.statusbar.config(text="Listening...")
        playsound("resources/mic.mp3")

        # Record sound until silent using microphone object into audio object
        with mic as micObj:
            # Blocking call until listening complete
            audio = recog.listen(micObj)

        # Update UI and play sound again once listening is complete or return
        # from method if the mic has been disabled during listening.
        if not self.root.micKilled.get():
            playsound("resources/mic.mp3")
            self.root.micButton.config(image=self.root.internetICO, text="Processing...")
            self.root.statusbar.config(text="Processing...")
        else:
            return

        # Attempt to transcribe captured audio to a string and catch errors
        try:
            # Blocking call until recognition complete
            said = recog.recognize_google(audio, language="en-GB").replace("open bracket", "(").replace("close bracket", ")").replace("colon", ":").replace("comma", ",")
        except sr.UnknownValueError:
            # Update UI and return if no
            self.root.micButton.config(image=self.root.micICO, text="Microphone Ready")
            self.root.statusbar.config(text="Couldn't Understand")
            return
        except sr.RequestError:
            # Update UI and return if the recognize request failed
            self.root.micButton.config(image=self.root.nointernetICO, text="Internet Offline")
            self.root.statusbar.config(text="Internet Offline")
            return

        # Update UI button to show the microphone is ready again and the status
        # bar to show what was transcribed
        self.root.micButton.config(image=self.root.micICO, text="Microphone Ready")
        self.root.statusbar.config(text="Heard: \"" + said + "\"")

        # said = "please move the cursor up by 7 places"

        # If the spoken command contains the word 'type' insert the proceeding
        # string to the code editor and update syntax highlighting
        if "type " in said and len(self.root.notebook.tabs()) > 0:
            self.root.notebook.nametowidget(self.root.notebook.select()).text.insert("insert", said[said.find("type ") + 5:])
            self.root.notebook.nametowidget(self.root.notebook.select()).syntaxHighlight()
        # If the spoken command contains the word 'cursor' get magnitude and
        # direction then move the cursor if valid
        elif "cursor " in said and len(self.root.notebook.tabs()) > 0:
            # Identify amount to move cursor or use 1 if unable to find number
            for word in said[said.find("cursor ") + 7:].split(" "):
                if word.isdigit():
                    by = word
                    break
            else:
                by = "1"

            # Move cursor to the right by specified number of places
            if "right" in said[said.find("cursor ") + 7:]:
                self.root.notebook.nametowidget(self.root.notebook.select()).text.mark_set("insert", "insert" + "+" + by + "c")
            # Move cursor to the left by specified number of places
            elif "left" in said[said.find("cursor ") + 7:]:
                self.root.notebook.nametowidget(self.root.notebook.select()).text.mark_set("insert", "insert" + "-" + by + "c")
            # Move cursor up the specified number of lines
            elif "up" in said[said.find("cursor ") + 7:]:
                self.root.notebook.nametowidget(self.root.notebook.select()).text.mark_set("insert", "insert" + "-" + by + "l")
            # Move cursor down the specified number of lines
            elif "down" in said[said.find("cursor ") + 7:]:
                self.root.notebook.nametowidget(self.root.notebook.select()).text.mark_set("insert", "insert" + "+" + by + "l")
            # Move cursor to the start of the line
            elif "start" in said[said.find("cursor ") + 7:] and "line" in said[said.find("cursor ") + 7:]:
                self.root.notebook.nametowidget(self.root.notebook.select()).text.mark_set("insert", "insert" + " linestart")
            # Move cursor to the end of the line
            elif "end" in said[said.find("cursor ") + 7:] and "line" in said[said.find("cursor ") + 7:]:
                self.root.notebook.nametowidget(self.root.notebook.select()).text.mark_set("insert", "insert" + " lineend")
            # Move cursor to the start of the file
            elif "start" in said[said.find("cursor ") + 7:]:
                self.root.notebook.nametowidget(self.root.notebook.select()).text.mark_set("insert", "0.0")
            # Move cursor to the end of the file
            elif "end" in said[said.find("cursor ") + 7:]:
                self.root.notebook.nametowidget(self.root.notebook.select()).text.mark_set("insert", "end")
        # If the spoken command contains the word 'save' call the save method
        # of the current tab to either save or save as
        elif "save" in said and len(self.root.notebook.tabs()) > 0:
            self.root.notebook.nametowidget(self.root.notebook.select()).save()
        # If the spoken command contains 'new/create/make' and 'tab' create a
        # new code editor object parented to the main window's notebook
        elif (("new" in said and "tab" in said) or ("create" in said and "tab" in said) or ("make" in said and "tab" in said)) and len(self.root.notebook.tabs()) > 0:
            Page(self.root.notebook, textFont=self.root.pageFont)
        # If the spoken command contains 'close/delete/remove' and 'tab' call
        # the close method of the current tab to close it prompting save if
        # required
        elif (("close" in said and "tab" in said) or ("delete" in said and "tab" in said) or ("remove" in said and "tab" in said)) and len(self.root.notebook.tabs()) > 0:
            self.root.notebook.nametowidget(self.root.notebook.select()).close()
        # If the spoken command contains the word 'open' create the open file
        # dialogue
        elif "open" in said and len(self.root.notebook.tabs()) > 0:
            self.root.openFileDialogue()
        # If the spoken command contains the word 'compile/run/execute' call
        # the run method of the current tab to execute the program
        elif ("compile" in said or "run" in said or "execute" in said) and len(self.root.notebook.tabs()) > 0:
            self.root.notebook.nametowidget(self.root.notebook.select()).run()

    def start(self):
        # Begin voice control method used to start and handle threads.
        #
        # Checks to see if the voice control thread belonging to the object is
        # not currently running and if the microphone is not disabled. If both
        # conditions are met, the thread object is overwritten with a new one
        # using the above blocking recognise function as its target and is
        # started. This is the main method that will be called to invoke voice
        # control.
        #
        # Accepts no parameters.

        if not self.thread.is_alive() and not self.root.micKilled.get():
            self.thread = Thread(target=self.recognize)
            self.thread.start()
