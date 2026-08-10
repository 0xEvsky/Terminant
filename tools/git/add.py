from tools.base import Tool

from ._common import open_repo, status_snapshot


class GitAdd(Tool):
    @property
    def name(self):
        return "git.add"

    @property
    def description(self):
        return "stage files or unstage them when guided commits need a clean index"

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
                "description": "files or directories to stage or unstage",
                "required": False,
                "default": [],
            },
            "unstage": {
                "type": "boolean",
                "description": "when true, unstage the selected paths instead of staging them",
                "required": False,
                "default": False,
            },
            "all": {
                "type": "boolean",
                "description": "stage all tracked changes",
                "required": False,
                "default": False,
            },
            "update": {
                "type": "boolean",
                "description": "stage modifications and deletions for tracked files only",
                "required": False,
                "default": False,
            },
            "force": {
                "type": "boolean",
                "description": "force adding ignored files",
                "required": False,
                "default": False,
            },
        }

    def execute(self, **kwargs):
        repo_path = kwargs.get("repo_path", ".")
        paths = kwargs.get("paths") or []
        unstage = kwargs.get("unstage", False)
        all_files = kwargs.get("all", False)
        update = kwargs.get("update", False)
        force = kwargs.get("force", False)

        repo, error = open_repo(repo_path)
        if error:
            return error

        try:
            if unstage:
                reset_args = ["HEAD"]
                if paths:
                    reset_args.extend(["--", *paths])
                repo.git.reset(*reset_args)
                action = "unstage"
            else:
                add_args = []
                if all_files:
                    add_args.append("--all")
                if update:
                    add_args.append("--update")
                if force:
                    add_args.append("--force")
                if paths:
                    add_args.extend(["--", *paths])
                repo.git.add(*add_args)
                action = "stage"

            return {
                "action": action,
                "paths": paths,
                **status_snapshot(repo),
            }
        except Exception as exc:
            return {"error": str(exc)}
