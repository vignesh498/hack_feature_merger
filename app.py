from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
import json
import logging
from dependency_service import DependencyService
from vcs_handler import generate_git_patch, generate_svn_patch
from document_processor import extract_text_from_file
from gemini_helper import analyze_brd_and_patch
import dotenv
dotenv.load_dotenv()
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['GENERATED_FOLDER'] = 'generated'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

WORKFLOW_STAGES = [
    'Dependency Analyzer',
    'Patch Generation',
    'AI Analysis',
    'Merging',
    'Unit Testing',
    'Release Documentation'
]

class Feature(db.Model):
    __tablename__ = 'features'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text)
    current_stage = db.Column(db.String(50), default='Dependency Analyzer')
    stage_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    file_path = db.Column(db.String(500))
    stage_data = db.Column(db.Text, default='{}')
    
    commit_id = db.Column(db.String(100))
    patch_file_path = db.Column(db.String(500))
    analysis_file_path = db.Column(db.String(500))
    
    def __repr__(self):
        return f'<Feature {self.name}>'
    
    def get_stage_data(self):
        try:
            return json.loads(self.stage_data or '{}')
        except Exception as e:
            logging.error(f"Error parsing stage_data for feature {self.id}: {str(e)}")
            return {}
    
    def set_stage_data(self, data):
        try:
            self.stage_data = json.dumps(data)
        except (TypeError, ValueError) as e:
            logging.error(f"Error serializing stage_data for feature {self.id}: {str(e)}")
            logging.error(f"Attempted to serialize: {data}")
            raise ValueError(f"Cannot serialize stage data: {str(e)}")

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    features = Feature.query.order_by(Feature.updated_at.desc()).all()
    return render_template('index.html', features=features, stages=WORKFLOW_STAGES)

@app.route('/feature/create', methods=['GET', 'POST'])
def create_feature():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Feature name is required!', 'error')
            return redirect(url_for('create_feature'))
        
        existing = Feature.query.filter_by(name=name).first()
        if existing:
            flash('A feature with this name already exists!', 'error')
            return redirect(url_for('create_feature'))
        
        file = request.files.get('file')
        file_path = None
        
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}")
            file.save(file_path)
        
        feature = Feature(
            name=name,
            description=description,
            file_path=file_path,
            current_stage=WORKFLOW_STAGES[0],
            stage_index=0
        )
        
        db.session.add(feature)
        db.session.commit()
        
        flash(f'Feature "{name}" created successfully!', 'success')
        return redirect(url_for('workflow', feature_id=feature.id))
    
    return render_template('create_feature.html')

@app.route('/feature/<int:feature_id>/workflow')
def workflow(feature_id):
    feature = Feature.query.get_or_404(feature_id)
    stage_data = feature.get_stage_data()
    
    return render_template('workflow.html', 
                         feature=feature, 
                         stages=WORKFLOW_STAGES,
                         stage_data=stage_data)

@app.route('/feature/<int:feature_id>/stage/<int:stage_index>', methods=['GET', 'POST'])
def process_stage(feature_id, stage_index):
    feature = Feature.query.get_or_404(feature_id)
    
    if stage_index < 0 or stage_index >= len(WORKFLOW_STAGES):
        flash('Invalid stage!', 'error')
        return redirect(url_for('workflow', feature_id=feature_id))
    
    stage_name = WORKFLOW_STAGES[stage_index]
    stage_data = feature.get_stage_data()
    analysis_result = None
    repo_info = None
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'analyze' and stage_name == 'Dependency Analyzer':
            repo_path = request.form.get('repo_path', '').strip()
            branch = request.form.get('branch', '').strip()
            target_commit = request.form.get('target_commit', '').strip()
            start_date = request.form.get('start_date', '').strip()
            end_date = request.form.get('end_date', '').strip()
            
            if not repo_path:
                flash('Repository path is required!', 'error')
            elif not branch:
                flash('Branch name is required!', 'error')
            elif not target_commit:
                flash('Target commit hash is required!', 'error')
            else:
                result = DependencyService.validate_and_analyze(
                    repo_path=repo_path,
                    branch=branch,
                    target_commit=target_commit,
                    start_date=start_date if start_date else None,
                    end_date=end_date if end_date else None
                )
                
                if result['success']:
                    analysis_result = result['data']
                    stage_data[stage_name] = {
                        'completed': False,
                        'timestamp': datetime.utcnow().isoformat(),
                        'repo_path': repo_path,
                        'branch': branch,
                        'target_commit': target_commit,
                        'start_date': start_date,
                        'end_date': end_date,
                        'analysis': analysis_result
                    }
                    feature.set_stage_data(stage_data)
                    db.session.commit()
                    flash(f'Analysis complete! Found {analysis_result["total_dependencies"]} dependencies.', 'success')
                else:
                    flash(result['error'], 'error')
        
        elif action == 'generate_patch' and stage_name == 'Patch Generation':
            vcs_type = request.form.get('vcs_type', '').strip()
            repo_url = request.form.get('repo_url', '').strip()
            commit_hash = request.form.get('commit_hash', '').strip()
            
            if not vcs_type or not repo_url or not commit_hash:
                flash('All fields are required for patch generation!', 'error')
            else:
                try:
                    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                    patch_filename = f"{feature.name.replace(' ', '_')}_{timestamp}.patch"
                    patch_path = os.path.join(app.config['GENERATED_FOLDER'], patch_filename)
                    
                    if vcs_type == 'git':
                        generate_git_patch(repo_url, commit_hash, patch_path)
                    elif vcs_type == 'svn':
                        generate_svn_patch(repo_url, commit_hash, patch_path)
                    else:
                        flash('Invalid VCS type!', 'error')
                        return render_template('stage.html', 
                                             feature=feature, 
                                             stage_name=stage_name,
                                             stage_index=stage_index,
                                             stage_content=get_stage_content(stage_name, feature),
                                             stage_data=stage_data.get(stage_name, {}),
                                             total_stages=len(WORKFLOW_STAGES))
                    
                    stage_data[stage_name] = {
                        'completed': False,
                        'timestamp': datetime.utcnow().isoformat(),
                        'vcs_type': vcs_type,
                        'repo_url': repo_url,
                        'commit_hash': commit_hash,
                        'patch_file': patch_path,
                        'patch_filename': patch_filename
                    }
                    feature.set_stage_data(stage_data)
                    
                    feature.commit_id = commit_hash
                    feature.patch_file_path = patch_path
                    
                    db.session.commit()
                    flash(f'Patch generated successfully: {patch_filename}', 'success')
                    
                except Exception as e:
                    logging.error(f"Error generating patch: {str(e)}")
                    flash(f'Error generating patch: {str(e)}', 'error')
        
        elif action == 'analyze_ai' and stage_name == 'AI Analysis':
            if 'brd_file' not in request.files:
                flash('Please upload a BRD/User Story document!', 'error')
            else:
                brd_file = request.files['brd_file']
                
                if not brd_file.filename:
                    flash('No file selected!', 'error')
                else:
                    try:
                        patch_generation_data = stage_data.get('Patch Generation', {})
                        patch_file_path = patch_generation_data.get('patch_file')
                        
                        if not patch_file_path or not os.path.exists(patch_file_path):
                            flash('No patch file found. Please complete Patch Generation stage first!', 'error')
                        else:
                            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                            brd_filename = secure_filename(brd_file.filename)
                            brd_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{brd_filename}")
                            brd_file.save(brd_path)
                            
                            brd_content = extract_text_from_file(brd_path)
                            
                            with open(patch_file_path, 'r', encoding='utf-8') as f:
                                patch_content = f.read()
                            
                            analysis_result = analyze_brd_and_patch(brd_content, patch_content)
                            
                            analysis_filename = f"{feature.name.replace(' ', '_')}_analysis_{timestamp}.md"
                            analysis_path = os.path.join(app.config['GENERATED_FOLDER'], analysis_filename)
                            
                            with open(analysis_path, 'w', encoding='utf-8') as f:
                                f.write(analysis_result)
                            
                            stage_data[stage_name] = {
                                'completed': False,
                                'timestamp': datetime.utcnow().isoformat(),
                                'brd_file': brd_path,
                                'brd_filename': brd_filename,
                                'patch_file': patch_file_path,
                                'analysis_file': analysis_path,
                                'analysis_filename': analysis_filename,
                                'analysis_preview': analysis_result[:500] + '...' if len(analysis_result) > 500 else analysis_result
                            }
                            feature.set_stage_data(stage_data)
                            
                            feature.analysis_file_path = analysis_path
                            
                            db.session.commit()
                            flash(f'AI Analysis completed! Saved as {analysis_filename}', 'success')
                            
                    except Exception as e:
                        logging.error(f"Error in AI analysis: {str(e)}")
                        if "GEMINI_API_KEY" in str(e):
                            flash('Gemini API key is not configured. Please add GEMINI_API_KEY to your environment secrets.', 'error')
                        else:
                            flash(f'Error during AI analysis: {str(e)}', 'error')
        
        elif action == 'manual_merge' and stage_name == 'Merging':
            patch_generation_data = stage_data.get('Patch Generation', {})
            commit_hash = patch_generation_data.get('commit_hash')
            repo_url = patch_generation_data.get('repo_url')
            vcs_type = patch_generation_data.get('vcs_type')
            
            if not commit_hash or not repo_url:
                flash('Missing commit information. Please complete Patch Generation stage first!', 'error')
            else:
                import re
                if not re.match(r'^[a-zA-Z0-9]+$', str(commit_hash)):
                    flash('Invalid commit hash format!', 'error')
                else:
                    if vcs_type == 'svn':
                        merge_command = f"svn merge -c {commit_hash} {repo_url}"
                    elif vcs_type == 'git':
                        merge_command = f"git cherry-pick {commit_hash}"
                    else:
                        merge_command = "Unsupported VCS type"
                    
                    stage_data[stage_name] = {
                        'completed': False,
                        'timestamp': datetime.utcnow().isoformat(),
                        'merge_status': 'command_ready',
                        'merge_command': merge_command,
                        'merge_message': 'Manual merge command generated. Please execute the command in your local working copy.',
                        'vcs_type': vcs_type,
                        'commit_hash': commit_hash,
                        'repo_url': repo_url,
                        'method': 'manual'
                    }
                    feature.set_stage_data(stage_data)
                    db.session.commit()
                    flash(f'Merge command generated. Please run it in your local working copy.', 'info')
        
        elif action == 'upload_unit_tests' and stage_name == 'Unit Testing':
            test_cases_file = request.files.get('test_cases_file')
            playwright_prompt_file = request.files.get('playwright_prompt_file')
            
            if not test_cases_file or not test_cases_file.filename:
                if not stage_data.get(stage_name, {}).get('test_cases_filename'):
                    flash('Unit Test Cases Sheet is required!', 'error')
                    return redirect(url_for('process_stage', feature_id=feature_id, stage_index=stage_index))
            
            if not playwright_prompt_file or not playwright_prompt_file.filename:
                if not stage_data.get(stage_name, {}).get('playwright_prompt_filename'):
                    flash('Playwright Prompt File is required!', 'error')
                    return redirect(url_for('process_stage', feature_id=feature_id, stage_index=stage_index))
            
            try:
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                
                test_cases_path = None
                test_cases_filename = None
                if test_cases_file and test_cases_file.filename:
                    test_cases_filename = secure_filename(test_cases_file.filename)
                    test_cases_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_testcases_{test_cases_filename}")
                    test_cases_file.save(test_cases_path)
                else:
                    test_cases_path = stage_data.get(stage_name, {}).get('test_cases_path')
                    test_cases_filename = stage_data.get(stage_name, {}).get('test_cases_filename')
                
                playwright_prompt_path = None
                playwright_prompt_filename = None
                if playwright_prompt_file and playwright_prompt_file.filename:
                    playwright_prompt_filename = secure_filename(playwright_prompt_file.filename)
                    playwright_prompt_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_playwright_{playwright_prompt_filename}")
                    playwright_prompt_file.save(playwright_prompt_path)
                else:
                    playwright_prompt_path = stage_data.get(stage_name, {}).get('playwright_prompt_path')
                    playwright_prompt_filename = stage_data.get(stage_name, {}).get('playwright_prompt_filename')
                
                stage_data[stage_name] = {
                    'completed': False,
                    'timestamp': datetime.utcnow().isoformat(),
                    'test_cases_path': test_cases_path,
                    'test_cases_filename': test_cases_filename,
                    'playwright_prompt_path': playwright_prompt_path,
                    'playwright_prompt_filename': playwright_prompt_filename
                }
                
                feature.set_stage_data(stage_data)
                db.session.commit()
                
                flash('Test documentation uploaded successfully!', 'success')
                
            except Exception as e:
                logging.error(f"Error uploading test files: {str(e)}")
                flash(f'Error uploading files: {str(e)}', 'error')
        
        elif action == 'skip':
            if stage_index < len(WORKFLOW_STAGES) - 1:
                feature.current_stage = WORKFLOW_STAGES[stage_index + 1]
                feature.stage_index = stage_index + 1
                db.session.commit()
                flash(f'Skipped "{stage_name}"', 'info')
            else:
                flash('This is the final stage!', 'info')
            return redirect(url_for('workflow', feature_id=feature_id))
        
        elif action == 'complete':
            stage_data[stage_name] = stage_data.get(stage_name, {})
            stage_data[stage_name]['completed'] = True
            stage_data[stage_name]['timestamp'] = datetime.utcnow().isoformat()
            stage_data[stage_name]['notes'] = request.form.get('notes', '')
            feature.set_stage_data(stage_data)
            
            if stage_index < len(WORKFLOW_STAGES) - 1:
                feature.current_stage = WORKFLOW_STAGES[stage_index + 1]
                feature.stage_index = stage_index + 1
                flash(f'Completed "{stage_name}"!', 'success')
            else:
                flash(f'Feature "{feature.name}" workflow completed!', 'success')
            
            db.session.commit()
            return redirect(url_for('workflow', feature_id=feature_id))
    
    if stage_name == 'Dependency Analyzer' and stage_name in stage_data:
        analysis_result = stage_data[stage_name].get('analysis')
        repo_path = stage_data[stage_name].get('repo_path', '')
        if repo_path and not analysis_result:
            repo_info = DependencyService.get_repository_info(repo_path)
            if repo_info['success']:
                repo_info = repo_info['data']
    
    stage_content = get_stage_content(stage_name, feature)
    
    patch_file_info = None
    if stage_name == 'AI Analysis' and 'Patch Generation' in stage_data:
        patch_file_info = stage_data['Patch Generation'].get('patch_file')
    
    return render_template('stage.html', 
                         feature=feature, 
                         stage_name=stage_name,
                         stage_index=stage_index,
                         stage_content=stage_content,
                         stage_data=stage_data.get(stage_name, {}),
                         all_stage_data=stage_data,
                         patch_file_info=patch_file_info,
                         analysis_result=analysis_result,
                         repo_info=repo_info,
                         total_stages=len(WORKFLOW_STAGES))

def get_stage_content(stage_name, feature):
    content = {
        'Dependency Analyzer': {
            'title': 'Dependency Analysis',
            'description': 'Analyze dependencies between old and new versions',
            'placeholder': 'AI will analyze code dependencies, imports, and module relationships...'
        },
        'Patch Generation': {
            'title': 'Patch Generation',
            'description': 'Generate patches to migrate features',
            'placeholder': 'AI will generate patch files showing differences and migration steps...'
        },
        'AI Analysis': {
            'title': 'AI Code Analysis',
            'description': 'Deep AI analysis of code compatibility',
            'placeholder': 'AI will provide insights on code quality, compatibility issues, and recommendations...'
        },
        'Merging': {
            'title': 'Code Merging',
            'description': 'Merge feature code into current version',
            'placeholder': 'AI will assist with conflict resolution and smart merging strategies...'
        },
        'Unit Testing': {
            'title': 'Unit Testing',
            'description': 'Run and validate unit tests',
            'placeholder': 'AI will generate and execute unit tests to verify functionality...'
        },
        'Release Documentation': {
            'title': 'Release Documentation',
            'description': 'Generate release notes and documentation',
            'placeholder': 'AI will create comprehensive documentation for the merged feature...'
        }
    }
    
    return content.get(stage_name, {
        'title': stage_name,
        'description': 'Process this stage',
        'placeholder': 'Processing...'
    })

@app.route('/feature/<int:feature_id>/delete', methods=['POST'])
def delete_feature(feature_id):
    feature = Feature.query.get_or_404(feature_id)
    name = feature.name
    
    if feature.file_path and os.path.exists(feature.file_path):
        os.remove(feature.file_path)
    
    db.session.delete(feature)
    db.session.commit()
    
    flash(f'Feature "{name}" deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/download/analysis/<int:feature_id>')
def download_analysis(feature_id):
    from flask import send_file
    feature = Feature.query.get_or_404(feature_id)
    stage_data = feature.get_stage_data()
    
    analysis_data = stage_data.get('AI Analysis', {})
    analysis_file = analysis_data.get('analysis_file')
    
    if not analysis_file or not os.path.exists(analysis_file):
        flash('Analysis file not found!', 'error')
        return redirect(url_for('workflow', feature_id=feature_id))
    
    return send_file(analysis_file, as_attachment=True, download_name=analysis_data.get('analysis_filename', 'analysis.md'))

@app.route('/download/patch/<int:feature_id>')
def download_patch(feature_id):
    from flask import send_file
    feature = Feature.query.get_or_404(feature_id)
    stage_data = feature.get_stage_data()
    
    patch_data = stage_data.get('Patch Generation', {})
    patch_file = patch_data.get('patch_file')
    
    if not patch_file or not os.path.exists(patch_file):
        flash('Patch file not found!', 'error')
        return redirect(url_for('workflow', feature_id=feature_id))
    
    return send_file(patch_file, as_attachment=True, download_name=patch_data.get('patch_filename', 'patch.patch'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
