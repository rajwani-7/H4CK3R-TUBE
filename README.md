# H4CK3R TUBE - YouTube Video Downloader

A YouTube video downloader with a hacking-themed UI. This project includes a Flask backend for video downloading and a modern HTML/CSS/JS frontend for a great user experience.

## Features

- Download YouTube videos with progress tracking
- Multiple format options (1080p, 720p, best quality, audio only, etc.)
- Hacking-themed UI with glitch effects and animations
- Sound effects for interactions
- Mobile-responsive design
- Can be deployed to Vercel (with limited functionality)

## Project Structure

```
/project-folder
├── app.py                # Flask backend code
├── api/                  # Vercel API handlers
│   └── index.py          # Vercel API entrypoint
├── static/               # Static assets
│   ├── js/               # JavaScript files
│   ├── sounds/           # Sound effects
│   └── favicon.ico       # Favicon
├── templates/            # HTML templates
│   └── index.html        # Main application page
├── downloads/            # Folder to store downloaded files (local only)
├── setup.sh              # Setup script for Unix/Mac
├── setup.bat             # Setup script for Windows
├── cleanup.sh            # Cleanup script for Unix/Mac
├── cleanup.bat           # Cleanup script for Windows
├── vercel.json           # Vercel configuration
└── requirements.txt      # Backend dependencies
```

## Requirements

### Backend
- Python 3.7+
- Flask
- yt-dlp
- Flask-CORS

## Quick Setup

### Using Setup Scripts (Recommended)

1. For Windows users:
   ```
   setup.bat
   ```

2. For macOS/Linux users:
   ```
   chmod +x setup.sh
   ./setup.sh
   ```

3. Start the application:
   ```
   python app.py
   ```
   
The application will be available at http://localhost:5000

## Deploying to Vercel

This application can be deployed to Vercel with limited functionality:

1. Install the Vercel CLI:
   ```
   npm install -g vercel
   ```

2. Login to Vercel:
   ```
   vercel login
   ```

3. Deploy the project:
   ```
   vercel
   ```

**Note about Vercel deployment:** Due to serverless limitations, the Vercel deployment will only show video information and formats. Actual video downloading is disabled in the cloud environment. Users will need to use yt-dlp locally to download videos.

### Manual Installation

1. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

3. Install the backend dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Download sound effects and favicon:
   - On Windows:
     ```
     download_sounds.bat
     download_favicon.bat
     ```
   - On macOS/Linux:
     ```
     # Install sound effects manually or use curl commands from the bat files
     ```

5. Start the Flask server:
   ```
   python app.py
   ```
   The application will be available at http://localhost:5000

## Cleaning Up

To clean the project (remove cache files, etc.):

1. For Windows users:
   ```
   cleanup.bat
   ```

2. For macOS/Linux users:
   ```
   chmod +x cleanup.sh
   ./cleanup.sh
   ```

The cleanup scripts will ask you which components you want to clean:
- Python cache files (`__pycache__`, `.pyc` files)
- Python virtual environment (`venv`)
- Downloads folder

## ffmpeg Installation

To enable video and audio merging, install ffmpeg:

- On Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- On macOS: `brew install ffmpeg`
- On Linux: `sudo apt install ffmpeg`

## Note

This application is for educational purposes only. Please respect YouTube's terms of service and copyright laws when downloading videos.

## License

MIT 