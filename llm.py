import aiohttp
import json
import requests
from config import ollama_base_url, llm_model_name

# ---------- 大模型通信 ----------
async def ollama_stream(prompt):
    async with aiohttp.ClientSession() as session:
        async with session.post(ollama_base_url,json={
            "model": llm_model_name,  
            "prompt": prompt, 
            "stream": True,          
            "options": {              
                "temperature": 0,     
                "max_tokens": 64800       
                }
            }) as response:
            ans = []
            sentence = ''
            response.raise_for_status()
            try:
                async for reses in response.content.iter_any():
                    lines = reses.decode('utf-8').split('\n')
                    for line in lines:
                        if line:
                            response_text = json.loads(line)['response']
                            sentence += response_text
                            if response_text == '。' or response_text == '？' or response_text == '！' or response_text == '\n' or response_text == '\n\n' :
                                ans.append(sentence)
                                sentence.replace('\n','')
                                yield sentence
                                sentence = ''
            except Exception as e:
                print(e)
                return
            

def ollama(prompt):
    with requests.post(ollama_base_url,json={
        "model": llm_model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "max_tokens": 64800
        }
    }) as response:
        return response.json()['response']