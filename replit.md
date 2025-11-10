# AI Feature Merge Assistant

## Overview
A Flask-based web application that helps integrate features developed in older versions of a product into the current version using AI for analysis, patch generation, and conflict resolution.

## Tech Stack
- **Backend**: Python Flask
- **Frontend**: HTML + TailwindCSS
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **AI Integration**: Gemini/OpenAI (ready for integration)
- **File Handling**: Local storage (uploads/, generated/)

## Project Structure
```
.
├── app.py                    # Main Flask application
├── dependency_service.py     # Repository analysis service
├── git_dependency_analyzer.py # Git commit dependency analyzer
├── document_processor.py     # Multi-format document text extraction
├── gemini_helper.py          # Gemini AI integration helper
├── vcs_handler.py            # Git/SVN patch generation handler
├── templates/                # HTML templates with TailwindCSS
│   ├── base.html            # Base template with navigation
│   ├── index.html           # Dashboard showing all features
│   ├── create_feature.html  # Feature creation form
│   ├── workflow.html        # Workflow progress view
│   └── stage.html           # Individual stage processing
├── uploads/                  # Uploaded BRD/feature files
├── generated/                # Generated patches and AI analysis
├── requirements.txt          # Python dependencies
└── LOCAL_SETUP.md            # Local installation guide
```

## Features
1. **Feature Management**
   - Create new feature merge projects
   - View all features in dashboard
   - Resume from last saved stage
   - Delete features

2. **Multi-Stage Workflow**
   - Dependency Analyzer
   - Patch Generation
   - AI Analysis
   - Merging
   - Unit Testing
   - Release Documentation

3. **Smart Navigation**
   - Progress tracking with visual indicators
   - Skip option for each stage
   - Auto-save of progress
   - Resume capability

## Database Schema
- **Features Table**: Stores feature information, current stage, progress, and metadata
- Fields: 
  - id, name, description
  - current_stage, stage_index
  - created_at, updated_at
  - file_path (uploaded BRD/feature file)
  - stage_data (JSON data for all stages)
  - commit_id (from Patch Generation stage)
  - patch_file_path (generated patch file from Stage 2)
  - analysis_file_path (AI analysis document from Stage 3)

## Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Flask session secret
- `GEMINI_API_KEY`: For Gemini AI (optional)
- `OPENAI_API_KEY`: For OpenAI AI (optional)

## Recent Changes
- 2025-11-09: Initial project setup with Flask, PostgreSQL, and TailwindCSS
- 2025-11-09: Implemented 6-stage workflow system with skip/resume functionality
- 2025-11-09: Created responsive UI with progress tracking
- 2025-11-09: Integrated Patch Generation stage with Git/SVN support
- 2025-11-09: Integrated AI Analysis stage using Google Gemini API
- 2025-11-09: Added multi-format document processor (PDF, DOCX, TXT, Excel, CSV)
- 2025-11-09: Created LOCAL_SETUP.md for local installation instructions
- 2025-11-09: Added database columns to store commit_id, patch_file_path, and analysis_file_path
- 2025-11-09: Created migrate_db.py for database schema migration
