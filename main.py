#!/usr/bin/env python3
"""Main entry point for the Email Review SharePoint Agent"""

import sys
import argparse
import logging
from src.config import Config
from src.agent import EmailReviewSharePointAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Email Review SharePoint Agent - Automatically review emails and update SharePoint"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to JSON configuration file"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of emails to process (default: 10)"
    )
    parser.add_argument(
        "--no-env",
        action="store_true",
        help="Don't load configuration from environment variables"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Load configuration
        logger.info("Loading configuration...")
        config_manager = Config(
            config_file=args.config,
            use_env=not args.no_env
        )
        config = config_manager.load()

        # Create and run agent
        logger.info("Starting Email Review SharePoint Agent...")
        agent = EmailReviewSharePointAgent(config)
        result = agent.run(limit=args.limit)

        # Print results
        if result["success"]:
            logger.info(f"✓ Agent completed successfully!")
            logger.info(f"  Processed {result['processed']} emails")
            return 0
        else:
            logger.error(f"✗ Agent failed")
            for error in result["errors"]:
                logger.error(f"  - {error}")
            return 1

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except KeyboardInterrupt:
        logger.info("\nAgent stopped by user")
        return 0
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
