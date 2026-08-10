from tools.base import Tool
from logger import log_info

from git import Repo
from git.exc import InvalidGitRepositoryError

from ._common import diff_path


class GitLog(Tool):
    @property
    def name(self):
        return "git.log"

    @property
    def description(self):
        return "extract commit history, authors, dates, and per-commit diff summaries"

    @property
    def arguments(self):
        return {
            "repo_path": {
                "type": "string",
                "description": "path to the git repository (default: current directory)",
                "required": False,
                "default": "."
            },
            "revision": {
                "type": "string",
                "description": "revision or branch to inspect (default: HEAD)",
                "required": False,
                "default": "HEAD"
            },
            "max_count": {
                "type": "integer",
                "description": "maximum number of commits to return (default: 10)",
                "required": False,
                "default": 10
            },
            "include_file_stats": {
                "type": "boolean",
                "description": "include per-file change counts for each commit",
                "required": False,
                "default": True
            },
            "include_diffs": {
                "type": "boolean",
                "description": "include per-file diff summaries for each commit",
                "required": False,
                "default": True
            }
        }

    def execute(self, **kwargs):
        repo_path = kwargs.get("repo_path", ".")
        revision = kwargs.get("revision", "HEAD")
        max_count = kwargs.get("max_count", 10)
        include_file_stats = kwargs.get("include_file_stats", True)
        include_diffs = kwargs.get("include_diffs", True)

        try:
            repo = Repo(repo_path)
            history = []

            for commit in repo.iter_commits(revision, max_count=max_count):
                commit_entry = {
                    "hash": commit.hexsha,
                    "short_hash": commit.hexsha[:7],
                    "summary": commit.summary,
                    "message": commit.message.strip(),
                    "author": {
                        "name": commit.author.name,
                        "email": commit.author.email,
                    },
                    "authored_date": commit.authored_datetime.isoformat(),
                    "committed_date": commit.committed_datetime.isoformat(),
                    "parents": [parent.hexsha[:7] for parent in commit.parents],
                    "stats": commit.stats.total,
                }

                if include_file_stats:
                    commit_entry["files"] = [
                        {
                            "path": path,
                            "insertions": file_stats.get("insertions", 0),
                            "deletions": file_stats.get("deletions", 0),
                            "lines": file_stats.get("lines", 0),
                        }
                        for path, file_stats in sorted(commit.stats.files.items())
                    ]

                if include_diffs and commit.parents:
                    parent = commit.parents[0]
                    commit_entry["diffs"] = [
                        {
                            "path": diff_path(diff_item),
                            "change_type": diff_item.change_type,
                            "a_mode": diff_item.a_mode,
                            "b_mode": diff_item.b_mode,
                            "renamed": diff_item.renamed_file,
                            "new_file": diff_item.new_file,
                            "deleted_file": diff_item.deleted_file,
                        }
                        for diff_item in parent.diff(commit)
                    ]
                elif include_diffs:
                    commit_entry["diffs"] = []

                history.append(commit_entry)

            return {
                "revision": revision,
                "commit_count": len(history),
                "history": history,
            }
        except InvalidGitRepositoryError:
            log_info(f"Not a git repository: {repo_path}")
            return {"error": f"Not a git repository: {repo_path}"}
        except Exception as e:
            log_info(str(e))
            return {"error": str(e)}