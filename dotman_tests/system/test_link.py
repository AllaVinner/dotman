from os import path
from dotman_tests.test_utils import ensure_folder_tree
import json
from pathlib import Path
from dotman.main import (
    DotProject,
    ProjectConfig,
    ProjectStructure,
    PrefixType,
    PrefixTypeLiteral,
    CustomPrefix,
)
import pytest


@pytest.mark.parametrize("is_project_in_home", [True, False])
@pytest.mark.parametrize("prefix_type", ["home", "root"])
def test_basic_linking(
    prefix_type: PrefixTypeLiteral, is_project_in_home: bool, tmp_path: Path
):
    # Setup
    root_path = Path(tmp_path, "root")
    home_path = Path(root_path, "home")
    if is_project_in_home:
        projects_path = Path(home_path, "projects")
    else:
        projects_path = Path(root_path, "projects")
    files_path = Path(home_path, "files")
    source_file = Path(files_path, "my_config.txt")
    source_file_content = "Configuration Content ..."
    ensure_folder_tree(
        folders=[projects_path, home_path], files=[(source_file, source_file_content)]
    )
    project_path = Path(projects_path, "my_project")
    # Test Call
    dot_project = DotProject.ensure(Path(project_path))
    dot_project.set_home_path(home_path)
    dot_project.set_root_path(root_path)
    dot_project.add_link(source_path=source_file, prefix_type=prefix_type)

    # Assertions
    expected_source_file_path = Path(project_path, source_file.name)
    assert Path(project_path).exists()
    assert expected_source_file_path.exists()
    assert expected_source_file_path.read_text() == source_file_content
    assert Path(source_file).exists()
    assert Path(source_file).is_symlink()
    assert Path(source_file).resolve() == expected_source_file_path
    config_file = Path(project_path, ProjectStructure.PUBLIC_CONFIG)
    with open(config_file, "r") as f:
        config = json.load(f)
    assert "links" in config
    assert source_file.name in config["links"]
    link_config = config["links"][source_file.name]
    if prefix_type == "home":
        assert (
            link_config.get("link_path")
            == source_file.relative_to(home_path).as_posix()
        )
    elif prefix_type == "root":
        assert (
            link_config.get("link_path")
            == source_file.relative_to(root_path).as_posix()
        )
    else:
        raise ValueError("Unreachable")
    assert link_config.get("target_name") == source_file.name
    assert link_config.get("prefix_type") == prefix_type

    # Add another file
    source_file_2 = Path(files_path, "my_config_2.txt")
    source_file_2_content = "Configuration Content 2 ..."
    ensure_folder_tree(files=[(source_file_2, source_file_2_content)])
    dot_project.add_link(source_path=source_file_2, prefix_type=prefix_type)

    expected_source_file_2_path = Path(project_path, source_file_2.name)
    assert Path(project_path).exists()
    assert expected_source_file_2_path.exists()
    assert expected_source_file_2_path.read_text() == source_file_2_content
    assert Path(source_file_2).exists()
    assert Path(source_file_2).is_symlink()
    assert Path(source_file_2).resolve() == expected_source_file_2_path
    config_file_2 = Path(project_path, ProjectStructure.PUBLIC_CONFIG)
    with open(config_file_2, "r") as f:
        config_2 = json.load(f)
    assert "links" in config_2
    assert source_file_2.name in config_2["links"]
    link_config_2 = config_2["links"][source_file_2.name]
    if prefix_type == "home":
        assert (
            link_config_2.get("link_path")
            == source_file_2.relative_to(home_path).as_posix()
        )
    elif prefix_type == "root":
        assert (
            link_config_2.get("link_path")
            == source_file_2.relative_to(root_path).as_posix()
        )
    else:
        raise ValueError("Unreachable")
    assert link_config_2.get("target_name") == source_file_2.name
    assert link_config.get("prefix_type") == prefix_type


@pytest.mark.parametrize("is_project_in_home", [False])
def test_custom_linking(is_project_in_home: bool, tmp_path: Path):
    # Setup
    root_path = Path(tmp_path, "root")
    custom_path = Path(root_path, "custom")
    home_path = Path(custom_path, "home")
    if is_project_in_home:
        projects_path = Path(home_path, "projects")
    else:
        projects_path = Path(root_path, "projects")
    files_path = Path(home_path, "files")
    source_file = Path(files_path, "my_config.txt")
    source_file_content = "Configuration Content ..."
    ensure_folder_tree(
        folders=[projects_path, home_path], files=[(source_file, source_file_content)]
    )
    project_path = Path(projects_path, "my_project")
    prefix_name = "custom-prefix"
    # Test Call
    dot_project = DotProject.ensure(Path(project_path))
    dot_project.set_home_path(home_path)
    dot_project.set_root_path(root_path)
    custom_prefix = CustomPrefix(name=prefix_name, path=custom_path)
    dot_project.add_link(
        source_path=source_file,
        prefix_type="custom",
        prefix_config=custom_prefix,
    )

    # Assertions
    expected_source_file_path = Path(project_path, source_file.name)
    assert Path(project_path).exists()
    assert expected_source_file_path.exists()
    assert expected_source_file_path.read_text() == source_file_content
    assert Path(source_file).exists()
    assert Path(source_file).is_symlink()
    assert Path(source_file).resolve() == expected_source_file_path

    actual_project = DotProject.from_path(project_path)
    assert source_file.name in actual_project.config.links

    link_config = actual_project.config.links[source_file.name]
    assert link_config.link_path == source_file.relative_to(custom_path)
    assert link_config.target_name == source_file.name
    assert link_config.prefix_type == "custom"
    assert link_config.prefix_config is not None
    assert link_config.prefix_config.name == prefix_name

    assert prefix_name in actual_project.config.prefixes
    assert actual_project.config.prefixes[prefix_name].path == custom_path
