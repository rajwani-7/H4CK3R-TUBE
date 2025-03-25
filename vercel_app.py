from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import os
import uuid
import time
import re
import json
from urllib.parse import urlparse, parse_qs
import requests  # Added for HTTP requests

# Try to import yt-dlp, but have a fallback if it fails
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except (ImportError, MemoryError):
    # If yt-dlp fails to import (common in serverless due to size/memory)
    YT_DLP_AVAILABLE = False

# Set up paths for templates and static files
# This is important for Vercel deployment
root_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(root_dir, 'templates')
static_dir = os.path.join(root_dir, 'static')

app = Flask(__name__, 
            template_folder=template_dir,
            static_folder=static_dir)
CORS(app)  # Enable CORS for all routes

# For Vercel deployment
IS_VERCEL = os.environ.get('VERCEL_ENV', True)  # Default to True for Vercel
DOWNLOADS_ENABLED = False  # Always disabled for Vercel

# Dictionary to track requests
video_info_cache = {}

# Create a temporary directory for Vercel
downloads_folder = '/tmp'
if not os.path.exists(downloads_folder):
    os.makedirs(downloads_folder)

def get_video_info(url, request_id):
    """Extract video information without downloading"""
    try:
        # More lightweight options for Vercel
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'no_color': True,
            'geo_bypass': True,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'logtostderr': False,
            'format': 'best',  # Only consider best format to reduce memory
            'max_downloads': 1,
            'cachedir': False  # Disable cache to reduce disk usage
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract basic info first - more lightweight
            info_dict = ydl.extract_info(url, download=False, process=False)
            
            if info_dict is None:
                video_info_cache[request_id] = {
                    'status': 'error',
                    'error': 'Failed to retrieve video information'
                }
                return
            
            # Get basic video info only
            title = info_dict.get('title', 'Unknown')
            duration = info_dict.get('duration')
            
            # Use a simplified format list to reduce memory usage
            formats = []
            # Only process a few key formats to save memory
            for fmt in info_dict.get('formats', [])[:5]:  # Limit to first 5 formats
                if fmt.get('format_id'):
                    formats.append({
                        'format_id': fmt.get('format_id'),
                        'format': fmt.get('format', 'Unknown'),
                        'ext': fmt.get('ext', 'mp4')
                    })
            
            # Prepare response with minimal data
            video_info_cache[request_id] = {
                'status': 'success',
                'title': title,
                'duration': duration,
                'formats': formats,
                'url': url,
                'timestamp': time.time()
            }
            
    except MemoryError:
        video_info_cache[request_id] = {
            'status': 'error',
            'error': 'Memory limit exceeded. Try a different video or use the tool locally.'
        }
    except Exception as e:
        video_info_cache[request_id] = {
            'status': 'error',
            'error': str(e)
        }

# Add a simplified video info extractor that doesn't rely on yt-dlp
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
        # Fallback mechanism in case templates are not found
        error_message = f"Error rendering template: {str(e)}"
        # Try to find the template file directly
        template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'index.html')
        
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
    """Get video information without downloading"""
    url = request.json.get('url')
    
    if not url:
        return jsonify({'status': 'error', 'error': 'URL is required'}), 400
    
    # Validate URL (basic check)
    if not url.startswith(('http://', 'https://')):
        return jsonify({'status': 'error', 'error': 'Invalid URL format'}), 400
    
    # If yt-dlp is not available, use the simple method
    if not YT_DLP_AVAILABLE:
        # Extract just the video ID and basic info
        video_id = get_youtube_video_id(url)
        if not video_id:
            return jsonify({'status': 'error', 'error': 'Could not extract YouTube video ID'}), 400
        
        return jsonify({
            'success': True,
            'info': {
                'status': 'success',
                'title': 'YouTube Video',  # We don't have the actual title
                'video_id': video_id,
                'url': url,
                'thumbnail': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
                'message': 'Limited information available in serverless environment'
            },
            'downloadable': False,
            'limited_info': True
        })
    
    # Generate a unique ID for this request
    request_id = str(uuid.uuid4())
    
    try:
        # Get video info (in the same thread for simplicity on Vercel)
        get_video_info(url, request_id)
        
        # Return the result
        if request_id in video_info_cache:
            result = video_info_cache[request_id]
            return jsonify({
                'success': result['status'] == 'success',
                'info': result,
                'downloadable': DOWNLOADS_ENABLED
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to retrieve video information'
            })
    except MemoryError:
        # Memory errors are common in serverless environments
        return jsonify({
            'success': False,
            'message': 'Memory limit exceeded. Try a different video or use the tool locally.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

# In Vercel environment, replace download with a message
@app.route('/api/download', methods=['POST'])
def start_download():
    return jsonify({
        'success': False,
        'message': 'Downloads are disabled in the cloud environment. Please use the YouTube-DL tool locally.'
    })

@app.route('/api/vercel-info')
def vercel_info():
    """Return information about the Vercel environment"""
    return jsonify({
        'isVercel': IS_VERCEL,
        'downloadsEnabled': DOWNLOADS_ENABLED,
        'environment': {
            'vercelEnv': os.environ.get('VERCEL_ENV', 'Vercel'),
            'region': os.environ.get('VERCEL_REGION', 'unknown'),
            'url': os.environ.get('VERCEL_URL', 'unknown')
        }
    })

@app.route('/api/health-check')
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time()
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

@app.route('/api/simple-info', methods=['POST'])
def simple_info():
    """A simplified endpoint that doesn't use yt-dlp to avoid memory issues"""
    url = request.json.get('url')
    
    if not url:
        return jsonify({'status': 'error', 'error': 'URL is required'}), 400
    
    video_id = get_youtube_video_id(url)
    if not video_id:
        return jsonify({'status': 'error', 'error': 'Could not extract YouTube video ID'}), 400
    
    # No need to call YouTube API - just return basic info that we can determine from the URL
    return jsonify({
        'status': 'success',
        'video_id': video_id,
        'youtube_url': f'https://www.youtube.com/watch?v={video_id}',
        'embed_url': f'https://www.youtube.com/embed/{video_id}',
        'thumbnail': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
        'message': 'This is basic information only. For full details, run the tool locally.'
    })

if __name__ == '__main__':
    app.run(debug=True, threaded=True)

# This is needed for Vercel
app = app 