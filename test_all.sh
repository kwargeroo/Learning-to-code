#!/bin/bash
# Run all tests in sequence

set -e  # Exit on first error

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         EMAIL REVIEW SHAREPOINT AGENT - TEST SUITE         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Verify setup first
echo "Running setup verification..."
python verify_setup.py
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Setup verification failed. Please fix configuration before testing."
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    COMPONENT TESTS                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Track results
TESTS_PASSED=0
TESTS_FAILED=0

# Test email
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 1/3: Email Connection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python test_email.py
if [ $? -eq 0 ]; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi
echo ""

# Test SharePoint
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 2/3: SharePoint Connection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python test_sharepoint.py
if [ $? -eq 0 ]; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi
echo ""

# Test review logic
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 3/3: Email Review Logic"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python test_review.py
if [ $? -eq 0 ]; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                      TEST SUMMARY                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Tests Passed: $TESTS_PASSED/3"
echo "Tests Failed: $TESTS_FAILED/3"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo "✓ ALL TESTS PASSED"
    echo ""
    echo "Your agent is ready to use! Try:"
    echo "  python main.py --limit 5"
    exit 0
else
    echo "✗ SOME TESTS FAILED"
    echo ""
    echo "Please check the output above for details."
    echo "See IMPLEMENTATION_GUIDE.md for troubleshooting."
    exit 1
fi
