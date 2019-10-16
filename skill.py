from pytlas import training, translations, intent, meta
import sys
import os
import subprocess
import logging
import time
import select

#
# GameState and GameStateCheap
# have been  extracted and adapted from https://raw.githubusercontent.com/erkyrath/plotex/master/regtest.py
# This script is in the public domaine <see http://eblong.com/zarf/plotex/regtest.html> for details  
#

class SimpleCommand:
  def __init__(self, text):
    self.cmd = text
    self.type = 'line'

class GameState:
    """The GameState class wraps the connection to the interpreter subprocess
    (the pipe in and out streams). It's responsible for sending commands
    to the interpreter, and receiving the game output back.

    Currently this class is set up to manage exactly one each of story,
    status, and graphics windows. (A missing window is treated as blank.)
    This is not very general -- we should understand the notion of multiple
    windows -- but it's adequate for now.

    This is a virtual base class. Subclasses should customize the
    initialize, perform_input, and accept_output methods.
    """
    def __init__(self, infile, outfile):
        self.infile = infile
        self.outfile = outfile
        # Lists of strings
        self.statuswin = []
        self.graphicswin = []
        self.storywin = []
        # Lists of line data lists
        self.statuswindat = []
        self.graphicswindat = []
        self.storywindat = []

    def initialize(self):
        pass

    def perform_input(self, cmd):
        raise Exception('perform_input not implemented')
        
    def accept_output(self):
        raise Exception('accept_output not implemented')

class GameStateCheap(GameState):
    """Wrapper for a simple stdin/stdout (dumb terminal) interpreter.
    This class never fills in the status window -- that's always blank.
    It can only handle line input (not character input).
    """
    def __init__(self, infile, outfile,timeout_secs, verbose):
      GameState.__init__(self,infile, outfile)
      self.timeout_secs = timeout_secs
      self.verbose = verbose

    def perform_input(self, cmd):
        if cmd.type != 'line':
            raise Exception('Cheap mode only supports line input')
        self.infile.write((cmd.cmd+'\n').encode())
        self.infile.flush()

    def accept_output(self):
        self.storywin = []
        output = bytearray()
        _output = bytearray()
        
        timeout_time = time.time() + self.timeout_secs

        while (select.select([self.outfile],[],[],self.timeout_secs)[0] != []):
            ch = self.outfile.read(1)
            if ch == b'':
                break
            _output += ch
            if (_output[-2:] == b'\n>'):
                break
            output += ch

        if time.time() >= timeout_time:
            raise Exception('Timed out awaiting output')
            
        dat = output.decode('utf-8')
        res = dat.split('\n')
        if (self.verbose):
            for ln in res:
                if (ln == '>'):
                    continue
                print(ln)
        self.storywin = res
        return dat.strip()


proc = None
game_state = None

# Hey there o/
# Glad you're taking some times to make a skill for the pytlas assistant!
# Here is all you have to know to make your own skills, let's go!

# Start by defining training data used to trigger your skill.
# Here we are defining the TEMPLATE_SKILL_INTENT with some training data.
# In english:

@training('en')
def en_training(): return """
%[start_interactive_fiction]
  let's play to an interactive fiction
  open the fiction @[filename]
  start the fiction @[filename]

%[interactive_fiction/quit]
  quit

%[interactive_fiction/save]
  save @[save_name]

%[interactive_fiction/restore]
  restore @[save_name]

@[filename]
  LostPig.z8
  minizork.z3

@[save_name]
  save1
  my_save
"""

# Let's define some metadata for this skill. This step is optional but enables
# pytlas to list loaded skills with more informations:

@meta()
def skill_meta(_): return {
  'name': _('interactive fiction skill'),
  'description': _('Play inform interactive fiction'),
  'author': 'atlassistant',
  'version': '1.0.0',
  'homepage': 'https://github.com/atlassistant/pytlas-template',
}

# The final part is your handler registered to be called upon TEMPLATE_SKILL_INTENT
# recognition by the pytlas interpreter.

@intent('start_interactive_fiction')
def on_start_interactive_fiction(req):
  global proc
  global game_state
  zvm_path = req.agent.settings.get('zvm_path', section='interactive fiction')
  zvm_path = "zvm" if not zvm_path else zvm_path
  save_directory = req.agent.settings.get('save_directory', section='interactive fiction')
  if save_directory == None:
    empty_save_directory_confirmed = req.intent.slot('empty_save_directory_confirmed').first().value
    if empty_save_directory_confirmed == None:
      return req.agent.ask('empty_save_directory_confirmed',\
        req._('Save directory has not been set.You can set the save directory in the pytlas settings under the item "save_directory" in the "interactive section".\nYour game save will be writen in the current directory "{0}".\nDo you want continue?').format(os.getcwd()),\
        ['yes','no'])
    if not empty_save_directory_confirmed:
      req.agent.done()
      return
    else:
      save_directory  = os.getcwd()

  story_directory = req.agent.settings.get('story_directory', section='interactive fiction')
  if story_directory == None:
    empty_story_directory_confirmed = req.intent.slot('empty_story_directory_confirmed').first().value
    if empty_story_directory_confirmed == None:
      return req.agent.ask('empty_story_directory_confirmed',\
        req._('Story directory has not been set.You can set the story directory in the pytlas settings under the item "story_directory" in the "interactive section".\nStories will be searched in the current directory "{0}".\nDo you want continue?').format(os.getcwd()),\
        ['yes','no'])
    if not empty_story_directory_confirmed:
      req.agent.answer(req._(''))
      req.agent.done()
      return
    else:
      story_directory  = os.getcwd()

  story_filename = req.intent.slot('filename').first().value
  if not story_filename:
    req.agent.ask('filename',req._('Wich fiction would you play?'))

  story_path = os.path.join(story_directory,story_filename)
  if not os.path.isfile(story_path):    
    req.agent.answer(req._('Sorry, no story named {0} has been found in {1}.'.format(story_filename, story_directory)))
    req.agent.done

  args = [zvm_path]+[story_path]
  try:
    proc = subprocess.Popen(args,
                        bufsize=0,
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        cwd=save_directory)
  except Exception as ex:
    req.agent.answer(req._('Unable to start {0} : {1}'.format(zvm_path, ex)))
    req.agent.done
  if not proc:
    req.agent.answer(req._('Unable to start {0}'.format(zvm_path)))
    req.agent.done


  game_state = GameStateCheap(proc.stdin, proc.stdout, 1.0, False)
  game_state.initialize()
  res = game_state.accept_output()
  req.agent.context('interactive_fiction')
  req.agent.answer(req._(res))
  req.agent.done()

@intent('interactive_fiction/save')
def on_save(req):
  global proc
  global game_state
  save_name = req.intent.slot('save_name').first().value
  if not save_name:
    req.agent.ask('save_name',req._('Please enter a name'))
  game_state.perform_input(SimpleCommand("save"))
  game_state.perform_input(SimpleCommand(save_name))
  res = game_state.accept_output()
  logging.getLogger("interactive_fiction").info(res)
  req.agent.answer(req._(res))
  req.agent.done()  

@intent('interactive_fiction/restore')
def on_restore(req):
  global proc
  global game_state
  save_name = req.intent.slot('save_name').first().value
  if not save_name:
    req.agent.ask('save_name',req._('Please enter a name'))
  game_state.perform_input(SimpleCommand("restore"))
  game_state.perform_input(SimpleCommand(save_name))
  res = game_state.accept_output()
  logging.getLogger("interactive_fiction").info(res)
  req.agent.answer(req._(res))
  req.agent.done()  

@intent('interactive_fiction/quit')
def on_quit(req):
  global proc
  global game_state
  game_state = None
  proc.stdin.close()
  proc.stdout.close()
  proc.kill()
  proc.poll()
  req.agent.context(None)
  req.agent.answer(req._('Goodbye'))
  req.agent.done()

@intent('interactive_fiction/__fallback__')
def on_standard_input(req):
  global proc
  global game_state
  content = req.intent.slot('text').first().value
  game_state.perform_input(SimpleCommand(content))
  res = game_state.accept_output()
  req.agent.answer(req._(res))
  req.agent.done()