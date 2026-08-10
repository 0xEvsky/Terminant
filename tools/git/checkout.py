from tools.base import Tool

from ._common import open_repo, status_snapshot


class GitCheckout(Tool):
    @property
    def name(self):
        return "git.checkout"

    @property
    def description(self):
        return "switch branches, create branches, or restore files from a revision"

    @property
    def arguments(self):
        return {
            "repo_path": {
                "type": "string",
                "description": "path to the git repository (default: current directory)",
                "required": False,
                "default": ".",
            },
            "target": {
                "type": "string",
                "description": "branch, commit, or path target",
                "required": False,
                "default": None,
            },
            "paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "files to restore when doing a path checkout",
                "required": False,
                "default": [],
            },
            "create_branch": {
                "type": "boolean",
                "description": "create a new branch before switching",
                "required": False,
                "default": False,
            },
            "force": {
                "type": "boolean",
                "description": "force checkout and discard local changes",
                "required": False,
                "default": False,
            },
            "start_point": {
                "type": "string",
                "description": "branch or commit to branch from when creating a branch",
                "required": False,
                "default": None,
            },
        }

    def execute(self, **kwargs):
        repo_path = kwargs.get("repo_path", ".")
        target = kwargs.get("target")
        paths = kwargs.get("paths") or []
        create_branch = kwargs.get("create_branch", False)
        force = kwargs.get("force", False)
        start_point = kwargs.get("start_point")

        repo, error = open_repo(repo_path)
        if error:
            return error

        try:
            if paths:
                checkout_args = []
                if force:
                    checkout_args.append("--force")
                if target:
                    checkout_args.append(target)
                checkout_args.extend(["--", *paths])
                result = repo.git.checkout(*checkout_args)
                action = "restore_files"
            else:
                if not target:
                    return {"error": "target is required when switching branches"}
                checkout_args = []
                if force:
                    checkout_args.append("--force")
                if create_branch:
                    checkout_args.extend(["-b", target])
                    if start_point:
                        checkout_args.append(start_point)
                else:
                    checkout_args.append(target)
                result = repo.git.checkout(*checkout_args)
                action = "switch_branch" if not create_branch else "create_branch"

            return {
                "action": action,
                "target": target,
                "paths": paths,
                "result": result,
                **status_snapshot(repo),
            }
        except Exception as exc:
            return {"error": str(exc)}
