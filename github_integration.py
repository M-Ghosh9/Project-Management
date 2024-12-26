from github import Github
from github.GithubException import GithubException

def log_issue_to_github(token, repo_name, title, description, priority):
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        issue_title = f"[{priority}] {title}"
        issue_body = description
        repo.create_issue(title=issue_title, body=issue_body)
    except GithubException as e:
        raise Exception(f"GitHub error: {e.data.get('message', str(e))}")
    except Exception as e:
        raise Exception(f"Failed to log issue: {str(e)}")
