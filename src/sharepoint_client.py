"""SharePoint client module for updating spreadsheets via Microsoft Graph API"""

import requests
import msal
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SharePointClient:
    """Client for interacting with SharePoint via Microsoft Graph API"""

    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        """
        Initialize SharePoint client

        Args:
            tenant_id: Azure AD tenant ID
            client_id: Azure AD application (client) ID
            client_secret: Azure AD client secret
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"

    def authenticate(self) -> bool:
        """
        Authenticate with Microsoft Graph API

        Returns:
            bool: True if authentication successful
        """
        try:
            authority = f"https://login.microsoftonline.com/{self.tenant_id}"
            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=authority,
                client_credential=self.client_secret
            )

            # Acquire token for Microsoft Graph
            result = app.acquire_token_for_client(
                scopes=["https://graph.microsoft.com/.default"]
            )

            if "access_token" in result:
                self.access_token = result["access_token"]
                logger.info("Successfully authenticated with Microsoft Graph")
                return True
            else:
                error = result.get("error_description", "Unknown error")
                logger.error(f"Authentication failed: {error}")
                return False

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def get_list_items(self, site_id: str, list_id: str) -> List[Dict]:
        """
        Get items from a SharePoint list

        Args:
            site_id: SharePoint site ID
            list_id: SharePoint list ID

        Returns:
            List of items
        """
        if not self.access_token:
            logger.error("Not authenticated. Call authenticate() first.")
            return []

        try:
            url = f"{self.graph_endpoint}/sites/{site_id}/lists/{list_id}/items"
            params = {"expand": "fields"}

            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()

            items = response.json().get("value", [])
            logger.info(f"Retrieved {len(items)} items from list")
            return items

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching list items: {e}")
            return []

    def update_list_item(self, site_id: str, list_id: str, item_id: str,
                        fields: Dict) -> bool:
        """
        Update a SharePoint list item

        Args:
            site_id: SharePoint site ID
            list_id: SharePoint list ID
            item_id: Item ID to update
            fields: Dictionary of field names and values to update

        Returns:
            bool: True if update successful
        """
        if not self.access_token:
            logger.error("Not authenticated. Call authenticate() first.")
            return False

        try:
            url = f"{self.graph_endpoint}/sites/{site_id}/lists/{list_id}/items/{item_id}/fields"

            response = requests.patch(
                url,
                headers=self._get_headers(),
                json=fields
            )
            response.raise_for_status()

            logger.info(f"Successfully updated item {item_id}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating list item: {e}")
            return False

    def create_list_item(self, site_id: str, list_id: str, fields: Dict) -> Optional[str]:
        """
        Create a new SharePoint list item

        Args:
            site_id: SharePoint site ID
            list_id: SharePoint list ID
            fields: Dictionary of field names and values

        Returns:
            str: Created item ID if successful, None otherwise
        """
        if not self.access_token:
            logger.error("Not authenticated. Call authenticate() first.")
            return None

        try:
            url = f"{self.graph_endpoint}/sites/{site_id}/lists/{list_id}/items"

            payload = {"fields": fields}

            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload
            )
            response.raise_for_status()

            item_id = response.json().get("id")
            logger.info(f"Successfully created item {item_id}")
            return item_id

        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating list item: {e}")
            return None

    def find_item_by_field(self, site_id: str, list_id: str,
                          field_name: str, field_value: str) -> Optional[Dict]:
        """
        Find a list item by a specific field value

        Args:
            site_id: SharePoint site ID
            list_id: SharePoint list ID
            field_name: Field name to search
            field_value: Field value to match

        Returns:
            Item dictionary if found, None otherwise
        """
        items = self.get_list_items(site_id, list_id)

        for item in items:
            fields = item.get("fields", {})
            if fields.get(field_name) == field_value:
                return item

        return None

    def get_site_id_by_name(self, site_name: str) -> Optional[str]:
        """
        Get SharePoint site ID by site name

        Args:
            site_name: SharePoint site name

        Returns:
            Site ID if found, None otherwise
        """
        if not self.access_token:
            logger.error("Not authenticated. Call authenticate() first.")
            return None

        try:
            # Search for the site
            url = f"{self.graph_endpoint}/sites"
            params = {"search": site_name}

            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()

            sites = response.json().get("value", [])

            if sites:
                site_id = sites[0]["id"]
                logger.info(f"Found site ID: {site_id}")
                return site_id
            else:
                logger.warning(f"No site found with name: {site_name}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error finding site: {e}")
            return None

    def get_list_id_by_name(self, site_id: str, list_name: str) -> Optional[str]:
        """
        Get SharePoint list ID by list name

        Args:
            site_id: SharePoint site ID
            list_name: List/library name

        Returns:
            List ID if found, None otherwise
        """
        if not self.access_token:
            logger.error("Not authenticated. Call authenticate() first.")
            return None

        try:
            url = f"{self.graph_endpoint}/sites/{site_id}/lists"
            params = {"$filter": f"displayName eq '{list_name}'"}

            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()

            lists = response.json().get("value", [])

            if lists:
                list_id = lists[0]["id"]
                logger.info(f"Found list ID: {list_id}")
                return list_id
            else:
                logger.warning(f"No list found with name: {list_name}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error finding list: {e}")
            return None
