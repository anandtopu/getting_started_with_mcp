"""Run the full browser host; configuration and keys stay server-side."""

import sys

from common.web_chat import main

if __name__ == "__main__":
    sys.argv = [sys.argv[0], "--port", "8766"]
    main()
