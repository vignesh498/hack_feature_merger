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

## Replit Setup
- **Development Server**: Flask app runs on 0.0.0.0:5000 (development mode with debug enabled)
- **Production Deployment**: Uses Gunicorn WSGI server configured for autoscale deployment
- **Database**: PostgreSQL database pre-configured via DATABASE_URL environment variable
- **Dependencies**: All Python packages installed via packager tool
- **File Storage**: uploads/ and generated/ directories created with .gitkeep files

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
- 2025-11-10: Configured for Replit environment with workflow, deployment, and gitignore setup
- 2025-11-10: Implemented Stage 4 (Merging) with dual approach:
  - Manual Merge: Generates SVN/Git merge command with validation for user to run locally
  - AI Merge: Provides downloadable analysis and patch files from previous stages
- 2025-11-10: Security hardening: Eliminated command injection and XSS vulnerabilities using data attributes and HTML escaping
- 2025-11-10: Implemented Stage 5 (Unit Testing) with file upload functionality:
  - Displays instructional message to proceed with Playwright testing in copilot
  - Upload forms for unit test cases sheet and Playwright prompt text file
  - Secure file storage with timestamped filenames using secure_filename
  - Files stored in database via stage_data JSON field for persistence
  - Visual feedback showing uploaded filenames after successful upload
- 2025-11-15: GitHub import setup for Replit environment:
  - Installed all Python dependencies (Flask, SQLAlchemy, Gunicorn, Google Gemini, etc.)
  - Created .gitignore for Python project with uploads/ and generated/ directories
  - Configured PostgreSQL database connection using existing DATABASE_URL
  - Set up flask-app workflow to run on 0.0.0.0:5000 for development
  - Configured deployment with Gunicorn for autoscale production deployment
  - Verified app is running successfully and responding to requests
- 2025-11-15: Enhanced Stage 4 (Merging - Manual Merge) with dry-run SVN merge:
  - Added local SVN working copy path input field (e.g., /home/user/svn/trunk)
  - Implemented automatic SVN dry-run merge that executes in the specified working copy directory
  - Path validation: Checks if directory exists and is accessible before running dry-run
  - Dry-run command executes with `cwd=working_copy_path` to run in the local SVN directory
  - Conflict detection logic parses dry-run output for merge conflicts ('C' flag, 'conflict' keyword, non-zero exit code)
  - Display two distinct outcomes:
    * No conflicts: Show success message with manual merge command and step-by-step instructions
    * Conflicts detected: Show warning message with full dry-run output and recommendation to use AI-assisted merge
  - Enhanced UI with color-coded status indicators (green for success, red for conflicts)
  - Improved user experience with monospace font for paths and clear next-step instructions
- 2025-11-16: Implemented multi-commit support for Stage 2 (Patch Generation) and Stage 4 (Merging):
  - Stage 2: Now accepts comma-separated commit hashes/revisions (e.g., "abc123, def456, ghi789")
  - Generates individual patch files for each commit hash provided
  - Backend validates each commit hash and creates timestamped patch files
  - UI displays all generated patches with detailed information per commit
  - Stage 4: Enhanced to handle multiple commits from Patch Generation stage
  - Generates combined merge commands for Git (cherry-pick) and SVN (merge -c)
  - Dry-run merge executes for multiple commits with proper conflict detection
  - UI shows all commits being merged with individual commit IDs listed
  - Maintains backward compatibility with single-commit workflow
  - Enhanced user feedback messages to indicate batch processing of multiple commits
- 2025-11-16: Implemented Stage 6 (Release Documentation) with complete version management:
  - Database: Created ReleaseVersion model with version_number, is_released, released_at fields
  - Added release_version_id foreign key to Feature model for version tracking
  - Migration script: migrate_release_version.py to update database schema
  - Stage 6 UI: Form for version number input and feature release notes with three action buttons:
    * Save Release Notes: Save progress without completing
    * Complete & Continue: Complete feature and add more features to the release
    * Release Version: Finalize the release and view comprehensive release summary
  - Release Summary View: Displays all features in a release with downloadable artifacts:
    * Feature release notes for each feature
    * BRD/User Story documents
    * AI analysis files (analysis.md)
    * Patch files (multiple patches supported)
    * Unit test cases sheets and Playwright prompts
  - Secure file downloads: Implemented download_file route with path traversal protection
    * Uses os.path.commonpath for robust directory containment validation
    * Restricts downloads to uploads/ and generated/ directories only
    * Returns 403 for unauthorized paths, 404 for missing files
  - Version reuse: Multiple features can be added to the same release version
  - Release finalization: Marks release as completed with timestamp when "Release Version" is clicked
