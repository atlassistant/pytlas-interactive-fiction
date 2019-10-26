pytlas-interactive-fiction [![Build Status](https://travis-ci.org/atlassistant/pytlas-interactive-fiction.svg?branch=master)](https://travis-ci.org/atlassistant/pytlas-interactive-fiction) ![License]( https://img.shields.io/badge/License-GPL%20v3-blue.svg)
===

This skill allow you to play interactive fiction in pytlas environnement, and so combine the easy of use of pytlas assistant with wonderfull interactive stories from the huge library generated all along the decades with the great inform tools.

## Supported languages

- English

## Typical sentences

- Play the fiction LostPig.z8
- Save to my_save
- Restore my_save

## Installation

The skill is based on the fantastic curiousdannii' virtual z-machine ifvms ( see https://github.com/curiousdannii/ifvms.js ). 

To work properly this engine should be installed first.
Install node.js and npm first if they aren't already installed
```
apt install nodejs, npm
```
Next, install ifvms.js
```
npm install -g ifvms
```
You should have ifvms installed. You can verify it using the command
```
zvm -v
```
This should return the z virtual machine version. 

We advise you to create a folder containing your downloaded stories and eventually another folder containing your game saves. You should give read access to the first and read/write access to the second to the account running pytlas.

You can search and freely download lot of fictions from https://ifdb.tads.org/
 

## Configuration

Your pytlas settings should contains a section 'interactive fiction' with the next parameters:
- zvm_path : Path to the virtual z-machine engine. This setting is optional if you had installed "ifvms" globally. In this case zvm should be in the environment path.
- game_directory : The path of the folder containing downloaded stories. This is where pytlas look for a requested story. The account executing  pytlas must have at least a read access on this folder. This setting is optional. By default pytlas use the current folder.
- save_directory : The path of the folder containing your game saves, this is where pytlas save and restore your game saves. The account executing pytlas must have read/write access. This setting is optional. By default game saves are writen in the current folder.

## Launching tests

In order to launch tests, you will need to install required dependencies and then launch the test suite with:

```bash
$ pip install -r requirements_tests.txt
$ python -m nose --with-coverage --cover-package=pytlas-template
```
