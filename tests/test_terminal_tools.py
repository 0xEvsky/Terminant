import os
import platform
from tools.terminal.environment import Environment
from tools.terminal.execute import Execute
from tools.terminal.process_status import ProcessStatus
from tools.terminal.which import Which


def test_terminal_environment():
    result = Environment().execute()
    assert result.success
    assert isinstance(result.output, dict)
    # Check that we have some environment variables
    assert len(result.output) > 0
    # Check for a couple of common variables on Windows
    if platform.system().lower() == "windows":
        assert "PATH" in result.output
        assert "SYSTEMROOT" in result.output
    else:
        # On Unix-like systems, check for some common variables
        assert "PATH" in result.output
        assert "HOME" in result.output or "USER" in result.output


def test_terminal_execute_success():
    # Use a command that should succeed and produce output
    if platform.system().lower() == "windows":
        command = "echo hello"
    else:
        command = "echo hello"
    result = Execute().execute(command=command)
    assert result.success
    # The output should contain "hello" (maybe with a newline stripped)
    assert "hello" in result.output


def test_terminal_execute_failure():
    # Use a command that fails (exit with non-zero)
    if platform.system().lower() == "windows":
        command = "cmd /c exit 1"
    else:
        command = "sh -c 'exit 1'"
    result = Execute().execute(command=command)
    assert not result.success
    # Should have an error message
    assert result.output is not None
    assert len(result.output) > 0


def test_terminal_execute_not_found():
    # Use a command that does not exist
    command = "this_command_definitely_does_not_exist_12345"
    result = Execute().execute(command=command)
    assert not result.success
    # Should contain an error about command not found
    assert "not found" in result.output.lower() or "not recognized" in result.output.lower()


def test_terminal_process_status_current_pid():
    # Test with the current process ID
    pid = os.getpid()
    result = ProcessStatus().execute(pid=pid)
    assert result.success
    assert isinstance(result.output, dict)
    assert result.output["pid"] == pid
    assert result.output["running"] is True
    assert result.output["status"] == "running"


def test_terminal_process_status_nonexistent_pid():
    # Test with a PID that is very unlikely to exist
    # Use a large PID
    pid = 999999
    result = ProcessStatus().execute(pid=pid)
    assert result.success
    assert isinstance(result.output, dict)
    assert result.output["pid"] == pid
    assert result.output["running"] is False
    assert result.output["status"] == "not_found"


def test_terminal_process_status_invalid_pid():
    # Test with a non-integer PID (should error)
    result = ProcessStatus().execute(pid="not_a_number")
    assert not result.success
    assert "invalid process id" in result.output.lower()


def test_terminal_which_found():
    # Test finding an existing command
    if platform.system().lower() == "windows":
        command = "where"
    else:
        command = "ls"
    result = Which().execute(command=command)
    assert result.success
    assert isinstance(result.output, str)
    assert len(result.output) > 0
    # The output should be a path to the command
    # We can check that the file exists
    assert os.path.exists(result.output)


def test_terminal_which_not_found():
    # Test for a non-existent command
    command = "this_command_definitely_does_not_exist_12345"
    result = Which().execute(command=command)
    assert not result.success
    assert "not found" in result.output.lower()