## API 接口列表
### 1. 聊天接口
- **URL**: `/chat`
- **Method**: `GET`
- **参数**:
  - `text` (str): 用户输入的文本
- **返回**: 
  - `StreamingResponse`: 实时流式响应，包含聊天结果
- **说明**: 根据用户输入的文本，返回聊天结果
### 2. 获取特定对话
- **URL**: `/conversation/{conversation_id}`
- **Method**: `GET`
- **参数**:
  - `conversation_id` (str): 对话ID
- **返回**:
  - `conversation[0]` 或 `{"error": "Not Found"}`: 对话内容或错误信息
- **说明**: 根据对话ID获取特定对话内容
### 3. 获取所有对话
- **URL**: `/conversations`
- **Method**: `GET`
- **参数**: 无
- **返回**:
  - `conversations`: 所有对话的列表
- **说明**: 获取所有对话的列表
### 4. 分页获取对话
- **URL**: `/conversations`
- **Method**: `POST`
- **参数**:
  - `start` (int): 开始位置
  - `limit` (int): 获取数量
- **返回**:
  - `conversations`: 分页后的对话列表
- **说明**: 根据开始位置和获取数量分页获取对话
### 5. 删除对话
- **URL**: `/delete/{conversation_id}`
- **Method**: `GET`
- **参数**:
  - `conversation_id` (str): 对话ID
- **返回**:
  - `res`: 删除结果
- **说明**: 根据对话ID删除特定对话
### 6. 添加对话
- **URL**: `/chat`
- **Method**: `POST`
- **参数**:
  - `text` (str): 用户输入的文本
- **返回**:
  - `conversation`: 新增的对话内容
- **说明**: 添加新的对话，并返回对话内容
### 7. 文本转语音
- **URL**: `/tts`
- **Method**: `GET`
- **参数**:
  - `text` (str): 需要转换的文本
- **返回**:
  - `Response`: 音频文件，媒体类型为`audio/mpeg`
- **说明**: 将文本转换为语音并返回音频文件
### 8. 语音转文本
- **URL**: `/stt`
- **Method**: `POST`
- **参数**:
  - `file` (UploadFile): 上传的音频文件
- **返回**:
  - `{"message": res}`: 转换后的文本信息
  - 或 `JSONResponse`: 错误信息（不支持的文件类型）
- **说明**: 将上传的音频文件转换为文本，并返回转换后的文本信息。如果文件类型不支持，则返回错误信息。
---