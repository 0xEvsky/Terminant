from tools.filesystem import list_files

tool_registry = {
    "filesystem.list_files": list_files.ListFiles()
}

def get_tool(tool_name):
    return tool_registry.get(tool_name)