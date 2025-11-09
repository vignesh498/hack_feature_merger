from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
import json
import logging
from dependency_service import DependencyService

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
    
    return render_template('stage.html', 
                         feature=feature, 
                         stage_name=stage_name,
                         stage_index=stage_index,
                         stage_content=stage_content,
                         stage_data=stage_data.get(stage_name, {}),
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
