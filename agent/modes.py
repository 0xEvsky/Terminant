from dataclasses import dataclass

@dataclass
class AgentMode:
    ...

@dataclass
class ManualMode(AgentMode):
    ...

@dataclass
class AutoMode(AgentMode):
    ...

