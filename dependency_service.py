import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from git_dependency_analyzer import GitAnalyzer
import json

logger = logging.getLogger(__name__)

class DependencyService:
    """Service layer for Git dependency analysis."""
    
    @staticmethod
    def _make_json_serializable(obj: Any) -> Any:
        """
        Recursively convert data structures to be JSON serializable.
        Converts tuples to lists and handles nested structures.
        """
        if isinstance(obj, dict):
            return {key: DependencyService._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [DependencyService._make_json_serializable(item) for item in obj]
        elif isinstance(obj, tuple):
            return [DependencyService._make_json_serializable(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            return str(obj)
    
    @staticmethod
    def validate_and_analyze(repo_path: str, branch: str, target_commit: str, 
                            start_date: Optional[str] = None, 
                            end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate inputs and perform dependency analysis.
        
        Returns:
            Dictionary with 'success', 'data', and 'error' keys
        """
        try:
            analyzer = GitAnalyzer(repo_path)
            
            if not analyzer.is_valid_repo():
                return {
                    'success': False,
                    'error': f'Invalid Git repository path: {repo_path}',
                    'data': None
                }
            
            branches = analyzer.get_branches()
            if not branches:
                return {
                    'success': False,
                    'error': 'No branches found in repository',
                    'data': None
                }
            
            if branch not in branches:
                return {
                    'success': False,
                    'error': f'Branch "{branch}" not found. Available branches: {", ".join(branches[:5])}',
                    'data': None
                }
            
            if start_date and end_date:
                try:
                    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                except ValueError as e:
                    return {
                        'success': False,
                        'error': f'Invalid date format. Use YYYY-MM-DD: {str(e)}',
                        'data': None
                    }
            else:
                end_dt = datetime.now()
                start_dt = end_dt - timedelta(days=30)
            
            dependencies = analyzer.analyze_dependencies(
                branch=branch,
                target_commit_hash=target_commit,
                start_date=start_dt,
                end_date=end_dt
            )
            
            commits = analyzer.get_commits_in_range(branch, start_dt, end_dt)
            target_changes = analyzer.get_commit_file_changes(target_commit)
            
            data = {
                'dependencies': dependencies,
                'total_dependencies': len(dependencies),
                'target_commit': target_commit,
                'branch': branch,
                'date_range': {
                    'start': start_dt.strftime("%Y-%m-%d"),
                    'end': end_dt.strftime("%Y-%m-%d")
                },
                'total_commits': len(commits),
                'target_files_changed': len(target_changes),
                'target_file_list': list(target_changes.keys())
            }
            
            serializable_data = DependencyService._make_json_serializable(data)
            
            try:
                json.dumps(serializable_data)
            except (TypeError, ValueError) as e:
                logger.error(f"Data serialization test failed: {str(e)}")
                raise ValueError(f"Analysis results contain non-serializable data: {str(e)}")
            
            return {
                'success': True,
                'error': None,
                'data': serializable_data
            }
            
        except Exception as e:
            logger.error(f"Error in dependency analysis: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f'Analysis error: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def get_repository_info(repo_path: str) -> Dict[str, Any]:
        """
        Get basic repository information (branches, recent commits).
        
        Returns:
            Dictionary with 'success', 'data', and 'error' keys
        """
        try:
            analyzer = GitAnalyzer(repo_path)
            
            if not analyzer.is_valid_repo():
                return {
                    'success': False,
                    'error': f'Invalid Git repository path: {repo_path}',
                    'data': None
                }
            
            branches = analyzer.get_branches()
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            recent_commits = []
            
            if branches:
                try:
                    recent_commits = analyzer.get_commits_in_range(
                        branches[0], start_date, end_date
                    )[:10]
                except:
                    pass
            
            return {
                'success': True,
                'error': None,
                'data': {
                    'branches': branches,
                    'recent_commits': recent_commits,
                    'default_branch': branches[0] if branches else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting repository info: {str(e)}")
            return {
                'success': False,
                'error': f'Repository error: {str(e)}',
                'data': None
            }
