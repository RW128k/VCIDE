# OCR A Level Computer Science Programming Project
# Voice Control Integrated Development Environment - main.py
# Created by Riordan Gunn, May 2021
#
# This file creates an object of the main window class and starts its
# event loop. Essentially launches the program.
#
# Required Modules:
#   app: Main window file used to start the program.

from IDE.app import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
