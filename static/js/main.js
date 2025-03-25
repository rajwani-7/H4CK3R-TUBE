document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const downloadForm = document.getElementById('download-form');
    const downloadStatus = document.getElementById('download-status');
    const downloadSuccess = document.getElementById('download-success');
    const downloadError = document.getElementById('download-error');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const progressPercentage = document.getElementById('progress-percentage');
    const downloadSpeed = document.getElementById('download-speed');
    const downloadEta = document.getElementById('download-eta');
    const downloadFilename = document.getElementById('download-filename');
    const downloadQuality = document.getElementById('download-quality');
    const successTitle = document.getElementById('success-title');
    const successQuality = document.getElementById('success-quality');
    const successFilename = document.getElementById('success-filename');
    const downloadLink = document.getElementById('download-link');
    const errorMessage = document.getElementById('error-message');
    const retryButton = document.getElementById('retry-button');
    const downloadsList = document.getElementById('downloads-list');
    const noDownloads = document.getElementById('no-downloads');
    const vercelWarning = document.getElementById('vercel-warning');

    // Sound effects
    const soundClick = document.getElementById('sound-click');
    const soundSuccess = document.getElementById('sound-success');
    const soundError = document.getElementById('sound-error');
    const soundTyping = document.getElementById('sound-typing');

    // App state
    let isVercelEnvironment = false;
    let downloadsEnabled = true;

    // Function to play sounds
    function playSound(sound) {
        if (sound) {
            sound.currentTime = 0;
            sound.play().catch(e => console.error("Error playing sound:", e));
        }
    }

    // Add sound effects to buttons
    const buttons = document.querySelectorAll('button, select, input[type="text"], a.block');
    buttons.forEach(button => {
        button.addEventListener('click', () => playSound(soundClick));
    });

    // Global variables
    let currentDownloadId = null;
    let progressInterval = null;

    // Check if running in Vercel environment
    checkVercelEnvironment();
    
    // Load previous downloads on page load (only on local environment)
    if (downloadsEnabled) {
        loadDownloads();
    }

    // Event Listeners
    downloadForm.addEventListener('submit', handleDownload);
    retryButton.addEventListener('click', handleRetry);

    // Check if we're running in Vercel environment
    function checkVercelEnvironment() {
        fetch('/api/vercel-info')
            .then(response => response.json())
            .then(data => {
                isVercelEnvironment = data.isVercel;
                downloadsEnabled = data.downloadsEnabled;
                
                if (isVercelEnvironment) {
                    vercelWarning.classList.remove('hidden');
                    
                    // Modify form submission text in Vercel environment
                    const submitButton = downloadForm.querySelector('button[type="submit"]');
                    if (submitButton) {
                        submitButton.textContent = 'GET VIDEO INFO';
                    }
                }
            })
            .catch(error => {
                console.error('Error checking environment:', error);
            });
    }

    // Handle the download form submission
    function handleDownload(e) {
        e.preventDefault();
        
        const url = document.getElementById('url').value.trim();
        const format = document.getElementById('format').value;
        
        if (!url) {
            showError('Please enter a YouTube URL');
            return;
        }
        
        if (!isValidYouTubeUrl(url)) {
            showError('Please enter a valid YouTube URL');
            return;
        }
        
        playSound(soundClick);
        
        if (isVercelEnvironment) {
            // In Vercel environment, just get video info
            getVideoInfo(url, format);
        } else {
            // In local environment, download the video
            startDownload(url, format);
        }
    }
    
    // Validate YouTube URL
    function isValidYouTubeUrl(url) {
        // Test with regex
        return /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/.test(url);
    }
    
    // Get video info (for Vercel environment)
    function getVideoInfo(url, format) {
        // Reset UI
        resetUI();
        
        // Show download status
        downloadStatus.classList.remove('hidden');
        progressText.textContent = 'Fetching video info...';
        
        // Make API call to get video info
        fetch('/api/video-info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const info = data.info;
                
                // Update UI with video info
                showVideoInfo(info, format);
                playSound(soundSuccess);
            } else {
                showError(data.message || 'Failed to get video information');
            }
        })
        .catch(error => {
            showError('Server error: ' + error.message);
        });
    }
    
    // Show video info for Vercel environment
    function showVideoInfo(info, requestedFormat) {
        downloadStatus.classList.add('hidden');
        downloadSuccess.classList.remove('hidden');
        
        successTitle.textContent = info.title || 'Video';
        successQuality.textContent = requestedFormat || 'Unknown';
        successFilename.textContent = `${info.title}.mp4`;
        
        // Change download link text and behavior
        downloadLink.textContent = 'SEE FORMATS';
        downloadLink.href = '#';
        downloadLink.addEventListener('click', (e) => {
            e.preventDefault();
            showFormatsModal(info);
        });
    }
    
    // Show formats modal with command line examples
    function showFormatsModal(info) {
        // Create modal backdrop
        const backdrop = document.createElement('div');
        backdrop.className = 'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50';
        document.body.appendChild(backdrop);
        
        // Create modal content
        const modal = document.createElement('div');
        modal.className = 'bg-gray-900 border border-terminal-green p-6 rounded-md max-w-2xl w-full max-h-[80vh] overflow-y-auto';
        
        // Title
        const title = document.createElement('h2');
        title.className = 'text-2xl mb-4 text-terminal-green';
        title.textContent = '> Available Formats';
        
        // Video info
        const videoInfo = document.createElement('div');
        videoInfo.className = 'mb-4';
        videoInfo.innerHTML = `
            <p class="mb-2"><span class="text-terminal-green">Title:</span> ${info.title}</p>
            <p class="mb-4"><span class="text-terminal-green">Duration:</span> ${formatDuration(info.duration)}</p>
            <p class="text-sm text-terminal-gray mb-2">To download this video, use yt-dlp command line tool:</p>
            <div class="bg-gray-800 p-3 rounded overflow-x-auto">
                <code class="text-sm">yt-dlp "${info.url}"</code>
            </div>
        `;
        
        // Formats table
        const formatsDiv = document.createElement('div');
        formatsDiv.className = 'mt-4';
        formatsDiv.innerHTML = `
            <p class="mb-2 text-terminal-green">Available formats:</p>
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="border-b border-terminal-gray">
                            <th class="py-2 text-left">Format</th>
                            <th class="py-2 text-left">Resolution</th>
                            <th class="py-2 text-left">Command</th>
                        </tr>
                    </thead>
                    <tbody id="formats-body">
                    </tbody>
                </table>
            </div>
        `;
        
        // Close button
        const closeButton = document.createElement('button');
        closeButton.className = 'mt-6 py-2 px-4 bg-terminal-green text-black font-bold rounded hover:bg-green-600 transition-colors';
        closeButton.textContent = 'CLOSE';
        closeButton.addEventListener('click', () => {
            document.body.removeChild(backdrop);
            playSound(soundClick);
        });
        
        // Assemble modal
        modal.appendChild(title);
        modal.appendChild(videoInfo);
        modal.appendChild(formatsDiv);
        modal.appendChild(closeButton);
        backdrop.appendChild(modal);
        
        // Populate formats table
        const formatsBody = document.getElementById('formats-body');
        if (formatsBody) {
            info.formats.forEach(format => {
                if (format.height || format.width) {  // Only video formats
                    const tr = document.createElement('tr');
                    tr.className = 'border-b border-gray-800';
                    
                    const resolution = format.height ? `${format.width}x${format.height}` : 'Audio only';
                    const command = `yt-dlp -f ${format.format_id} "${info.url}"`;
                    
                    tr.innerHTML = `
                        <td class="py-2">${format.format || format.format_id}</td>
                        <td class="py-2">${resolution}</td>
                        <td class="py-2">
                            <div class="bg-gray-800 p-1 rounded">
                                <code class="text-xs">${command}</code>
                            </div>
                        </td>
                    `;
                    
                    formatsBody.appendChild(tr);
                }
            });
        }
        
        playSound(soundClick);
    }
    
    // Format duration in seconds to MM:SS
    function formatDuration(seconds) {
        if (!seconds) return 'Unknown';
        
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    
    // Start the download process (local environment only)
    function startDownload(url, format) {
        // Reset UI
        resetUI();
        
        // Show download status
        downloadStatus.classList.remove('hidden');
        
        // Make API call to start download
        fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url, format }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentDownloadId = data.download_id;
                downloadFilename.textContent = `Filename: ${data.filename || 'Preparing...'}`;
                downloadQuality.textContent = `Quality: ${format}`;
                
                // Start checking progress
                startProgressChecking(data.download_id);
            } else {
                showError(data.message || 'Failed to start download');
            }
        })
        .catch(error => {
            showError('Server error: ' + error.message);
        });
    }
    
    // Start checking download progress
    function startProgressChecking(downloadId) {
        if (progressInterval) {
            clearInterval(progressInterval);
        }
        
        progressInterval = setInterval(() => {
            checkProgress(downloadId);
        }, 1000);
    }
    
    // Check download progress
    function checkProgress(downloadId) {
        fetch(`/api/progress/${downloadId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateProgressUI(data);
                
                if (data.status === 'complete') {
                    clearInterval(progressInterval);
                    playSound(soundSuccess);
                    showDownloadSuccess(data);
                    loadDownloads(); // Refresh downloads list
                } else if (data.status === 'error') {
                    clearInterval(progressInterval);
                    playSound(soundError);
                    showError(data.message || 'Download failed');
                }
            }
        })
        .catch(error => {
            console.error('Error checking progress:', error);
        });
    }
    
    // Update progress UI
    function updateProgressUI(data) {
        const percentage = data.percentage || 0;
        progressBar.style.width = `${percentage}%`;
        progressText.textContent = data.status || 'Downloading...';
        progressPercentage.textContent = `${percentage}%`;
        
        if (data.speed) {
            downloadSpeed.textContent = `Speed: ${data.speed}`;
        }
        
        if (data.eta) {
            downloadEta.textContent = `ETA: ${data.eta}`;
        }
        
        if (data.filename) {
            downloadFilename.textContent = `Filename: ${data.filename}`;
        }
    }
    
    // Show download success
    function showDownloadSuccess(data) {
        downloadStatus.classList.add('hidden');
        downloadSuccess.classList.remove('hidden');
        
        successTitle.textContent = data.title || 'Video';
        successQuality.textContent = data.format || 'Unknown';
        successFilename.textContent = data.filename || 'Unknown';
        
        downloadLink.href = `/api/download/${data.download_id}`;
    }
    
    // Show error
    function showError(message) {
        downloadStatus.classList.add('hidden');
        downloadError.classList.remove('hidden');
        errorMessage.textContent = message;
        playSound(soundError);
    }
    
    // Handle retry button
    function handleRetry() {
        downloadError.classList.add('hidden');
        const url = document.getElementById('url').value.trim();
        const format = document.getElementById('format').value;
        playSound(soundClick);
        
        if (isVercelEnvironment) {
            getVideoInfo(url, format);
        } else {
            startDownload(url, format);
        }
    }
    
    // Reset UI
    function resetUI() {
        // Hide all status containers
        downloadStatus.classList.add('hidden');
        downloadSuccess.classList.add('hidden');
        downloadError.classList.add('hidden');
        
        // Reset progress
        progressBar.style.width = '0%';
        progressText.textContent = '0%';
        progressPercentage.textContent = '0%';
        downloadSpeed.textContent = 'Speed: 0 KB/s';
        downloadEta.textContent = 'ETA: --:--';
        downloadFilename.textContent = 'Filename: --';
        downloadQuality.textContent = 'Quality: --';
        
        // Clear intervals
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }
    }
    
    // Load previous downloads
    function loadDownloads() {
        fetch('/api/downloads')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.downloads.length > 0) {
                noDownloads.classList.add('hidden');
                renderDownloadsList(data.downloads);
            } else {
                noDownloads.classList.remove('hidden');
                downloadsList.innerHTML = '';
                downloadsList.appendChild(noDownloads);
            }
        })
        .catch(error => {
            console.error('Error loading downloads:', error);
        });
    }
    
    // Render downloads list
    function renderDownloadsList(downloads) {
        // Clear the list except for the "no downloads" message
        while (downloadsList.firstChild) {
            downloadsList.removeChild(downloadsList.firstChild);
        }
        
        // Add each download to the list
        downloads.forEach(download => {
            const downloadItem = document.createElement('div');
            downloadItem.className = 'bg-gray-800 p-4 rounded-md';
            
            const title = document.createElement('h3');
            title.className = 'font-bold mb-2 text-terminal-green';
            title.textContent = download.title || 'Unknown Video';
            
            const details = document.createElement('div');
            details.className = 'text-sm text-terminal-gray';
            details.innerHTML = `
                <p>Format: ${download.format || 'Unknown'}</p>
                <p>Downloaded: ${new Date(download.timestamp * 1000).toLocaleString()}</p>
            `;
            
            const downloadBtn = document.createElement('a');
            downloadBtn.href = `/api/download/${download.download_id}`;
            downloadBtn.className = 'block mt-2 py-1 px-3 bg-terminal-green text-black text-sm font-bold rounded hover:bg-green-600 transition-colors text-center';
            downloadBtn.textContent = 'DOWNLOAD';
            
            // Add sound to dynamically created download buttons
            downloadBtn.addEventListener('click', () => playSound(soundClick));
            
            downloadItem.appendChild(title);
            downloadItem.appendChild(details);
            downloadItem.appendChild(downloadBtn);
            
            downloadsList.appendChild(downloadItem);
        });
    }

    // Terminal typing effect for headers
    const terminalTexts = document.querySelectorAll('h2');
    terminalTexts.forEach(text => {
        const originalText = text.textContent;
        text.textContent = '';
        
        let i = 0;
        const typeWriter = () => {
            if (i < originalText.length) {
                text.textContent += originalText.charAt(i);
                if (i % 3 === 0 && soundTyping) playSound(soundTyping); // Play typing sound every few characters
                i++;
                setTimeout(typeWriter, Math.random() * 100 + 50);
            }
        };
        
        setTimeout(() => {
            typeWriter();
        }, Math.random() * 500);
    });
}); 