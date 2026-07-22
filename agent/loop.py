from cli.interface import getPrompt, display
from agent.agent import Agent

def runAgentLoop(agent: Agent):
    while True:
        prompt = getPrompt()

        if prompt == 'exit':
            print('Goodbye..')
            break

        # thinking
        resposne = agent.step(prompt)
        display(resposne)