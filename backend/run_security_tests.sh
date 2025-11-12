#!/bin/bash

###############################################################################
# Security Test Runner Script
# 
# This script runs all security tests for the Campus Resource Hub backend.
# It provides various options for running different test suites and 
# generating coverage reports.
#
# Usage:
#   ./run_security_tests.sh [OPTIONS]
#
# Options:
#   --all           Run all security tests (default)
#   --csrf          Run CSRF protection tests only
#   --rate-limit    Run rate limiting tests only
#   --headers       Run security headers tests only
#   --secrets       Run secret management tests only
#   --validation    Run input validation tests only
#   --baseline      Run baseline integration tests only
#   --coverage      Generate HTML coverage report
#   --verbose       Enable verbose output
#   --quick         Run tests without coverage (faster)
#   --help          Show this help message
#
# Examples:
#   ./run_security_tests.sh
#   ./run_security_tests.sh --csrf --verbose
#   ./run_security_tests.sh --all --coverage
#   ./run_security_tests.sh --baseline --verbose
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
RUN_ALL=true
RUN_CSRF=false
RUN_RATE_LIMIT=false
RUN_HEADERS=false
RUN_SECRETS=false
RUN_VALIDATION=false
RUN_BASELINE=false
COVERAGE=false
VERBOSE=false
QUICK=false

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            RUN_ALL=true
            shift
            ;;
        --csrf)
            RUN_ALL=false
            RUN_CSRF=true
            shift
            ;;
        --rate-limit)
            RUN_ALL=false
            RUN_RATE_LIMIT=true
            shift
            ;;
        --headers)
            RUN_ALL=false
            RUN_HEADERS=true
            shift
            ;;
        --secrets)
            RUN_ALL=false
            RUN_SECRETS=true
            shift
            ;;
        --validation)
            RUN_ALL=false
            RUN_VALIDATION=true
            shift
            ;;
        --baseline)
            RUN_ALL=false
            RUN_BASELINE=true
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --quick)
            QUICK=true
            shift
            ;;
        --help)
            head -n 30 "$0" | tail -n 27
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help to see available options"
            exit 1
            ;;
    esac
done

# Function to print section headers
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# Function to print success message
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error message
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print warning message
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to print info message
print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    print_error "pytest is not installed!"
    print_info "Install with: pip install pytest pytest-cov"
    exit 1
fi

# Print banner
print_header "Campus Resource Hub - Security Test Suite"

# Build pytest command options
PYTEST_OPTS="-v"
if [ "$VERBOSE" = true ]; then
    PYTEST_OPTS="$PYTEST_OPTS --tb=short -s"
else
    PYTEST_OPTS="$PYTEST_OPTS --tb=line"
fi

if [ "$COVERAGE" = true ] && [ "$QUICK" = false ]; then
    PYTEST_OPTS="$PYTEST_OPTS --cov=. --cov-report=term-missing --cov-report=html"
    print_info "Coverage reporting enabled"
fi

# Track test results
TOTAL_TESTS=0
FAILED_TESTS=0
TEST_FILES=()

# Function to run a test file
run_test() {
    local test_name=$1
    local test_file=$2
    
    print_info "Running: $test_name"
    
    if pytest "tests/security/$test_file" $PYTEST_OPTS; then
        print_success "$test_name passed"
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
    else
        print_error "$test_name failed"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
    fi
    
    echo ""
}

# Run tests based on options
if [ "$RUN_ALL" = true ]; then
    print_header "Running All Security Tests"
    
    run_test "CSRF Protection Tests" "test_csrf_protection.py"
    run_test "Rate Limiting Tests" "test_rate_limiting.py"
    run_test "Security Headers Tests" "test_security_headers.py"
    run_test "Secret Management Tests" "test_secret_management.py"
    run_test "Input Validation Tests" "test_input_validation.py"
    run_test "Baseline Integration Tests" "test_baseline_security.py"
else
    if [ "$RUN_CSRF" = true ]; then
        run_test "CSRF Protection Tests" "test_csrf_protection.py"
    fi
    
    if [ "$RUN_RATE_LIMIT" = true ]; then
        run_test "Rate Limiting Tests" "test_rate_limiting.py"
    fi
    
    if [ "$RUN_HEADERS" = true ]; then
        run_test "Security Headers Tests" "test_security_headers.py"
    fi
    
    if [ "$RUN_SECRETS" = true ]; then
        run_test "Secret Management Tests" "test_secret_management.py"
    fi
    
    if [ "$RUN_VALIDATION" = true ]; then
        run_test "Input Validation Tests" "test_input_validation.py"
    fi
    
    if [ "$RUN_BASELINE" = true ]; then
        run_test "Baseline Integration Tests" "test_baseline_security.py"
    fi
fi

# Print summary
print_header "Test Summary"

if [ $TOTAL_TESTS -eq 0 ]; then
    print_warning "No tests were run"
    exit 0
fi

echo "Total test suites run: $TOTAL_TESTS"
echo "Successful: $((TOTAL_TESTS - FAILED_TESTS))"
echo "Failed: $FAILED_TESTS"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    print_success "All security tests passed! ✓"
    
    if [ "$COVERAGE" = true ]; then
        echo ""
        print_info "Coverage report generated at: htmlcov/index.html"
        print_info "View with: open htmlcov/index.html (macOS) or xdg-open htmlcov/index.html (Linux)"
    fi
    
    exit 0
else
    print_error "Some security tests failed!"
    print_warning "Please review the test output above for details"
    exit 1
fi
