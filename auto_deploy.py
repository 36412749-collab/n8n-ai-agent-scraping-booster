#!/usr/bin/env python3
"""
Master Python Automation Deployment Script
Initializes git, sets remote, and pushes n8n workflow templates to GitHub.
"""

import os
import subprocess
import sys

REPO_URL = "https://github.com/36412749-collab/n8n-ai-agent-scraping-booster.git"
BRANCH = "main"
COMMIT_MSG = "Deploy production-ready elite n8n workflows and proxy automation tools"


def run(cmd: list[str], check: bool = True, env: dict | None = None) -> subprocess.CompletedProcess:
    print(f"[RUN] {' '.join(cmd)}")
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__)),
        env=merged_env,
    )
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())
    if check and result.returncode != 0:
        print(f"[ERROR] Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    return result


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    print(f"[INFO] Working directory: {base_dir}")

    git_dir = os.path.join(base_dir, ".git")
    if not os.path.isdir(git_dir):
        print("[INFO] No .git found — initializing repository...")
        run(["git", "init"])
        run(["git", "branch", "-M", BRANCH])
    else:
        print("[INFO] Existing .git repository detected.")

    remote_check = run(["git", "remote", "get-url", "origin"], check=False)
    if remote_check.returncode != 0:
        print(f"[INFO] Adding remote origin: {REPO_URL}")
        run(["git", "remote", "add", "origin", REPO_URL])
    else:
        current_url = remote_check.stdout.strip()
        if current_url != REPO_URL:
            print(f"[INFO] Updating remote origin: {current_url} -> {REPO_URL}")
            run(["git", "remote", "set-url", "origin", REPO_URL])
        else:
            print(f"[INFO] Remote origin already set: {REPO_URL}")

    run(["git", "branch", "-M", BRANCH])

    run(["git", "add", "."])

    status = run(["git", "status", "--porcelain"], check=False)
    if not status.stdout.strip():
        print("[INFO] Nothing to commit — working tree clean.")
    else:
        git_identity = {
            "GIT_AUTHOR_NAME": "36412749-collab",
            "GIT_AUTHOR_EMAIL": "36412749-collab@users.noreply.github.com",
            "GIT_COMMITTER_NAME": "36412749-collab",
            "GIT_COMMITTER_EMAIL": "36412749-collab@users.noreply.github.com",
        }
        run(["git", "commit", "-m", COMMIT_MSG], env=git_identity)

    print(f"[INFO] Pushing to origin/{BRANCH}...")
    push_result = run(["git", "push", "-u", "origin", BRANCH], check=False)
    if push_result.returncode != 0:
        print("[WARN] Standard push failed — attempting force-with-lease for initial deploy...")
        push_result = run(["git", "push", "-u", "origin", BRANCH, "--force-with-lease"], check=False)
        if push_result.returncode != 0:
            print("[ERROR] Push failed. Ensure GitHub credentials are configured.")
            sys.exit(1)

    print("[SUCCESS] Deployment complete.")
    print(f"[SUCCESS] Repository: {REPO_URL}")


if __name__ == "__main__":
    main()
