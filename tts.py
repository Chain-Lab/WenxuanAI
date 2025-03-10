import requests

def tts(text):
    ref_audio = '/home/zwc/tts/GPT-SoVITS-main/nahida.mp3'
    prompt_text = "过去的经历，使你成为了一个对我和须弥有用的个体，拉拢你的确是我计划的一部分"
    url = 'http://113.54.158.149:9880/tts'
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