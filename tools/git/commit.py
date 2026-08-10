from tools.base import Tool

from ._common import open_repo, status_snapshot


class GitCommit(Tool):
    @property
    def name(self):
        return "git.commit"

    @property
    def description(self):
        return "create a commit from staged changes with a clear message"

    @property
    def arguments(self):
        return {
            "repo_path": {
                "type": "string",
                "description": "path to the git repository (default: current directory)",
                "required": False,
                "default": ".",
            },
            "message": {
                "type": "string",
                "description": "commit message",
                "required": True,
            },
            "all": {
                "type": "boolean",
                "description": "stage tracked changes before committing",
                "required": False,
                "default": False,
            },
            "amend": {
                "type": "boolean",
                "description": "amend the previous commit",
                "required": False,
                "default": False,
            },
            "allow_empty": {
                "type": "boolean",
                "description": "create an empty commit if there is nothing staged",
                "required": False,
                "default": False,
            },
        }

    def execute(self, **kwargs):
        repo_path = kwargs.get("repo_path", ".")
        message = kwargs.get("message")
        all_files = kwargs.get("all", False)
        amend = kwargs.get("amend", False)
        allow_empty = kwargs.get("allow_empty", False)

        if not message:
            return {"error": "message is required"}

        repo, error = open_repo(repo_path)
        if error:
            return error

        try:
            commit_args = ["-m", message]
            if all_files:
                commit_args.insert(0, "--all")
            if amend:
                commit_args.insert(0, "--amend")
            if allow_empty:
                commit_args.insert(0, "--allow-empty")

            result = repo.git.commit(*commit_args)
            head_commit = repo.head.commit

            return {
                "result": result,
                "commit": {
                    "hash": head_commit.hexsha,
                    "short_hash": head_commit.hexsha[:7],
                    "message": head_commit.message.strip(),
                    "author": {
                        "name": head_commit.author.name,
                        "email": head_commit.author.email,
                    },
                },
                **status_snapshot(repo),
            }
        except Exception as exc:
            return {"error": str(exc)}
