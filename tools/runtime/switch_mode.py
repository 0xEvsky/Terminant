from tools.base import Tool

class SwitchMode(Tool):
    @property
    def name(self):
        return 'Mode'

    @property
    def description(self):
        return 'Switches agent mode to <mode>'

    @property
    def arguments(self):
        return {
            "mode": {
                "type": "string"
            }
        }