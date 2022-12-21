# Voice Control IDE

A simple text editor for writing Python using your voice.

With VCIDE, using only your voice and a microphone, you can create and edit Python programs by speaking commands to your computer. All of the usual features of a text editor can be accessed in the conventional way via mouse and keyboard but also using hands-free speech recognition to aid development for those who may not be able to use traditional input devices or those who wish to experiment with a new way of programming. VCIDE will feel familiar to users of IDLE, the IDE packaged with Python, while also providing a more comprehensive interface featuring a file system browser and toolbar. Taking advantage of the Google Cloud Speech API, voice commands are interpreted quickly and accurately to make the development experience as smooth as possible. Simply press the right hand shift key, wait for the audible tone and begin writing software with your voice!

## Features
* Fast and accurate speech recognition powered by Google
* Intuitive voice commands for a natural programming experience
* Full featured file system browser
* Real time Python syntax highlighting
* Auto indent following colons and previous indents
* Ability to toggle microphone on/off
* Microphone status (Ready/Listening/Processing/Offline)
* Font configurable to meet your needs

## Example Commands
* `"Type 'for i in range open bracket 1 comma 100 close bracket colon'"`
* `"Shift the cursor up by seven places"`
* `"Move the cursor left"`
* `"Place the cursor at the end of the line"`
* `"Send the cursor to the start of the file"`
* `"Save the document"`
* `"Create a new tab"`
* `"Close the current tab"`
* `"Open a file"`
* `"Execute the program"`

## Required Libraries
* [**SpeechRecognition**](https://pypi.org/project/SpeechRecognition/) - Library to interface with the Google Cloud Speech API to turn sound into text
* [**playsound**](https://pypi.org/project/playsound/) - Library to play audio files on many platforms

## Screenshot
![screenshot](https://user-images.githubusercontent.com/45309105/209005428-8c8aedf6-91dd-4a5b-80ec-774cc3fcc13d.png)
