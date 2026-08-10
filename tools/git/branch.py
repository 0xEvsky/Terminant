from tools.base import Tool
from logger import log_info

from git import Repo
from git.exc import InvalidGitRepositoryError


class GitBranch(Tool):
    @property
    def name(self):
        return "git.branch"

    @property
    def description(self):
        return "list local and remote branches and identify the current branch"

    @property
    def arguments(self):
        return {
            "repo_path": {
                "type": "string",
                "description": "path to the git repository (default: current directory)",
                "required": False,
                "default": "."
            }
        }

    def execute(self, **kwargs):
        repo_path = kwargs.get("repo_path", ".")

        try:
            repo = Repo(repo_path)

            try:
                current_branch = repo.active_branch.name
                detached_head = False
            except TypeError:
                current_branch = repo.head.commit.hexsha[:7]
                detached_head = True

            local_branches = []
            for branch in sorted(repo.branches, key=lambda item: item.name):
                tracking_branch = branch.tracking_branch()
                ahead_by = None
                behind_by = None

                if tracking_branch is not None:
                    ahead_by = sum(1 for _ in repo.iter_commits(f"{tracking_branch.name}..{branch.name}"))
                    behind_by = sum(1 for _ in repo.iter_commits(f"{branch.name}..{tracking_branch.name}"))

                local_branches.append(
                    {
                        "name": branch.name,
                        "commit": branch.commit.hexsha[:7],
                        "is_current": branch.name == current_branch,
                        "tracking": tracking_branch.name if tracking_branch else None,
                        "ahead_by": ahead_by,
                        "behind_by": behind_by,
                    }
                )

            remote_branches = []
            for remote in sorted(repo.remotes, key=lambda item: item.name):
                for reference in sorted(remote.refs, key=lambda item: item.name):
                    if reference.remote_head == "HEAD":
                        continue

                    remote_branches.append(
                        {
                            "remote": remote.name,
                            "name": reference.remote_head,
                            "ref": reference.name,
                            "commit": reference.commit.hexsha[:7],
                        }
                    )

            return {
                "current_branch": current_branch,
                "detached_head": detached_head,
                "local_branches": local_branches,
                "remote_branches": remote_branches,
            }
        except InvalidGitRepositoryError:
            log_info(f"Not a git repository: {repo_path}")
            return {"error": f"Not a git repository: {repo_path}"}
        except Exception as e:
            log_info(str(e))
            return {"error": str(e)}