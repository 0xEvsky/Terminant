from pathlib import Path

from git import Repo

from tools.git.add import GitAdd
from tools.git.blame import GitBlame
from tools.git.branch import GitBranch
from tools.git.checkout import GitCheckout
from tools.git.commit import GitCommit
from tools.git.diff import GitDiff
from tools.git.log import GitLog
from tools.git.merge import GitMerge
from tools.git.rebase import GitRebase
from tools.git.remote import GitRemote
from tools.git.show import GitShow
from tools.git.stash import GitStash
from tools.git.tag import GitTag
from tools.git.rm import GitRm
from tools.registry import get_tool


def _create_repo(tmp_path: Path) -> Repo:
    repo = Repo.init(tmp_path)
    repo.git.config("user.name", "Test User")
    repo.git.config("user.email", "test@example.com")

    readme = tmp_path / "README.md"
    readme.write_text("one\n", encoding="utf-8")
    repo.index.add([str(readme)])
    repo.index.commit("initial commit")

    feature = repo.create_head("feature")
    feature.checkout()

    readme.write_text("two\n", encoding="utf-8")
    repo.index.add([str(readme)])
    repo.index.commit("feature commit")

    master = repo.heads.master
    master.checkout()

    remote_path = tmp_path / "remote.git"
    remote_repo = Repo.init(remote_path, bare=True)
    origin = repo.create_remote("origin", str(remote_path))
    origin.push(all=True)
    origin.fetch()

    return repo


def test_git_log_returns_commit_history(tmp_path):
    repo = _create_repo(tmp_path)

    result = GitLog().execute(repo_path=str(repo.working_dir), max_count=2)

    assert result["commit_count"] == 2
    assert result["history"][0]["author"]["name"] == "Test User"
    assert result["history"][0]["files"]
    assert result["history"][0]["diffs"]


def test_git_branch_lists_current_and_remote_branches(tmp_path):
    repo = _create_repo(tmp_path)

    result = GitBranch().execute(repo_path=str(repo.working_dir))

    assert result["current_branch"] == "master"
    assert any(branch["name"] == "master" for branch in result["local_branches"])
    assert any(branch["name"] == "feature" for branch in result["remote_branches"])


def test_git_diff_returns_working_tree_and_ref_diffs(tmp_path):
    repo = _create_repo(tmp_path)

    readme = tmp_path / "README.md"
    readme.write_text("three\n", encoding="utf-8")

    working_tree_result = GitDiff().execute(repo_path=str(repo.working_dir), mode="working_tree")
    refs_result = GitDiff().execute(
        repo_path=str(repo.working_dir),
        mode="refs",
        left_ref="master",
        right_ref="feature",
    )

    assert "two" in refs_result["diff"]
    assert working_tree_result["mode"] == "working_tree"
    assert "three" in working_tree_result["diff"]


def test_git_registry_includes_new_tools():
    for tool_name in [
        "git.add",
        "git.rm",
        "git.commit",
        "git.stash",
        "git.checkout",
        "git.merge",
        "git.rebase",
        "git.show",
        "git.blame",
        "git.tag",
        "git.remote",
    ]:
        assert get_tool(tool_name) is not None


def test_git_workflow_and_info_tools_smoke_test(tmp_path):
    repo = Repo.init(tmp_path)
    repo.git.config("user.name", "Test User")
    repo.git.config("user.email", "test@example.com")

    readme = tmp_path / "README.md"
    readme.write_text("one\n", encoding="utf-8")
    repo.index.add([str(readme)])
    repo.index.commit("initial commit")

    readme.write_text("two\n", encoding="utf-8")
    add_result = GitAdd().execute(repo_path=str(repo.working_dir), paths=["README.md"])
    commit_result = GitCommit().execute(repo_path=str(repo.working_dir), message="update readme")
    show_result = GitShow().execute(repo_path=str(repo.working_dir), revision="HEAD")
    blame_result = GitBlame().execute(repo_path=str(repo.working_dir), path="README.md")
    tag_result = GitTag().execute(repo_path=str(repo.working_dir), action="create", tag_name="v1.0.0")
    remote_result = GitRemote().execute(repo_path=str(repo.working_dir), action="list")

    assert add_result["staged_files"]
    assert commit_result["commit"]["message"] == "update readme"
    assert "README.md" in show_result["result"]
    assert blame_result["entries"]
    assert tag_result["tag"] == "v1.0.0"
    assert remote_result["remotes"] == []


def test_git_add_unstage_and_rm_cached(tmp_path):
    repo = Repo.init(tmp_path)
    repo.git.config("user.name", "Test User")
    repo.git.config("user.email", "test@example.com")

    readme = tmp_path / "README.md"
    readme.write_text("one\n", encoding="utf-8")
    repo.index.add([str(readme)])
    repo.index.commit("initial commit")

    readme.write_text("two\n", encoding="utf-8")
    stage_result = GitAdd().execute(repo_path=str(repo.working_dir), paths=["README.md"])
    unstage_result = GitAdd().execute(repo_path=str(repo.working_dir), paths=["README.md"], unstage=True)
    rm_result = GitRm().execute(repo_path=str(repo.working_dir), paths=["README.md"], cached=True)

    assert "README.md" in stage_result["staged_files"]
    assert stage_result["action"] == "stage"
    assert unstage_result["action"] == "unstage"
    assert rm_result["action"] == "rm"


def test_git_checkout_merge_stash_and_rebase(tmp_path):
    repo = Repo.init(tmp_path)
    repo.git.config("user.name", "Test User")
    repo.git.config("user.email", "test@example.com")

    readme = tmp_path / "README.md"
    readme.write_text("base\n", encoding="utf-8")
    repo.index.add([str(readme)])
    repo.index.commit("initial commit")

    repo.create_head("feature").checkout()
    readme.write_text("feature\n", encoding="utf-8")
    repo.index.add([str(readme)])
    repo.index.commit("feature commit")

    rebase_result = GitRebase().execute(repo_path=str(repo.working_dir), upstream="master")
    checkout_result = GitCheckout().execute(repo_path=str(repo.working_dir), target="master")

    readme.write_text("master change\n", encoding="utf-8")
    stash_result = GitStash().execute(repo_path=str(repo.working_dir), action="save", message="wip")
    repo.heads.feature.checkout()
    readme.write_text("feature conflict\n", encoding="utf-8")
    repo.index.add([str(readme)])
    repo.index.commit("feature conflict commit")
    repo.heads.master.checkout()
    readme.write_text("master conflict\n", encoding="utf-8")
    repo.index.add([str(readme)])
    repo.index.commit("master conflict commit")

    merge_result = GitMerge().execute(repo_path=str(repo.working_dir), target="feature", abort_on_conflict=True)

    assert rebase_result.get("error") is None
    assert checkout_result["action"] == "switch_branch"
    assert stash_result["action"] == "save"
    assert merge_result["target"] == "feature"