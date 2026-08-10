from tools.base import Tool
from logger import log_info

from git import Repo
from git.exc import InvalidGitRepositoryError


class GitDiff(Tool):
    @property
    def name(self):
        return "git.diff"

    @property
    def description(self):
        return "show diffs for the working tree, staging area, or between refs"

    @property
    def arguments(self):
        return {
            "repo_path": {
                "type": "string",
                "description": "path to the git repository (default: current directory)",
                "required": False,
                "default": "."
            },
            "mode": {
                "type": "string",
                "description": "diff mode: working_tree, staging, or refs",
                "required": False,
                "default": "working_tree"
            },
            "left_ref": {
                "type": "string",
                "description": "left side reference when mode is refs",
                "required": False,
                "default": None
            },
            "right_ref": {
                "type": "string",
                "description": "right side reference when mode is refs",
                "required": False,
                "default": None
            },
            "path": {
                "type": "string",
                "description": "optional file or directory path filter",
                "required": False,
                "default": None
            },
            "context_lines": {
                "type": "integer",
                "description": "number of context lines to show in the unified diff",
                "required": False,
                "default": 3
            }
        }

    def execute(self, **kwargs):
        repo_path = kwargs.get("repo_path", ".")
        mode = kwargs.get("mode", "working_tree")
        left_ref = kwargs.get("left_ref")
        right_ref = kwargs.get("right_ref")
        path = kwargs.get("path")
        context_lines = kwargs.get("context_lines", 3)

        try:
            repo = Repo(repo_path)

            diff_args = [f"--unified={context_lines}"]
            name_status_args = ["--name-status"]
            stat_args = ["--stat"]

            if mode == "staging":
                diff_args.append("--cached")
                name_status_args.append("--cached")
                stat_args.append("--cached")
            elif mode == "refs":
                if not left_ref or not right_ref:
                    return {"error": "left_ref and right_ref are required when mode is refs"}
                diff_args.extend([left_ref, right_ref])
                name_status_args.extend([left_ref, right_ref])
                stat_args.extend([left_ref, right_ref])

            if path:
                diff_args.extend(["--", path])
                name_status_args.extend(["--", path])
                stat_args.extend(["--", path])

            diff_text = repo.git.diff(*diff_args)
            name_status = repo.git.diff(*name_status_args)
            stat_text = repo.git.diff(*stat_args)

            result = {
                "mode": mode,
                "repo_path": repo_path,
                "left_ref": left_ref,
                "right_ref": right_ref,
                "path": path,
                "diff": diff_text,
                "name_status": name_status,
                "stat": stat_text,
            }

            if mode == "working_tree":
                result["untracked_files"] = repo.untracked_files

            return result
        except InvalidGitRepositoryError:
            log_info(f"Not a git repository: {repo_path}")
            return {"error": f"Not a git repository: {repo_path}"}
        except Exception as e:
            log_info(str(e))
            return {"error": str(e)}