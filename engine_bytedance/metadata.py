"""Identity constants. Standard library only.

The TUI imports this module, not ``engine.py``, so reading the provider's
display name never pulls in the provider's SDK.
"""

PROVIDER_NAME = "BytePlus"
PROVIDER_HOMEPAGE = "https://www.byteplus.com"
PLATFORM = "bytedance"
API_KEY_ENV_VAR = "ARK_API_KEY"
API_KEY_PATTERN = r".+"
