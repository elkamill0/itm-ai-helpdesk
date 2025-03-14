import os


def test_poetry_script():
    root_dir = os.getcwd()

    assert os.path.isfile(os.path.join(root_dir, "check_poetry_version.sh")), (
        "check_poetry_version.sh not found in the root directory"
    )
