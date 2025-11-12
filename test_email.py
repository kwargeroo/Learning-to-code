#!/usr/bin/env python3
"""Test email connection independently"""

import sys
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from src.email_client import EmailClient

def test_email_connection():
    """Test email connection and fetch"""
    print("=" * 60)
    print("EMAIL CONNECTION TEST")
    print("=" * 60)

    # Get credentials from environment
    server = os.getenv("EMAIL_SERVER", "imap.gmail.com")
    email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    port = int(os.getenv("EMAIL_PORT", "993"))

    if not email or not password:
        print("❌ ERROR: EMAIL_ADDRESS and EMAIL_PASSWORD must be set in .env file")
        return False

    print(f"\n1. Testing connection to {server}:{port}")
    print(f"   Email: {email}")

    # Create client
    client = EmailClient(server, email, password, port)

    # Test connection
    print("\n2. Attempting to connect...")
    if not client.connect():
        print("❌ FAILED: Could not connect to email server")
        print("\nTroubleshooting tips:")
        print("  - Gmail users: Enable IMAP in Gmail settings")
        print("  - Gmail users: Use an App Password, not your regular password")
        print("  - Check that the server and port are correct")
        print("  - Verify your credentials")
        return False

    print("✓ Connected successfully!")

    # Test fetching emails
    print("\n3. Fetching recent emails (max 5)...")
    try:
        emails = client.fetch_emails(limit=5, unread_only=False)

        if not emails:
            print("⚠ WARNING: No emails found")
            print("   This is OK if your inbox is empty")
        else:
            print(f"✓ Found {len(emails)} emails\n")

            print("Recent emails:")
            print("-" * 60)
            for i, email_data in enumerate(emails, 1):
                subject = email_data.get("subject", "No Subject")[:50]
                from_addr = email_data.get("from", "Unknown")[:30]
                print(f"{i}. From: {from_addr}")
                print(f"   Subject: {subject}")
                print()

        client.disconnect()
        print("✓ EMAIL TEST PASSED")
        return True

    except Exception as e:
        print(f"❌ ERROR fetching emails: {e}")
        client.disconnect()
        return False

if __name__ == "__main__":
    success = test_email_connection()
    sys.exit(0 if success else 1)
