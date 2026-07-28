"""
File Utilities & Path Handling Module for CodeSlim.

Provides target discovery, path validation, file size guards,
and `.codeslimignore` glob matching.
"""

import fnmatch
from pathlib import Path

from codeslim.utils.logger import get_logger

log = get_logger("codeslim.utils.file_utils")

# Maximum supported file size (500 KB)
MAX_FILE_SIZE_BYTES = 500 * 1024

# Default directories and file patterns ignored automatically
DEFAULT_IGNORE_PATTERNS = {
    "**/__pycache__/**",
    "**/.venv/**",
    "**/venv/**",
    "**/node_modules/**",
    "**/.git/**",
    "**/.pytest_cache/**",
    "**/build/**",
    "**/dist/**",
    "**/*.egg-info/**",
    "**/migrations/**",
}


def load_ignore_patterns(root_dir: Path) -> set[str]:
    """
    Load glob patterns from `.codeslimignore` if present.

    Args:
        root_dir: Root directory of target search.

    Returns:
        Set of ignore patterns.
    """
    patterns = set(DEFAULT_IGNORE_PATTERNS)
    ignore_file = root_dir / ".codeslimignore"

    if ignore_file.exists() and ignore_file.is_file():
        try:
            content = ignore_file.read_text(encoding="utf-8")
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.add(line)
            log.info("loaded_ignore_patterns", count=len(patterns), path=str(ignore_file))
        except Exception as exc:
            log.warning("failed_loading_ignore_file", path=str(ignore_file), error=str(exc))

    return patterns


def is_ignored(file_path: Path, root_dir: Path, ignore_patterns: set[str]) -> bool:
    """
    Check if a path matches any ignore pattern.

    Args:
        file_path: Path to inspect.
        root_dir: Base search directory.
        ignore_patterns: Active glob patterns.

    Returns:
        True if path matches an ignore rule; False otherwise.
    """
    rel_path_str = str(file_path.relative_to(root_dir)).replace("\\", "/")

    for pattern in ignore_patterns:
        clean_pattern = pattern.strip()

        if fnmatch.fnmatch(rel_path_str, clean_pattern) or fnmatch.fnmatch(file_path.name, clean_pattern):
            return True

        if clean_pattern.endswith("/") and rel_path_str.startswith(clean_pattern.rstrip("/")):
            return True

    return False


def validate_file_path(file_path: Path, max_size_bytes: int = MAX_FILE_SIZE_BYTES) -> Path:
    """
    Validate existence, file type, and size limits.

    Args:
        file_path: Target path.
        max_size_bytes: Size threshold in bytes.

    Returns:
        Resolved absolute Path.

    Raises:
        FileNotFoundError: If path does not exist.
        ValueError: If path is not a file or exceeds size limit.
    """
    resolved = file_path.resolve()

    if not resolved.exists():
        log.error("file_validation_failed_not_found", path=str(file_path))
        raise FileNotFoundError(f"File not found: {file_path}")

    if not resolved.is_file():
        log.error("file_validation_failed_not_a_file", path=str(file_path))
        raise ValueError(f"Path is not a regular file: {file_path}")

    size = resolved.stat().st_size
    if size > max_size_bytes:
        log.error("file_too_large", path=str(file_path), size_kb=size / 1024, max_kb=max_size_bytes / 1024)
        raise ValueError(
            f"File size ({size / 1024:.1f} KB) exceeds maximum supported limit "
            f"({max_size_bytes / 1024:.1f} KB): {file_path}"
        )

    return resolved


def collect_target_files(target_path: Path) -> list[Path]:
    """
    Discover all target Python files given a single file or directory path.

    Args:
        target_path: Path to file or directory.

    Returns:
        Sorted list of resolved Python file paths.

    Raises:
        FileNotFoundError: If target path does not exist.
        ValueError: If target file is non-Python or directory yields no Python files.
    """
    resolved = target_path.resolve()

    if not resolved.exists():
        log.error("target_path_not_found", path=str(target_path))
        raise FileNotFoundError(f"Target path does not exist: {target_path}")

    if resolved.is_file():
        if resolved.suffix != ".py":
            log.warning("non_python_file_targeted", path=str(target_path))
            raise ValueError(f"CodeSlim only analyzes Python (.py) files: {target_path}")
        return [validate_file_path(resolved)]

    log.info("discovering_files_in_directory", directory=str(resolved))
    ignore_patterns = load_ignore_patterns(resolved)
    collected_files: list[Path] = []

    for file_path in resolved.rglob("*.py"):
        if is_ignored(file_path, resolved, ignore_patterns):
            log.debug("file_ignored", file=str(file_path.relative_to(resolved)))
            continue

        try:
            valid_file = validate_file_path(file_path)
            collected_files.append(valid_file)
        except ValueError as exc:
            log.warning("skipping_invalid_file", file=file_path.name, reason=str(exc))

    log.info("file_discovery_complete", total_found=len(collected_files), directory=str(resolved))

    if not collected_files:
        raise ValueError(f"No valid Python (.py) files found in target directory: {target_path}")

    return sorted(collected_files)
