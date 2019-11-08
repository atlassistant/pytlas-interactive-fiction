import os
import sys
import subprocess
import time
import select
from pytlas import training, translations, intent, meta
from pytlas.handling.hooks import on_agent_created, on_agent_destroyed

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
      super().__init__(infile, outfile)
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

@training('en')
def en_data(): return """
%[start_interactive_fiction]
  play interactive fiction
  let's play to an interactive fiction
  start the interactive fiction named @[filename]

@[filename]
  filename.zblorb
  filename.z5
  filename.z8
"""

"""
%[interactive_fiction/quit]
  I quit now

%[interactive_fiction/save]
  could you save the game to @[save_name]

%[interactive_fiction/restore]
  could you restore the game @[save_name]

@[filename]
  LostPig.z8

@[save_name]
  in_the_wood
"""

@meta()
def skill_meta(_): return {
  'name': _('interactive fiction skill'),
  'description': _('Play inform interactive fiction'),
  'author': 'atlassistant',
  'version': '1.0.0',
  'homepage': 'https://github.com/atlassistant/pytlas-template',
}

agents = {}


def clean(agt):
  global agents
  if agt.id in agents:
    agents[agt.id]["game_state"] = None
    proc = agents[agt.id]["proc"]
    if proc != None:
      proc.stdin.close()
      proc.stdout.close()
      proc.kill()
      proc.poll()
    agents[agt.id]["proc"] = None
    agents.pop(agt.id,None)


@on_agent_created()
def when_an_agent_is_created(agt):
  # On conserve une référence à l'agent
  global agents
  agents[agt.id] = {"proc":None,"game_state":None}

@on_agent_destroyed()
def when_an_agent_is_destroyed(agt):
  # On devrait clear les timers pour l'agent à ce moment là
  global agents
  clean(agt)

@intent('start_interactive_fiction')
def on_start_interactive_fiction(req):
  global agents
  agent_id = req.agent.id
  if not agent_id in agents:
    when_an_agent_is_created(req.agent)

  zvm_path = req.agent.settings.get('zvm_path', section='interactive_fiction')
  zvm_path = "zvm" if not zvm_path else zvm_path
  game_saves_folder = req.agent.settings.get('game_saves_folder', section='interactive_fiction')
  req.agent._logger.info(req.agent.settings._data)
  if game_saves_folder == None:
    empty_game_saves_folder_confirmed = req.intent.slot('empty_game_saves_folder_confirmed').first().value
    if empty_game_saves_folder_confirmed == None:
      return req.agent.ask('empty_game_saves_folder_confirmed',\
        req._('Game saves folder has not been set. Your game saves will be writen in the current folder "{0}".\nDo you want continue?').format(os.getcwd()),\
        ['yes','no'])
    if empty_game_saves_folder_confirmed == 'no':
      req.agent.done()
      return
    else:
      game_saves_folder  = os.getcwd()

  stories_folder = req.agent.settings.get('stories_folder', section='interactive_fiction')
  if stories_folder == None:
    empty_stories_folder_confirmed = req.intent.slot('empty_stories_folder_confirmed').first().value
    if empty_stories_folder_confirmed == None:
      return req.agent.ask('empty_stories_folder_confirmed',\
        req._('Stories folder has not been set. Stories will be load from the current folder "{0}".\nDo you want continue?').format(os.getcwd()),\
        ['yes','no'])
    if empty_stories_folder_confirmed == 'no':
      req.agent.done()
      return
    else:
      stories_folder  = os.getcwd()

  story_filename = req.intent.slot('filename').first().value
  if not story_filename:
    req.agent.ask('filename',req._('Wich fiction would you play?'))

  story_path = os.path.join(stories_folder,story_filename)
  if not os.path.isfile(story_path):    
    req.agent.answer(req._('Sorry, no story named {0} has been found in {1}.'.format(story_filename, stories_folder)))
    req.agent.done()
    return

  args = [zvm_path]+[story_path]
  try:
    proc = subprocess.Popen(args,
                        bufsize=0,
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        cwd=game_saves_folder)
  except Exception as ex:
    req.agent.answer(req._('Unable to start {0} : {1}'.format(zvm_path, ex)))
    req.agent.done()
    return
  if not proc:
    req.agent.answer(req._('Unable to start {0}'.format(zvm_path)))
    req.agent.done()
    return
  game_state = GameStateCheap(proc.stdin, proc.stdout, 1.0, False)
  game_state.initialize()
  res = game_state.accept_output()
  agents[agent_id]["proc"] = proc
  agents[agent_id]["game_state"] = game_state 
  req.agent.context('interactive_fiction')
  req.agent.answer(req._(res))
  req.agent.done()

"""
@intent('interactive_fiction/save')
def on_save(req):
  global agents
  agent_id = req.agent.id
  if not agent_id in agents:
    req.agent.answer("Panic! No game found")
    req.agent.done()
    return

  game_state = agents[agent_id]["game_state"]

  save_name = req.intent.slot('save_name').first().value
  if not save_name:
    req.agent.ask('save_name',req._('Please enter a name'))
  #game_state.perform_input(SimpleCommand("save"))
  #game_state.perform_input(SimpleCommand(save_name))
  res = game_state.accept_output()
  logging.getLogger("interactive_fiction").info(res)
  req.agent.answer(req._(res))
  req.agent.done()  

@intent('interactive_fiction/restore')
def on_restore(req):
  global agents
  agent_id = req.agent.id
  if not agent_id in agents:
    req.agent.answer("Panic! No game found")
    req.agent.done()
    return

  game_state = agents[agent_id]["game_state"]

  save_name = req.intent.slot('save_name').first().value
  if not save_name:
    req.agent.ask('save_name',req._('Please enter a name'))
  #game_state.perform_input(SimpleCommand("restore"))
  #game_state.perform_input(SimpleCommand(save_name))
  res = game_state.accept_output()
  logging.getLogger("interactive_fiction").info(res)
  req.agent.answer(req._(res))
  req.agent.done()  

@intent('interactive_fiction/quit')
def on_quit(req):
  clean(req.agent)
  req.agent.context(None)
  req.agent.answer(req._('Goodbye'))
  req.agent.done()

@intent('interactive_fiction/__fallback__')
def on_standard_input(req):
  global agents
  agent_id = req.agent.id
  if not agent_id in agents:
    req.agent.answer("Panic! No game found")
    req.agent.done()
    return

  game_state = agents[agent_id]["game_state"]

  content = req.intent.slot('text').first().value
  #game_state.perform_input(SimpleCommand(content))
  res = game_state.accept_output()
  req.agent.answer(req._(res))
  req.agent.done()
"""