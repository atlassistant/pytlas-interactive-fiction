import os
from sure import expect
from pytlas.testing import create_skill_agent
from pytlas.settings import CONFIG

# Testing a pytlas skill is easy.
# Start by instantiating an agent trained only for this skill.

praxix_response = \
"""

Praxix: A Z-code interpreter unit test
Release 1 / Serial number 180329 / Inform v6.31, compiler options S

A voice booooms out: Welcome to the test chamber.

Type "help" to repeat this message, "quit" to exit, "all" to run all tests, or one of the following test options: "operand", "arith", "comarith", "bitwise", "shift", "inc", "incchk", "array", "undo", "multiundo", "indirect", "streamtrip", "streamop", "throwcatch", "tables", "specfixes", "spec11", "spec12".
(Some tests check unspecified behaviour, and their results will be marked by (Unspecified).)


>
"""

class TestInteractiveFictionkill:

  def test_it_should_ask_for_game_save_folder(self):
    pass

  def test_it_should_failed_to_find_storie(self):
    pass
  
  def test_it_should_failed_to_find_zvm(self):
    pass

  def test_it_should_launch_the_storie(self):
    test_game_saves_folder_path = os.path.join(os.path.dirname(__file__),'test')
    test_stories_folder_path = os.path.join(os.path.dirname(__file__),'test')
    CONFIG.set('game_saves_folder',test_game_saves_folder_path,section='interactive_fiction')
    CONFIG.set('stories_folder',test_stories_folder_path,section='interactive_fiction')
    agent = create_skill_agent(os.path.dirname(__file__), lang='en')
    agent.parse("play interactive fiction named praxix.z5")
    call = agent.model.on_answer.get_call()
    expect(call.text).to.equal(praxix_response)
