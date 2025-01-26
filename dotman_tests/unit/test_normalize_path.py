import os
from typing import assert_type
from dotman_tests.test_utils import ensure_folder_tree
from pathlib import Path
from dotman.main import normalize_path


def test_root_paths():
    assert normalize_path(Path("/a/b")).as_posix() == Path("/a/b").as_posix()
    assert normalize_path(Path("/")).as_posix() == Path("/").as_posix()
    assert normalize_path(Path("/a/b/../c")).as_posix() == Path("/a/c").as_posix()
    assert normalize_path(Path("/a/b/..//./c")).as_posix() == Path("/a/c").as_posix()
    assert (
        normalize_path(Path("/a/../../..//./a/c")).as_posix() == Path("/a/c").as_posix()
    )


def test_cwd_paths():
    cwd = os.getcwd()
    assert normalize_path(Path("a/b")).as_posix() == Path(cwd, "a/b").as_posix()
    assert normalize_path(Path("")).as_posix() == Path(cwd).as_posix()
    assert normalize_path(Path(".")).as_posix() == Path(cwd).as_posix()
    assert normalize_path(Path("a/b/../..")).as_posix() == Path(cwd).as_posix()
    assert normalize_path(Path("./a/b/./c")).as_posix() == Path(cwd, "a/b/c").as_posix()


def test_home_paths():
    home = Path.home()
    assert normalize_path(Path("~/a/b")).as_posix() == Path(home, "a/b").as_posix()
    assert normalize_path(Path("~")).as_posix() == Path(home).as_posix()
    assert normalize_path(Path("~/a/b/../..")).as_posix() == Path(home).as_posix()
    assert (
        normalize_path(Path("~/a/b/./c")).as_posix() == Path(home, "a/b/c").as_posix()
    )


def test_symlink_paths(tmp_path):
    a = Path(tmp_path, "a")
    b = Path(a, "b")
    c = Path(b, "c")
    f = Path(c, "file.txt")

    ensure_folder_tree(folders=[c], files=[(f, "some")])
    link_to_b = Path(tmp_path, "link_to_b")
    link_to_b.symlink_to(b)

    sym_path_to_f = Path(tmp_path, "link_to_b/c/file.txt")
    abs_path_to_f = Path(tmp_path, "a/b/c/file.txt")
    sym_path_to_f_resolved = sym_path_to_f.resolve()
    sym_path_to_f_norm = normalize_path(sym_path_to_f)

    assert sym_path_to_f.read_text() == "some"
    assert abs_path_to_f.read_text() == "some"
    assert sym_path_to_f_resolved.read_text() == "some"
    assert sym_path_to_f_norm.read_text() == "some"
    assert sym_path_to_f.as_posix() == sym_path_to_f_norm.as_posix()
    assert sym_path_to_f_resolved.as_posix() == abs_path_to_f.as_posix()
    assert sym_path_to_f.as_posix() != abs_path_to_f.as_posix()
    assert Path(*sym_path_to_f_norm.parts[-3:]).as_posix() == "link_to_b/c/file.txt"
    assert Path(*sym_path_to_f_resolved.parts[-4:]).as_posix() == "a/b/c/file.txt"
