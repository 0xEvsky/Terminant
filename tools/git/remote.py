from tools.base import Tool

from ._common import open_repo


class GitRemote(Tool):
    @property
    def name(self):
        return "git.remote"

    @property
    def description(self):
        return "list, add, remove, rename, or update git remotes"

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
                "description": "remote action: list, add, remove, rename, set_url, get_url, fetch",
                "required": False,
                "default": "list",
            },
            "name": {
                "type": "string",
                "description": "remote name",
                "required": False,
                "default": None,
            },
            "url": {
                "type": "string",
                "description": "remote url",
                "required": False,
                "default": None,
            },
            "new_name": {
                "type": "string",
                "description": "replacement name when renaming a remote",
                "required": False,
                "default": None,
            },
        }

    def execute(self, **kwargs):
        repo_path = kwargs.get("repo_path", ".")
        action = kwargs.get("action", "list")
        name = kwargs.get("name")
        url = kwargs.get("url")
        new_name = kwargs.get("new_name")

        repo, error = open_repo(repo_path)
        if error:
            return error

        try:
            if action == "list":
                remotes = []
                for remote in repo.remotes:
                    remotes.append(
                        {
                            "name": remote.name,
                            "urls": list(remote.urls),
                            "refs": [ref.name for ref in remote.refs if ref.remote_head != "HEAD"],
                        }
                    )
                return {"action": action, "remotes": remotes}

            if action == "add":
                if not name or not url:
                    return {"error": "name and url are required"}
                remote = repo.create_remote(name, url)
                return {"action": action, "name": remote.name, "url": url}

            if action == "remove":
                if not name:
                    return {"error": "name is required"}
                repo.delete_remote(name)
                return {"action": action, "name": name}

            if action == "rename":
                if not name or not new_name:
                    return {"error": "name and new_name are required"}
                remote = repo.remotes[name]
                remote.rename(new_name)
                return {"action": action, "name": name, "new_name": new_name}

            if action == "set_url":
                if not name or not url:
                    return {"error": "name and url are required"}
                repo.git.remote("set-url", name, url)
                return {"action": action, "name": name, "url": url}

            if action == "get_url":
                if not name:
                    return {"error": "name is required"}
                remote = repo.remotes[name]
                return {"action": action, "name": name, "urls": list(remote.urls)}

            if action == "fetch":
                if not name:
                    return {"error": "name is required"}
                result = repo.git.remote("fetch", name)
                return {"action": action, "name": name, "result": result}

            return {"error": f"Unsupported remote action: {action}"}
        except Exception as exc:
            return {"error": str(exc)}
