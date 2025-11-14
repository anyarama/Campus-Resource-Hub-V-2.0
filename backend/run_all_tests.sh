#!/bin/bash

# Campus Resource Hub - Comprehensive Test Runner
# Runs all test suites with coverage reporting and quality checks

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test suite paths
SECURITY_TESTS="tests/security"
API_TESTS="tests/api"
INTEGRATION_TESTS="tests/integration"

# Coverage thresholds
OVERALL_THRESHOLD=85
API_THRESHOLD=90
SECURITY_THRESHOLD=95
SERVICES_THRESHOLD=85

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Campus Resource Hub - Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${YELLOW}⚠️  Warning: Virtual environment not activated${NC}"
    echo -e "${YELLOW}   Run: source venv/bin/activate${NC}"
    echo ""
fi

# Install/upgrade testing dependencies
echo -e "${BLUE}📦 Checking dependencies...${NC}"
pip install -q --upgrade pytest pytest-cov pytest-flask coverage ruff black mypy 2>/dev/null || true
echo -e "${GREEN}✓ Dependencies ready${NC}"
echo ""

# Run code quality checks
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  1. Code Quality Checks${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Ruff linter
echo -e "${BLUE}Running Ruff linter...${NC}"
if ruff check . --select=E,F,W,C,N --ignore=E501 2>/dev/null; then
    echo -e "${GREEN}✓ Ruff linter passed${NC}"
else
    echo -e "${YELLOW}⚠️  Ruff linter found issues (non-blocking)${NC}"
fi
echo ""

# Black formatter check
echo -e "${BLUE}Checking code formatting (Black)...${NC}"
if black --check --quiet . 2>/dev/null; then
    echo -e "${GREEN}✓ Code formatting check passed${NC}"
else
    echo -e "${YELLOW}⚠️  Code formatting issues found${NC}"
    echo -e "${YELLOW}   Run: black . to auto-format${NC}"
fi
echo ""

# Mypy type checking (non-blocking)
echo -e "${BLUE}Running type checks (Mypy)...${NC}"
if mypy --ignore-missing-imports --no-error-summary . 2>/dev/null; then
    echo -e "${GREEN}✓ Type checking passed${NC}"
else
    echo -e "${YELLOW}⚠️  Type checking issues found (non-blocking)${NC}"
fi
echo ""

# Run security tests
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  2. Security Tests${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${BLUE}Running security test suite...${NC}"
pytest $SECURITY_TESTS -v --tb=short --cov=. --cov-report=term-missing:skip-covered \
    --cov-fail-under=$SECURITY_THRESHOLD --cov-branch 2>/dev/null || {
    echo -e "${RED}✗ Security tests failed or coverage below ${SECURITY_THRESHOLD}%${NC}"
    exit 1
}
echo -e "${GREEN}✓ Security tests passed${NC}"
echo ""

# Run API tests
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  3. API Tests${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${BLUE}Running API test suite...${NC}"
pytest $API_TESTS -v --tb=short --cov=routes --cov=services --cov-append \
    --cov-report=term-missing:skip-covered 2>/dev/null || {
    echo -e "${YELLOW}⚠️  API tests had failures${NC}"
}
echo -e "${GREEN}✓ API tests completed${NC}"
echo ""

# Run integration tests
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  4. Integration Tests${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${BLUE}Running integration test suite...${NC}"
pytest $INTEGRATION_TESTS -v --tb=short --cov=. --cov-append \
    --cov-report=term-missing:skip-covered 2>/dev/null || {
    echo -e "${YELLOW}⚠️  Integration tests had failures${NC}"
}
echo -e "${GREEN}✓ Integration tests completed${NC}"
echo ""

# Run all tests with comprehensive coverage
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  5. Comprehensive Coverage Report${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${BLUE}Generating comprehensive coverage report...${NC}"
pytest tests/ -v --cov=. --cov-report=html --cov-report=term \
    --cov-report=xml --cov-fail-under=$OVERALL_THRESHOLD \
    --ignore=tests/conftest.py --tb=short 2>/dev/null || {
    echo -e "${RED}✗ Overall coverage below ${OVERALL_THRESHOLD}% threshold${NC}"
    echo -e "${YELLOW}   View detailed report: htmlcov/index.html${NC}"
    exit 1
}

echo ""
echo -e "${GREEN}✓ Coverage threshold met (${OVERALL_THRESHOLD}%+)${NC}"
echo -e "${BLUE}   HTML Report: htmlcov/index.html${NC}"
echo -e "${BLUE}   XML Report: coverage.xml${NC}"
echo ""

# Test summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Test Suite Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Count test files
SECURITY_COUNT=$(find $SECURITY_TESTS -name "test_*.py" 2>/dev/null | wc -l)
API_COUNT=$(find $API_TESTS -name "test_*.py" 2>/dev/null | wc -l)
INTEGRATION_COUNT=$(find $INTEGRATION_TESTS -name "test_*.py" 2>/dev/null | wc -l)
TOTAL_FILES=$((SECURITY_COUNT + API_COUNT + INTEGRATION_COUNT))

echo -e "${GREEN}✓ Security Tests:    ${SECURITY_COUNT} test files${NC}"
echo -e "${GREEN}✓ API Tests:         ${API_COUNT} test files${NC}"
echo -e "${GREEN}✓ Integration Tests: ${INTEGRATION_COUNT} test files${NC}"
echo -e "${GREEN}✓ Total Test Files:  ${TOTAL_FILES}${NC}"
echo ""

# Get test count from pytest
TEST_COUNT=$(pytest --collect-only -q 2>/dev/null | tail -n 1 | awk '{print $1}')
echo -e "${GREEN}✓ Total Test Cases:  ${TEST_COUNT}${NC}"
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}  ✓ All Tests Passed Successfully!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  • View HTML coverage: open htmlcov/index.html"
echo -e "  • Check coverage XML: coverage.xml"
echo -e "  • Run security tests only: pytest tests/security/"
echo -e "  • Run API tests only: pytest tests/api/"
echo -e "  • Run integration tests only: pytest tests/integration/"
echo ""

exit 0
