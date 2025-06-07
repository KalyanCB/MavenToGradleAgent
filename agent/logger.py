# agent/logger.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
def log_success(message):
    print(f"✅ {message}")

logger = logging.getLogger(__name__)