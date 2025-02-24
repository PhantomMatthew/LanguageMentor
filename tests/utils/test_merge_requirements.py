import os
import sys
import pytest
import importlib
import importlib.metadata
from unittest.mock import mock_open, patch, MagicMock

# Import the module under test
try:
    from src.utils.merge_requirements import (
        parse_package_spec,
        get_installed_versions,
        read_requirements,
        merge_requirements,
        main
    )
except ImportError as e:
    print(f"Import Error: {e}")
    raise

def test_parse_package_spec():
    """Test package specification parsing"""
    # Test exact version
    name, op, version = parse_package_spec("pytest==7.4.3")
    assert name == "pytest"
    assert op == "=="
    assert version == "7.4.3"

    # Test greater than version
    name, op, version = parse_package_spec("loguru>=0.7.2")
    assert name == "loguru"
    assert op == ">="
    assert version == "0.7.2"

    # Test package without version
    name, op, version = parse_package_spec("requests")
    assert name == "requests"
    assert op is None
    assert version is None

    # Test package with spaces
    name, op, version = parse_package_spec("pytest  ==  7.4.3")
    assert name == "pytest"
    assert op == "=="
    assert version == "7.4.3"

@patch('importlib.metadata.version')
def test_get_installed_versions(mock_version):
    """Test getting installed package versions"""
    # Mock installed versions
    def mock_version_side_effect(x):
        if x == 'missing':
            raise importlib.metadata.PackageNotFoundError()
        return {
            'pytest': '7.4.3',
            'loguru': '0.7.2',
        }[x]
    
    mock_version.side_effect = mock_version_side_effect

    packages = ['pytest==7.4.3', 'loguru>=0.7.2', 'missing']
    installed = get_installed_versions(packages)
    
    assert installed == {
        'pytest': '7.4.3',
        'loguru': '0.7.2'
    }

def test_read_requirements():
    """Test reading requirements.txt file"""
    mock_content = '''
# Comments should be ignored
pytest==7.4.3
loguru>=0.7.2
requests

'''
    with patch('builtins.open', mock_open(read_data=mock_content)):
        with patch('os.path.exists', return_value=True):
            req_versions = read_requirements()
            
            assert req_versions == {
                'pytest': '==7.4.3',
                'loguru': '>=0.7.2',
                'requests': None
            }

def test_read_requirements_no_file():
    """Test reading non-existent requirements.txt"""
    with patch('os.path.exists', return_value=False):
        req_versions = read_requirements()
        assert req_versions == {}

def test_merge_requirements():
    """Test merging requirements"""
    installed_versions = {
        'pytest': '7.4.3',
        'loguru': '0.7.2',
        'new_package': '1.0.0'
    }
    
    req_versions = {
        'pytest': '==7.4.3',  # Match
        'loguru': '==0.7.1',  # Conflict
        'old_package': '==2.0.0'  # Not installed
    }
    
    merged, conflicts = merge_requirements(installed_versions, req_versions)
    
    assert conflicts == True
    assert 'pytest==7.4.3' in merged
    assert '<<<<<<< HEAD' in merged
    assert 'loguru==0.7.1' in merged
    assert 'loguru==0.7.2' in merged
    assert '>>>>>>> Merged version' in merged
    assert 'new_package==1.0.0' in merged
    assert 'old_package==2.0.0' in merged

def test_merge_requirements_no_conflicts():
    """Test merging requirements without conflicts"""
    installed_versions = {
        'pytest': '7.4.3',
        'loguru': '0.7.2'
    }
    
    req_versions = {
        'pytest': '==7.4.3',
        'loguru': '>=0.7.0'  # Not exact version, no conflict
    }
    
    merged, conflicts = merge_requirements(installed_versions, req_versions)
    
    assert conflicts == False
    assert 'pytest==7.4.3' in merged
    assert 'loguru>=0.7.0' in merged

@patch('src.utils.merge_requirements.read_requirements')
@patch('src.utils.merge_requirements.get_installed_versions')
@patch('builtins.open', new_callable=mock_open)
@patch('builtins.print')
def test_main(mock_print, mock_file, mock_get_installed, mock_read_req):
    """Test main function"""
    # Mock requirements.txt content
    mock_read_req.return_value = {
        'pytest': '==7.4.3',
        'loguru': '==0.7.2'
    }
    
    # Mock installed versions
    mock_get_installed.return_value = {
        'pytest': '7.4.3',
        'loguru': '0.7.2'
    }
    
    main()
    
    # Verify file was written
    mock_file.assert_called_once_with('requirements.txt', 'w')
    
    # Verify success message was printed
    mock_print.assert_called_once_with("requirements.txt 已更新，无版本冲突。")

@patch('src.utils.merge_requirements.read_requirements')
@patch('src.utils.merge_requirements.get_installed_versions')
@patch('builtins.open', new_callable=mock_open)
@patch('builtins.print')
def test_main_with_conflicts(mock_print, mock_file, mock_get_installed, mock_read_req):
    """Test main function with version conflicts"""
    # Mock requirements.txt content
    mock_read_req.return_value = {
        'pytest': '==7.4.3',
        'loguru': '==0.7.1'  # Conflict
    }
    
    # Mock installed versions
    mock_get_installed.return_value = {
        'pytest': '7.4.3',
        'loguru': '0.7.2'
    }
    
    main()
    
    # Verify conflict message was printed
    mock_print.assert_called_once_with("requirements.txt 已更新，存在版本冲突。请手动解决冲突标记。") 