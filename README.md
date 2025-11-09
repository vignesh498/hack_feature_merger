# AI Feature Merge Assistant

A Flask-based web application that helps integrate features developed in older versions of a product into the current version using AI-powered analysis and multi-stage workflow management.

## Features

### Dashboard
- View all feature merge projects
- See current stage and progress for each feature
- Quick access to resume or delete features

### Feature Creation
- Create new merge projects with name and description
- Optional file upload for feature code/patches
- Automatic workflow initialization

### 6-Stage Workflow
1. **Dependency Analyzer** - Analyze dependencies between old and new versions
2. **Patch Generation** - Generate patches to migrate features
3. **AI Analysis** - Deep AI analysis of code compatibility
4. **Merging** - Merge feature code into current version
5. **Unit Testing** - Run and validate unit tests
6. **Release Documentation** - Generate release notes and documentation

### Smart Features
- **Resume Capability**: Pick up where you left off
- **Skip Option**: Skip any stage if needed
- **Progress Tracking**: Visual progress indicators
- **Auto-Save**: Progress automatically saved to database

## How to Use

1. **Start the Application**
   - The app is already running at the webview URL
   - Click "Create Feature" to get started

2. **Create a Feature**
   - Enter feature name (required)
   - Add description (optional)
   - Upload feature files (optional)
   - Click "Create Feature & Start Workflow"

3. **Work Through Stages**
   - Each stage shows AI analysis placeholder content
   - Add notes if needed
   - Choose to either:
     - **Complete & Continue** - Mark as done and move to next stage
     - **Skip This Stage** - Jump to next stage without processing

4. **Resume Anytime**
   - Return to dashboard and click "Resume" on any feature
   - Your progress is automatically saved

## Tech Stack

- **Backend**: Flask with SQLAlchemy
- **Database**: PostgreSQL
- **Frontend**: HTML with TailwindCSS
- **File Storage**: Local directories (uploads/, generated/)

## Project Structure

```
.
├── app.py                     # Main Flask application
├── templates/                 # Frontend templates
│   ├── base.html             # Base layout
│   ├── index.html            # Dashboard
│   ├── create_feature.html   # Feature creation
│   ├── workflow.html         # Workflow overview
│   └── stage.html            # Individual stage
├── uploads/                   # Uploaded files
├── generated/                 # Generated patches
└── requirements.txt          # Dependencies
```

## Database Schema

**Features Table**:
- `id`: Primary key
- `name`: Feature name (unique)
- `description`: Feature description
- `current_stage`: Current workflow stage
- `stage_index`: Index of current stage (0-5)
- `file_path`: Path to uploaded file
- `stage_data`: JSON data for each stage
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Dependency Analyzer - Git Integration

The **Dependency Analyzer** stage now includes full Git repository analysis powered by the `GitAnalyzer` class:

### How It Works

1. Navigate to the Dependency Analyzer stage for any feature
2. Fill in the analysis form:
   - **Repository Path**: Path to your Git repo (use "." for current directory)
   - **Branch**: The branch to analyze (e.g., "main", "develop")
   - **Target Commit**: The commit hash you want to analyze (minimum 8 characters)
   - **Date Range**: Optional start and end dates (defaults to last 30 days)
3. Click "Run Dependency Analysis"

### What You Get

The analysis identifies all commits that modified the same files and code regions as your target commit:

- **Dependency Count**: Number of dependent commits found
- **File Overlaps**: Which files were modified by multiple commits
- **Line-Level Analysis**: Detects overlapping code changes
- **Commit Details**: Hash, author, date, and message for each dependency
- **Visual Results**: Color-coded cards showing overlap counts and affected files

### Use Cases

- **Feature Merging**: Identify which older commits your feature depends on
- **Code Review**: See related changes that might affect your work
- **Conflict Prevention**: Detect potential merge conflicts before they happen
- **Change Impact**: Understand the scope of dependencies for a commit

## Next Steps

To enhance with more AI capabilities:

1. **Add API Keys** (optional for now)
   - Gemini: Set `GEMINI_API_KEY` environment variable
   - OpenAI: Set `OPENAI_API_KEY` environment variable

2. **Enhance Other Stages**
   - Integrate AI for patch generation
   - Add AI-powered conflict resolution
   - Implement automated unit test generation

## Development Notes

- Database tables are automatically created on app startup
- Session data is stored in PostgreSQL
- File uploads limited to 16MB
- TailwindCSS loaded via CDN (for production, install locally)

## Support

The application is designed to be intuitive and user-friendly. Each stage provides clear instructions and placeholder content showing what AI processing will occur in the full implementation.

---

**Ready to merge your legacy features!** 🚀
