import pytest
import yaml
from pathlib import Path
from agastya.mana.manager import ManaManager, ManaInfo

@pytest.fixture
def temp_config_dir(tmp_path):
    return tmp_path / "config_dir"

@pytest.fixture
def temp_workspace(tmp_path):
    return tmp_path / "workspace"

@pytest.fixture
def manager(temp_config_dir):
    temp_config_dir.mkdir()
    return ManaManager(config_dir=temp_config_dir)

def test_is_mana_directory_with_nav(temp_workspace, manager):
    mana_dir = temp_workspace / "valid_mana"
    mana_dir.mkdir(parents=True)
    (mana_dir / "NAV.md").touch()

    assert manager.is_mana(mana_dir) is True

def test_is_mana_directory_without_nav(temp_workspace, manager):
    invalid_dir = temp_workspace / "invalid_mana"
    invalid_dir.mkdir(parents=True)
    
    assert manager.is_mana(invalid_dir) is False

def test_register_mana(temp_workspace, manager):
    mana_dir = temp_workspace / "my_mana"
    mana_dir.mkdir(parents=True)
    (mana_dir / "NAV.md").touch()

    manager.register(mana_dir)
    manas = manager.list_all()

    assert len(manas) == 1
    assert manas[0].name == "my_mana"
    assert manas[0].path == str(mana_dir)

def test_register_mana_no_nav(temp_workspace, manager):
    invalid_dir = temp_workspace / "invalid_mana"
    invalid_dir.mkdir(parents=True)

    with pytest.raises(ValueError, match="Directory does not contain a NAV.md file"):
        manager.register(invalid_dir)

def test_register_mana_duplicate(temp_workspace, manager):
    mana_dir = temp_workspace / "my_mana"
    mana_dir.mkdir(parents=True)
    (mana_dir / "NAV.md").touch()

    manager.register(mana_dir)
    with pytest.raises(ValueError, match="Mana with name 'my_mana' is already registered"):
        manager.register(mana_dir)

def test_unregister_mana(temp_workspace, manager):
    mana_dir = temp_workspace / "my_mana"
    mana_dir.mkdir(parents=True)
    (mana_dir / "NAV.md").touch()

    manager.register(mana_dir)
    manager.unregister("my_mana")

    manas = manager.list_all()
    assert len(manas) == 0

def test_unregister_missing_mana(manager):
    with pytest.raises(ValueError, match="Mana 'not_found' is not registered"):
        manager.unregister("not_found")

def test_init_mana(temp_workspace, manager):
    new_mana_dir = temp_workspace / "new_domain"
    
    manager.init(new_mana_dir)
    
    # Assert correct directory structure is created
    assert new_mana_dir.exists()
    assert (new_mana_dir / "NAV.md").exists()
    assert (new_mana_dir / "schema.md").exists()
    assert (new_mana_dir / "log.md").exists()
    assert (new_mana_dir / "inbox.md").exists()
    assert (new_mana_dir / "raw").is_dir()
    assert (new_mana_dir / "pages").is_dir()
    assert (new_mana_dir / ".agastya").is_dir()

def test_init_mana_existing_nav(temp_workspace, manager):
    mana_dir = temp_workspace / "existing_mana"
    mana_dir.mkdir(parents=True)
    (mana_dir / "NAV.md").touch()

    with pytest.raises(ValueError, match="Directory is already a mana"):
        manager.init(mana_dir)

def test_manas_yaml_persistence(temp_config_dir, temp_workspace):
    manager1 = ManaManager(config_dir=temp_config_dir)
    
    mana_dir = temp_workspace / "persisted_mana"
    mana_dir.mkdir(parents=True)
    (mana_dir / "NAV.md").touch()

    manager1.register(mana_dir)

    manager2 = ManaManager(config_dir=temp_config_dir)
    manas = manager2.list_all()
    
    assert len(manas) == 1
    assert manas[0].name == "persisted_mana"
