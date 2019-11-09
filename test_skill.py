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
Release 1 / Serial number 191109 / Inform 7 build 6M62 (I6/v6.33 lib 6/12N) 

World
Test room

You can see a Poster here.
"""

class TestInteractiveFictionkill:

  def test_it_should_ask_for_game_saves_folder(self):
    agent = create_skill_agent(os.path.dirname(__file__), lang='en')
    agent.settings.reset()
    agent.parse("play interactive fiction named Test.zblorb")
    call = agent.model.on_ask.get_call()
    expect(call.text).to.equal('Game saves folder has not been set. Your game saves will be writen in the current folder "{0}".\nDo you want continue?'.format(os.getcwd()))

  def test_it_should_failed_to_find_stories_folder(self):
    test_game_saves_folder_path = os.path.join(os.path.dirname(__file__),'test')
    agent = create_skill_agent(os.path.dirname(__file__), lang='en')
    agent.settings.reset()
    agent.settings.set('game_saves_folder',test_game_saves_folder_path,section='interactive_fiction')
    agent.parse("play interactive fiction named Test.zblorb")
    call = agent.model.on_ask.get_call()
    expect(call.text).to.equal('Stories folder has not been set. Stories will be load from the current folder "{0}".\nDo you want continue?'.format(os.getcwd()))

  def test_it_should_failed_to_find_story(self):
    test_game_saves_folder_path = os.path.join(os.path.dirname(__file__),'test')
    test_stories_folder_path = os.path.join(os.path.dirname(__file__),'test/test.materials/Release')
    agent = create_skill_agent(os.path.dirname(__file__), lang='en')
    agent.settings.reset()
    agent.settings.set('game_saves_folder',test_game_saves_folder_path,section='interactive_fiction')
    agent.settings.set('stories_folder',test_stories_folder_path,section='interactive_fiction')
    agent.parse("play interactive fiction named invalid.zblorb")
    call = agent.model.on_answer.get_call()
    expect(call.text).to.equal('Sorry, no story named {0} has been found in {1}.'.format('invalid.zblorb', test_stories_folder_path))

  def test_it_should_failed_to_find_zvm(self):
    test_zvm_path = os.path.join(os.path.dirname(__file__),'invalid_zvm')
    test_game_saves_folder_path = os.path.join(os.path.dirname(__file__),'test')
    test_stories_folder_path = os.path.join(os.path.dirname(__file__),'test/test.materials/Release')
    agent = create_skill_agent(os.path.dirname(__file__), lang='en')
    agent.settings.reset()
    agent.settings.set('zvm_path',test_zvm_path,section='interactive_fiction')
    agent.settings.set('game_saves_folder',test_game_saves_folder_path,section='interactive_fiction')
    agent.settings.set('stories_folder',test_stories_folder_path,section='interactive_fiction')
    agent.parse("play interactive fiction named Test.zblorb")
    call = agent.model.on_answer.get_call()
    expect(call.text).to.equal('Unable to start {0}'.format(test_zvm_path))
  
  def test_it_should_launch_the_storie(self):
    test_game_saves_folder_path = os.path.join(os.path.dirname(__file__),'test')
    test_stories_folder_path = os.path.join(os.path.dirname(__file__),'test/test.materials/Release')
    agent = create_skill_agent(os.path.dirname(__file__), lang='en')
    agent.settings.reset()
    agent.settings.set('game_saves_folder',test_game_saves_folder_path,section='interactive_fiction')
    agent.settings.set('stories_folder',test_stories_folder_path,section='interactive_fiction')
    agent.parse("play interactive fiction named Test.zblorb")
    call = agent.model.on_answer.get_call()
    expect(call.text).to.equal(test_response.strip())

  def test_it_should_display_hello_world(self):
    test_game_saves_folder_path = os.path.join(os.path.dirname(__file__),'test')
    test_stories_folder_path = os.path.join(os.path.dirname(__file__),'test/test.materials/Release')
    agent = create_skill_agent(os.path.dirname(__file__), lang='en')
    agent.settings.reset()
    agent.settings.set('game_saves_folder',test_game_saves_folder_path,section='interactive_fiction')
    agent.settings.set('stories_folder',test_stories_folder_path,section='interactive_fiction')
    agent.parse("play interactive fiction named Test.zblorb")
    agent.parse('read the Poster')
    call = agent.model.on_answer.get_call()
    expect(call.text).to.equal("read the Poster\nHello world!")

  def test_it_should_save_game(self):
    test_game_saves_folder_path = os.path.join(os.path.dirname(__file__),'test')
    test_stories_folder_path = os.path.join(os.path.dirname(__file__),'test/test.materials/Release')
    game_save_name = 'test_save'
    game_save_filename = '{0}.{1}'.format(game_save_name, 'glksave')
    game_save_path = os.path.join(test_game_saves_folder_path, game_save_filename) 
    if os.path.isfile(game_save_path):
      os.remove(game_save_path)      
    agent = create_skill_agent(os.path.dirname(__file__), lang='en')
    agent.settings.reset()
    agent.settings.set('game_saves_folder',test_game_saves_folder_path,section='interactive_fiction')
    agent.settings.set('stories_folder',test_stories_folder_path,section='interactive_fiction')
    agent.parse("play interactive fiction named Test.zblorb")
    agent.parse("save the game as {0}".format(game_save_name))
    call = agent.model.on_answer.get_call()
    is_file = os.path.isfile(game_save_path)
    if is_file:
      os.remove(game_save_path)      
    expect(is_file).to.equal(True)
    expect(call.text).to.equal("save\n\nPlease enter a file name (without an extension): Ok.")

  def test_it_should_failed_to_restore_saved_game(self):
    test_game_saves_folder_path = os.path.join(os.path.dirname(__file__),'test')
    test_stories_folder_path = os.path.join(os.path.dirname(__file__),'test/test.materials/Release')
    game_save_name = 'invalid_test_save'
    game_save_filename = '{0}.{1}'.format(game_save_name, 'glksave')
    game_save_path = os.path.join(test_game_saves_folder_path, game_save_filename) 
    if os.path.isfile(game_save_path):
      os.remove(game_save_path)      
    agent = create_skill_agent(os.path.dirname(__file__), lang='en')
    agent.settings.reset()
    agent.settings.set('game_saves_folder',test_game_saves_folder_path,section='interactive_fiction')
    agent.settings.set('stories_folder',test_stories_folder_path,section='interactive_fiction')
    agent.parse("play interactive fiction named Test.zblorb")
    agent.parse("restore the game {0}".format(game_save_name))
    call = agent.model.on_answer.get_call()
    expect(call.text).to.equal("restore\n\nPlease enter a file name (without an extension): Restore failed.")

  def test_it_should_restore_saved_game(self):
    test_game_saves_folder_path = os.path.join(os.path.dirname(__file__),'test')
    test_stories_folder_path = os.path.join(os.path.dirname(__file__),'test/test.materials/Release')
    game_save_name = 'test_save'
    game_save_filename = '{0}.{1}'.format(game_save_name, 'glksave')
    game_save_path = os.path.join(test_game_saves_folder_path, game_save_filename) 
    if os.path.isfile(game_save_path):
      os.remove(game_save_path)      
    agent = create_skill_agent(os.path.dirname(__file__), lang='en')
    agent.settings.reset()
    agent.settings.set('game_saves_folder',test_game_saves_folder_path,section='interactive_fiction')
    agent.settings.set('stories_folder',test_stories_folder_path,section='interactive_fiction')
    agent.parse("play interactive fiction named Test.zblorb")
    agent.parse("save the game as {0}".format(game_save_name))
    agent.parse("restore the game {0}".format(game_save_name))
    call = agent.model.on_answer.get_call()
    if os.path.isfile(game_save_path):
      os.remove(game_save_path)      
    expect(call.text).to.equal("restore\n\nPlease enter a file name (without an extension): Ok.")

  def test_it_should_quit_the_game(self):
    test_game_saves_folder_path = os.path.join(os.path.dirname(__file__),'test')
    test_stories_folder_path = os.path.join(os.path.dirname(__file__),'test/test.materials/Release')
    agent = create_skill_agent(os.path.dirname(__file__), lang='en')
    agent.settings.reset()
    agent.settings.set('game_saves_folder',test_game_saves_folder_path,section='interactive_fiction')
    agent.settings.set('stories_folder',test_stories_folder_path,section='interactive_fiction')
    agent.parse("play interactive fiction named Test.zblorb")
    agent.parse('quit the game')
    call = agent.model.on_answer.get_call()
    expect(call.text).to.equal('Goodbye')

