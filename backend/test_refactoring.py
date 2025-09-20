"""
Lightweight test to verify the modular structure without external dependencies.
This tests that the modules are properly structured and Python files are valid.
"""

import os
import ast

def validate_python_file(filepath):
    """Validate that a Python file has valid syntax."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def test_file_structure():
    """Test that all expected files exist and have valid Python syntax."""
    expected_files = [
        'app/__init__.py',
        'app/config.py',
        'app/main.py',
        'app/models/__init__.py',
        'app/models/schemas.py',
        'app/database/__init__.py',
        'app/database/connection.py',
        'app/database/db_manager.py',
        'app/services/__init__.py',
        'app/services/fact_checker.py',
        'app/utils/__init__.py',
        'app/utils/helpers.py',
        'app/routes/__init__.py',
        'app/routes/api.py',
    ]
    
    print("Testing file structure and syntax:")
    all_valid = True
    
    for file_path in expected_files:
        if os.path.exists(file_path):
            valid, error = validate_python_file(file_path)
            if valid:
                print(f"✓ {file_path} - valid syntax")
            else:
                print(f"❌ {file_path} - {error}")
                all_valid = False
        else:
            print(f"❌ {file_path} - file missing")
            all_valid = False
    
    return all_valid

def test_basic_imports():
    """Test basic imports that don't require external dependencies."""
    try:
        # Test configuration without loading environment variables
        import sys
        sys.path.insert(0, '.')
        
        # Test basic module structure by checking if files can be parsed
        from app.config import Config
        print("✓ Configuration class imported")
        
        # Test utility functions
        from app.utils.helpers import normalize_claim, truncate_text
        print("✓ Utility functions imported")
        
        # Test basic functionality
        normalized = normalize_claim("  Test   Claim  ")
        assert normalized == "test claim", f"Expected 'test claim', got '{normalized}'"
        
        truncated = truncate_text("Hello World", 5)
        assert truncated == "Hello", f"Expected 'Hello', got '{truncated}'"
        
        print("✓ Basic utility functions work correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING MODULAR REFACTORING")
    print("=" * 60)
    
    structure_valid = test_file_structure()
    imports_valid = test_basic_imports()
    
    print("\n" + "=" * 60)
    if structure_valid and imports_valid:
        print("✅ REFACTORING VALIDATION SUCCESSFUL!")
        print("✓ All module files exist and have valid syntax")
        print("✓ Basic imports and functionality work correctly")
        print("✓ Modular structure is properly implemented")
    else:
        print("❌ REFACTORING VALIDATION FAILED!")
        if not structure_valid:
            print("❌ File structure or syntax issues found")
        if not imports_valid:
            print("❌ Import or functionality issues found")
    print("=" * 60)