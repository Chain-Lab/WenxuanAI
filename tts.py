import requests
from config import tts_url, ref_audio_path, ref_audio_text

def tts(text):
    ref_audio = ref_audio_path
    prompt_text = ref_audio_text
    url = tts_url
    test_times = 3
    res = None
    while test_times > 0:
        res = requests.post(url, json={
            "text": "" + text,
            "text_lang": "zh",
            "ref_audio_path": ref_audio,
            "prompt_lang": "zh",
            "prompt_text": prompt_text,
            "text_split_method": "cut5",
            "batch_size": 1,
            "media_type": "wav",
            "streaming_mode": False
        }, headers={'Content-Type': 'application/json'})
        if res.status_code == 200:
            return res.content
        test_times -= 1
    print(f'Error: {res.content}') if res.status_code != 200 else None