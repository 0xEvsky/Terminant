from tools.filesystem import create_directory, copy_file, delete_file, file_info, list_files, move_file, read_file, search_files, write_file
from tools.terminal import environment, execute, process_status, which

tool_registry = {
    "filesystem.list_files": list_files.ListFiles(),
    "filesystem.read_file": read_file.ReadFile(),
    "filesystem.write_file": write_file.WriteFile(),
    "filesystem.search_files": search_files.SearchFiles(),
    "filesystem.file_info": file_info.FileInfo(),
    "filesystem.create_directory": create_directory.CreateDirectory(),
    "filesystem.delete_file": delete_file.DeleteFile(),
    "filesystem.move_file": move_file.MoveFile(),
    "filesystem.copy_file": copy_file.CopyFile(),
    "terminal.execute": execute.Execute(),
    "terminal.which": which.Which(),
    "terminal.environment": environment.Environment(),
    "terminal.process_status": process_status.ProcessStatus(),
}

def get_tool(tool_name):
    return tool_registry.get(tool_name)