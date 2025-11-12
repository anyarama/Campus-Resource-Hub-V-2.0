"""
Secret Management Security Tests
Tests for secrets validation and secure configuration management.
"""

import pytest
import os
from unittest.mock import patch
from backend.utils.secrets_validator import SecretsValidator
from backend.config import ProductionConfig, DevelopmentConfig, TestingConfig


class TestSecretsValidatorSecretKey:
    """Test SECRET_KEY validation."""
    
    def test_validate_strong_secret_key(self):
        """Verify strong secret key passes validation."""
        strong_key = "a1b2c3d4e5f6789012345678901234567890abcdefghijklmnopqrstuvwxyz12"
        is_valid, issues = SecretsValidator.validate_secret_key(strong_key)
        
        assert is_valid
        assert len(issues) == 0
    
    def test_validate_empty_secret_key(self):
        """Verify empty secret key fails validation."""
        is_valid, issues = SecretsValidator.validate_secret_key("")
        
        assert not is_valid
        assert len(issues) > 0
        assert any('not set' in issue for issue in issues)
    
    def test_validate_short_secret_key(self):
        """Verify secret key below minimum length fails."""
        short_key = "abc123"  # Only 6 characters
        is_valid, issues = SecretsValidator.validate_secret_key(short_key)
        
        assert not is_valid
        assert any('too short' in issue for issue in issues)
    
    def test_validate_weak_pattern_dev(self):
        """Verify secret key with 'dev' pattern fails."""
        weak_key = "development-secret-key-12345678901234567890"
        is_valid, issues = SecretsValidator.validate_secret_key(weak_key)
        
        assert not is_valid
        assert any('dev' in issue.lower() for issue in issues)
    
    def test_validate_weak_pattern_test(self):
        """Verify secret key with 'test' pattern fails."""
        weak_key = "test-secret-key-12345678901234567890"
        is_valid, issues = SecretsValidator.validate_secret_key(weak_key)
        
        assert not is_valid
        assert any('test' in issue.lower() for issue in issues)
    
    def test_validate_weak_pattern_password(self):
        """Verify secret key with 'password' pattern fails."""
        weak_key = "password123456789012345678901234567890"
        is_valid, issues = SecretsValidator.validate_secret_key(weak_key)
        
        assert not is_valid
        assert any('password' in issue.lower() for issue in issues)
    
    def test_validate_low_entropy(self):
        """Verify secret key with low entropy fails."""
        low_entropy_key = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"  # All same character
        is_valid, issues = SecretsValidator.validate_secret_key(low_entropy_key)
        
        assert not is_valid
        assert any('entropy' in issue.lower() for issue in issues)
    
    def test_generate_secret_key(self):
        """Verify generate_secret_key produces valid key."""
        generated_key = SecretsValidator.generate_secret_key()
        
        # Should be 64 characters (32 bytes as hex)
        assert len(generated_key) == 64
        
        # Should pass validation
        is_valid, issues = SecretsValidator.validate_secret_key(generated_key)
        assert is_valid


class TestSecretsValidatorDatabaseURL:
    """Test DATABASE_URL validation."""
    
    def test_validate_postgresql_url_development(self):
        """Verify PostgreSQL URL is valid for development."""
        db_url = "postgresql://user:pass@localhost:5432/dbname"
        is_valid, issues = SecretsValidator.validate_database_url(db_url, 'development')
        
        assert is_valid
        assert len(issues) == 0
    
    def test_validate_sqlite_url_development(self):
        """Verify SQLite URL is valid for development."""
        db_url = "sqlite:///dev.db"
        is_valid, issues = SecretsValidator.validate_database_url(db_url, 'development')
        
        assert is_valid
        assert len(issues) == 0
    
    def test_validate_sqlite_url_production_fails(self):
        """Verify SQLite URL fails for production."""
        db_url = "sqlite:///prod.db"
        is_valid, issues = SecretsValidator.validate_database_url(db_url, 'production')
        
        assert not is_valid
        assert any('sqlite' in issue.lower() for issue in issues)
    
    def test_validate_empty_database_url(self):
        """Verify empty DATABASE_URL fails."""
        is_valid, issues = SecretsValidator.validate_database_url("", 'production')
        
        assert not is_valid
        assert any('not set' in issue for issue in issues)
    
    def test_validate_weak_credentials_warning(self):
        """Verify weak credentials in URL trigger warning."""
        db_url = "postgresql://admin:password@localhost:5432/dbname"
        is_valid, issues = SecretsValidator.validate_database_url(db_url, 'production')
        
        # Should have warning about weak credentials
        assert any('weak credentials' in issue.lower() or 'password' in issue.lower() 
                   for issue in issues)


class TestSecretsValidatorCORSOrigins:
    """Test CORS_ORIGINS validation."""
    
    def test_validate_https_origins_production(self):
        """Verify HTTPS origins pass for production."""
        cors_origins = "https://example.com,https://www.example.com"
        is_valid, issues = SecretsValidator.validate_cors_origins(cors_origins, 'production')
        
        assert is_valid
        assert len(issues) == 0
    
    def test_validate_localhost_production_fails(self):
        """Verify localhost in CORS_ORIGINS fails for production."""
        cors_origins = "https://example.com,http://localhost:3000"
        is_valid, issues = SecretsValidator.validate_cors_origins(cors_origins, 'production')
        
        assert not is_valid
        assert any('localhost' in issue.lower() for issue in issues)
    
    def test_validate_http_production_fails(self):
        """Verify HTTP (not HTTPS) fails for production."""
        cors_origins = "http://example.com"
        is_valid, issues = SecretsValidator.validate_cors_origins(cors_origins, 'production')
        
        assert not is_valid
        assert any('https' in issue.lower() for issue in issues)
    
    def test_validate_wildcard_production_fails(self):
        """Verify wildcard (*) fails for production."""
        cors_origins = "*"
        is_valid, issues = SecretsValidator.validate_cors_origins(cors_origins, 'production')
        
        assert not is_valid
        assert any('wildcard' in issue.lower() or '*' in issue for issue in issues)
    
    def test_validate_empty_cors_origins(self):
        """Verify empty CORS_ORIGINS fails."""
        is_valid, issues = SecretsValidator.validate_cors_origins("", 'production')
        
        assert not is_valid
        assert any('not set' in issue for issue in issues)
    
    def test_validate_localhost_development_passes(self):
        """Verify localhost is acceptable for development."""
        cors_origins = "http://localhost:5173,http://localhost:3000"
        is_valid, issues = SecretsValidator.validate_cors_origins(cors_origins, 'development')
        
        assert is_valid
        assert len(issues) == 0


class TestSecretsValidatorEnvironmentConfig:
    """Test full environment configuration validation."""
    
    @patch.dict(os.environ, {
        'SECRET_KEY': 'a1b2c3d4e5f6789012345678901234567890abcdefghijklmnopqrstuvwxyz12',
        'DATABASE_URL': 'postgresql://user:pass@localhost:5432/db',
        'CORS_ORIGINS': 'https://example.com',
        'FLASK_ENV': 'production'
    })
    def test_validate_valid_production_config(self):
        """Verify valid production configuration passes."""
        results = SecretsValidator.validate_environment_config('production')
        
        # All should be valid
        assert results['SECRET_KEY'][0] is True
        assert results['DATABASE_URL'][0] is True
        assert results['CORS_ORIGINS'][0] is True
    
    @patch.dict(os.environ, {
        'SECRET_KEY': 'weak',
        'DATABASE_URL': 'sqlite:///test.db',
        'CORS_ORIGINS': 'http://localhost:3000',
        'FLASK_ENV': 'production'
    })
    def test_validate_weak_production_config(self):
        """Verify weak production configuration fails."""
        results = SecretsValidator.validate_environment_config('production')
        
        # All should fail
        assert results['SECRET_KEY'][0] is False
        assert results['DATABASE_URL'][0] is False
        assert results['CORS_ORIGINS'][0] is False
    
    @patch.dict(os.environ, {
        'SECRET_KEY': 'dev-key',
        'DATABASE_URL': 'sqlite:///dev.db',
        'CORS_ORIGINS': 'http://localhost:5173',
        'FLASK_ENV': 'development'
    })
    def test_validate_development_config(self):
        """Verify development configuration is more permissive."""
        results = SecretsValidator.validate_environment_config('development')
        
        # Development should be more lenient (but SECRET_KEY still has issues)
        assert results['SECRET_KEY'][0] is False  # Still too weak
        assert results['DATABASE_URL'][0] is True  # SQLite OK in dev
        assert results['CORS_ORIGINS'][0] is True  # Localhost OK in dev


class TestProductionConfigValidation:
    """Test ProductionConfig class validation."""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_production_config_missing_secret_key(self):
        """Verify ProductionConfig fails without SECRET_KEY."""
        with pytest.raises(ValueError) as exc_info:
            ProductionConfig()
        
        assert 'SECRET_KEY' in str(exc_info.value)
    
    @patch.dict(os.environ, {
        'SECRET_KEY': 'short',
        'DATABASE_URL': 'postgresql://localhost/db',
        'CORS_ORIGINS': 'https://example.com'
    })
    def test_production_config_short_secret_key(self):
        """Verify ProductionConfig fails with short SECRET_KEY."""
        with pytest.raises(ValueError) as exc_info:
            ProductionConfig()
        
        assert 'too short' in str(exc_info.value).lower()
    
    @patch.dict(os.environ, {
        'SECRET_KEY': 'a'*64,
        'DATABASE_URL': 'sqlite:///prod.db',
        'CORS_ORIGINS': 'https://example.com'
    })
    def test_production_config_sqlite_database(self):
        """Verify ProductionConfig fails with SQLite."""
        with pytest.raises(ValueError) as exc_info:
            ProductionConfig()
        
        assert 'sqlite' in str(exc_info.value).lower()
    
    @patch.dict(os.environ, {
        'SECRET_KEY': 'a'*64,
        'DATABASE_URL': 'postgresql://localhost/db',
        'CORS_ORIGINS': 'http://localhost:3000'
    })
    def test_production_config_localhost_cors(self):
        """Verify ProductionConfig fails with localhost in CORS."""
        with pytest.raises(ValueError) as exc_info:
            ProductionConfig()
        
        assert 'localhost' in str(exc_info.value).lower()
    
    @patch.dict(os.environ, {
        'SECRET_KEY': 'dev-secret-key-' + 'a'*50,
        'DATABASE_URL': 'postgresql://localhost/db',
        'CORS_ORIGINS': 'https://example.com'
    })
    def test_production_config_weak_secret_pattern(self):
        """Verify ProductionConfig fails with weak secret pattern."""
        with pytest.raises(ValueError) as exc_info:
            ProductionConfig()
        
        assert 'weak pattern' in str(exc_info.value).lower()


class TestDevelopmentConfigValidation:
    """Test DevelopmentConfig allows more permissive settings."""
    
    def test_development_config_no_validation_errors(self):
        """Verify DevelopmentConfig doesn't raise errors."""
        # Should not raise any exceptions
        config = DevelopmentConfig()
        
        assert config.DEBUG is True
        assert config.TESTING is False


class TestTestingConfigValidation:
    """Test TestingConfig configuration."""
    
    def test_testing_config_csrf_disabled(self):
        """Verify CSRF is disabled in testing."""
        config = TestingConfig()
        
        assert config.WTF_CSRF_ENABLED is False
        assert config.TESTING is True


class TestSecretsInGitignore:
    """Test that sensitive files are properly ignored."""
    
    def test_gitignore_exists(self):
        """Verify .gitignore file exists."""
        gitignore_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            '.gitignore'
        )
        
        assert os.path.exists(gitignore_path)
    
    def test_gitignore_includes_env_files(self):
        """Verify .gitignore includes .env files."""
        gitignore_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            '.gitignore'
        )
        
        with open(gitignore_path, 'r') as f:
            content = f.read()
        
        # Should ignore .env files
        assert '.env' in content
        assert '.env.local' in content or '.env*' in content
    
    def test_gitignore_includes_database_files(self):
        """Verify .gitignore includes database files."""
        gitignore_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            '.gitignore'
        )
        
        with open(gitignore_path, 'r') as f:
            content = f.read()
        
        # Should ignore database files
        assert '*.db' in content or '*.sqlite' in content


class TestEnvExampleFile:
    """Test .env.example file completeness."""
    
    def test_env_example_exists(self):
        """Verify .env.example file exists."""
        env_example_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            '.env.example'
        )
        
        assert os.path.exists(env_example_path)
    
    def test_env_example_has_secret_key(self):
        """Verify .env.example includes SECRET_KEY."""
        env_example_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            '.env.example'
        )
        
        with open(env_example_path, 'r') as f:
            content = f.read()
        
        assert 'SECRET_KEY' in content
    
    def test_env_example_has_database_url(self):
        """Verify .env.example includes DATABASE_URL."""
        env_example_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            '.env.example'
        )
        
        with open(env_example_path, 'r') as f:
            content = f.read()
        
        assert 'DATABASE_URL' in content
    
    def test_env_example_has_cors_origins(self):
        """Verify .env.example includes CORS_ORIGINS."""
        env_example_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            '.env.example'
        )
        
        with open(env_example_path, 'r') as f:
            content = f.read()
        
        assert 'CORS_ORIGINS' in content
    
    def test_env_example_has_warnings(self):
        """Verify .env.example includes security warnings."""
        env_example_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            '.env.example'
        )
        
        with open(env_example_path, 'r') as f:
            content = f.read()
        
        # Should have warnings about not committing
        assert 'NEVER commit' in content or 'DO NOT commit' in content or 'never committed' in content.lower()
