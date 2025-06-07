import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI & GitHub credentials (must be set in .env)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# GitHub repository info
REPO_OWNER = os.getenv("GITHUB_REPO_OWNER", "KalyanCB")
REPO_NAME = os.getenv("GITHUB_REPO_NAME", "M2GExample")
REPO_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}.git"
REPO_FULL_NAME = f"{REPO_OWNER}/{REPO_NAME}"

# Branch configuration
FEATURE_BRANCH = os.getenv("FEATURE_BRANCH_NAME", "gradle-migration")
BASE_BRANCH = os.getenv("BASE_BRANCH_NAME", "main")