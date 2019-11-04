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