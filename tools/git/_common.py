from logger import log_info

from git import Repo
from git.exc import InvalidGitRepositoryError


def open_repo(repo_path: str):
    try:
        return Repo(repo_path), None
    except InvalidGitRepositoryError:
        log_info(f"Not a git repository: {repo_path}")
        return None, {"error": f"Not a git repository: {repo_path}"}
    except Exception as exc:
        log_info(str(exc))
        return None, {"error": str(exc)}


def branch_snapshot(repo):
    try:
        branch_name = repo.active_branch.name
        detached_head = False
    except TypeError:
        branch_name = repo.head.commit.hexsha[:7]
        detached_head = True

    return branch_name, detached_head


def diff_path(item):
    return item.a_path or item.b_path or item.path


def status_snapshot(repo):
    branch_name, detached_head = branch_snapshot(repo)

    return {
        "current_branch": branch_name,
        "detached_head": detached_head,
        "is_dirty": repo.is_dirty(untracked_files=True),
        "staged_files": [diff_path(item) for item in repo.index.diff("HEAD")],
        "unstaged_files": [diff_path(item) for item in repo.index.diff(None)],
        "untracked_files": repo.untracked_files,
    }
