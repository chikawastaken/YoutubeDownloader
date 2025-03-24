from flask import Flask, render_template, request, Response
import yt_dlp
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    resolution = request.form['resolution']

    # Resolution mapping to yt-dlp format codes
    resolution_map = {
        "360p": "18",
        "480p": "135+140",
        "720p": "136+140",
        "1080p": "137+140"
    }
    
    format_code = resolution_map.get(resolution, "18")  # Default to 360p

    # Get video title
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        title = info_dict.get('title', 'video')

    filename = f"{title}_{resolution}.mp4"

    # Command to download and stream video
    cmd = [
        "yt-dlp",
        "-f", format_code,
        "-o", "-",  # Output to stdout
        url
    ]

    def generate():
        """ Stream video data in chunks to user. """
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        for chunk in iter(lambda: process.stdout.read(4096), b""):
            yield chunk
        process.stdout.close()
        process.wait()

    return Response(generate(), content_type="video/mp4", headers={
        "Content-Disposition": f"attachment; filename={filename}"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)  # Allows access from other devices
