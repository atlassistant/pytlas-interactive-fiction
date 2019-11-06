import os
from sure import expect
from pytlas.settings import CONFIG
from pytlas.testing import create_skill_agent

# Testing a pytlas skill is easy.
# Start by instantiating an agent trained only for this skill.

test_response = \
"""



Test
An Interactive Fiction by lekstonjm
Release 1 / Serial number 191106 / Inform 7 build 6M62 (I6/v6.33 lib 6/12N) 

World
Hello world!

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
    CONFIG.reset()
    CONFIG.set('game_saves_folder',test_game_saves_folder_path,section='interactive_fiction')
    CONFIG.set('stories_folder',test_stories_folder_path,section='interactive_fiction')
    agent = create_skill_agent(os.path.dirname(__file__), lang='en')
    agent.parse("play interactive fiction named Test.zblorb")
    call = agent.model.on_answer.get_call()
    expect(call.text).to.equal(test_response)
