import os
import shutil
from urllib.parse import quote
from git import Repo, GitCommandError
from dotenv import load_dotenv
import requests

load_dotenv()

GITHUB_USER = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPO_NAME")
REPO_FULL_NAME = os.getenv("GITHUB_REPO_FULL_NAME")

def get_authenticated_url():
    encoded_user = quote(GITHUB_USER, safe='')
    encoded_token = quote(GITHUB_TOKEN, safe='')
    return f"https://{encoded_user}:{encoded_token}@github.com/{GITHUB_USER}/{REPO_NAME}.git"

def clone_repo(local_dir="repo"):
    if os.path.exists(local_dir):
        print(f"⚠️ Repo folder {local_dir} already exists. Deleting...")
        shutil.rmtree(local_dir)

    auth_url = get_authenticated_url()
    print(f"🔄 Cloning repository from {auth_url}...")
    return Repo.clone_from(auth_url, local_dir)

def create_branch(repo_path="repo", branch_name="gradle-migration"):
    repo = Repo(repo_path)
    print(f"🌿 Checking out or creating branch {branch_name}...")

    origin = repo.remote("origin")
    origin.fetch()

    if f"origin/{branch_name}" in repo.refs:
        print(f"🔁 Branch {branch_name} exists remotely. Checking out and rebasing...")
        repo.git.checkout("-B", branch_name, f"origin/{branch_name}")
        try:
            repo.git.pull("--rebase", "origin", branch_name)
        except GitCommandError as e:
            print(f"⚠️ Rebase failed: {e.stderr or str(e)}")
    else:
        print(f"🌱 Branch {branch_name} does not exist remotely. Creating it...")
        repo.git.checkout("-b", branch_name)

    # Set upstream
    try:
        repo.git.push("--set-upstream", "origin", branch_name)
        print(f"✅ Upstream set: origin/{branch_name}")
    except GitCommandError as e:
        print(f"⚠️ Failed to set upstream: {e.stderr or str(e)}")
        
def commit_and_push(repo_path, branch_name, commit_message, files_to_commit=None):
    repo = Repo(repo_path)
    
    # Normalize file paths
    full_paths = []
    if files_to_commit:
        for f in files_to_commit:
            full_path = f if os.path.isabs(f) else os.path.join(repo_path, f)
            if os.path.exists(full_path):
                full_paths.append(full_path)
            else:
                print(f"⚠️ File not found: {full_path}")

    if not full_paths:
        print("⚠️ No valid files to commit.")
        return
    for f in full_paths:
        print(f"🔍 Checking if file exists: {f} -> {os.path.exists(f)}")    
    
    relative_paths = [os.path.relpath(p, start=repo_path) for p in full_paths]
    repo.index.add(relative_paths)
    repo.index.commit(commit_message)

    try:
        repo.remote().set_url(get_authenticated_url())
        print("🔄 Pulling with rebase...")
        repo.git.pull("--rebase")
        print("📤 Pushing branch...")
        repo.git.push("origin", branch_name)
        print("✅ Changes committed and pushed.")
    except GitCommandError as e:
        print(f"⚠️ Push failed: \n  stderr: '{e.stderr or str(e)}'")

def pull_request_exists(branch, base="main"):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    url = f"https://api.github.com/repos/{REPO_FULL_NAME}/pulls"
    params = {"head": f"{GITHUB_USER}:{branch}", "base": base}
    print("🔍 Checking if PR already exists...")
    response = requests.get(url, headers=headers, params=params)
    if response.ok:
        prs = response.json()
        if prs:
            print(f"ℹ️ Pull request already exists: {prs[0]['html_url']}")
            return True
    return False

def create_pull_request(branch, base, title, body):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    url = f"https://api.github.com/repos/{REPO_FULL_NAME}/pulls"
    payload = {
        "title": title,
        "head": branch,
        "base": base,
        "body": body
    }
    print("📬 Creating Pull Request...")
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print(f"✅ Pull Request created: {response.json().get('html_url')}")
    else:
        print(f"❌ Failed to create PR: {response.status_code} {response.text}")