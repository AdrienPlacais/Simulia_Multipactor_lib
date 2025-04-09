"""Define tests for :class:`.ParticleMonitor`."""

from pathlib import Path

import pytest

from simultipac.particle_monitor.particle_monitor import (
    _absolute_file_paths,
    _get_float_from_filename,
    _sorted_particle_monitor_files,
)


@pytest.mark.tmp
def test_returns_all_files(tmp_path: Path) -> None:
    """Test that all files in a directory are returned.

    Parameters
    ----------
    tmp_path :
        Pytest fixture providing a temporary directory.
    """
    (tmp_path / "file1.txt").write_text("a")
    (tmp_path / "file2.csv").write_text("b")
    (tmp_path / "file3.log").write_text("c")

    files = list(_absolute_file_paths(tmp_path))
    assert len(files) == 3
    assert all(isinstance(f, Path) for f in files)


@pytest.mark.tmp
def test_ignores_given_suffix(tmp_path: Path) -> None:
    """Test that files with specified ignored suffixes are not returned.

    Parameters
    ----------
    tmp_path :
        Pytest fixture providing a temporary directory.
    """
    (tmp_path / "keep1.txt").write_text("x")
    (tmp_path / "ignore1.swp").write_text("x")
    (tmp_path / "ignore2.swp").write_text("x")

    files = list(
        _absolute_file_paths(tmp_path, particle_monitor_ignore={".swp"})
    )
    names = [f.name for f in files]
    assert "keep1.txt" in names
    assert "ignore1.swp" not in names


@pytest.mark.tmp
def test_recursively_finds_files(tmp_path: Path) -> None:
    """Test that the function recursively finds files in subdirectories.

    Parameters
    ----------
    tmp_path :
        Pytest fixture providing a temporary directory.
    """
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "inner.txt").write_text("inner")
    (tmp_path / "outer.txt").write_text("outer")

    files = list(_absolute_file_paths(tmp_path))
    names = [f.name for f in files]
    assert "outer.txt" in names
    assert "inner.txt" in names


@pytest.mark.tmp
def test_no_files_returns_empty(tmp_path: Path) -> None:
    """Test that an empty directory yields an empty result.

    Parameters
    ----------
    tmp_path :
        Pytest fixture providing a temporary directory.
    """
    files = list(_absolute_file_paths(tmp_path))
    assert files == []


@pytest.mark.tmp
def test_empty_ignored_means_no_exclusion(tmp_path: Path) -> None:
    """
    Test that no files are excluded when ``particle_monitor_ignore`` is empty.

    Parameters
    ----------
    tmp_path :
        Pytest fixture providing a temporary directory.
    """
    (tmp_path / "a.swp").write_text("should not be ignored")
    files = list(_absolute_file_paths(tmp_path, particle_monitor_ignore=set()))
    names = [f.name for f in files]
    assert "a.swp" in names


@pytest.mark.tmp
@pytest.mark.parametrize(
    "filename,expected",
    [
        ("position  monitor 1_0.117175810039043.txt", 0.117175810039043),
        ("position  monitor 1_7.81172066926956E-02.txt", 7.81172066926956e-2),
        ("monitor_output_1.23.txt", 1.23),
        ("x_42.txt", 42.0),
        ("some_path/abc_1.0.txt", 1.0),
        ("another_path/def_5E+01.txt", 5e1),
    ],
)
def test_get_float_from_filename_valid(
    filename: str | Path, expected: float
) -> None:
    """Test that the float is correctly extracted from valid filenames."""
    assert _get_float_from_filename(Path(filename)) == pytest.approx(expected)


@pytest.mark.tmp
@pytest.mark.parametrize(
    "filename",
    [
        "monitor.txt",
        "monitor_abc.txt",
        "monitor_1.23.csv",
        "monitor_.txt",
        "monitor_123",
        "monitor.txt.bak",
    ],
)
def test_get_float_from_filename_invalid(filename: str | Path) -> None:
    """Test that ValueError is raised for invalid filenames."""
    with pytest.raises(ValueError, match="Cannot extract float from filename"):
        _get_float_from_filename(Path(filename))


@pytest.mark.tmp
def test_sorted_particle_monitor_files_order(tmp_path: Path) -> None:
    """Test that files are correctly sorted by float extracted from filename."""
    # Files created out of order
    filenames = [
        "particle monitor 1_1.0.txt",
        "particle monitor 1_0.1.txt",
        "particle monitor 1_1.2.txt",
        "particle monitor 1_7.81E-02.txt",
        "particle monitor 1_0.9.txt",
    ]
    for name in filenames:
        (tmp_path / name).write_text("dummy")

    sorted_files, max_time = _sorted_particle_monitor_files(tmp_path)
    sorted_names = [f.name for f in sorted_files]

    expected_order = [
        "particle monitor 1_7.81E-02.txt",
        "particle monitor 1_0.1.txt",
        "particle monitor 1_0.9.txt",
        "particle monitor 1_1.0.txt",
        "particle monitor 1_1.2.txt",
    ]

    assert sorted_names == expected_order
    assert max_time == 1.2


@pytest.mark.tmp
def test_sorted_particle_monitor_files_ignores_non_txt(tmp_path: Path) -> None:
    """Test that files with invalid extensions or formats are ignored."""
    valid_files = [
        "particle monitor 1_0.1.txt",
        "particle monitor 1_0.2.txt",
    ]
    invalid_files = [
        "particle monitor 1_0.3.csv",  # wrong extension
        "particle monitor 1_1.0.txt.swp",  # extra extension
    ]

    for name in valid_files + invalid_files:
        (tmp_path / name).write_text("x")

    sorted_files, max_time = _sorted_particle_monitor_files(
        tmp_path, particle_monitor_ignore=(".swp", ".csv")
    )
    sorted_names = [f.name for f in sorted_files]

    assert sorted_names == sorted(valid_files)
    assert max_time == 0.2


@pytest.mark.tmp
def test_sorted_particle_monitor_files_empty_dir(tmp_path: Path) -> None:
    """Test that an empty directory returns an empty list."""
    sorted_files, max_time = _sorted_particle_monitor_files(tmp_path)
    assert sorted_files == []
    assert max_time == 0.0
