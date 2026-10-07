from pathlib import Path
from tools.filesystem.list_files import ListFiles
from tools.filesystem.copy_file import CopyFile
from tools.filesystem.delete_file import DeleteFile
from tools.filesystem.create_directory import CreateDirectory
from tools.filesystem.file_info import FileInfo
from tools.filesystem.move_file import MoveFile
from tools.filesystem.read_file import ReadFile
from tools.filesystem.search_files import SearchFiles
from tools.filesystem.write_file import WriteFile


def test_filesystem_list_files(tmp_path):
    Path(tmp_path).mkdir(exist_ok=True)

    result = ListFiles().execute(path=str(tmp_path))

    assert result.success
    assert isinstance(result.output, list)
    assert result.output == []  # The directory is empty, so the output should be an empty list

    Path(tmp_path / "file1.txt").touch()

    result = ListFiles().execute(path=str(tmp_path))

    assert result.success
    assert isinstance(result.output, list)
    assert result.output == ["file1.txt"]


def test_filesystem_copy_file(tmp_path):
    source_file = tmp_path / "source.txt"
    destination_file = tmp_path / "destination.txt"

    source_file.write_text("This is a test file.")
    result = CopyFile().execute(source=str(source_file), destination=str(destination_file))

    assert result.success
    assert destination_file.exists()
    assert destination_file.read_text() == "This is a test file."


def test_filesystem_copy_file_nonexistent_source(tmp_path):
    source_file = tmp_path / "nonexistent.txt"
    destination_file = tmp_path / "destination.txt"

    result = CopyFile().execute(source=str(source_file), destination=str(destination_file))

    assert not result.success
    assert "not found" in result.output
    assert not destination_file.exists()


def test_filesystem_delete_file(tmp_path):
    file_to_delete = tmp_path / "file_to_delete.txt"

    file_to_delete.write_text("This is a test file.")

    result = DeleteFile().execute(path=str(file_to_delete))

    assert result.success
    assert not file_to_delete.exists()


def test_filesystem_delete_file_nonexistent(tmp_path):
    file_to_delete = tmp_path / "nonexistent.txt"

    result = DeleteFile().execute(path=str(file_to_delete))

    assert not result.success
    assert "not found" in result.output


def test_filesystem_create_directory(tmp_path):
    dir_path = tmp_path / "new_directory"
    result = CreateDirectory().execute(path=str(dir_path))

    assert result.success
    assert dir_path.exists()
    assert dir_path.is_dir()

    # Test creating nested directory
    nested_dir = tmp_path / "parent" / "child"
    result = CreateDirectory().execute(path=str(nested_dir))
    assert result.success
    assert nested_dir.exists()
    assert nested_dir.is_dir()

    # Test creating an already existing directory (should not error)
    result = CreateDirectory().execute(path=str(dir_path))
    assert result.success


def test_filesystem_file_info(tmp_path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Hello, world!")

    result = FileInfo().execute(path=str(file_path))
    assert result.success
    info = result.output
    assert info["name"] == "test_file.txt"
    assert info["is_file"] is True
    assert info["is_directory"] is False
    assert info["size"] == len("Hello, world!")
    assert "modified" in info

    # Test directory info
    dir_path = tmp_path / "subdir"
    dir_path.mkdir()
    result = FileInfo().execute(path=str(dir_path))
    assert result.success
    info = result.output
    assert info["name"] == "subdir"
    assert info["is_file"] is False
    assert info["is_directory"] is True

    # Test non-existent path
    result = FileInfo().execute(path=str(tmp_path / "nonexistent.txt"))
    assert not result.success
    assert "not found" in result.output


def test_filesystem_move_file(tmp_path):
    source = tmp_path / "source.txt"
    dest = tmp_path / "dest.txt"
    source.write_text("Move me!")

    result = MoveFile().execute(source=str(source), destination=str(dest))
    assert result.success
    assert not source.exists()
    assert dest.exists()
    assert dest.read_text() == "Move me!"

    # Test moving to an existing file (should overwrite? shutil.move will raise if destination exists on Windows?)
    # We'll skip this for simplicity, but we can test moving to a non-existing destination in a nested path.
    source2 = tmp_path / "source2.txt"
    dest2 = tmp_path / "subdir" / "dest2.txt"
    source2.write_text("Move me too!")
    # Create the destination directory
    dest2.parent.mkdir(parents=True, exist_ok=True)
    result = MoveFile().execute(source=str(source2), destination=str(dest2))
    assert result.success
    assert not source2.exists()
    assert dest2.exists()
    assert dest2.read_text() == "Move me too!"
    assert dest2.parent.exists()

    # Test error: source not found
    result = MoveFile().execute(source=str(tmp_path / "missing.txt"), destination=str(dest))
    assert not result.success
    assert "not found" in result.output


def test_filesystem_read_file(tmp_path):
    file_path = tmp_path / "read_test.txt"
    content = "Reading this file."
    file_path.write_text(content)

    result = ReadFile().execute(path=str(file_path))
    assert result.success
    assert result.output == content

    # Test reading empty file
    empty_file = tmp_path / "empty.txt"
    empty_file.touch()
    result = ReadFile().execute(path=str(empty_file))
    assert result.success
    assert result.output == ""

    # Test error: file not found
    result = ReadFile().execute(path=str(tmp_path / "missing.txt"))
    assert not result.success
    assert "not found" in result.output


def test_filesystem_search_files(tmp_path):
    # Create some files
    (tmp_path / "foo.txt").write_text("foo")
    (tmp_path / "bar.txt").write_text("bar")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "baz.txt").write_text("baz")
    (tmp_path / "subdir" / "qux.log").write_text("qux")

    # Search for all .txt files
    result = SearchFiles().execute(path=str(tmp_path), pattern="*.txt")
    assert result.success
    files = set(result.output)
    expected = {
        str(tmp_path / "foo.txt"),
        str(tmp_path / "bar.txt"),
        str(tmp_path / "subdir" / "baz.txt"),
    }
    assert files == expected

    # Search for nothing
    result = SearchFiles().execute(path=str(tmp_path), pattern="*.nonexistent")
    assert result.success
    assert result.output == []

    # Test error: path not found -> returns success with empty list (glob behavior)
    result = SearchFiles().execute(path=str(tmp_path / "missing"), pattern="*")
    assert result.success
    assert result.output == []


def test_filesystem_write_file(tmp_path):
    file_path = tmp_path / "write_test.txt"
    content = "Writing to this file."

    result = WriteFile().execute(path=str(file_path), content=content)
    assert result.success
    assert file_path.exists()
    assert file_path.read_text() == content

    # Test writing to a file in a non-existent directory (should fail)
    bad_path = tmp_path / "nosuchdir" / "file.txt"
    result = WriteFile().execute(path=str(bad_path), content="oops")
    assert not result.success
    # The error message may vary; we check for "not found" or "Permission denied"
    assert "not found" in result.output or "Permission denied" in result.output

    # Test writing empty content
    empty_file = tmp_path / "empty.txt"
    result = WriteFile().execute(path=str(empty_file), content="")
    assert result.success
    assert empty_file.exists()
    assert empty_file.read_text() == ""