from pathlib import Path

from git import Repo

from tools.agent.git.add import GitAdd
from tools.agent.git.blame import GitBlame
from tools.agent.git.branch import GitBranch
from tools.agent.git.checkout import GitCheckout
from tools.agent.git.commit import GitCommit
from tools.agent.git.diff import GitDiff
from tools.agent.git.log import GitLog
from tools.agent.git.merge import GitMerge
from tools.agent.git.rebase import GitRebase
from tools.agent.git.remote import GitRemote
from tools.agent.git.show import GitShow
from tools.agent.git.stash import GitStash
from tools.agent.git.tag import GitTag
from tools.agent.git.rm import GitRm
from tools.agent.registry import get_tool


def _create_repo(tmp_path: Path) -> Repo:
    repo = Repo.init(tmp_path)
    repo.git.config("user.name", "Test User")
    repo.git.config("user.email", "test@example.com")

    readme = tmp_path / "README.md"
    readme.write_text("one\n", encoding="utf-8")
    repo.index.add([str(readme)])
    repo.index.commit("initial commit")
    repo.git.branch("-M", "master")

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

    assert result.success
    assert result.output["commit_count"] == 2
    assert result.output["history"][0]["author"]["name"] == "Test User"
    assert result.output["history"][0]["files"]
    assert result.output["history"][0]["diffs"]


def test_git_branch_lists_current_and_remote_branches(tmp_path):
    repo = _create_repo(tmp_path)

    result = GitBranch().execute(repo_path=str(repo.working_dir))

    assert result.success
    assert result.output["current_branch"] == "master"
    assert any(branch["name"] == "master" for branch in result.output["local_branches"])
    assert any(branch["name"] == "feature" for branch in result.output["remote_branches"])


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

    assert refs_result.success
    assert working_tree_result.success
    assert "two" in refs_result.output["diff"]
    assert working_tree_result.output["mode"] == "working_tree"
    assert "three" in working_tree_result.output["diff"]


def test_git_registry_includes_new_tools():
    for tool_name in [
        "git_add",
        "git_rm",
        "git_commit",
        "git_stash",
        "git_checkout",
        "git_merge",
        "git_rebase",
        "git_show",
        "git_blame",
        "git_tag",
        "git_remote",
    ]:
        assert get_tool(tool_name) is not None


def _create_workflow_repo(tmp_path: Path) -> Repo:
    repo = Repo.init(tmp_path)
    repo.git.config("user.name", "Test User")
    repo.git.config("user.email", "test@example.com")

    readme = tmp_path / "README.md"
    readme.write_text("one\n", encoding="utf-8")
    repo.index.add([str(readme)])
    repo.index.commit("initial commit")

    readme.write_text("two\n", encoding="utf-8")
    return repo


def test_git_add_reports_staged_files(tmp_path):
    repo = _create_workflow_repo(tmp_path)

    add_result = GitAdd().execute(repo_path=str(repo.working_dir), paths=["README.md"])
    assert add_result.success
    assert add_result.output["staged_files"]


def test_git_commit_reports_commit_details(tmp_path):
    repo = _create_workflow_repo(tmp_path)
    commit_result = GitCommit().execute(repo_path=str(repo.working_dir), message="update readme")

    assert commit_result.success
    assert commit_result.output["commit"]["message"] == "update readme"


def test_git_show_reports_revision_contents(tmp_path):
    repo = _create_workflow_repo(tmp_path)
    show_result = GitShow().execute(repo_path=str(repo.working_dir), revision="HEAD")

    assert show_result.success
    assert "README.md" in show_result.output["result"]


def test_git_blame_reports_entries(tmp_path):
    repo = _create_workflow_repo(tmp_path)
    blame_result = GitBlame().execute(repo_path=str(repo.working_dir), path="README.md")

    assert blame_result.success
    assert blame_result.output["entries"]


def test_git_tag_reports_created_tag(tmp_path):
    repo = _create_workflow_repo(tmp_path)
    tag_result = GitTag().execute(repo_path=str(repo.working_dir), action="create", tag_name="v1.0.0")

    assert tag_result.success
    assert tag_result.output["tag"] == "v1.0.0"


def test_git_remote_reports_remotes(tmp_path):
    repo = _create_workflow_repo(tmp_path)
    remote_result = GitRemote().execute(repo_path=str(repo.working_dir), action="list")

    assert remote_result.success
    assert remote_result.output["remotes"] == []


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

    assert stage_result.output["staged_files"]
    assert stage_result.output["action"] == "stage"
    assert unstage_result.output["action"] == "unstage"
    assert rm_result.output["action"] == "rm"


def test_git_checkout_merge_stash_and_rebase(tmp_path):
    repo = Repo.init(tmp_path)
    repo.git.config("user.name", "Test User")
    repo.git.config("user.email", "test@example.com")

    readme = tmp_path / "README.md"
    readme.write_text("base\n", encoding="utf-8")
    repo.index.add([str(readme)])
    repo.index.commit("initial commit")
    repo.git.branch("-M", "master")

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

    assert rebase_result.success
    assert checkout_result.output["action"] == "switch_branch"
    assert stash_result.output["action"] == "save"
    assert merge_result.output["target"] == "feature"