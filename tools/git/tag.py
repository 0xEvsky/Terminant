from tools.base import Tool

from ._common import open_repo


class GitTag(Tool):
    @property
    def name(self):
        return "git.tag"

    @property
    def description(self):
        return "list, create, or delete git tags"

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
                "description": "tag action: list, create, or delete",
                "required": False,
                "default": "list",
            },
            "tag_name": {
                "type": "string",
                "description": "tag name for create or delete",
                "required": False,
                "default": None,
            },
            "revision": {
                "type": "string",
                "description": "revision to tag when creating a tag",
                "required": False,
                "default": "HEAD",
            },
            "message": {
                "type": "string",
                "description": "annotated tag message",
                "required": False,
                "default": None,
            },
        }

    def execute(self, **kwargs):
        repo_path = kwargs.get("repo_path", ".")
        action = kwargs.get("action", "list")
        tag_name = kwargs.get("tag_name")
        revision = kwargs.get("revision", "HEAD")
        message = kwargs.get("message")

        repo, error = open_repo(repo_path)
        if error:
            return error

        try:
            if action == "list":
                tags = []
                for tag in sorted(repo.tags, key=lambda item: item.name):
                    commit = tag.commit
                    tags.append(
                        {
                            "name": tag.name,
                            "commit": commit.hexsha[:7],
                            "message": commit.message.strip(),
                        }
                    )
                return {"action": action, "tags": tags}

            if not tag_name:
                return {"error": "tag_name is required"}

            if action == "create":
                if message:
                    result = repo.create_tag(tag_name, revision, message=message)
                else:
                    result = repo.create_tag(tag_name, revision)
                return {
                    "action": action,
                    "tag": result.name,
                    "revision": revision,
                    "message": message,
                }

            if action == "delete":
                repo.delete_tag(tag_name)
                return {"action": action, "tag": tag_name}

            return {"error": f"Unsupported tag action: {action}"}
        except Exception as exc:
            return {"error": str(exc)}
