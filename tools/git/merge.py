from tools.base import Tool

from ._common import open_repo, status_snapshot


class GitMerge(Tool):
    @property
    def name(self):
        return "git.merge"

    @property
    def description(self):
        return "merge branches and report conflicts when they occur"

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
                "description": "branch or commit to merge into the current branch",
                "required": True,
            },
            "no_commit": {
                "type": "boolean",
                "description": "stop before creating the merge commit",
                "required": False,
                "default": False,
            },
            "squash": {
                "type": "boolean",
                "description": "perform a squash merge",
                "required": False,
                "default": False,
            },
            "abort_on_conflict": {
                "type": "boolean",
                "description": "abort the merge if conflicts are detected",
                "required": False,
                "default": False,
            },
        }

    def execute(self, **kwargs):
        repo_path = kwargs.get("repo_path", ".")
        target = kwargs.get("target")
        no_commit = kwargs.get("no_commit", False)
        squash = kwargs.get("squash", False)
        abort_on_conflict = kwargs.get("abort_on_conflict", False)

        if not target:
            return {"error": "target is required"}

        repo, error = open_repo(repo_path)
        if error:
            return error

        try:
            merge_args = []
            if no_commit:
                merge_args.append("--no-commit")
            if squash:
                merge_args.append("--squash")
            merge_args.append(target)

            result = repo.git.merge(*merge_args)
            return {
                "target": target,
                "result": result,
                "conflicts": [],
                **status_snapshot(repo),
            }
        except Exception as exc:
            unmerged = []
            try:
                unmerged = sorted(repo.index.unmerged_blobs().keys())
            except Exception:
                unmerged = []

            if abort_on_conflict:
                try:
                    repo.git.merge("--abort")
                except Exception:
                    pass

            return {
                "target": target,
                "error": str(exc),
                "conflicts": unmerged,
                **status_snapshot(repo),
            }
