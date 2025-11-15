"""Email review module for analyzing email content and determining actions"""

import re
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailReviewer:
    """Analyzes email content and determines appropriate status updates"""

    def __init__(self, use_ai: bool = False, openai_api_key: Optional[str] = None):
        """
        Initialize email reviewer

        Args:
            use_ai: Whether to use AI (OpenAI) for review (default: False, uses rules)
            openai_api_key: OpenAI API key (required if use_ai=True)
        """
        self.use_ai = use_ai
        self.openai_api_key = openai_api_key

        if use_ai and not openai_api_key:
            logger.warning("AI review enabled but no API key provided. Falling back to rule-based review.")
            self.use_ai = False

        # Initialize OpenAI client if using AI
        if self.use_ai:
            try:
                from openai import OpenAI
                self.ai_client = OpenAI(api_key=openai_api_key)
                logger.info("AI-powered review enabled")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.use_ai = False

    def review_email(self, email_data: Dict) -> Dict:
        """
        Review an email and determine the appropriate status and metadata

        Args:
            email_data: Email data dictionary from EmailClient

        Returns:
            Dictionary with review results including status, priority, category, etc.
        """
        if self.use_ai:
            return self._ai_review(email_data)
        else:
            return self._rule_based_review(email_data)

    def _rule_based_review(self, email_data: Dict) -> Dict:
        """
        Rule-based email review using pattern matching

        Args:
            email_data: Email data dictionary

        Returns:
            Review results dictionary
        """
        subject = email_data.get("subject", "").lower()
        body = email_data.get("body", "").lower()
        from_address = email_data.get("from", "").lower()

        # Initialize result
        result = {
            "status": "Pending Review",
            "priority": "Medium",
            "category": "General",
            "action_required": False,
            "notes": ""
        }

        # Priority detection
        urgent_keywords = ["urgent", "asap", "immediately", "critical", "emergency"]
        low_priority_keywords = ["fyi", "for your information", "no rush"]

        if any(keyword in subject or keyword in body for keyword in urgent_keywords):
            result["priority"] = "High"
            result["action_required"] = True
        elif any(keyword in subject or keyword in body for keyword in low_priority_keywords):
            result["priority"] = "Low"

        # Status detection
        approval_keywords = ["approve", "approved", "approval needed", "please review"]
        completed_keywords = ["completed", "done", "finished", "closed"]
        rejected_keywords = ["rejected", "declined", "not approved"]

        if any(keyword in subject or keyword in body for keyword in approval_keywords):
            result["status"] = "Pending Approval"
            result["action_required"] = True
        elif any(keyword in subject or keyword in body for keyword in completed_keywords):
            result["status"] = "Completed"
        elif any(keyword in subject or keyword in body for keyword in rejected_keywords):
            result["status"] = "Rejected"

        # Category detection
        if any(keyword in subject or keyword in body for keyword in ["invoice", "payment", "billing"]):
            result["category"] = "Finance"
        elif any(keyword in subject or keyword in body for keyword in ["meeting", "schedule", "calendar"]):
            result["category"] = "Meeting"
        elif any(keyword in subject or keyword in body for keyword in ["report", "analytics", "data"]):
            result["category"] = "Reporting"
        elif any(keyword in subject or keyword in body for keyword in ["support", "help", "issue", "problem"]):
            result["category"] = "Support"

        # Extract reference numbers (e.g., ticket numbers, order IDs)
        reference_patterns = [
            r"#(\d+)",  # #12345
            r"ticket[:\s]+(\w+)",  # Ticket: ABC123
            r"order[:\s]+(\w+)",  # Order: ORD456
            r"ref[:\s]+(\w+)"  # Ref: REF789
        ]

        references = []
        for pattern in reference_patterns:
            matches = re.findall(pattern, subject + " " + body, re.IGNORECASE)
            references.extend(matches)

        if references:
            result["reference_id"] = references[0]

        # Generate summary note
        result["notes"] = f"Reviewed email from {from_address}. Subject: {email_data.get('subject', 'N/A')}"

        logger.info(f"Rule-based review completed: {result['status']}, {result['priority']}")
        return result

    def _ai_review(self, email_data: Dict) -> Dict:
        """
        AI-powered email review using OpenAI

        Args:
            email_data: Email data dictionary

        Returns:
            Review results dictionary
        """
        try:
            subject = email_data.get("subject", "")
            body = email_data.get("body", "")
            from_address = email_data.get("from", "")

            # Create prompt for AI
            prompt = f"""
Analyze the following email and provide a structured review:

From: {from_address}
Subject: {subject}
Body: {body[:1000]}  # Limit body length

Please provide:
1. Status (choose one: Pending Review, Pending Approval, In Progress, Completed, Rejected, On Hold)
2. Priority (choose one: Low, Medium, High, Critical)
3. Category (choose one: General, Finance, Meeting, Reporting, Support, HR, Sales, Technical)
4. Action Required (Yes/No)
5. Brief notes or summary (1-2 sentences)
6. Reference ID if any (ticket number, order ID, etc.)

Format your response as JSON with these exact keys:
status, priority, category, action_required (boolean), notes, reference_id (or null)
"""

            # Call OpenAI API
            response = self.ai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an email analysis assistant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            # Parse AI response
            import json
            result = json.loads(response.choices[0].message.content)

            logger.info(f"AI review completed: {result.get('status')}, {result.get('priority')}")
            return result

        except Exception as e:
            logger.error(f"AI review failed: {e}. Falling back to rule-based review.")
            return self._rule_based_review(email_data)

    def extract_tracking_info(self, email_data: Dict) -> Dict:
        """
        Extract tracking information from email for SharePoint updates

        Args:
            email_data: Email data dictionary

        Returns:
            Dictionary with tracking fields
        """
        return {
            "EmailSubject": email_data.get("subject", ""),
            "EmailFrom": email_data.get("from", ""),
            "EmailDate": email_data.get("date", ""),
            "EmailID": email_data.get("id", "")
        }
