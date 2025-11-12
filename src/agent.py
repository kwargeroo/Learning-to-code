"""Main agent orchestrator for email review and SharePoint updates"""

from typing import Dict, Optional
import logging
from .email_client import EmailClient
from .sharepoint_client import SharePointClient
from .email_reviewer import EmailReviewer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailReviewSharePointAgent:
    """Main agent that orchestrates email review and SharePoint updates"""

    def __init__(self, config: Dict):
        """
        Initialize the agent with configuration

        Args:
            config: Configuration dictionary containing email and SharePoint settings
        """
        self.config = config

        # Initialize email client
        email_config = config.get("email", {})
        self.email_client = EmailClient(
            server=email_config.get("server"),
            email_address=email_config.get("address"),
            password=email_config.get("password"),
            port=email_config.get("port", 993)
        )

        # Initialize SharePoint client
        sp_config = config.get("sharepoint", {})
        self.sp_client = SharePointClient(
            tenant_id=sp_config.get("tenant_id"),
            client_id=sp_config.get("client_id"),
            client_secret=sp_config.get("client_secret")
        )

        # Initialize email reviewer
        review_config = config.get("review", {})
        self.reviewer = EmailReviewer(
            use_ai=review_config.get("use_ai", False),
            openai_api_key=review_config.get("openai_api_key")
        )

        self.site_id = None
        self.list_id = None

    def initialize(self) -> bool:
        """
        Initialize connections to email and SharePoint

        Returns:
            bool: True if initialization successful
        """
        logger.info("Initializing agent...")

        # Connect to email
        if not self.email_client.connect():
            logger.error("Failed to connect to email server")
            return False

        # Authenticate with SharePoint
        if not self.sp_client.authenticate():
            logger.error("Failed to authenticate with SharePoint")
            return False

        # Get SharePoint site and list IDs
        sp_config = self.config.get("sharepoint", {})
        site_name = sp_config.get("site_name")
        list_name = sp_config.get("list_name")

        if site_name:
            self.site_id = self.sp_client.get_site_id_by_name(site_name)
            if not self.site_id:
                logger.error(f"Could not find SharePoint site: {site_name}")
                return False
        else:
            self.site_id = sp_config.get("site_id")

        if list_name and self.site_id:
            self.list_id = self.sp_client.get_list_id_by_name(self.site_id, list_name)
            if not self.list_id:
                logger.error(f"Could not find SharePoint list: {list_name}")
                return False
        else:
            self.list_id = sp_config.get("list_id")

        if not self.site_id or not self.list_id:
            logger.error("SharePoint site_id and list_id must be provided")
            return False

        logger.info("Agent initialized successfully")
        return True

    def process_emails(self, limit: int = 10, mark_as_read: bool = True) -> int:
        """
        Process emails and update SharePoint

        Args:
            limit: Maximum number of emails to process
            mark_as_read: Whether to mark processed emails as read

        Returns:
            Number of emails successfully processed
        """
        logger.info(f"Processing up to {limit} emails...")

        # Fetch emails
        email_config = self.config.get("email", {})
        folder = email_config.get("folder", "INBOX")
        unread_only = email_config.get("unread_only", True)

        emails = self.email_client.fetch_emails(
            folder=folder,
            limit=limit,
            unread_only=unread_only
        )

        if not emails:
            logger.info("No emails to process")
            return 0

        processed_count = 0

        for email_data in emails:
            try:
                if self._process_single_email(email_data):
                    processed_count += 1

                    # Mark as read if configured
                    if mark_as_read:
                        self.email_client.mark_as_read(email_data["id"])

            except Exception as e:
                logger.error(f"Error processing email {email_data.get('id')}: {e}")
                continue

        logger.info(f"Successfully processed {processed_count}/{len(emails)} emails")
        return processed_count

    def _process_single_email(self, email_data: Dict) -> bool:
        """
        Process a single email

        Args:
            email_data: Email data dictionary

        Returns:
            bool: True if processed successfully
        """
        try:
            # Review the email
            review_result = self.reviewer.review_email(email_data)
            logger.info(f"Email reviewed: {email_data.get('subject')} -> {review_result.get('status')}")

            # Extract tracking info
            tracking_info = self.reviewer.extract_tracking_info(email_data)

            # Prepare SharePoint fields
            sp_fields = {
                "Title": email_data.get("subject", "No Subject"),
                "Status": review_result.get("status", "Pending Review"),
                "Priority": review_result.get("priority", "Medium"),
                "Category": review_result.get("category", "General"),
                "Notes": review_result.get("notes", ""),
                "EmailFrom": tracking_info.get("EmailFrom", ""),
                "EmailDate": tracking_info.get("EmailDate", ""),
            }

            # Add reference ID if available
            if review_result.get("reference_id"):
                sp_fields["ReferenceID"] = review_result["reference_id"]

            # Check if item already exists (by email subject or ID)
            existing_item = self.sp_client.find_item_by_field(
                self.site_id,
                self.list_id,
                "Title",
                email_data.get("subject", "")
            )

            if existing_item:
                # Update existing item
                item_id = existing_item["id"]
                success = self.sp_client.update_list_item(
                    self.site_id,
                    self.list_id,
                    item_id,
                    sp_fields
                )
                logger.info(f"Updated existing SharePoint item: {item_id}")
            else:
                # Create new item
                item_id = self.sp_client.create_list_item(
                    self.site_id,
                    self.list_id,
                    sp_fields
                )
                logger.info(f"Created new SharePoint item: {item_id}")

            return True

        except Exception as e:
            logger.error(f"Error processing email: {e}")
            return False

    def cleanup(self):
        """Clean up connections"""
        logger.info("Cleaning up agent...")
        self.email_client.disconnect()

    def run(self, limit: int = 10) -> Dict:
        """
        Run the agent end-to-end

        Args:
            limit: Maximum number of emails to process

        Returns:
            Dictionary with run results
        """
        result = {
            "success": False,
            "processed": 0,
            "errors": []
        }

        try:
            # Initialize
            if not self.initialize():
                result["errors"].append("Initialization failed")
                return result

            # Process emails
            processed = self.process_emails(limit=limit)
            result["processed"] = processed
            result["success"] = True

        except Exception as e:
            logger.error(f"Agent run failed: {e}")
            result["errors"].append(str(e))

        finally:
            # Cleanup
            self.cleanup()

        return result
