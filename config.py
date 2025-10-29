import os

# Read credentials from environment variables for security.
# Configure these via systemd EnvironmentFile or your shell.
FROLING_USERNAME = os.getenv("FROLING_USERNAME")
FROLING_PASSWORD = os.getenv("FROLING_PASSWORD")

if not FROLING_USERNAME or not FROLING_PASSWORD:
    raise RuntimeError(
        "FROLING_USERNAME and FROLING_PASSWORD must be set as environment variables"
    )