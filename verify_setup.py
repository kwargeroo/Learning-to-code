#!/usr/bin/env python3
"""Comprehensive setup verification script"""

import sys
import os
from dotenv import load_dotenv

def check_environment():
    """Check Python environment and dependencies"""
    print("=" * 60)
    print("ENVIRONMENT CHECK")
    print("=" * 60)

    # Check Python version
    print(f"\nPython version: {sys.version.split()[0]}")
    if sys.version_info < (3, 7):
        print("❌ ERROR: Python 3.7+ required")
        return False
    print("✓ Python version OK")

    # Check for required packages
    required_packages = [
        "msal", "requests", "dotenv", "email_validator", "dateutil", "openai"
    ]

    print("\nChecking dependencies...")
    missing = []

    for package in required_packages:
        try:
            if package == "dotenv":
                __import__("dotenv")
            elif package == "dateutil":
                __import__("dateutil")
            else:
                __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (missing)")
            missing.append(package)

    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("✓ All dependencies installed")
    return True


def check_configuration():
    """Check configuration files"""
    print("\n" + "=" * 60)
    print("CONFIGURATION CHECK")
    print("=" * 60)

    # Check for .env file
    if not os.path.exists(".env"):
        print("\n❌ .env file not found")
        print("\nTo create it:")
        print("  1. Copy the example: cp .env.example .env")
        print("  2. Edit .env and add your credentials")
        return False

    print("\n✓ .env file exists")

    # Load and check variables
    load_dotenv()

    required_vars = {
        "Email": ["EMAIL_ADDRESS", "EMAIL_PASSWORD"],
        "SharePoint": ["SHAREPOINT_TENANT_ID", "SHAREPOINT_CLIENT_ID", "SHAREPOINT_CLIENT_SECRET"]
    }

    all_set = True

    for category, vars in required_vars.items():
        print(f"\n{category} configuration:")
        for var in vars:
            value = os.getenv(var)
            if value:
                # Show partial value for security
                display = value[:8] + "..." if len(value) > 8 else "***"
                print(f"  ✓ {var}: {display}")
            else:
                print(f"  ✗ {var}: NOT SET")
                all_set = False

    # Check site/list configuration
    print("\nSharePoint Site/List configuration:")
    site_name = os.getenv("SHAREPOINT_SITE_NAME")
    site_id = os.getenv("SHAREPOINT_SITE_ID")
    list_name = os.getenv("SHAREPOINT_LIST_NAME")
    list_id = os.getenv("SHAREPOINT_LIST_ID")

    if site_name or site_id:
        print(f"  ✓ Site: {site_name or site_id}")
    else:
        print("  ✗ Site: NOT SET (need SHAREPOINT_SITE_NAME or SHAREPOINT_SITE_ID)")
        all_set = False

    if list_name or list_id:
        print(f"  ✓ List: {list_name or list_id}")
    else:
        print("  ✗ List: NOT SET (need SHAREPOINT_LIST_NAME or SHAREPOINT_LIST_ID)")
        all_set = False

    if not all_set:
        print("\n❌ Some required configuration variables are missing")
        return False

    print("\n✓ All required configuration set")
    return True


def main():
    """Run all verification checks"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "EMAIL REVIEW SHAREPOINT AGENT" + " " * 19 + "║")
    print("║" + " " * 16 + "SETUP VERIFICATION" + " " * 24 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")

    checks = [
        ("Environment", check_environment),
        ("Configuration", check_configuration)
    ]

    results = []

    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check failed with error: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_passed = all(result for _, result in results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    if all_passed:
        print("\n" + "=" * 60)
        print("✓ SETUP VERIFICATION PASSED")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Test email connection:      python test_email.py")
        print("  2. Test SharePoint connection: python test_sharepoint.py")
        print("  3. Test review logic:          python test_review.py")
        print("  4. Run the agent:              python main.py --limit 5")
        return 0
    else:
        print("\n" + "=" * 60)
        print("✗ SETUP VERIFICATION FAILED")
        print("=" * 60)
        print("\nPlease fix the issues above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
