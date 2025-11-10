import subprocess
import os
import logging

logger = logging.getLogger(__name__)

def generate_git_patch(repo_url: str, commit_hash: str, output_path: str) -> None:
    try:
        temp_dir = f"/tmp/git_clone_{commit_hash}"
        
        if os.path.exists(temp_dir):
            subprocess.run(['rm', '-rf', temp_dir], check=True)
        
        logger.info(f"Cloning repository: {repo_url}")
        subprocess.run(['git', 'clone', repo_url, temp_dir], check=True, capture_output=True, text=True)
        
        logger.info(f"Generating patch for commit: {commit_hash}")
        result = subprocess.run(
            ['git', 'show', commit_hash],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.stdout)
        
        subprocess.run(['rm', '-rf', temp_dir], check=True)
        
        logger.info(f"Patch saved to: {output_path}")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e.stderr if e.stderr else str(e)}")
        raise Exception(f"Failed to generate Git patch: {e.stderr if e.stderr else str(e)}")
    except Exception as e:
        logger.error(f"Error generating Git patch: {str(e)}")
        raise

def generate_svn_patch(repo_url: str, revision: str, output_path: str) -> None:
    try:
        logger.info(f"Generating SVN patch for revision: {revision}")
        result = subprocess.run(
            ['svn', 'diff', '-c', revision, repo_url],
            capture_output=True,
            text=True,
            check=True
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.stdout)
        
        logger.info(f"SVN patch saved to: {output_path}")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"SVN command failed: {e.stderr if e.stderr else str(e)}")
        raise Exception(f"Failed to generate SVN patch: {e.stderr if e.stderr else str(e)}")
    except Exception as e:
        logger.error(f"Error generating SVN patch: {str(e)}")
        raise
