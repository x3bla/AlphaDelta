import yt_dlp

# yt_dlp.utils.bug_reports_message = lambda: ''  # no idea what this does

# https://github.com/ytdl-org/youtube-dl/blob/master/README.md#post-processing-options
ytdlp_format_options = {  # sets the quality of the audio
    'format': 'worstaudio',
    'outtmpl': 'zz-%(id)s-%(title)s.%(ext)s',  # z to put it at the most bottom
    'restrictfilenames': True,
    'noplaylist': False,
    'ignoreerrors': True,
    'logtostderr': False,
    # 'cookiefile': "./Cookies",
    # 'concurrent_fragment_downloads': 5,  # parallel downloading, if needed
    # 'max_filesize': 5000000,  # 5MB bytes | look at getVideoData
    'quiet': False,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}  # spam of comments to see which is unneeded

ytdl = yt_dlp.YoutubeDL(ytdlp_format_options)  # loading youtube download options

async def get_info(search_string):  # returns video info
    data = ytdl.extract_info(search_string, download=False)
    if data is None:
        return None

    entries = data.get('entries')
    if entries is not None:
        if len(entries) > 0:
            entry = entries[0]
        else:
            return None
    else:
        entry = data

    if entry["duration"] > 3600:  # if audio is longer than 1 hour, say no
        return False
    else:
        return entry

async def get_file(url):  # returns file name
    info = ytdl.extract_info(url, download=True)
    file_name = ytdl.prepare_filename(info)
    return file_name

