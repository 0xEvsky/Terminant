from tools.filesystem import create_directory, copy_file, delete_file, file_info, list_files, move_file, read_file, search_files, write_file
from tools.git import add, blame, branch, checkout, commit, diff, log, merge, rebase, remote, rm, show, stash, status, tag
from tools.terminal import environment, execute, process_status, which

tool_registry = {
    "filesystem_list_files": list_files.ListFiles(),
    "filesystem_read_file": read_file.ReadFile(),
    "filesystem_write_file": write_file.WriteFile(),
    "filesystem_search_files": search_files.SearchFiles(),
    "filesystem_file_info": file_info.FileInfo(),
    "filesystem_create_directory": create_directory.CreateDirectory(),
    "filesystem_delete_file": delete_file.DeleteFile(),
    "filesystem_move_file": move_file.MoveFile(),
    "filesystem_copy_file": copy_file.CopyFile(),
    "git_status": status.GitStatus(),
    "git_log": log.GitLog(),
    "git_branch": branch.GitBranch(),
    "git_diff": diff.GitDiff(),
    "git_add": add.GitAdd(),
    "git_rm": rm.GitRm(),
    "git_commit": commit.GitCommit(),
    "git_stash": stash.GitStash(),
    "git_checkout": checkout.GitCheckout(),
    "git_merge": merge.GitMerge(),
    "git_rebase": rebase.GitRebase(),
    "git_show": show.GitShow(),
    "git_blame": blame.GitBlame(),
    "git_tag": tag.GitTag(),
    "git_remote": remote.GitRemote(),
    "terminal_execute": execute.Execute(),
    "terminal_which": which.Which(),
    "terminal_environment": environment.Environment(),
    "terminal_process_status": process_status.ProcessStatus(),
}

def get_tool(tool_name):
    return tool_registry.get(tool_name)