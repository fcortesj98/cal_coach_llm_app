"""Entry point: `python app.py` serves the AI Nutrition Coach on port 5000."""

from __future__ import annotations

import argparse
import logging

from nutrition_coach import create_app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the AI Nutrition Coach web app.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--debug", action="store_true", help="Enable Flask debug mode")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    args = parse_args()
    create_app().run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
