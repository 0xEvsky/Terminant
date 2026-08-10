from tools.base import Tool
from logger import log_info

from git import Repo
from git.exc import InvalidGitRepositoryError

class GitStatus(Tool):
    @property
    def name(self):
        return "git.status"
    
    @property
    def description(self):
        return "parse current branch, staged/unstaged changes, untracked files"
    
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
        repo_path = kwargs.get('repo_path', '.')
        try:
            repo = Repo(repo_path)
            
            return {
                "branch": repo.active_branch.name,
                "is_dirty": repo.is_dirty(),
                "staged_files": [item[0] for item in repo.index.diff("HEAD")],
                "unstaged_files": [item[0] for item in repo.index.diff(None)],
                "untracked_files": repo.untracked_files,
                "commit_count": len(list(repo.iter_commits())),
                "last_commit": {
                    "hash": repo.head.commit.hexsha[:7],
                    "message": repo.head.commit.message.strip(),
                    "author": str(repo.head.commit.author),
                }
            }
        except InvalidGitRepositoryError:
            log_info(f"Not a git repository: {repo_path}")
            return {"error": f"Not a git repository: {repo_path}"}
        except Exception as e:
            log_info(str(e))
            return {"error": str(e)}