"""Allow running the validator with ``python -m configcheck``."""

import sys

from configcheck.cli import main

if __name__ == "__main__":
    sys.exit(main())
