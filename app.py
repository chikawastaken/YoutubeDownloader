import yt_dlp
from flask import Flask, render_template, request, Response

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    resolution = request.form['resolution']

    # Resolution mapping
    resolution_map = {
        "360p": "18",
        "480p": "135+140",
        "720p": "136+140",
        "1080p": "137+140"
    }
    
    format_code = resolution_map.get(resolution, "18")

    # yt-dlp options with cookies
    ydl_opts = {
        'format': format_code,
        'noplaylist': True,
        'quiet': True,
        'cookies': 'youtube_cookies.txt'  # <-- Use cookies file
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        title = info_dict.get('title', 'video')

    filename = f"{title}_{resolution}.mp4"

    def generate():
        """Stream video to user"""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            proc = ydl.popen(['-f', format_code, '-o', '-'], stdout=yt_dlp.PIPE)
            for chunk in iter(lambda: proc.stdout.read(4096), b""):
                yield chunk

    return Response(generate(), content_type="video/mp4", headers={
        "Content-Disposition": f"attachment; filename={filename}"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
