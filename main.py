import os
import uuid
import json
import uvicorn
from fastapi import Form, UploadFile, File, Response
from config import model_path, temp_path, conversation_db_path
from tempManager import TempCleanScheduler, async_temp_cleaner
from fastapi.responses import JSONResponse
# from faster_whisper import WhisperModel
from tts import tts
from fastapi import FastAPI
from chatManager import ChatHistoryManager
from config import *
from core import AgentManager
import os
import logging

log = logging.getLogger('app')
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.DEBUG) 



# whisper_model = WhisperModel(model_size_or_path=model_path, device="cuda", compute_type="int8_float16")
whisper_model = None
agent_manager  = AgentManager(
                        plugin_src=agent_path, 
                        base_url=base_url, 
                        api_key=api_key, 
                        model_name=llm_model_name,
                    )

app = FastAPI(lifespan=async_temp_cleaner)
if not os.path.exists(temp_path):
    os.makedirs(temp_path)

def new_conversation_context():
    return {
        "conversation_id": str(uuid.uuid4()),
        "message": []
    }

def add_message_to_conversation(conversation, role, content, markdown=""):
    conversation["message"].append({"role": role, "content": content, "markdown": markdown})


# ---------- API接口 ----------

@app.get("/conversation/{conversation_id}")
def get_conversation(conversation_id: str):
    with ChatHistoryManager(conversation_db_path) as chm:
        conversation = chm.get_conversation(conversation_id)
    return conversation[0] if len(conversation) > 0 else {"error": "Not Found"}

@app.get("/conversations")
def get_all_conversations():
    with ChatHistoryManager(conversation_db_path) as chm:
        conversations = chm.get_all_conversations() 
    return conversations

@app.post("/conversations")
def get_conversations(start:int= Form(...), limit:int= Form(...)):
    with ChatHistoryManager(conversation_db_path) as chm:
        conversations = chm.get_conversation_by_least_nums(start, limit)
    return conversations

@app.get("/delete/{conversation_id}")
def delete_conversation(conversation_id: str):
    with ChatHistoryManager(conversation_db_path) as chm:
        res = chm.delete_record(conversation_id)
    return res

@app.post("/chat")
def add_conversation(text:str = Form(...)):
    conversation = new_conversation_context()
    conversation_id = conversation["conversation_id"]
    result = json.loads(agent_manager(text)[-1]['content'])['data']['answer']
    # print(result)
    add_message_to_conversation(conversation, "user", text)
    add_message_to_conversation(conversation, "assistant", result, "")
    with ChatHistoryManager(conversation_db_path) as chm:
        chm.add_record(conversation_id, json.dumps(conversation))
    return conversation

@app.get("/tts")
def get_audio(text:str):
    return Response(tts(text), media_type="audio/mpeg")

@app.post("/stt")
async def get_text(file: UploadFile = File(...)):
    global temp_path, whisper_model
    if not file.content_type.startswith('audio/'):
        return JSONResponse(status_code=415, content={"message": "Unsupported file type"})
    filename = f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"
    file_path = os.path.join(temp_path, filename)
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    segments, info = whisper_model.transcribe(file_path, beam_size=5)
    res = ''
    for segment in segments:
        res += segment.text
    return {"message": res}



if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=9876)
