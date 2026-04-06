"""
Virtual File System (VFS) — in-memory file system simulator for OpenEnv CodeAgent.

Features
--------
- Directory tree with full path support
- Version tracking (per-file content history)
- Rollback to any previous version
- Path safety checks (no escaping /project/)
- Serialization to FileTree observation model
"""

from __future__ import annotations

import copy
import posixpath
from pathlib import PurePosixPath
from typing import Dict, List, Optional, Tuple

from models.observation import FileNode, FileTree


# ---------------------------------------------------------------------------
# Internal representations
# ---------------------------------------------------------------------------

class _FileEntry:
    """A single file with its content history."""

    def __init__(self, content: str) -> None:
        self._history: List[str] = [content]

    @property
    def content(self) -> str:
        return self._history[-1]

    @content.setter
    def content(self, new_content: str) -> None:
        self._history.append(new_content)

    def rollback(self, steps: int = 1) -> bool:
        """Roll back `steps` versions. Returns True on success."""
        if len(self._history) > steps:
            self._history = self._history[: len(self._history) - steps]
            return True
        return False

    @property
    def version(self) -> int:
        return len(self._history) - 1

    def diff(self) -> Optional[Tuple[str, str]]:
        """Return (previous, current) content tuple, or None if no history."""
        if len(self._history) < 2:
            return None
        return self._history[-2], self._history[-1]


class _DirEntry:
    """A directory node in the VFS tree."""

    def __init__(self) -> None:
        self.files: Dict[str, _FileEntry] = {}   # name → file
        self.dirs: Dict[str, "_DirEntry"] = {}   # name → subdir


# ---------------------------------------------------------------------------
# Public VFS class
# ---------------------------------------------------------------------------

ROOT_PREFIX = "/project"


class VirtualFileSystem:
    """
    In-memory virtual file system rooted at ``/project``.

    All paths must be absolute and must start with ``/project``.
    """

    def __init__(self) -> None:
        self._root = _DirEntry()
        # Ensure /project root exists
        self._root.dirs["project"] = _DirEntry()

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_path(path: str) -> str:
        """Normalise and security-check a path."""
        normalised = posixpath.normpath(path)
        if not normalised.startswith(ROOT_PREFIX):
            raise ValueError(
                f"Path '{path}' is outside the allowed root '{ROOT_PREFIX}'."
            )
        return normalised

    def _resolve(self, path: str) -> Tuple[_DirEntry, str]:
        """
        Walk the VFS tree to the *parent directory* of `path`.

        Returns (parent_dir_entry, leaf_name).
        Raises FileNotFoundError if any intermediate directory is missing.
        """
        path = self._validate_path(path)
        parts = PurePosixPath(path).parts  # ('/', 'project', ..., 'leaf')
        # Start from absolute root
        node: _DirEntry = self._root
        # Walk through all parts except the last (leaf)
        for part in parts[1:-1]:  # skip leading '/'
            if part not in node.dirs:
                raise FileNotFoundError(
                    f"Directory component '{part}' not found in path '{path}'."
                )
            node = node.dirs[part]
        leaf = parts[-1]
        return node, leaf

    # ------------------------------------------------------------------
    # Directory operations
    # ------------------------------------------------------------------

    def mkdir(self, path: str, exist_ok: bool = True) -> None:
        """Create a directory (and all parents) at ``path``."""
        path = self._validate_path(path)
        parts = PurePosixPath(path).parts  # ('/', 'project', ...)
        node: _DirEntry = self._root
        for part in parts[1:]:  # skip leading '/'
            if part not in node.dirs:
                node.dirs[part] = _DirEntry()
            node = node.dirs[part]

    # ------------------------------------------------------------------
    # File operations
    # ------------------------------------------------------------------

    def create_file(self, path: str, content: str = "") -> None:
        """Create a new file at ``path``. Raises FileExistsError if it exists."""
        path = self._validate_path(path)
        parent, leaf = self._get_or_create_parent(path)
        if leaf in parent.files:
            raise FileExistsError(f"File already exists: '{path}'.")
        parent.files[leaf] = _FileEntry(content)

    def write_file(self, path: str, content: str) -> None:
        """
        Write (overwrite) content to a file.
        Creates the file if it does not exist (and any missing parents).
        Records the old content in history if overwriting.
        """
        path = self._validate_path(path)
        parent, leaf = self._get_or_create_parent(path)
        if leaf in parent.files:
            parent.files[leaf].content = content
        else:
            parent.files[leaf] = _FileEntry(content)

    def read_file(self, path: str) -> str:
        """Read the current content of a file."""
        path = self._validate_path(path)
        parent, leaf = self._resolve(path)
        if leaf not in parent.files:
            raise FileNotFoundError(f"File not found: '{path}'.")
        return parent.files[leaf].content

    def delete_file(self, path: str) -> None:
        """Delete a file."""
        path = self._validate_path(path)
        parent, leaf = self._resolve(path)
        if leaf not in parent.files:
            raise FileNotFoundError(f"File not found: '{path}'.")
        del parent.files[leaf]

    def file_exists(self, path: str) -> bool:
        try:
            self._validate_path(path)
            parent, leaf = self._resolve(path)
            return leaf in parent.files
        except (FileNotFoundError, ValueError):
            return False

    def dir_exists(self, path: str) -> bool:
        try:
            path = self._validate_path(path)
            parts = PurePosixPath(path).parts
            node: _DirEntry = self._root
            for part in parts[1:]:
                if part not in node.dirs:
                    return False
                node = node.dirs[part]
            return True
        except ValueError:
            return False

    # ------------------------------------------------------------------
    # Version / rollback
    # ------------------------------------------------------------------

    def rollback_file(self, path: str, steps: int = 1) -> bool:
        """Roll back a file by `steps` versions. Returns True on success."""
        path = self._validate_path(path)
        parent, leaf = self._resolve(path)
        if leaf not in parent.files:
            raise FileNotFoundError(f"File not found: '{path}'.")
        return parent.files[leaf].rollback(steps)

    def file_version(self, path: str) -> int:
        path = self._validate_path(path)
        parent, leaf = self._resolve(path)
        if leaf not in parent.files:
            raise FileNotFoundError(f"File not found: '{path}'.")
        return parent.files[leaf].version

    def file_diff(self, path: str) -> Optional[Tuple[str, str]]:
        """Return (previous, current) content or None if no prior version."""
        path = self._validate_path(path)
        parent, leaf = self._resolve(path)
        if leaf not in parent.files:
            raise FileNotFoundError(f"File not found: '{path}'.")
        return parent.files[leaf].diff()

    # ------------------------------------------------------------------
    # Snapshot / restore
    # ------------------------------------------------------------------

    def snapshot(self) -> "_FSSnapshot":
        """Return a deep-copy snapshot of the entire VFS."""
        return _FSSnapshot(copy.deepcopy(self._root))

    def restore(self, snap: "_FSSnapshot") -> None:
        """Restore the VFS to a previously captured snapshot."""
        self._root = copy.deepcopy(snap._root)

    # ------------------------------------------------------------------
    # Listing
    # ------------------------------------------------------------------

    def list_files(self, directory: str = ROOT_PREFIX) -> List[str]:
        """Recursively list all file paths under ``directory``."""
        directory = self._validate_path(directory)
        results: List[str] = []
        self._walk(directory, results)
        return sorted(results)

    def _walk(self, dir_path: str, results: List[str]) -> None:
        parts = PurePosixPath(dir_path).parts
        node: _DirEntry = self._root
        for part in parts[1:]:
            if part not in node.dirs:
                return
            node = node.dirs[part]
        for fname in node.files:
            results.append(posixpath.join(dir_path, fname))
        for dname in node.dirs:
            self._walk(posixpath.join(dir_path, dname), results)

    # ------------------------------------------------------------------
    # Observation serialisation
    # ------------------------------------------------------------------

    def to_file_tree(self) -> FileTree:
        """Convert VFS state to the Observation FileTree model."""
        root_node, total_files, total_dirs = self._build_node(
            "/", self._root, "/"
        )
        return FileTree(
            root=root_node,
            total_files=total_files,
            total_dirs=total_dirs,
        )

    def _build_node(
        self, name: str, entry: _DirEntry, path: str
    ) -> Tuple[FileNode, int, int]:
        children: List[FileNode] = []
        total_files = 0
        total_dirs = 0

        for dname, dentry in sorted(entry.dirs.items()):
            child_path = posixpath.join(path, dname)
            child_node, f, d = self._build_node(dname, dentry, child_path)
            children.append(child_node)
            total_files += f
            total_dirs += d + 1

        for fname, fentry in sorted(entry.files.items()):
            file_path = posixpath.join(path, fname)
            children.append(
                FileNode(
                    name=fname,
                    path=file_path,
                    is_dir=False,
                    size_bytes=len(fentry.content.encode()),
                )
            )
            total_files += 1

        node = FileNode(
            name=name,
            path=path,
            is_dir=True,
            children=children,
        )
        return node, total_files, total_dirs

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_or_create_parent(self, path: str) -> Tuple[_DirEntry, str]:
        """Ensure all parent directories exist, return (parent_dir, leaf_name)."""
        parts = PurePosixPath(path).parts  # ('/', 'project', ..., 'leaf')
        node: _DirEntry = self._root
        for part in parts[1:-1]:
            if part not in node.dirs:
                node.dirs[part] = _DirEntry()
            node = node.dirs[part]
        return node, parts[-1]

    def load_initial_files(self, files: Dict[str, str]) -> None:
        """Bulk-load a dict of path → content into a fresh VFS."""
        for path, content in files.items():
            self.write_file(path, content)


class _FSSnapshot:
    """Immutable snapshot of the VFS tree."""

    def __init__(self, root: _DirEntry) -> None:
        self._root = root
