"""
Unit tests for the Virtual File System (VFS).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from filesystem.vfs import VirtualFileSystem


@pytest.fixture
def vfs() -> VirtualFileSystem:
    """Fresh VFS for each test."""
    return VirtualFileSystem()


# ── File operations ───────────────────────────────────────────────────────────

class TestFileOperations:
    def test_write_and_read(self, vfs: VirtualFileSystem) -> None:
        vfs.write_file("/project/main.py", "print('hello')")
        assert vfs.read_file("/project/main.py") == "print('hello')"

    def test_overwrite_updates_content(self, vfs: VirtualFileSystem) -> None:
        vfs.write_file("/project/main.py", "v1")
        vfs.write_file("/project/main.py", "v2")
        assert vfs.read_file("/project/main.py") == "v2"

    def test_create_and_read(self, vfs: VirtualFileSystem) -> None:
        vfs.create_file("/project/new.py", "# new")
        assert vfs.read_file("/project/new.py") == "# new"

    def test_create_raises_if_exists(self, vfs: VirtualFileSystem) -> None:
        vfs.create_file("/project/f.py", "x")
        with pytest.raises(FileExistsError):
            vfs.create_file("/project/f.py", "y")

    def test_delete_file(self, vfs: VirtualFileSystem) -> None:
        vfs.write_file("/project/tmp.py", "")
        vfs.delete_file("/project/tmp.py")
        assert not vfs.file_exists("/project/tmp.py")

    def test_delete_nonexistent_raises(self, vfs: VirtualFileSystem) -> None:
        with pytest.raises(FileNotFoundError):
            vfs.delete_file("/project/ghost.py")

    def test_read_nonexistent_raises(self, vfs: VirtualFileSystem) -> None:
        with pytest.raises(FileNotFoundError):
            vfs.read_file("/project/nope.py")


# ── Directory operations ──────────────────────────────────────────────────────

class TestDirectoryOperations:
    def test_mkdir_and_write_nested(self, vfs: VirtualFileSystem) -> None:
        vfs.mkdir("/project/src/utils")
        vfs.write_file("/project/src/utils/helpers.py", "# utils")
        assert vfs.file_exists("/project/src/utils/helpers.py")

    def test_auto_creates_parents(self, vfs: VirtualFileSystem) -> None:
        vfs.write_file("/project/deep/nested/file.py", "content")
        assert vfs.file_exists("/project/deep/nested/file.py")

    def test_dir_exists(self, vfs: VirtualFileSystem) -> None:
        vfs.mkdir("/project/subdir")
        assert vfs.dir_exists("/project/subdir")
        assert not vfs.dir_exists("/project/nonexistent")


# ── Path safety ───────────────────────────────────────────────────────────────

class TestPathSafety:
    def test_reject_path_outside_project(self, vfs: VirtualFileSystem) -> None:
        with pytest.raises(ValueError):
            vfs.write_file("/etc/passwd", "hacked")

    def test_reject_relative_path(self, vfs: VirtualFileSystem) -> None:
        with pytest.raises(ValueError):
            vfs.write_file("../../etc/passwd", "hacked")

    def test_normalise_double_slash(self, vfs: VirtualFileSystem) -> None:
        vfs.write_file("/project//file.py", "ok")
        assert vfs.file_exists("/project/file.py")


# ── Version tracking & rollback ───────────────────────────────────────────────

class TestVersioning:
    def test_version_increments(self, vfs: VirtualFileSystem) -> None:
        vfs.write_file("/project/f.py", "v0")
        assert vfs.file_version("/project/f.py") == 0
        vfs.write_file("/project/f.py", "v1")
        assert vfs.file_version("/project/f.py") == 1

    def test_rollback_one_step(self, vfs: VirtualFileSystem) -> None:
        vfs.write_file("/project/f.py", "original")
        vfs.write_file("/project/f.py", "changed")
        success = vfs.rollback_file("/project/f.py", steps=1)
        assert success
        assert vfs.read_file("/project/f.py") == "original"

    def test_rollback_fails_at_origin(self, vfs: VirtualFileSystem) -> None:
        vfs.write_file("/project/f.py", "only-version")
        success = vfs.rollback_file("/project/f.py", steps=1)
        assert not success  # no history to roll back to

    def test_diff_returns_previous_and_current(self, vfs: VirtualFileSystem) -> None:
        vfs.write_file("/project/f.py", "before")
        vfs.write_file("/project/f.py", "after")
        diff = vfs.file_diff("/project/f.py")
        assert diff == ("before", "after")

    def test_diff_returns_none_for_new_file(self, vfs: VirtualFileSystem) -> None:
        vfs.write_file("/project/f.py", "only")
        assert vfs.file_diff("/project/f.py") is None


# ── Listing ───────────────────────────────────────────────────────────────────

class TestListing:
    def test_list_files_empty(self, vfs: VirtualFileSystem) -> None:
        assert vfs.list_files() == []

    def test_list_files_returns_all(self, vfs: VirtualFileSystem) -> None:
        vfs.write_file("/project/a.py", "")
        vfs.write_file("/project/b.py", "")
        files = vfs.list_files()
        assert "/project/a.py" in files
        assert "/project/b.py" in files

    def test_list_files_nested(self, vfs: VirtualFileSystem) -> None:
        vfs.write_file("/project/src/main.py", "")
        vfs.write_file("/project/tests/test_main.py", "")
        files = vfs.list_files()
        assert any("src/main.py" in f for f in files)
        assert any("test_main.py" in f for f in files)


# ── Snapshot / restore ────────────────────────────────────────────────────────

class TestSnapshot:
    def test_snapshot_and_restore(self, vfs: VirtualFileSystem) -> None:
        vfs.write_file("/project/main.py", "original")
        snap = vfs.snapshot()
        vfs.write_file("/project/main.py", "modified")
        assert vfs.read_file("/project/main.py") == "modified"
        vfs.restore(snap)
        assert vfs.read_file("/project/main.py") == "original"


# ── FileTree serialization ────────────────────────────────────────────────────

class TestFileTree:
    def test_to_file_tree(self, vfs: VirtualFileSystem) -> None:
        vfs.write_file("/project/main.py", "x = 1")
        tree = vfs.to_file_tree()
        assert tree.total_files == 1
        assert tree.root is not None

    def test_to_file_tree_counts(self, vfs: VirtualFileSystem) -> None:
        vfs.write_file("/project/a.py", "")
        vfs.write_file("/project/b.py", "")
        vfs.write_file("/project/sub/c.py", "")
        tree = vfs.to_file_tree()
        assert tree.total_files == 3
