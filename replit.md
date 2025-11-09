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
├── app.py                 # Main Flask application
├── templates/             # HTML templates with TailwindCSS
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Dashboard showing all features
│   ├── create_feature.html  # Feature creation form
│   ├── workflow.html     # Workflow progress view
│   └── stage.html        # Individual stage processing
├── uploads/              # Uploaded feature files
├── generated/            # Generated patches and outputs
└── requirements.txt      # Python dependencies
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
- Fields: id, name, description, current_stage, stage_index, created_at, updated_at, file_path, stage_data

## Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Flask session secret
- `GEMINI_API_KEY`: For Gemini AI (optional)
- `OPENAI_API_KEY`: For OpenAI AI (optional)

## Recent Changes
- 2025-11-09: Initial project setup with Flask, PostgreSQL, and TailwindCSS
- 2025-11-09: Implemented 6-stage workflow system with skip/resume functionality
- 2025-11-09: Created responsive UI with progress tracking
