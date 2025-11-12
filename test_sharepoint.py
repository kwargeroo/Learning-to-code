#!/usr/bin/env python3
"""Test SharePoint connection independently"""

import sys
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from src.sharepoint_client import SharePointClient

def test_sharepoint_connection():
    """Test SharePoint authentication and basic operations"""
    print("=" * 60)
    print("SHAREPOINT CONNECTION TEST")
    print("=" * 60)

    # Get credentials from environment
    tenant_id = os.getenv("SHAREPOINT_TENANT_ID")
    client_id = os.getenv("SHAREPOINT_CLIENT_ID")
    client_secret = os.getenv("SHAREPOINT_CLIENT_SECRET")
    site_name = os.getenv("SHAREPOINT_SITE_NAME")
    site_id = os.getenv("SHAREPOINT_SITE_ID")
    list_name = os.getenv("SHAREPOINT_LIST_NAME")
    list_id = os.getenv("SHAREPOINT_LIST_ID")

    # Validate required credentials
    if not all([tenant_id, client_id, client_secret]):
        print("❌ ERROR: Missing SharePoint credentials in .env file")
        print("   Required: SHAREPOINT_TENANT_ID, SHAREPOINT_CLIENT_ID, SHAREPOINT_CLIENT_SECRET")
        return False

    print(f"\n1. Testing authentication")
    print(f"   Tenant ID: {tenant_id[:8]}...")
    print(f"   Client ID: {client_id[:8]}...")

    # Create client
    client = SharePointClient(tenant_id, client_id, client_secret)

    # Test authentication
    print("\n2. Attempting to authenticate with Microsoft Graph...")
    if not client.authenticate():
        print("❌ FAILED: Could not authenticate with SharePoint")
        print("\nTroubleshooting tips:")
        print("  - Verify Tenant ID, Client ID, and Client Secret are correct")
        print("  - Ensure the Azure AD app has Sites.ReadWrite.All permission")
        print("  - Check that admin consent has been granted")
        print("  - Wait a few minutes if you just created the app")
        return False

    print("✓ Authentication successful!")

    # Test site access
    print("\n3. Testing site access...")

    resolved_site_id = site_id
    if site_name and not site_id:
        print(f"   Looking up site by name: {site_name}")
        resolved_site_id = client.get_site_id_by_name(site_name)
        if not resolved_site_id:
            print(f"❌ FAILED: Could not find site '{site_name}'")
            print("\nTroubleshooting tips:")
            print("  - Check the site name is correct")
            print("  - Ensure the app has access to the site")
            print("  - Try using SHAREPOINT_SITE_ID directly instead")
            return False
        print(f"   ✓ Found site ID: {resolved_site_id}")
    elif site_id:
        print(f"   Using site ID: {site_id}")
    else:
        print("⚠ WARNING: No site name or ID provided")
        print("   Set SHAREPOINT_SITE_NAME or SHAREPOINT_SITE_ID to test further")
        print("\n✓ AUTHENTICATION TEST PASSED (partial)")
        return True

    # Test list access
    print("\n4. Testing list access...")

    resolved_list_id = list_id
    if list_name and not list_id:
        print(f"   Looking up list by name: {list_name}")
        resolved_list_id = client.get_list_id_by_name(resolved_site_id, list_name)
        if not resolved_list_id:
            print(f"❌ FAILED: Could not find list '{list_name}'")
            print("\nTroubleshooting tips:")
            print("  - Check the list name is correct (case-sensitive)")
            print("  - Ensure the list exists in the SharePoint site")
            print("  - Try using SHAREPOINT_LIST_ID directly instead")
            return False
        print(f"   ✓ Found list ID: {resolved_list_id}")
    elif list_id:
        print(f"   Using list ID: {list_id}")
    else:
        print("⚠ WARNING: No list name or ID provided")
        print("   Set SHAREPOINT_LIST_NAME or SHAREPOINT_LIST_ID to test further")
        print("\n✓ SHAREPOINT TEST PASSED (partial)")
        return True

    # Try to fetch items
    print("\n5. Testing list read access...")
    try:
        items = client.get_list_items(resolved_site_id, resolved_list_id)
        print(f"✓ Successfully read list (found {len(items)} items)")

        if items:
            print("\nSample item fields:")
            sample_fields = items[0].get("fields", {})
            for key in list(sample_fields.keys())[:5]:
                print(f"  - {key}")
    except Exception as e:
        print(f"❌ ERROR reading list: {e}")
        return False

    print("\n✓ SHAREPOINT TEST PASSED")
    return True

if __name__ == "__main__":
    success = test_sharepoint_connection()
    sys.exit(0 if success else 1)
