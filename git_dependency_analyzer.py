import os
import re
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Set, Tuple, Optional
import git
from git import Repo, InvalidGitRepositoryError

logger = logging.getLogger(__name__)

class GitAnalyzer:
    """Class to analyze Git repositories and detect commit dependencies."""
    
    def __init__(self, repo_path: str):
        """Initialize the GitAnalyzer with a repository path."""
        self.repo_path = repo_path
        self.repo = None
        
    def is_valid_repo(self) -> bool:
        """Check if the given path is a valid Git repository."""
        try:
            self.repo = Repo(self.repo_path)
            return not self.repo.bare
        except (InvalidGitRepositoryError, git.GitError):
            return False
        except Exception as e:
            logger.error(f"Error checking repository validity: {str(e)}")
            return False
    
    def get_branches(self) -> List[str]:
        """Get all branches from the repository."""
        if not self.repo:
            self.repo = Repo(self.repo_path)
        
        branches = []
        
        # Get local branches
        for branch in self.repo.heads:
            branches.append(branch.name)
        
        # Get remote branches
        for remote in self.repo.remotes:
            for ref in remote.refs:
                branch_name = f"{remote.name}/{ref.remote_head}"
                if branch_name not in branches:
                    branches.append(branch_name)
        
        return sorted(branches)
    
    def get_commits_in_range(self, branch: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get all commits in the specified branch and date range."""
        if not self.repo:
            self.repo = Repo(self.repo_path)
        
        commits = []
        
        try:
            # Handle remote branches
            if "/" in branch and branch not in [h.name for h in self.repo.heads]:
                # This is a remote branch
                branch_ref = branch
            else:
                branch_ref = branch
            
            # Get commits in date range
            commit_iter = self.repo.iter_commits(
                rev=branch_ref,
                since=start_date,
                until=end_date + timedelta(days=1)  # Include end date
            )
            
            for commit in commit_iter:
                commit_date = datetime.fromtimestamp(commit.committed_date)
                if start_date <= commit_date <= end_date + timedelta(days=1):
                    commits.append({
                        "hash": commit.hexsha[:8],
                        "full_hash": commit.hexsha,
                        "author": commit.author.name,
                        "date": commit_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "message": commit.message.strip()
                    })
            
            # Sort by date (newest first)
            commits.sort(key=lambda x: x["date"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting commits: {str(e)}")
            raise
        
        return commits
    
    def get_commit_file_changes(self, commit_hash: str) -> Dict[str, List[Tuple[int, int]]]:
        """Get file changes and line ranges for a specific commit."""
        if not self.repo:
            self.repo = Repo(self.repo_path)
        
        try:
            commit = self.repo.commit(commit_hash)
            file_changes = {}
            
            if commit.parents:
                # Compare with parent commit
                parent = commit.parents[0]
                diffs = parent.diff(commit, create_patch=True)
                
                for diff in diffs:
                    if diff.a_path:
                        file_path = diff.a_path
                        if file_path not in file_changes:
                            file_changes[file_path] = []
                        
                        # Parse diff to get line numbers
                        if diff.diff:
                            diff_text = diff.diff.decode('utf-8', errors='ignore') if isinstance(diff.diff, bytes) else str(diff.diff)
                            line_ranges = self._parse_diff_line_numbers(diff_text)
                            file_changes[file_path].extend(line_ranges)
                    
                    if diff.b_path and diff.b_path != diff.a_path:
                        file_path = diff.b_path
                        if file_path not in file_changes:
                            file_changes[file_path] = []
                        
                        # Parse diff to get line numbers
                        if diff.diff:
                            diff_text = diff.diff.decode('utf-8', errors='ignore') if isinstance(diff.diff, bytes) else str(diff.diff)
                            line_ranges = self._parse_diff_line_numbers(diff_text)
                            file_changes[file_path].extend(line_ranges)
            
            return file_changes
            
        except Exception as e:
            logger.error(f"Error getting file changes for commit {commit_hash}: {str(e)}")
            return {}
    
    def _parse_diff_line_numbers(self, diff_text: str) -> List[Tuple[int, int]]:
        """Parse diff text to extract line number ranges."""
        line_ranges = []
        
        # Regular expression to match diff headers like @@ -1,4 +1,6 @@
        hunk_pattern = r'@@\s*-(\d+)(?:,(\d+))?\s*\+(\d+)(?:,(\d+))?\s*@@'
        
        for match in re.finditer(hunk_pattern, diff_text):
            old_start = int(match.group(1))
            old_count = int(match.group(2)) if match.group(2) else 1
            new_start = int(match.group(3))
            new_count = int(match.group(4)) if match.group(4) else 1
            
            # Add both old and new line ranges
            line_ranges.append((old_start, old_start + old_count - 1))
            line_ranges.append((new_start, new_start + new_count - 1))
        
        return line_ranges
    
    def analyze_dependencies(self, branch: str, target_commit_hash: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Analyze dependencies for a target commit by comparing file and line overlaps."""
        if not self.repo:
            self.repo = Repo(self.repo_path)
        
        dependencies = []
        
        try:
            # Get all commits in the date range
            all_commits = self.get_commits_in_range(branch, start_date, end_date)
            
            # Get target commit changes
            target_changes = self.get_commit_file_changes(target_commit_hash)
            
            if not target_changes:
                logger.info(f"No file changes found for target commit {target_commit_hash}")
                return dependencies
            
            # Find the target commit in the list
            target_commit = None
            target_commit_date: Optional[datetime] = None
            for commit in all_commits:
                if commit["full_hash"] == target_commit_hash or commit["hash"] == target_commit_hash:
                    target_commit = commit
                    target_commit_date = datetime.strptime(commit["date"], "%Y-%m-%d %H:%M:%S")
                    break
            
            if not target_commit:
                logger.error(f"Target commit {target_commit_hash} not found in commit list")
                return dependencies
            
            # Check each earlier commit for dependencies
            for commit in all_commits:
                commit_date = datetime.strptime(commit["date"], "%Y-%m-%d %H:%M:%S")
                
                # Only check commits that are earlier than the target commit
                if target_commit_date is None or commit_date >= target_commit_date:
                    continue
                
                commit_changes = self.get_commit_file_changes(commit["full_hash"])
                
                # Check for file and line overlaps
                overlap_info = self._check_overlap(target_changes, commit_changes)
                
                if overlap_info["has_overlap"]:
                    dependencies.append({
                        "hash": commit["hash"],
                        "full_hash": commit["full_hash"],
                        "author": commit["author"],
                        "date": commit["date"],
                        "message": commit["message"],
                        "overlap_files": overlap_info["overlap_files"],
                        "overlap_count": overlap_info["overlap_count"]
                    })
            
            # Sort dependencies by date (newest first)
            dependencies.sort(key=lambda x: x["date"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error analyzing dependencies: {str(e)}")
            raise
        
        return dependencies
    
    def _check_overlap(self, target_changes: Dict[str, List[Tuple[int, int]]], 
                      commit_changes: Dict[str, List[Tuple[int, int]]]) -> Dict[str, Any]:
        """Check if there's any overlap between two sets of file changes."""
        overlap_files = []
        overlap_count = 0
        
        # Check for file overlaps
        common_files = set(target_changes.keys()) & set(commit_changes.keys())
        
        for file_path in common_files:
            target_lines = target_changes[file_path]
            commit_lines = commit_changes[file_path]
            
            # Check for line range overlaps
            file_has_overlap = False
            for target_start, target_end in target_lines:
                for commit_start, commit_end in commit_lines:
                    if self._ranges_overlap(target_start, target_end, commit_start, commit_end):
                        file_has_overlap = True
                        overlap_count += 1
                        break
                if file_has_overlap:
                    break
            
            if file_has_overlap:
                overlap_files.append(file_path)
        
        return {
            "has_overlap": len(overlap_files) > 0,
            "overlap_files": overlap_files,
            "overlap_count": overlap_count
        }
    
    def _ranges_overlap(self, start1: int, end1: int, start2: int, end2: int) -> bool:
        """Check if two line ranges overlap."""
        return start1 <= end2 and start2 <= end1
