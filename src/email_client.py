"""Email client module for fetching and parsing emails"""

import imaplib
import email
from email.header import decode_header
from typing import List, Dict, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailClient:
    """Client for connecting to email servers and fetching emails"""

    def __init__(self, server: str, email_address: str, password: str, port: int = 993):
        """
        Initialize email client

        Args:
            server: IMAP server address (e.g., 'imap.gmail.com')
            email_address: Email address for authentication
            password: Password or app-specific password
            port: IMAP port (default: 993 for SSL)
        """
        self.server = server
        self.email_address = email_address
        self.password = password
        self.port = port
        self.connection = None

    def connect(self) -> bool:
        """
        Connect to the email server

        Returns:
            bool: True if connection successful
        """
        try:
            self.connection = imaplib.IMAP4_SSL(self.server, self.port)
            self.connection.login(self.email_address, self.password)
            logger.info(f"Successfully connected to {self.server}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to email server: {e}")
            return False

    def disconnect(self):
        """Disconnect from the email server"""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
                logger.info("Disconnected from email server")
            except:
                pass

    def fetch_emails(self, folder: str = "INBOX", limit: int = 10,
                     unread_only: bool = True) -> List[Dict]:
        """
        Fetch emails from specified folder

        Args:
            folder: Email folder to fetch from (default: INBOX)
            limit: Maximum number of emails to fetch
            unread_only: Only fetch unread emails (default: True)

        Returns:
            List of email dictionaries with parsed content
        """
        if not self.connection:
            logger.error("Not connected to email server")
            return []

        emails = []

        try:
            # Select the folder
            self.connection.select(folder)

            # Search for emails
            search_criteria = "UNSEEN" if unread_only else "ALL"
            status, messages = self.connection.search(None, search_criteria)

            if status != "OK":
                logger.error(f"Failed to search emails: {status}")
                return []

            # Get email IDs
            email_ids = messages[0].split()

            # Fetch the most recent emails (up to limit)
            for email_id in email_ids[-limit:]:
                try:
                    email_data = self._fetch_email(email_id)
                    if email_data:
                        emails.append(email_data)
                except Exception as e:
                    logger.error(f"Error fetching email {email_id}: {e}")
                    continue

            logger.info(f"Fetched {len(emails)} emails from {folder}")
            return emails

        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []

    def _fetch_email(self, email_id: bytes) -> Optional[Dict]:
        """
        Fetch and parse a single email

        Args:
            email_id: Email ID from IMAP server

        Returns:
            Dictionary with email details
        """
        try:
            status, msg_data = self.connection.fetch(email_id, "(RFC822)")

            if status != "OK":
                return None

            # Parse email
            email_message = email.message_from_bytes(msg_data[0][1])

            # Extract subject
            subject = self._decode_header(email_message["Subject"])

            # Extract sender
            from_header = self._decode_header(email_message["From"])

            # Extract date
            date_str = email_message["Date"]

            # Extract body
            body = self._extract_body(email_message)

            return {
                "id": email_id.decode(),
                "subject": subject,
                "from": from_header,
                "date": date_str,
                "body": body,
                "raw_message": email_message
            }

        except Exception as e:
            logger.error(f"Error parsing email: {e}")
            return None

    def _decode_header(self, header: str) -> str:
        """Decode email header"""
        if not header:
            return ""

        decoded_parts = []
        for part, encoding in decode_header(header):
            if isinstance(part, bytes):
                decoded_parts.append(part.decode(encoding or "utf-8", errors="ignore"))
            else:
                decoded_parts.append(part)

        return "".join(decoded_parts)

    def _extract_body(self, email_message) -> str:
        """Extract email body text"""
        body = ""

        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                # Get text/plain parts
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
                    except:
                        pass
        else:
            try:
                body = email_message.get_payload(decode=True).decode(errors="ignore")
            except:
                body = str(email_message.get_payload())

        return body.strip()

    def mark_as_read(self, email_id: str):
        """Mark an email as read"""
        try:
            self.connection.store(email_id.encode(), '+FLAGS', '\\Seen')
        except Exception as e:
            logger.error(f"Error marking email as read: {e}")
