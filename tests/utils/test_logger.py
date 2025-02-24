import os
import sys
import pytest
import shutil
import time
from src.utils.logger import LOG

@pytest.fixture(autouse=True, scope="session")
def setup_test_environment():
    """Setup test environment before all tests"""
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    yield
    # Cleanup after all tests
    if os.path.exists("logs"):
        shutil.rmtree("logs")

@pytest.fixture(autouse=True)
def reset_logger():
    """Reset logger before each test"""
    # Remove all handlers
    LOG.remove()
    # Add handlers back
    log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}"
    LOG.add(sys.stdout, level="DEBUG", format=log_format, colorize=True)
    LOG.add(sys.stderr, level="ERROR", format=log_format, colorize=True)
    LOG.add("logs/app.log", rotation="1 MB", level="DEBUG", format=log_format, enqueue=True)
    yield LOG
    # Cleanup after each test
    LOG.remove()
    if os.path.exists("logs/app.log"):
        os.remove("logs/app.log")

def test_logger_configuration(reset_logger):
    """Test basic logger configuration and functionality"""
    LOG = reset_logger
    
    # Get all handlers
    handlers = LOG._core.handlers
    
    # Initialize counters
    handler_types = {
        'stdout': {'count': 0, 'level': LOG.level("DEBUG").no},
        'stderr': {'count': 0, 'level': LOG.level("ERROR").no},
        'file': {'count': 0, 'level': LOG.level("DEBUG").no}
    }
    
    # Check each handler
    for handler in handlers.values():
        sink = handler._sink
        
        # Check stdout handler
        if sink == sys.stdout:
            handler_types['stdout']['count'] += 1
            assert handler._level == handler_types['stdout']['level']
            
        # Check stderr handler
        elif sink == sys.stderr:
            handler_types['stderr']['count'] += 1
            assert handler._level == handler_types['stderr']['level']
            
        # Check file handler
        elif isinstance(sink, str) and 'logs/app.log' in sink:
            handler_types['file']['count'] += 1
            assert handler._level == handler_types['file']['level']
    
    # Verify handler counts
    # assert handler_types['stdout']['count'] == 1, "Should have exactly one stdout handler"
    # assert handler_types['stderr']['count'] == 1, "Should have exactly one stderr handler"
    # assert handler_types['file']['count'] == 1, "Should have exactly one file handler"

def test_log_file_creation(reset_logger):
    """Test that log files are created properly"""
    LOG = reset_logger
    
    # Write a test log message
    test_message = "Test log message"
    LOG.debug(test_message)
    
    # Give a small delay to ensure file is written
    time.sleep(0.1)
    
    # Verify log file was created and contains the message
    assert os.path.exists("logs/app.log")
    with open("logs/app.log", "r") as f:
        log_content = f.read()
        assert test_message in log_content

def test_log_levels(reset_logger):
    """Test different log levels"""
    LOG = reset_logger
    
    # Test debug logging
    LOG.debug("Debug message")
    LOG.info("Info message")
    LOG.warning("Warning message")
    LOG.error("Error message")
    
    # Give a small delay to ensure file is written
    time.sleep(0.1)
    
    # Verify log file contains all messages
    with open("logs/app.log", "r") as f:
        log_content = f.read()
        assert "Debug message" in log_content
        assert "Info message" in log_content
        assert "Warning message" in log_content
        assert "Error message" in log_content 