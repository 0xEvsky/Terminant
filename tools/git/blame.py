from tools.base import Tool

from ._common import open_repo


def _parse_blame_porcelain(output: str):
    lines = output.splitlines()
    entries = []
    index = 0

    while index < len(lines):
        header = lines[index].split()
        if len(header) < 4:
            index += 1
            continue

        commit_hash = header[0]
        final_line = int(header[2])
        group_size = int(header[3])
        index += 1

        metadata = {}
        while index < len(lines) and not lines[index].startswith("\t"):
            key, _, value = lines[index].partition(" ")
            metadata[key] = value
            index += 1

        content = ""
        if index < len(lines) and lines[index].startswith("\t"):
            content = lines[index][1:]
            index += 1

        entries.append(
            {
                "commit": commit_hash,
                "short_commit": commit_hash[:7],
                "final_line": final_line,
                "lines": group_size,
                "author": metadata.get("author"),
                "author_mail": metadata.get("author-mail", "").strip("<>") or None,
                "author_time": metadata.get("author-time"),
                "summary": metadata.get("summary"),
                "filename": metadata.get("filename"),
                "content": content,
            }
        )

    return entries


class GitBlame(Tool):
    @property
    def name(self):
        return "git.blame"

    @property
    def description(self):
        return "show who changed each line and when"

    @property
    def arguments(self):
        return {
            "repo_path": {
                "type": "string",
                "description": "path to the git repository (default: current directory)",
                "required": False,
                "default": ".",
            },
            "path": {
                "type": "string",
                "description": "file to inspect",
                "required": True,
            },
            "revision": {
                "type": "string",
                "description": "revision to blame against",
                "required": False,
                "default": "HEAD",
            },
            "start_line": {
                "type": "integer",
                "description": "first line to include",
                "required": False,
                "default": None,
            },
            "end_line": {
                "type": "integer",
                "description": "last line to include",
                "required": False,
                "default": None,
            },
        }

    def execute(self, **kwargs):
        repo_path = kwargs.get("repo_path", ".")
        path = kwargs.get("path")
        revision = kwargs.get("revision", "HEAD")
        start_line = kwargs.get("start_line")
        end_line = kwargs.get("end_line")

        if not path:
            return {"error": "path is required"}

        repo, error = open_repo(repo_path)
        if error:
            return error

        try:
            blame_args = ["--line-porcelain"]
            if start_line is not None and end_line is not None:
                blame_args.extend(["-L", f"{start_line},{end_line}"])
            blame_args.extend([revision, "--", path])
            result = repo.git.blame(*blame_args)
            return {
                "path": path,
                "revision": revision,
                "entries": _parse_blame_porcelain(result),
            }
        except Exception as exc:
            return {"error": str(exc)}
