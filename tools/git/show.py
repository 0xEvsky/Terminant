from tools.base import Tool

from ._common import open_repo


class GitShow(Tool):
    @property
    def name(self):
        return "git.show"

    @property
    def description(self):
        return "inspect a commit, tag, or other revision and show its patch"

    @property
    def arguments(self):
        return {
            "repo_path": {
                "type": "string",
                "description": "path to the git repository (default: current directory)",
                "required": False,
                "default": ".",
            },
            "revision": {
                "type": "string",
                "description": "commit, tag, or revision to inspect",
                "required": True,
            },
            "path": {
                "type": "string",
                "description": "optional file path to narrow the show output",
                "required": False,
                "default": None,
            },
            "stat": {
                "type": "boolean",
                "description": "include diffstat output",
                "required": False,
                "default": True,
            },
        }

    def execute(self, **kwargs):
        repo_path = kwargs.get("repo_path", ".")
        revision = kwargs.get("revision")
        path = kwargs.get("path")
        stat = kwargs.get("stat", True)

        if not revision:
            return {"error": "revision is required"}

        repo, error = open_repo(repo_path)
        if error:
            return error

        try:
            show_args = [revision]
            if stat:
                show_args.append("--stat")
            if path:
                show_args.extend(["--", path])

            result = repo.git.show(*show_args)
            commit = repo.commit(revision)
            return {
                "revision": revision,
                "path": path,
                "result": result,
                "commit": {
                    "hash": commit.hexsha,
                    "short_hash": commit.hexsha[:7],
                    "message": commit.message.strip(),
                    "author": {
                        "name": commit.author.name,
                        "email": commit.author.email,
                    },
                    "authored_date": commit.authored_datetime.isoformat(),
                    "committed_date": commit.committed_datetime.isoformat(),
                },
            }
        except Exception as exc:
            return {"error": str(exc)}
