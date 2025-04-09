from flask import Flask, render_template, request, Response, redirect, url_for
import yt_dlp
import subprocess
import os
import sys
import uuid

app = Flask(__name__)

# Store active downloads
active_downloads = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def start_download():
    url = request.form['url']
    resolution = request.form['resolution']
    
    download_id = str(uuid.uuid4())
    active_downloads[download_id] = {'url': url, 'resolution': resolution}
    
    return redirect(url_for('download', download_id=download_id))

@app.route('/download/<download_id>')
def download(download_id):
    if download_id not in active_downloads:
        return "Invalid download request", 404
    
    url = active_downloads[download_id]['url']
    resolution = active_downloads[download_id]['resolution']
    
    resolution_map = {
        "360p": "18",
        "480p": "135+140",
        "720p": "136+140",
        "1080p": "137+140"
    }
    format_code = resolution_map.get(resolution, "18")
    
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        title = info_dict.get('title', 'video')
    
    safe_title = "".join(c if c.isalnum() or c in " -_()" else "_" for c in title)
    filename = f"{safe_title}_{resolution}.mp4"
    
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "-f", format_code,
        "-o", "-",
        "--merge-output-format", "mp4",
        url
    ]
    
    def generate():
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=4096)
        for chunk in iter(lambda: process.stdout.read(4096), b""):
            yield chunk
        del active_downloads[download_id]
    
    return Response(generate(), content_type="video/mp4", headers={
        "Content-Disposition": f"attachment; filename={filename.encode('utf-8').decode('latin-1', 'ignore')}"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
