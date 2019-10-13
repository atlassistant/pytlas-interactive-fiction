pytlas-interactive-fiction [![Build Status](https://travis-ci.org/atlassistant/pytlas-interactive-fiction.svg?branch=master)](https://travis-ci.org/atlassistant/pytlas-interactive-fiction) ![License]( https://img.shields.io/badge/License-GPL%20v3-blue.svg)
===

WORK IN PROGRESS

## Supported languages

*Write down all languages supported by your skill below:*

- English

## Typical sentences

*Write some examples of how a user may trigger and interact with your skill:*

- Play the fiction LostPig.z8

## Configuration

- zvm_path : Path to the virtual z-machine ( see  https://github.com/curiousdannii/ifvms.js )
- game_directory : Directory containing downloaded stories

## Launching tests

In order to launch tests, you will need to install required dependencies and then launch the test suite with:

```bash
$ pip install -r requirements_tests.txt
$ python -m nose --with-coverage --cover-package=pytlas-template
```
