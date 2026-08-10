from tools.base import Tool

from ._common import open_repo, status_snapshot


class GitRebase(Tool):
    @property
    def name(self):
        return "git.rebase"

    @property
    def description(self):
        return "rebase commits onto a new base, with support for interactive cleanup"

    @property
    def arguments(self):
        return {
            "repo_path": {
                "type": "string",
                "description": "path to the git repository (default: current directory)",
                "required": False,
                "default": ".",
            },
            "upstream": {
                "type": "string",
                "description": "branch or commit to rebase onto",
                "required": True,
            },
            "branch": {
                "type": "string",
                "description": "branch to rebase; defaults to the current branch",
                "required": False,
                "default": None,
            },
            "interactive": {
                "type": "boolean",
                "description": "run an interactive rebase session",
                "required": False,
                "default": False,
            },
            "autosquash": {
                "type": "boolean",
                "description": "enable autosquash for fixup/squash commits",
                "required": False,
                "default": False,
            },
            "rebase_merges": {
                "type": "boolean",
                "description": "preserve merge commits during rebase",
                "required": False,
                "default": False,
            },
        }

    def execute(self, **kwargs):
        repo_path = kwargs.get("repo_path", ".")
        upstream = kwargs.get("upstream")
        branch = kwargs.get("branch")
        interactive = kwargs.get("interactive", False)
        autosquash = kwargs.get("autosquash", False)
        rebase_merges = kwargs.get("rebase_merges", False)

        if not upstream:
            return {"error": "upstream is required"}

        repo, error = open_repo(repo_path)
        if error:
            return error

        try:
            rebase_args = []
            if interactive:
                rebase_args.append("--interactive")
            if autosquash:
                rebase_args.append("--autosquash")
            if rebase_merges:
                rebase_args.append("--rebase-merges")
            if branch:
                rebase_args.extend(["--onto", upstream, branch])
            else:
                rebase_args.append(upstream)

            if interactive:
                result = repo.git.rebase(*rebase_args, env={"GIT_SEQUENCE_EDITOR": "true"})
            else:
                result = repo.git.rebase(*rebase_args)

            return {
                "upstream": upstream,
                "branch": branch,
                "interactive": interactive,
                "result": result,
                **status_snapshot(repo),
            }
        except Exception as exc:
            return {"error": str(exc), **status_snapshot(repo)}
