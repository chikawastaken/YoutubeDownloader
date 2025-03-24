from flask import Flask, render_template, request, Response
import yt_dlp

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

    # Define download options for yt-dlp
    ydl_opts = {
        'format': format_code,
        'noplaylist': True,  # Download only one video, not the whole playlist
        'quiet': True
    }

    def generate():
        """ Stream the video file directly to the user. """
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)  # Get video info
            title = info_dict.get('title', 'video')
            filename = f"{title}_{resolution}.mp4"

            # Pipe video data to response
            ydl_opts['outtmpl'] = '-'
            ydl_opts['merge_output_format'] = 'mp4'
            ydl_opts['progress_hooks'] = [lambda d: None]  # Prevent progress logs

            with ydl.popen(['-f', format_code, '-o', '-'], stdout=yt_dlp.PIPE) as proc:
                for chunk in iter(lambda: proc.stdout.read(4096), b""):
                    yield chunk

    return Response(generate(), content_type="video/mp4", headers={
        "Content-Disposition": f"attachment; filename={filename}"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)  # Allows access from other devices on the network
