from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import time
import re
import json
from urllib.parse import urlparse, parse_qs

# Set up paths for templates and static files
root_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(root_dir, 'templates')
static_dir = os.path.join(root_dir, 'static')

app = Flask(__name__, 
          template_folder=template_dir,
          static_folder=static_dir)
CORS(app)

# For Vercel deployment
IS_VERCEL = True
DOWNLOADS_ENABLED = False

def get_youtube_video_id(url):
    """Extract YouTube video ID from URL"""
    if not url:
        return None
    
    # YouTube URL patterns
    patterns = [
        r'^https?://(?:www\.)?youtube\.com/watch\?v=([^&]+)',
        r'^https?://(?:www\.)?youtube\.com/embed/([^/?]+)',
        r'^https?://youtu\.be/([^/?]+)'
    ]
    
    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            return match.group(1)
    
    # Try parsing the URL
    parsed_url = urlparse(url)
    if parsed_url.netloc in ('youtube.com', 'www.youtube.com'):
        query = parse_qs(parsed_url.query)
        if 'v' in query:
            return query['v'][0]
    
    return None

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        # Fallback mechanism
        error_message = f"Error rendering template: {str(e)}"
        template_path = os.path.join(template_dir, 'index.html')
        
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r') as f:
                    html_content = f.read()
                return html_content
            except Exception as read_error:
                return jsonify({
                    'error': f"Template exists but couldn't be read: {str(read_error)}",
                    'path': template_path
                })
        else:
            return jsonify({
                'error': error_message,
                'template_not_found': True,
                'looked_in': template_path
            })

@app.route('/api/video-info', methods=['POST'])
def get_info():
    """Simple video information extractor"""
    url = request.json.get('url')
    
    if not url:
        return jsonify({'status': 'error', 'error': 'URL is required'}), 400
    
    # Validate URL (basic check)
    if not url.startswith(('http://', 'https://')):
        return jsonify({'status': 'error', 'error': 'Invalid URL format'}), 400
    
    # Extract video ID
    video_id = get_youtube_video_id(url)
    if not video_id:
        return jsonify({'status': 'error', 'error': 'Could not extract YouTube video ID'}), 400
    
    # Return basic information
    return jsonify({
        'success': True,
        'info': {
            'status': 'success',
            'title': 'YouTube Video',
            'video_id': video_id,
            'url': url,
            'formats': [
                {'format_id': 'best', 'format': 'Best Quality', 'ext': 'mp4'},
                {'format_id': 'bestaudio', 'format': 'Best Audio', 'ext': 'mp3'}
            ],
            'command': f'yt-dlp {url} --format best',
            'command_audio': f'yt-dlp {url} --extract-audio --audio-format mp3',
            'thumbnail': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
            'timestamp': time.time()
        },
        'downloadable': False,
        'message': 'For full functionality, run the application locally'
    })

@app.route('/api/download', methods=['POST'])
def start_download():
    """Simulated download - actual downloads not supported on Vercel"""
    return jsonify({
        'success': False,
        'message': 'Downloads are disabled in the cloud environment. Please use the YouTube-DL tool locally.'
    })

@app.route('/api/downloads', methods=['GET'])
def get_downloads():
    """Simulated downloads list - not available on Vercel"""
    return jsonify({
        'success': True,
        'downloads': [],
        'message': 'Download history is not available in the cloud environment'
    })

@app.route('/api/health-check')
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'lightweight': True
    })

@app.route('/api/debug')
def debug_info():
    """Debug endpoint to help diagnose deployment issues"""
    root_path = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(root_path, 'templates')
    static_path = os.path.join(root_path, 'static')
    
    template_exists = os.path.exists(template_path)
    index_exists = os.path.exists(os.path.join(template_path, 'index.html'))
    static_exists = os.path.exists(static_path)
    
    dir_contents = {}
    try:
        if template_exists:
            dir_contents['templates'] = os.listdir(template_path)
        if static_exists:
            dir_contents['static'] = os.listdir(static_path)
        dir_contents['root'] = os.listdir(root_path)
    except Exception as e:
        dir_contents['error'] = str(e)
    
    return jsonify({
        'paths': {
            'root': root_path,
            'template': template_path,
            'static': static_path,
        },
        'exists': {
            'template_dir': template_exists,
            'index_html': index_exists,
            'static_dir': static_exists,
        },
        'environment': dict(os.environ),
        'directory_contents': dir_contents
    })

@app.route('/api/static-html')
def static_html():
    """Serve a simple static HTML page for troubleshooting"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>YouTube Downloader - Static Version</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h1 { color: #d32f2f; }
            input, button { padding: 10px; margin: 10px 0; width: 100%; box-sizing: border-box; }
            button { background: #d32f2f; color: white; border: none; cursor: pointer; }
            button:hover { background: #b71c1c; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>YouTube Downloader</h1>
            <p>This is a static HTML page served directly from the API. If you can see this page, your API is working correctly.</p>
            
            <div>
                <h2>Video Information</h2>
                <input type="text" id="url" placeholder="Enter YouTube URL" />
                <button onclick="alert('This is a static page for testing. The actual functionality is not available here.')">Get Info</button>
            </div>
            
            <p>Note: Vercel has limitations that prevent actual file downloads. This is just a demonstration of API functionality.</p>
        </div>
    </body>
    </html>
    """
    return html

# For Vercel
app = app 