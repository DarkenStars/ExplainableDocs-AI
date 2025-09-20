"""
Simple test to verify the modular structure without requiring FastAPI dependencies.
This tests that the modules are properly structured and can be imported.
"""

def test_module_structure():
    """Test that all modules can be imported without errors."""
    try:
        # Test configuration module
        from app.config import config
        print("✓ Configuration module imported successfully")
        
        # Test models module
        from app.models.schemas import VerifyRequest, VerifyResponse, Source, EvidenceItem, EvidenceBundle
        print("✓ Data models imported successfully")
        
        # Test database modules
        from app.database.connection import DatabasePool, db_pool
        from app.database.db_manager import setup_database, get_conn, put_conn, check_cache, upsert_result
        print("✓ Database modules imported successfully")
        
        # Test services module
        from app.services.fact_checker import search_claim, analyze_verdicts_improved, build_explanation, simple_fuse_verdict
        print("✓ Services module imported successfully")
        
        # Test utilities module
        from app.utils.helpers import normalize_claim, get_evidence_url, calculate_confidence, truncate_text
        print("✓ Utilities module imported successfully")
        
        print("\n🎉 All modules imported successfully!")
        print("✓ Modular refactoring completed successfully")
        
        # Test some basic functionality
        normalized = normalize_claim("  Test   Claim  ")
        assert normalized == "test claim", f"Expected 'test claim', got '{normalized}'"
        
        confidence = calculate_confidence("true", [{"sentence": "test"}], [])
        assert isinstance(confidence, int), f"Expected int, got {type(confidence)}"
        
        print("✓ Basic functionality tests passed")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except AssertionError as e:
        print(f"❌ Assertion error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_module_structure()
    if success:
        print("\n✅ Module structure validation completed successfully!")
    else:
        print("\n❌ Module structure validation failed!")
        exit(1)