from tools.base import Tool

from ._common import open_repo, status_snapshot


class GitStash(Tool):
    @property
    def name(self):
        return "git.stash"

    @property
    def description(self):
        return "save, apply, pop, list, or drop work-in-progress changes"

    @property
    def arguments(self):
        return {
            "repo_path": {
                "type": "string",
                "description": "path to the git repository (default: current directory)",
                "required": False,
                "default": ".",
            },
            "action": {
                "type": "string",
                "description": "stash action: save, apply, pop, list, drop, clear, or show",
                "required": False,
                "default": "save",
            },
            "message": {
                "type": "string",
                "description": "optional stash message when saving",
                "required": False,
                "default": None,
            },
            "stash_ref": {
                "type": "string",
                "description": "stash reference like stash@{0}",
                "required": False,
                "default": "stash@{0}",
            },
        }

    def execute(self, **kwargs):
        repo_path = kwargs.get("repo_path", ".")
        action = kwargs.get("action", "save")
        message = kwargs.get("message")
        stash_ref = kwargs.get("stash_ref", "stash@{0}")

        repo, error = open_repo(repo_path)
        if error:
            return error

        try:
            if action == "save":
                command = ["push"]
                if message:
                    command.extend(["-m", message])
                result = repo.git.stash(*command)
            elif action == "apply":
                result = repo.git.stash("apply", stash_ref)
            elif action == "pop":
                result = repo.git.stash("pop", stash_ref)
            elif action == "drop":
                result = repo.git.stash("drop", stash_ref)
            elif action == "clear":
                result = repo.git.stash("clear")
            elif action == "show":
                result = repo.git.stash("show", stash_ref)
            elif action == "list":
                result = repo.git.stash("list")
            else:
                return {"error": f"Unsupported stash action: {action}"}

            return {
                "action": action,
                "stash_ref": stash_ref,
                "result": result,
                **status_snapshot(repo),
            }
        except Exception as exc:
            return {"error": str(exc)}
