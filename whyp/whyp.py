import requests
import re
import sys

headers = {
    "Referer": "https://www.whyp.it/",
}

def get_audio_name(url: str) -> str:
    resp = requests.get(url).content.decode("utf8")
    return re.search(r"\w{8}-\w{4}-\w{4}-\w{4}-\w{12}.mp3", resp).group()

def download_file(audio_name: str):
    req = requests.get(f"https://cdn.whyp.it/{audio_name}", headers=headers, stream=True)
    with open(audio_name, "wb") as f:
        for chunk in req.iter_content(chunk_size=1024):
            f.write(chunk)

if __name__ == "__main__":
    audio_name = get_audio_name(sys.argv[1])
    download_file(audio_name)
