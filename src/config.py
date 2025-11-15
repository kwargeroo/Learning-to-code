"""Configuration management for the agent"""

import os
import json
from typing import Dict, Optional
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for loading and validating settings"""

    def __init__(self, config_file: Optional[str] = None, use_env: bool = True):
        """
        Initialize configuration

        Args:
            config_file: Path to JSON config file (optional)
            use_env: Whether to load from environment variables (default: True)
        """
        self.config_file = config_file
        self.use_env = use_env
        self.config = {}

        if use_env:
            load_dotenv()

    def load(self) -> Dict:
        """
        Load configuration from file and/or environment variables

        Returns:
            Configuration dictionary
        """
        # Start with defaults
        self.config = self._get_defaults()

        # Load from file if provided
        if self.config_file:
            self._load_from_file()

        # Override with environment variables if enabled
        if self.use_env:
            self._load_from_env()

        # Validate configuration
        self._validate()

        logger.info("Configuration loaded successfully")
        return self.config

    def _get_defaults(self) -> Dict:
        """Get default configuration"""
        return {
            "email": {
                "server": "imap.gmail.com",
                "port": 993,
                "folder": "INBOX",
                "unread_only": True
            },
            "review": {
                "use_ai": False
            },
            "agent": {
                "mark_as_read": True,
                "email_limit": 10
            }
        }

    def _load_from_file(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                file_config = json.load(f)

            # Merge with existing config
            self._deep_merge(self.config, file_config)
            logger.info(f"Loaded configuration from {self.config_file}")

        except FileNotFoundError:
            logger.warning(f"Config file not found: {self.config_file}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
        except Exception as e:
            logger.error(f"Error loading config file: {e}")

    def _load_from_env(self):
        """Load configuration from environment variables"""
        # Email configuration
        if os.getenv("EMAIL_SERVER"):
            self.config["email"]["server"] = os.getenv("EMAIL_SERVER")
        if os.getenv("EMAIL_ADDRESS"):
            self.config["email"]["address"] = os.getenv("EMAIL_ADDRESS")
        if os.getenv("EMAIL_PASSWORD"):
            self.config["email"]["password"] = os.getenv("EMAIL_PASSWORD")
        if os.getenv("EMAIL_PORT"):
            self.config["email"]["port"] = int(os.getenv("EMAIL_PORT"))

        # SharePoint configuration
        self.config.setdefault("sharepoint", {})
        if os.getenv("SHAREPOINT_TENANT_ID"):
            self.config["sharepoint"]["tenant_id"] = os.getenv("SHAREPOINT_TENANT_ID")
        if os.getenv("SHAREPOINT_CLIENT_ID"):
            self.config["sharepoint"]["client_id"] = os.getenv("SHAREPOINT_CLIENT_ID")
        if os.getenv("SHAREPOINT_CLIENT_SECRET"):
            self.config["sharepoint"]["client_secret"] = os.getenv("SHAREPOINT_CLIENT_SECRET")
        if os.getenv("SHAREPOINT_SITE_NAME"):
            self.config["sharepoint"]["site_name"] = os.getenv("SHAREPOINT_SITE_NAME")
        if os.getenv("SHAREPOINT_SITE_ID"):
            self.config["sharepoint"]["site_id"] = os.getenv("SHAREPOINT_SITE_ID")
        if os.getenv("SHAREPOINT_LIST_NAME"):
            self.config["sharepoint"]["list_name"] = os.getenv("SHAREPOINT_LIST_NAME")
        if os.getenv("SHAREPOINT_LIST_ID"):
            self.config["sharepoint"]["list_id"] = os.getenv("SHAREPOINT_LIST_ID")

        # Review configuration
        if os.getenv("REVIEW_USE_AI"):
            self.config["review"]["use_ai"] = os.getenv("REVIEW_USE_AI").lower() == "true"
        if os.getenv("OPENAI_API_KEY"):
            self.config["review"]["openai_api_key"] = os.getenv("OPENAI_API_KEY")

        logger.info("Loaded configuration from environment variables")

    def _deep_merge(self, base: Dict, update: Dict):
        """Deep merge update dictionary into base dictionary"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _validate(self):
        """Validate required configuration"""
        required_fields = [
            ("email", "address"),
            ("email", "password"),
            ("sharepoint", "tenant_id"),
            ("sharepoint", "client_id"),
            ("sharepoint", "client_secret")
        ]

        missing = []
        for section, field in required_fields:
            if section not in self.config or field not in self.config[section]:
                missing.append(f"{section}.{field}")

        if missing:
            raise ValueError(f"Missing required configuration fields: {', '.join(missing)}")

        # Validate that either site_name or site_id is provided
        sp_config = self.config.get("sharepoint", {})
        if not sp_config.get("site_name") and not sp_config.get("site_id"):
            raise ValueError("Either sharepoint.site_name or sharepoint.site_id must be provided")

        # Validate that either list_name or list_id is provided
        if not sp_config.get("list_name") and not sp_config.get("list_id"):
            raise ValueError("Either sharepoint.list_name or sharepoint.list_id must be provided")

    def get(self) -> Dict:
        """Get the configuration dictionary"""
        return self.config
