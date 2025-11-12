"""
Secrets Validation Utility
Validates environment variables and secrets for security compliance.
"""

import os
import re
from typing import List, Tuple, Dict


class SecretsValidator:
    """Validates secrets and environment configuration for security compliance."""
    
    # Minimum requirements for secret key strength
    MIN_SECRET_KEY_LENGTH = 32
    RECOMMENDED_SECRET_KEY_LENGTH = 64
    
    # Patterns for detecting weak or default secrets
    WEAK_PATTERNS = [
        r'test',
        r'dev',
        r'demo',
        r'example',
        r'changeme',
        r'password',
        r'secret',
        r'default',
        r'123456',
        r'admin',
    ]
    
    @staticmethod
    def validate_secret_key(secret_key: str) -> Tuple[bool, List[str]]:
        """
        Validate SECRET_KEY meets security requirements.
        
        Args:
            secret_key: The secret key to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        if not secret_key:
            issues.append("SECRET_KEY is not set")
            return False, issues
        
        # Check length
        if len(secret_key) < SecretsValidator.MIN_SECRET_KEY_LENGTH:
            issues.append(
                f"SECRET_KEY is too short (minimum {SecretsValidator.MIN_SECRET_KEY_LENGTH} characters, "
                f"got {len(secret_key)})"
            )
        
        if len(secret_key) < SecretsValidator.RECOMMENDED_SECRET_KEY_LENGTH:
            issues.append(
                f"SECRET_KEY should be at least {SecretsValidator.RECOMMENDED_SECRET_KEY_LENGTH} "
                f"characters for production (got {len(secret_key)})"
            )
        
        # Check for weak patterns
        secret_lower = secret_key.lower()
        for pattern in SecretsValidator.WEAK_PATTERNS:
            if re.search(pattern, secret_lower):
                issues.append(f"SECRET_KEY contains weak pattern: '{pattern}'")
        
        # Check entropy (basic check for randomness)
        unique_chars = len(set(secret_key))
        if unique_chars < 10:
            issues.append(
                f"SECRET_KEY has low entropy (only {unique_chars} unique characters)"
            )
        
        # Check if it's all alphanumeric (should have special chars ideally)
        if secret_key.isalnum() and len(secret_key) < 64:
            issues.append(
                "SECRET_KEY contains only alphanumeric characters. "
                "Consider using a hex-encoded random string."
            )
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    @staticmethod
    def validate_database_url(database_url: str, environment: str) -> Tuple[bool, List[str]]:
        """
        Validate DATABASE_URL configuration.
        
        Args:
            database_url: The database URL to validate
            environment: Current environment (development, testing, production)
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        if not database_url:
            issues.append("DATABASE_URL is not set")
            return False, issues
        
        # Production should not use SQLite
        if environment == 'production':
            if database_url.startswith('sqlite'):
                issues.append(
                    "Production environment should not use SQLite. "
                    "Use PostgreSQL or another production-grade database."
                )
            
            # Check for hardcoded credentials in URL
            if '@' in database_url:
                # Extract credentials part
                if 'password' in database_url.lower() or 'admin' in database_url.lower():
                    issues.append(
                        "DATABASE_URL may contain weak credentials. "
                        "Ensure strong passwords are used."
                    )
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    @staticmethod
    def validate_cors_origins(cors_origins: str, environment: str) -> Tuple[bool, List[str]]:
        """
        Validate CORS_ORIGINS configuration.
        
        Args:
            cors_origins: Comma-separated list of allowed origins
            environment: Current environment
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        if not cors_origins:
            issues.append("CORS_ORIGINS is not set")
            return False, issues
        
        origins = [origin.strip() for origin in cors_origins.split(',')]
        
        # Production should not allow localhost or wildcards
        if environment == 'production':
            for origin in origins:
                if 'localhost' in origin or '127.0.0.1' in origin:
                    issues.append(
                        f"Production CORS_ORIGINS should not include localhost: {origin}"
                    )
                
                if origin == '*':
                    issues.append(
                        "Production CORS_ORIGINS should not use wildcard '*'. "
                        "Specify exact domains."
                    )
                
                if not origin.startswith(('http://', 'https://')):
                    issues.append(f"Invalid CORS origin format: {origin}")
                
                # Production should use HTTPS
                if origin.startswith('http://') and not any(x in origin for x in ['localhost', '127.0.0.1']):
                    issues.append(
                        f"Production CORS_ORIGINS should use HTTPS, not HTTP: {origin}"
                    )
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    @staticmethod
    def validate_environment_config(environment: str = None) -> Dict[str, Tuple[bool, List[str]]]:
        """
        Validate all environment configuration.
        
        Args:
            environment: Environment name (defaults to FLASK_ENV)
            
        Returns:
            Dictionary of validation results for each configuration item
        """
        env = environment or os.environ.get('FLASK_ENV', 'development')
        
        results = {}
        
        # Validate SECRET_KEY
        secret_key = os.environ.get('SECRET_KEY', '')
        results['SECRET_KEY'] = SecretsValidator.validate_secret_key(secret_key)
        
        # Validate DATABASE_URL
        database_url = os.environ.get('DATABASE_URL', '')
        results['DATABASE_URL'] = SecretsValidator.validate_database_url(database_url, env)
        
        # Validate CORS_ORIGINS
        cors_origins = os.environ.get('CORS_ORIGINS', '')
        results['CORS_ORIGINS'] = SecretsValidator.validate_cors_origins(cors_origins, env)
        
        return results
    
    @staticmethod
    def validate_and_report(environment: str = None, strict: bool = False) -> bool:
        """
        Validate environment configuration and print report.
        
        Args:
            environment: Environment name
            strict: If True, fail on warnings; if False, only fail on errors
            
        Returns:
            True if validation passed, False otherwise
        """
        results = SecretsValidator.validate_environment_config(environment)
        
        has_errors = False
        print("\n" + "="*70)
        print("SECRETS VALIDATION REPORT")
        print("="*70)
        
        for key, (is_valid, issues) in results.items():
            status = "✅ PASS" if is_valid else "❌ FAIL"
            print(f"\n{key}: {status}")
            
            if issues:
                has_errors = True
                for issue in issues:
                    # Determine if it's a critical error or warning
                    is_critical = any(x in issue.lower() for x in [
                        'not set', 'too short', 'required', 'must'
                    ])
                    
                    if is_critical:
                        print(f"  ❌ ERROR: {issue}")
                    else:
                        print(f"  ⚠️  WARNING: {issue}")
                        if not strict:
                            has_errors = False  # Don't fail on warnings in non-strict mode
        
        print("\n" + "="*70)
        
        if has_errors:
            print("❌ Validation FAILED - Please fix the issues above")
        else:
            print("✅ Validation PASSED")
        
        print("="*70 + "\n")
        
        return not has_errors
    
    @staticmethod
    def generate_secret_key() -> str:
        """
        Generate a secure random secret key.
        
        Returns:
            64-character hex string suitable for SECRET_KEY
        """
        import secrets
        return secrets.token_hex(32)


def validate_secrets_cli():
    """CLI command to validate secrets configuration."""
    import sys
    
    # Check if running in production
    env = os.environ.get('FLASK_ENV', 'development')
    strict = env == 'production'
    
    print(f"Environment: {env}")
    print(f"Strict mode: {'ON' if strict else 'OFF'}")
    
    is_valid = SecretsValidator.validate_and_report(environment=env, strict=strict)
    
    if not is_valid:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    validate_secrets_cli()
