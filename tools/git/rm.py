from tools.base import Tool

from ._common import open_repo, status_snapshot


class GitRm(Tool):
    @property
    def name(self):
        return "git.rm"

    @property
    def description(self):
        return "remove files from the index or the working tree"

    @property
    def arguments(self):
        return {
            "repo_path": {
                "type": "string",
                "description": "path to the git repository (default: current directory)",
                "required": False,
                "default": ".",
            },
            "paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "files or directories to remove",
                "required": True,
            },
            "cached": {
                "type": "boolean",
                "description": "remove from index only and keep files in the working tree",
                "required": False,
                "default": False,
            },
            "force": {
                "type": "boolean",
                "description": "force removal of modified files",
                "required": False,
                "default": False,
            },
        }

    def execute(self, **kwargs):
        repo_path = kwargs.get("repo_path", ".")
        paths = kwargs.get("paths") or []
        cached = kwargs.get("cached", False)
        force = kwargs.get("force", False)

        if not paths:
            return {"error": "paths are required"}

        repo, error = open_repo(repo_path)
        if error:
            return error

        try:
            rm_args = []
            if cached:
                rm_args.append("--cached")
            if force:
                rm_args.append("--force")
            rm_args.extend(["--", *paths])
            repo.git.rm(*rm_args)

            return {
                "action": "rm",
                "cached": cached,
                "paths": paths,
                **status_snapshot(repo),
            }
        except Exception as exc:
            return {"error": str(exc)}
