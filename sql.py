from config import ollama_base_url, llm_model_name, sql_prompt, db_path
import requests
import sqlite3

def get_sql(text):
    with requests.post(ollama_base_url,json={
        "model": llm_model_name,
        "prompt": sql_prompt+text,
        "stream": False,
        "options": {
            "temperature": 0,
            "max_tokens": 256
        }
    }) as response:
        # print(response.content.json()['response'])
        if response.content.decode("utf-8") == "":
            return ""
        return response.json()['response'].split('```')[1].replace('\n',' ').replace('sql','').strip() if response.json()['response'].count('```') > 1 else response.json()['response'].strip()

def get_book_info(sql):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    res = []
    for row in rows:
        res_str = ''
        for i in range(len(row)):
            res_str += f'{row[i]};'
        res.append(res_str)
    return '\n'.join(res)