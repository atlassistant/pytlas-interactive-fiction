import os
from sure import expect
from pytlas.testing import create_skill_agent

# Testing a pytlas skill is easy.
# Start by instantiating an agent trained only for this skill.


class TestInteractiveFictionkill:

  def test_it_should_launch_the_skill(self):
    agent = create_skill_agent(os.path.dirname(__file__), lang='en')
    # Now, try to trigger our skill
    agent.parse('play interactive fiction')

    # And make assertions about how the model (the part between pytlas and the end user)
    # as answered: https://pytlas.readthedocs.io/en/latest/writing_skills/testing.html#writing-tests
    call = agent.model.on_answer.get_call()
    expect(call.text).to.equal('')
