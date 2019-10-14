pytlas-interactive-fiction [![Build Status](https://travis-ci.org/atlassistant/pytlas-interactive-fiction.svg?branch=master)](https://travis-ci.org/atlassistant/pytlas-interactive-fiction) ![License]( https://img.shields.io/badge/License-GPL%20v3-blue.svg)
===

This skill allow you to play interactive fiction in pytlas environnement, and so benefit the power of the  vocal command and intent detection with the huge interactive story library generated all along the decades with the wonderfull inform tools.

## Supported languages

- English

## Typical sentences

- Play the fiction LostPig.z8

## Installation

The skill is based on the curiousdannii' virtual z-machine ifvms ( see https://github.com/curiousdannii/ifvms.js ). 
To work properly this engine should be installed first.
This is a node.js based implementation. 
Install node.js and npm first if they aren't already installed
```
apt install nodejs, npm
```
Next intall ifvms.js
```
npm install -g ifvms
```
You should have ifvms installed.
You can verify it using the command
```
zvm -v
```
It should return the version


## Configuration

Your settings should contains a section 'interactive fiction' with the two next parameters
- zvm_path (optional, requiered if ifvms has not been globally installed) : Path to the virtual z-machine engine
- game_directory : Directory containing downloaded stories
- save_directory : Directory containing saved

## Launching tests

In order to launch tests, you will need to install required dependencies and then launch the test suite with:

```bash
$ pip install -r requirements_tests.txt
$ python -m nose --with-coverage --cover-package=pytlas-template
```
