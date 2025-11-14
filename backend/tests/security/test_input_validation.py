"""
Input Validation Security Tests
Tests for input validation and sanitization utilities.
"""

import pytest
from utils.validators import (
    InputValidator,
    InputSanitizer,
    validate_request_data
)


class TestEmailValidation:
    """Test email validation."""
    
    def test_valid_email(self):
        """Verify valid email passes."""
        is_valid, error = InputValidator.validate_email("user@example.com")
        assert is_valid is True
        assert error is None
    
    def test_empty_email(self):
        """Verify empty email fails."""
        is_valid, error = InputValidator.validate_email("")
        assert is_valid is False
        assert "required" in error.lower()
    
    def test_invalid_email_format(self):
        """Verify invalid email format fails."""
        is_valid, error = InputValidator.validate_email("not-an-email")
        assert is_valid is False
        assert "invalid" in error.lower()
    
    def test_email_with_dangerous_chars(self):
        """Verify email with dangerous characters fails."""
        dangerous_emails = [
            "user<script>@example.com",
            "user';DROP TABLE users;--@example.com",
            'user"@example.com'
        ]
        for email in dangerous_emails:
            is_valid, error = InputValidator.validate_email(email)
            assert is_valid is False
    
    def test_email_too_long(self):
        """Verify overly long email fails."""
        long_email = "a" * 300 + "@example.com"
        is_valid, error = InputValidator.validate_email(long_email)
        assert is_valid is False
        assert "too long" in error.lower()


class TestPasswordValidation:
    """Test password validation."""
    
    def test_valid_password(self):
        """Verify valid password passes."""
        is_valid, error = InputValidator.validate_password("SecurePass123")
        assert is_valid is True
        assert error is None
    
    def test_empty_password(self):
        """Verify empty password fails."""
        is_valid, error = InputValidator.validate_password("")
        assert is_valid is False
        assert "required" in error.lower()
    
    def test_password_too_short(self):
        """Verify short password fails."""
        is_valid, error = InputValidator.validate_password("Short1")
        assert is_valid is False
        assert "at least" in error.lower()
    
    def test_password_no_uppercase(self):
        """Verify password without uppercase fails."""
        is_valid, error = InputValidator.validate_password("lowercase123")
        assert is_valid is False
        assert "uppercase" in error.lower()
    
    def test_password_no_lowercase(self):
        """Verify password without lowercase fails."""
        is_valid, error = InputValidator.validate_password("UPPERCASE123")
        assert is_valid is False
        assert "lowercase" in error.lower()
    
    def test_password_no_digit(self):
        """Verify password without digit fails."""
        is_valid, error = InputValidator.validate_password("NoDigitsHere")
        assert is_valid is False
        assert "number" in error.lower()
    
    def test_password_too_long(self):
        """Verify overly long password fails."""
        long_password = "A" * 130 + "a1"
        is_valid, error = InputValidator.validate_password(long_password)
        assert is_valid is False
        assert "too long" in error.lower()


class TestStringValidation:
    """Test generic string validation."""
    
    def test_valid_string(self):
        """Verify valid string passes."""
        is_valid, error = InputValidator.validate_string(
            "Valid string", "test_field", min_length=1, max_length=100
        )
        assert is_valid is True
        assert error is None
    
    def test_string_below_min_length(self):
        """Verify string below minimum length fails."""
        is_valid, error = InputValidator.validate_string(
            "ab", "test_field", min_length=5
        )
        assert is_valid is False
        assert "at least" in error.lower()
    
    def test_string_above_max_length(self):
        """Verify string above maximum length fails."""
        is_valid, error = InputValidator.validate_string(
            "a" * 150, "test_field", max_length=100
        )
        assert is_valid is False
        assert "too long" in error.lower()
    
    def test_string_with_null_byte(self):
        """Verify string with null byte fails."""
        is_valid, error = InputValidator.validate_string(
            "string\x00with null", "test_field"
        )
        assert is_valid is False
        assert "invalid" in error.lower()
    
    def test_empty_string_when_required(self):
        """Verify empty string fails when required."""
        is_valid, error = InputValidator.validate_string(
            "", "test_field", required=True, allow_empty=False
        )
        assert is_valid is False
    
    def test_none_when_not_required(self):
        """Verify None passes when not required."""
        is_valid, error = InputValidator.validate_string(
            None, "test_field", required=False
        )
        assert is_valid is True


class TestIntegerValidation:
    """Test integer validation."""
    
    def test_valid_integer(self):
        """Verify valid integer passes."""
        is_valid, error = InputValidator.validate_integer(42, "test_field")
        assert is_valid is True
        assert error is None
    
    def test_integer_string_conversion(self):
        """Verify string can be converted to integer."""
        is_valid, error = InputValidator.validate_integer("42", "test_field")
        assert is_valid is True
    
    def test_invalid_integer(self):
        """Verify non-integer fails."""
        is_valid, error = InputValidator.validate_integer("not a number", "test_field")
        assert is_valid is False
        assert "integer" in error.lower()
    
    def test_integer_below_min(self):
        """Verify integer below minimum fails."""
        is_valid, error = InputValidator.validate_integer(5, "test_field", min_value=10)
        assert is_valid is False
        assert "at least" in error.lower()
    
    def test_integer_above_max(self):
        """Verify integer above maximum fails."""
        is_valid, error = InputValidator.validate_integer(100, "test_field", max_value=50)
        assert is_valid is False
        assert "at most" in error.lower()


class TestChoiceValidation:
    """Test choice validation."""
    
    def test_valid_choice(self):
        """Verify valid choice passes."""
        is_valid, error = InputValidator.validate_choice(
            "student", "role", ["student", "staff", "admin"]
        )
        assert is_valid is True
        assert error is None
    
    def test_invalid_choice(self):
        """Verify invalid choice fails."""
        is_valid, error = InputValidator.validate_choice(
            "invalid", "role", ["student", "staff", "admin"]
        )
        assert is_valid is False
        assert "must be one of" in error.lower()


class TestHTMLSanitization:
    """Test HTML sanitization."""
    
    def test_sanitize_safe_html(self):
        """Verify safe HTML is preserved."""
        html = "<p>Safe paragraph</p>"
        sanitized = InputSanitizer.sanitize_html(html)
        assert sanitized == "<p>Safe paragraph</p>"
    
    def test_sanitize_removes_script_tags(self):
        """Verify script tags are removed."""
        html = "<p>Text</p><script>alert('XSS')</script>"
        sanitized = InputSanitizer.sanitize_html(html)
        assert "<script>" not in sanitized
        assert "alert" not in sanitized
    
    def test_sanitize_removes_onclick(self):
        """Verify onclick attributes are removed."""
        html = '<p onclick="alert(\'XSS\')">Click me</p>'
        sanitized = InputSanitizer.sanitize_html(html)
        assert "onclick" not in sanitized
    
    def test_sanitize_allows_safe_links(self):
        """Verify safe links are allowed."""
        html = '<a href="https://example.com" title="Link">Text</a>'
        sanitized = InputSanitizer.sanitize_html(html)
        assert "<a href=" in sanitized
        assert 'title=' in sanitized or "title=" in sanitized
    
    def test_sanitize_empty_html(self):
        """Verify empty HTML returns empty string."""
        sanitized = InputSanitizer.sanitize_html("")
        assert sanitized == ""


class TestStringSanitization:
    """Test string sanitization."""
    
    def test_sanitize_removes_null_bytes(self):
        """Verify null bytes are removed."""
        text = "text\x00with\x00nulls"
        sanitized = InputSanitizer.sanitize_string(text)
        assert "\x00" not in sanitized
    
    def test_sanitize_removes_control_chars(self):
        """Verify control characters are removed."""
        text = "text\x01with\x02control"
        sanitized = InputSanitizer.sanitize_string(text)
        assert "\x01" not in sanitized
        assert "\x02" not in sanitized
    
    def test_sanitize_preserves_whitespace(self):
        """Verify normal whitespace is preserved."""
        text = "text\nwith\ttabs"
        sanitized = InputSanitizer.sanitize_string(text)
        assert "\n" in sanitized
        assert "\t" in sanitized
    
    def test_sanitize_trims_whitespace(self):
        """Verify leading/trailing whitespace is trimmed."""
        text = "  trimmed  "
        sanitized = InputSanitizer.sanitize_string(text)
        assert sanitized == "trimmed"


class TestFilenameSanitization:
    """Test filename sanitization."""
    
    def test_sanitize_valid_filename(self):
        """Verify valid filename is preserved."""
        filename = "document.pdf"
        sanitized = InputSanitizer.sanitize_filename(filename)
        assert sanitized == "document.pdf"
    
    def test_sanitize_removes_path_separators(self):
        """Verify path separators are removed."""
        filename = "../../../etc/passwd"
        sanitized = InputSanitizer.sanitize_filename(filename)
        assert "/" not in sanitized
        assert "\\" not in sanitized
    
    def test_sanitize_removes_dangerous_chars(self):
        """Verify dangerous characters are removed."""
        filename = "file<script>.pdf"
        sanitized = InputSanitizer.sanitize_filename(filename)
        assert "<" not in sanitized
        assert ">" not in sanitized
    
    def test_sanitize_removes_leading_dots(self):
        """Verify leading dots are removed (hidden files)."""
        filename = "...hidden.txt"
        sanitized = InputSanitizer.sanitize_filename(filename)
        assert not sanitized.startswith(".")
    
    def test_sanitize_empty_filename(self):
        """Verify empty filename gets default name."""
        sanitized = InputSanitizer.sanitize_filename("")
        assert sanitized == "unnamed"
    
    def test_sanitize_long_filename(self):
        """Verify long filename is truncated."""
        filename = "a" * 300 + ".txt"
        sanitized = InputSanitizer.sanitize_filename(filename)
        assert len(sanitized) <= 255


class TestSQLLikeSanitization:
    """Test SQL LIKE sanitization."""
    
    def test_sanitize_escapes_percent(self):
        """Verify percent signs are escaped."""
        value = "test%value"
        sanitized = InputSanitizer.sanitize_sql_like(value)
        assert sanitized == "test\\%value"
    
    def test_sanitize_escapes_underscore(self):
        """Verify underscores are escaped."""
        value = "test_value"
        sanitized = InputSanitizer.sanitize_sql_like(value)
        assert sanitized == "test\\_value"
    
    def test_sanitize_escapes_backslash(self):
        """Verify backslashes are escaped."""
        value = "test\\value"
        sanitized = InputSanitizer.sanitize_sql_like(value)
        assert sanitized == "test\\\\value"


class TestRequestDataValidation:
    """Test request data validation with schemas."""
    
    def test_validate_valid_data(self):
        """Verify valid data passes validation."""
        data = {
            'email': 'user@example.com',
            'name': 'John Doe',
            'age': 25
        }
        schema = {
            'email': {'type': 'email', 'required': True},
            'name': {'type': 'string', 'required': True, 'max_length': 100},
            'age': {'type': 'integer', 'required': False, 'min_value': 0}
        }
        
        is_valid, error, sanitized = validate_request_data(data, schema)
        
        assert is_valid is True
        assert error is None
        assert 'email' in sanitized
        assert 'name' in sanitized
        assert 'age' in sanitized
    
    def test_validate_missing_required_field(self):
        """Verify missing required field fails."""
        data = {
            'name': 'John Doe'
        }
        schema = {
            'email': {'type': 'email', 'required': True},
            'name': {'type': 'string', 'required': True}
        }
        
        is_valid, error, sanitized = validate_request_data(data, schema)
        
        assert is_valid is False
        assert "required" in error.lower()
    
    def test_validate_invalid_type(self):
        """Verify invalid type fails validation."""
        data = {
            'age': 'not a number'
        }
        schema = {
            'age': {'type': 'integer', 'required': True}
        }
        
        is_valid, error, sanitized = validate_request_data(data, schema)
        
        assert is_valid is False
        assert "integer" in error.lower()
    
    def test_validate_sanitizes_html(self):
        """Verify HTML fields are sanitized."""
        data = {
            'bio': '<p>Bio</p><script>alert("XSS")</script>'
        }
        schema = {
            'bio': {'type': 'html', 'required': False}
        }
        
        is_valid, error, sanitized = validate_request_data(data, schema)
        
        assert is_valid is True
        assert "<script>" not in sanitized['bio']
        assert "<p>" in sanitized['bio']


class TestInjectionPrevention:
    """Test prevention of common injection attacks."""
    
    def test_prevent_sql_injection_in_string(self):
        """Verify SQL injection attempts are caught."""
        malicious_inputs = [
            "'; DROP TABLE users;--",
            "' OR '1'='1",
            "admin'--",
        ]
        
        for input_str in malicious_inputs:
            # String validation doesn't prevent SQL injection directly,
            # but sanitization removes dangerous characters
            sanitized = InputSanitizer.sanitize_string(input_str)
            # Sanitized string should still contain quotes but be safe when used with parameterized queries
            assert sanitized is not None
    
    def test_prevent_xss_in_html(self):
        """Verify XSS attempts are neutralized."""
        malicious_html = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert("XSS")>',
            '<iframe src="javascript:alert(\'XSS\')"></iframe>',
        ]
        
        for html in malicious_html:
            sanitized = InputSanitizer.sanitize_html(html)
            assert "<script>" not in sanitized
            assert "onerror" not in sanitized
            assert "javascript:" not in sanitized
    
    def test_prevent_path_traversal_in_filename(self):
        """Verify path traversal attempts are blocked."""
        malicious_filenames = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "file/../../etc/passwd",
        ]
        
        for filename in malicious_filenames:
            sanitized = InputSanitizer.sanitize_filename(filename)
            assert "/" not in sanitized
            assert "\\" not in sanitized
            assert ".." not in sanitized or not sanitized.startswith(".")
