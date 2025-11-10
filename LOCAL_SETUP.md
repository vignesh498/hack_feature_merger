# Local Installation Guide

This guide will help you set up and run the AI Feature Merge Assistant on your local machine.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Git (for version control operations)
- SVN (optional, for SVN repository support)

## Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd ai-feature-merge-assistant
```

## Step 2: Install Python Dependencies

```bash
pip install flask
pip install sqlalchemy
pip install psycopg2-binary
pip install PyPDF2
pip install python-docx
pip install pandas
pip install openpyxl
pip install requests
pip install google-generativeai
pip install openai
```

Or install all at once from requirements.txt:

```bash
pip install -r requirements.txt
```

## Step 3: Set Up PostgreSQL Database

1. Install PostgreSQL on your system
2. Create a new database:

```bash
createdb feature_merge_db
```

3. Note your database credentials (username, password, host, port)

## Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/feature_merge_db
SESSION_SECRET=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

Replace the placeholders with your actual credentials.

### Getting API Keys

- **Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)

## Step 5: Create Required Directories

```bash
mkdir uploads
mkdir generated
```

## Step 6: Initialize the Database

The database tables will be created automatically when you first run the application.

## Step 7: Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## System Requirements

- **Operating System**: Linux, macOS, or Windows
- **RAM**: Minimum 2GB
- **Disk Space**: 500MB for application and dependencies
- **Network**: Internet connection required for AI API calls

## Optional: Virtual Environment (Recommended)

It's recommended to use a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Troubleshooting

### Database Connection Issues

If you encounter database connection errors:

1. Verify PostgreSQL is running: `pg_isready`
2. Check your DATABASE_URL format
3. Ensure the database exists: `psql -l`

### Import Errors

If you get import errors:

1. Make sure all dependencies are installed
2. Check Python version: `python --version`
3. Reinstall requirements: `pip install -r requirements.txt --force-reinstall`

### Git/SVN Not Found

If patch generation fails:

1. Install Git: `apt-get install git` (Linux) or download from [git-scm.com](https://git-scm.com)
2. Install SVN: `apt-get install subversion` (Linux) or download from [Apache SVN](https://subversion.apache.org)

### AI Analysis Fails

If AI analysis doesn't work:

1. Verify your API key is set correctly in `.env`
2. Check your API quota/billing
3. Ensure internet connection is active

## Production Deployment

For production deployment:

1. Use a production WSGI server (Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn --bind 0.0.0.0:5000 app:app
   ```

2. Set up proper environment variables
3. Use a production-grade database
4. Enable HTTPS/SSL
5. Set `DEBUG=False` in app configuration

## Support

For issues or questions, please refer to the project documentation or contact the development team.
