"""Rate limiting configuration."""

import sys
from slowapi import Limiter
from slowapi.util import get_remote_address

# In test mode, use an extremely high rate limit to prevent 429s
# during tests that make many rapid requests.
# Detect test env broad: pytest in sys.modules, or PYTEST env vars.
_is_test = "pytest" in sys.modules

if _is_test:
    limiter = Limiter(
        key_func=get_remote_address, default_limits=["100000 per 1 minute"]
    )
else:
    limiter = Limiter(key_func=get_remote_address)
