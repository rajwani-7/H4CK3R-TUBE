from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import yt_dlp
import os
import threading
import uuid
import time
import re
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Check if we're running on Vercel
IS_VERCEL = os.environ.get('VERCEL_ENV', False)

# Dictionary to track download progress
download_progress = {}

# Dictionary to track requests
video_info_cache = {}

# For Vercel deployment, we need to use /tmp for temporary storage
if IS_VERCEL:
    downloads_folder = '/tmp'
    DOWNLOADS_ENABLED = False  # Disable actual downloading on Vercel
else:
    downloads_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
    DOWNLOADS_ENABLED = True   # Enable downloading on local server

# Create downloads folder if it doesn't exist
if not os.path.exists(downloads_folder):
    os.makedirs(downloads_folder)

def sanitize_filename(filename):
    """Sanitize the filename to remove invalid characters"""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def download_progress_hook(d):
    """Track download progress"""
    # Get the download_id directly from the dict
    download_id = d.get('download_id')
    
    if download_id is None or download_id not in download_progress:
        return
    
    if d['status'] == 'downloading':
        try:
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)
            
            if total_bytes > 0:
                percent = (downloaded_bytes / total_bytes) * 100
            else:
                percent = 0
                
            download_progress[download_id].update({
                'status': 'downloading',
                'percent': round(percent, 2),
                'speed': d.get('speed', 0),
                'eta': d.get('eta', 0),
                'filename': d.get('filename', '')
            })
        except Exception as e:
            download_progress[download_id].update({
                'status': 'error',
                'error': str(e)
            })
            
    elif d['status'] == 'finished':
        download_progress[download_id].update({
            'status': 'processing',
            'percent': 100,
            'filename': d.get('filename', '')
        })
        
    elif d['status'] == 'error':
        download_progress[download_id].update({
            'status': 'error',
            'error': str(d.get('error', 'Unknown error'))
        })

def download_video(url, download_id, options):
    try:
        format_option = options.get('format', 'bestvideo[height<=720]+bestaudio/best[height<=720]')
        
        # Set download options
        ydl_opts = {
            'format': format_option,
            'outtmpl': os.path.join(downloads_folder, '%(title)s.%(ext)s'),
            'progress_hooks': [download_progress_hook],
            'noplaylist': True,
            'merge_output_format': 'mp4',  # Merge video and audio into mp4
            # Add download_id directly to each progress hook call
            'download_id': download_id,
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': True
        }
        
        # Log the requested format for debugging
        print(f"Download initiated with format: {format_option}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # First get video info
            try:
                info_dict = ydl.extract_info(url, download=False)
                if info_dict is None:
                    raise Exception("Failed to retrieve video information")
                
                # Get thumbnail URL from info dict
                thumbnail_url = None
                if 'thumbnail' in info_dict:
                    thumbnail_url = info_dict['thumbnail']
                elif 'thumbnails' in info_dict and len(info_dict['thumbnails']) > 0:
                    thumbnail_url = info_dict['thumbnails'][-1]['url']  # Get the last (usually highest quality) thumbnail
                
                # Now download the video
                ydl.download([url])
                
                # Get actual quality that was downloaded
                requested_height = None
                if "720" in format_option:
                    requested_height = "720p"
                elif "1080" in format_option:
                    requested_height = "1080p"
                else:
                    requested_height = "Best Available"
                
                # Update progress when complete
                filename = sanitize_filename(info_dict.get('title', 'video') + '.mp4')
                download_progress[download_id].update({
                    'status': 'complete',
                    'filename': filename,
                    'title': info_dict.get('title', 'Unknown'),
                    'requested_quality': requested_height,
                    'thumbnail': thumbnail_url,
                    'percent': 100
                })
            except Exception as inner_e:
                print(f"Error during video info extraction: {str(inner_e)}")
                raise inner_e
        
    except Exception as e:
        print(f"Download error: {str(e)}")
        download_progress[download_id].update({
            'status': 'error',
            'error': str(e)
        })

def get_video_info(url, request_id):
    """Extract video information without downloading"""
    try:
        # Set download options for testing
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,  # Don't download, just get info
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info without downloading
            info_dict = ydl.extract_info(url, download=False)
            
            if info_dict is None:
                video_info_cache[request_id] = {
                    'status': 'error',
                    'error': 'Failed to retrieve video information'
                }
                return
            
            # Get thumbnail URLs
            thumbnails = []
            if 'thumbnail' in info_dict:
                thumbnails.append({'url': info_dict['thumbnail'], 'type': 'default'})
            
            if 'thumbnails' in info_dict:
                for i, thumb in enumerate(info_dict['thumbnails']):
                    if 'url' in thumb:
                        thumbnails.append({'url': thumb['url'], 'type': f'thumbnail_{i}'})
            
            # Get available formats
            formats = []
            for fmt in info_dict.get('formats', []):
                if fmt.get('format_id'):
                    formats.append({
                        'format_id': fmt.get('format_id'),
                        'format': fmt.get('format'),
                        'width': fmt.get('width'),
                        'height': fmt.get('height'),
                        'ext': fmt.get('ext')
                    })
            
            # Prepare response
            video_info_cache[request_id] = {
                'status': 'success',
                'title': info_dict.get('title', 'Unknown'),
                'duration': info_dict.get('duration'),
                'thumbnails': thumbnails,
                'formats': formats,
                'url': url,
                'timestamp': time.time()
            }
            
    except Exception as e:
        video_info_cache[request_id] = {
            'status': 'error',
            'error': str(e)
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/video-info', methods=['POST'])
def get_info():
    """Get video information without downloading"""
    url = request.json.get('url')
    
    if not url:
        return jsonify({'status': 'error', 'error': 'URL is required'}), 400
    
    # Validate URL (basic check)
    if not url.startswith(('http://', 'https://')):
        return jsonify({'status': 'error', 'error': 'Invalid URL format'}), 400
    
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
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

# If downloads are enabled (local environment), include these routes
if DOWNLOADS_ENABLED:
    @app.route('/api/download', methods=['POST'])
    def start_download():
        url = request.json.get('url')
        format_option = request.json.get('format', 'best')
        
        if not url:
            return jsonify({'status': 'error', 'error': 'URL is required'}), 400
        
        # Validate URL (basic check)
        if not url.startswith(('http://', 'https://')):
            return jsonify({'status': 'error', 'error': 'Invalid URL format'}), 400
        
        # Generate a unique ID for this download
        download_id = str(uuid.uuid4())
        
        # Initialize progress tracking
        download_progress[download_id] = {
            'status': 'starting',
            'percent': 0,
            'url': url
        }
        
        # Start download in a separate thread
        download_thread = threading.Thread(
            target=download_video,
            args=(url, download_id, {'format': format_option})
        )
        download_thread.daemon = True
        download_thread.start()
        
        return jsonify({
            'status': 'started',
            'download_id': download_id
        })
else:
    # In Vercel environment, replace download with a message
    @app.route('/api/download', methods=['POST'])
    def start_download():
        return jsonify({
            'success': False,
            'message': 'Downloads are disabled in the cloud environment. Please use the YouTube-DL tool locally.'
        })

@app.route('/api/progress/<download_id>')
def get_progress(download_id):
    if download_id not in download_progress:
        return jsonify({'status': 'not_found'}), 404
    
    return jsonify(download_progress[download_id])

@app.route('/downloads/<path:filename>')
def download_file(filename):
    try:
        # Log the download request
        print(f"Download requested for file: {filename}")
        print(f"Download folder path: {downloads_folder}")
        
        # Check if file exists
        file_path = os.path.join(downloads_folder, filename)
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return jsonify({'error': 'File not found'}), 404
            
        return send_from_directory(
            directory=downloads_folder, 
            path=filename, 
            as_attachment=True
        )
    except Exception as e:
        print(f"Error serving file {filename}: {str(e)}")
        return jsonify({'error': f'Error serving file: {str(e)}'}), 500

@app.route('/api/downloads')
def list_downloads():
    files = []
    try:
        for entry in os.scandir(downloads_folder):
            if entry.is_file():
                files.append({
                    'name': entry.name,
                    'size': entry.stat().st_size,
                    'created': entry.stat().st_ctime
                })
    except Exception as e:
        print(f"Error listing downloads: {str(e)}")
    return jsonify(files)

@app.route('/api/vercel-info')
def vercel_info():
    """Return information about the Vercel environment"""
    return jsonify({
        'isVercel': IS_VERCEL,
        'downloadsEnabled': DOWNLOADS_ENABLED,
        'environment': {
            'vercelEnv': os.environ.get('VERCEL_ENV', 'Not running on Vercel'),
            'region': os.environ.get('VERCEL_REGION', 'unknown'),
            'url': os.environ.get('VERCEL_URL', 'unknown')
        }
    })

if __name__ == '__main__':
    app.run(debug=True, threaded=True)

# This is needed for Vercel
app = app 