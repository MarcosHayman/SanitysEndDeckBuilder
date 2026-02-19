# INSIGHT APPARATUS
#### A Sanity's End Deck Building tool

## What is Sanity's End?
Sanity's End is a Home-made TCG (HTCG) with horror and lovecraftian themes. You can find more information about the game on the official [YouTube Channel](https://www.youtube.com/@SanitysEndHTCG) or you can join us on [Discord](discord.gg/7g2CBKsxwk).

## What is this project?
Since the game is quite recent and it's still in it's early stages, there are no deck building tools available and I took upon myself to make one!

This is a simple Command Line Interface (CLI) application that works as an offline deck-building tool that uses the file [cards.db](cards.db) as a local database with the help of [Sqlite3](https://sqlite.org/quickstart.html).

## Requirements
To use this project you need to have [Python](https://www.python.org/) version 3.10 or higher installed in your system and a couple of pip packages installed. It's recommended that you use pip and a Virtual Enviroment to install the packages as it's explained in this [guide](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).
There's a [requirements.txt](requirements.txt) file to be used for this purpose.

### Installing the packages
In case you don't want to read or follow the guide,I'll give the essential steps for downloading the required packages

#### On Windows
Open the comand line in this folder and run the following command to create a virtual enviroment
``` bash
py -m venv .venv
```
You can then run the following command to activate the virtual enviroment
``` bash
.venv\Scripts\activate
```
While a virtual enviroment is active, python packages are installed locally in the .venv folder created with the creation of the virtual enviroment, this is important so there are no other compatibilities issues in this or other python projects.

While installing Python, pip is usually installed with it, you can check if it's up-to-date with the commands:
```bash
py -m pip install --upgrade pip
py -m pip --version
```
You can then install the packages with the command:
```bash
py -m pip install -r requirements.txt
```
#### On Unix/MacOs
Open the comand line in this folder and run the following command to create a virtual enviroment
``` bash
python3 -m venv .venv
```
You can then run the following command to activate the virtual enviroment
``` bash
source .venv/bin/activate
```
While a virtual enviroment is active, python packages are installed locally in the .venv folder created with the creation of the virtual enviroment, this is important so there are no other compatibilities issues in this or other python projects.

The Python installers for macOS include pip. On Linux, you may have to install an additional package such as python3-pip. You can make sure that pip is up-to-date by running:
```bash
python3 -m pip install --upgrade pip
python3 -m pip --version
```
You can then install the packages with the command:
```bash
python3 -m pip install --upgrade requests
```
### Using the Application
Once all dependencies are installed, activate the virtual enviroment (with the same command as on the installing packages section) and then simply run this command:
```bash
python main.py
```
To finally run the Deck Builder!
#### Importing and exporting decks

To import a Deck from untap, simply place the file in this folder and run the *Import Deck* command in the application.   
When exporting a deck, choose a Deck created in this in the *View Decks* section and select the *Export Deck* option.

** I didn't spend to much time on this, if you want to break it, you will be able to lol


