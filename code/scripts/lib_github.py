#!/usr/bin/env python3.12
import os
import json
import requests
from dotenv import load_dotenv
from logger import logger

load_dotenv()


# from https://github.com/user/settings/tokens
GH_USER = os.getenv('GH_USER')
GH_TOKEN = os.getenv('GH_TOKEN')


gh = requests.Session()
gh.auth = (GH_USER, GH_TOKEN)
base_url = "https://api.github.com"


def get_recent_user_activity(username):
    return requests.get(f"{base_url}/users/{username}/events/public?per_page=100").json()


def get_recent_repo_activity(org, repo):
    return requests.get(f"{base_url}/repos/{org}/{repo}/events?per_page=100").json()


def summarise_activity_by_repo(activity=None):
    summary = {}
    for event in activity:
        event_type = event["type"]
        repo = event["repo"]["name"]


def check_release_exists(org, repo, release_name):
    r = gh.get(f"{base_url}/repos/{org}/{repo}/releases").json()
    for release in r:
        if release["name"] == release_name:
            status_logger.info(f"A release with the name '{release_name}' already exists at {release['html_url']}!")
            return True
    return False


# https://docs.github.com/en/rest/reference/releases#create-a-release
def create_release(owner, repo, data):
    url = f"{base_url}/repos/{owner}/{repo}/releases"
    r = gh.post(url, data=data)
    if 'html_url' in r.json():
        success_logger.info(f"Draft release created at {r.json()['html_url']}")
    else:
        error_logger.info("Error creating release!")
        error_logger.info(data)
        error_logger.info(r.json())


def get_run_branch(run_url):
    r = requests.get(f"{run_url}")
    if 'head_branch' in r.json():
        return r.json()['head_branch']
    return None

def get_github_folder_contents(owner, repo, path, branch=None):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    if branch:
        url += f"?ref={branch}"
    r = gh.get(url)
    return r.json()
    