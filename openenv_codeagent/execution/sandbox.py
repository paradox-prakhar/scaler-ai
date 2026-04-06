"""
Sandbox Execution Engine — restricted code execution for OpenEnv CodeAgent.

Architecture
------------
- Uses ``multiprocessing`` to isolate execution in a child process.
- ``run_pytest_style`` writes VFS files to a temp dir and runs tests via subprocess.
- Hard timeout enforced by Process.join(timeout) + terminate().
- Stdout/stderr captured via queue.
"""

from __future__ import annotations

import multiprocessing
import os
import queue
import subprocess
import sys
import tempfile
import textwrap
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# Windows requires this when using multiprocessing in scripts
if sys.platform == "win32":
    multiprocessing.freeze_support()


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ExecutionResult:
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0
    timed_out: bool = False
    error: Optional[str] = None
    execution_time_ms: float = 0.0

    @property
    def success(self) -> bool:
        return self.returncode == 0 and not self.timed_out and self.error is None

    def combined_output(self) -> str:
        parts = []
        if self.stdout:
            parts.append(self.stdout)
        if self.stderr:
            parts.append(f"[stderr]\n{self.stderr}")
        if self.timed_out:
            parts.append("[TIMEOUT] Execution exceeded time limit.")
        if self.error:
            parts.append(f"[ERROR] {self.error}")
        return "\n".join(parts)


# ---------------------------------------------------------------------------
# Worker function (runs in child process) — for arbitrary code snippets
# ---------------------------------------------------------------------------

def _restricted_exec_worker(
    code: str,
    global_env: Dict[str, Any],
    result_queue: "multiprocessing.Queue[Dict]",
) -> None:
    """
    Child process: execute ``code`` inside a restricted environment.
    Puts a result dict onto ``result_queue``.
    """
    import io
    import sys
    import time

    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()

    # Redirect output
    sys.stdout = stdout_buf
    sys.stderr = stderr_buf

    start = time.perf_counter()
    returncode = 0
    error_msg: Optional[str] = None

    try:
        # Attempt to import RestrictedPython; fall back to plain exec if unavailable
        try:
            from RestrictedPython import compile_restricted, safe_globals, safe_builtins
            from RestrictedPython.Guards import safe_import, guarded_iter_unpack_sequence

            restricted_globals = dict(safe_globals)
            restricted_globals["__builtins__"] = dict(safe_builtins)
            restricted_globals["__builtins__"]["__import__"] = safe_import
            restricted_globals["_getiter_"] = iter
            restricted_globals["_getattr_"] = getattr
            restricted_globals["_write_"] = lambda x: x
            restricted_globals["_iter_unpack_sequence_"] = guarded_iter_unpack_sequence
            restricted_globals.update(global_env)

            byte_code = compile_restricted(code, filename="<agent_code>", mode="exec")
            exec(byte_code, restricted_globals)

        except ImportError:
            # RestrictedPython not installed — use plain exec with limited builtins
            # In a subprocess, __builtins__ can be a module OR a dict depending on context
            import builtins as _builtins_module
            _all_builtins = vars(_builtins_module)
            safe_builtins_plain = {
                k: v
                for k, v in _all_builtins.items()
                if k not in ("open", "__import__", "exec", "eval", "compile")
            }
            exec_globals = {"__builtins__": safe_builtins_plain}
            exec_globals.update(global_env)
            exec(compile(code, "<agent_code>", "exec"), exec_globals)

    except SystemExit as e:
        returncode = e.code if isinstance(e.code, int) else 1
    except Exception:
        returncode = 1
        error_msg = traceback.format_exc()

    elapsed_ms = (time.perf_counter() - start) * 1000

    result_queue.put(
        {
            "stdout": stdout_buf.getvalue(),
            "stderr": stderr_buf.getvalue(),
            "returncode": returncode,
            "error": error_msg,
            "execution_time_ms": elapsed_ms,
        }
    )


# ---------------------------------------------------------------------------
# Worker function for tempdir-based test execution
# ---------------------------------------------------------------------------

def _tempdir_exec_worker(
    vfs_files: Dict[str, str],
    test_path: str,
    runner_code: str,
    result_queue: "multiprocessing.Queue[Dict]",
) -> None:
    """
    Child process: write VFS files to a temp directory, then execute the runner.
    """
    import io
    import os
    import sys
    import tempfile
    import time
    import traceback

    result = {
        "stdout": "",
        "stderr": "",
        "returncode": 0,
        "error": None,
        "execution_time_ms": 0.0,
    }

    start = time.perf_counter()

    try:
        with tempfile.TemporaryDirectory(prefix="openenv_") as tmpdir:
            # Write all VFS files into the tmpdir
            for vpath, content in vfs_files.items():
                # Strip leading slash and convert to OS path
                rel = vpath.lstrip("/")
                dest = os.path.join(tmpdir, rel.replace("/", os.sep))
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(dest, "w", encoding="utf-8") as f:
                    f.write(content)

            # Write the runner script
            runner_path = os.path.join(tmpdir, "_openenv_runner.py")
            with open(runner_path, "w", encoding="utf-8") as f:
                f.write(runner_code)

            # Execute runner script as a subprocess
            env = os.environ.copy()
            env["PYTHONPATH"] = tmpdir
            proc = subprocess.run(
                [sys.executable, runner_path],
                capture_output=True,
                text=True,
                timeout=30,
                env=env,
                cwd=tmpdir,
            )
            result["stdout"] = proc.stdout
            result["stderr"] = proc.stderr
            result["returncode"] = proc.returncode

    except subprocess.TimeoutExpired:
        result["returncode"] = 124
        result["error"] = "Subprocess timed out after 30 seconds."
    except Exception:
        result["returncode"] = 1
        result["error"] = traceback.format_exc()

    result["execution_time_ms"] = (time.perf_counter() - start) * 1000
    result_queue.put(result)


# ---------------------------------------------------------------------------
# Public executor
# ---------------------------------------------------------------------------

class RestrictedExecutor:
    """
    Execute arbitrary code snippets in a sandboxed subprocess.

    Parameters
    ----------
    timeout_seconds : float
        Wall-clock timeout. Processes exceeding this are killed.
    max_output_chars : int
        Truncate stdout/stderr beyond this length to prevent memory abuse.
    """

    def __init__(
        self,
        timeout_seconds: float = 10.0,
        max_output_chars: int = 8192,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_output_chars = max_output_chars

    def execute(
        self,
        code: str,
        global_env: Optional[Dict[str, Any]] = None,
    ) -> ExecutionResult:
        """
        Run ``code`` in a restricted subprocess and return the result.
        """
        import time

        if global_env is None:
            global_env = {}

        result_queue: multiprocessing.Queue = multiprocessing.Queue()
        proc = multiprocessing.Process(
            target=_restricted_exec_worker,
            args=(code, global_env, result_queue),
            daemon=True,
        )

        start = time.perf_counter()
        proc.start()
        proc.join(timeout=self.timeout_seconds)
        elapsed_ms = (time.perf_counter() - start) * 1000

        timed_out = proc.is_alive()
        if timed_out:
            proc.terminate()
            proc.join(timeout=2)
            if proc.is_alive():
                proc.kill()
            return ExecutionResult(
                timed_out=True,
                returncode=124,
                execution_time_ms=elapsed_ms,
            )

        try:
            raw = result_queue.get_nowait()
        except queue.Empty:
            return ExecutionResult(
                error="Process exited without producing output.",
                returncode=1,
                execution_time_ms=elapsed_ms,
            )

        return ExecutionResult(
            stdout=self._trunc(raw.get("stdout", "")),
            stderr=self._trunc(raw.get("stderr", "")),
            returncode=raw.get("returncode", 0),
            error=raw.get("error"),
            execution_time_ms=raw.get("execution_time_ms", elapsed_ms),
        )

    def execute_file(
        self,
        source: str,
        filename: str = "<file>",
        global_env: Optional[Dict[str, Any]] = None,
    ) -> ExecutionResult:
        """Convenience wrapper: execute source read from a VFS file."""
        code = f"# {filename}\n" + textwrap.dedent(source)
        return self.execute(code, global_env=global_env)

    def run_pytest_style(
        self,
        test_source: str,
        subject_source: str,
        subject_module_name: str = "solution",
        vfs_files: Optional[Dict[str, str]] = None,
        test_path: str = "",
    ) -> ExecutionResult:
        """
        Run a pytest-style test file against subject modules.

        Strategy
        --------
        1. Write all VFS files to a temp directory.
        2. Add the project root (/project equivalent) to sys.path.
        3. Execute the test file with a simple inline runner.

        Parameters
        ----------
        test_source : str
            Source code of the test file.
        subject_source : str
            Source code of all project files combined (used as fallback).
        subject_module_name : str
            Module name hint (used only in fallback mode).
        vfs_files : dict, optional
            Full VFS state {vfs_path: content}. When provided, proper
            temp-dir execution is used (preferred).
        test_path : str
            VFS path of the test file (e.g. /project/tests/test_solution.py).
        """
        import time

        # Runner script that collects and runs all test_* functions
        runner_template = textwrap.dedent("""\
            import sys, os

            # Add project dir (the temp root) and /project subdir to path
            _root = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, _root)
            sys.path.insert(0, os.path.join(_root, 'project'))

            # Execute the test file source directly
            _test_globals = dict(__name__='__main__', __file__=__file__)

            {test_source_exec}

            _passed = 0
            _failed = 0
            _errors = 0

            for _name in sorted(list(_test_globals.keys())):
                _fn = _test_globals[_name]
                if _name.startswith('test_') and callable(_fn):
                    try:
                        _fn()
                        _passed += 1
                        print('PASS: ' + _name)
                    except AssertionError as _e:
                        _failed += 1
                        print('FAIL: ' + _name + ' -- ' + str(_e))
                    except Exception as _e:
                        _errors += 1
                        print('ERROR: ' + _name + ' -- ' + str(_e))

            _total = _passed + _failed + _errors
            print('')
            print('=== ' + str(_passed) + '/' + str(_total) + ' tests passed ===')
            if _failed or _errors:
                sys.exit(1)
        """)

        if vfs_files:
            # Preferred: use temp dir with real imports
            # Always exec test_source as a string — the VFS files on disk enable imports
            test_source_exec = "exec(compile(" + repr(test_source) + ", 'test_file.py', 'exec'), _test_globals)"
            runner_code = runner_template.replace(
                "{test_source_exec}",
                test_source_exec
            )
            result_queue: multiprocessing.Queue = multiprocessing.Queue()
            start = time.perf_counter()
            proc = multiprocessing.Process(
                target=_tempdir_exec_worker,
                args=(vfs_files, test_path, runner_code, result_queue),
                daemon=True,
            )
            proc.start()
            proc.join(timeout=self.timeout_seconds + 5)  # extra buffer for subproc
            elapsed_ms = (time.perf_counter() - start) * 1000

            timed_out = proc.is_alive()
            if timed_out:
                proc.terminate()
                proc.join(timeout=2)
                if proc.is_alive():
                    proc.kill()
                return ExecutionResult(timed_out=True, returncode=124, execution_time_ms=elapsed_ms)

            try:
                raw = result_queue.get_nowait()
            except queue.Empty:
                return ExecutionResult(error="No output from test process.", returncode=1, execution_time_ms=elapsed_ms)

            return ExecutionResult(
                stdout=self._trunc(raw.get("stdout", "")),
                stderr=self._trunc(raw.get("stderr", "")),
                returncode=raw.get("returncode", 0),
                error=raw.get("error"),
                execution_time_ms=raw.get("execution_time_ms", elapsed_ms),
            )

        else:
            # Fallback: flat injection (used when no vfs_files provided)
            # Build runner that embeds test source literally
            test_source_exec = "exec(" + repr(test_source) + ", _test_globals)"
            runner_code = runner_template.replace("{test_source_exec}", test_source_exec)
            flat_vfs = {"/project/tests/test_file.py": test_source}
            result_queue = multiprocessing.Queue()
            start = time.perf_counter()
            proc = multiprocessing.Process(
                target=_tempdir_exec_worker,
                args=(flat_vfs, "", runner_code, result_queue),
                daemon=True,
            )
            proc.start()
            proc.join(timeout=self.timeout_seconds + 5)
            elapsed_ms = (time.perf_counter() - start) * 1000

            timed_out = proc.is_alive()
            if timed_out:
                proc.terminate()
                proc.join(timeout=2)
                if proc.is_alive():
                    proc.kill()
                return ExecutionResult(timed_out=True, returncode=124, execution_time_ms=elapsed_ms)

            try:
                raw = result_queue.get_nowait()
            except queue.Empty:
                return ExecutionResult(error="No output from test process.", returncode=1, execution_time_ms=elapsed_ms)

            return ExecutionResult(
                stdout=self._trunc(raw.get("stdout", "")),
                stderr=self._trunc(raw.get("stderr", "")),
                returncode=raw.get("returncode", 0),
                error=raw.get("error"),
                execution_time_ms=raw.get("execution_time_ms", elapsed_ms),
            )

    def _trunc(self, s: str) -> str:
        if len(s) > self.max_output_chars:
            return s[: self.max_output_chars] + "\n... [output truncated]"
        return s
