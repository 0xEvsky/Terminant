from cli.interface import getPrompt, display
from agent.agent import Agent

def runAgentLoop(agent: Agent):
    while True:
        prompt = getPrompt()

        if prompt == 'exit':
            print('Goodbye..')
            break
        
        elif prompt == '/agent':
            agent.agent_mode = True

        resposne = agent.step(prompt)
        display(resposne)