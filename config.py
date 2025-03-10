# ---------- 配置信息 ----------
ollama_base_url = 'http://113.54.158.149:11434/api/generate'
num_workers = 4
model_path = '/home/zwc/.cache/huggingface/hub/models--Systran--faster-whisper-large-v3/snapshots/edaa852ec7e145841d8ffdb056a99866b5f0a478'
model_size = "large-v3"
conversation_db_path = './history.db'
db_path = './books.db'
temp_path = './temp'
llm_model_name = 'qwen2.5:14b' # qwen2.5:14b glm4:latest
sql_prompt = '''你需要将用户的需求转换为合适的sql语句，用于查询数据库，注意：如果需要查询的的字段数据库中没有，你必须返回空字符串，不要用其它字段代替。
只给出sql语句，不要解释。
数据库名为：data。
数据库字段为如下:
{
  [
    {
      "name": "title",
      "meaning": "书名"
    },
    {
      "name": "author",
      "meaning": "作者"
    },
    {
      "name": "isbn",
      "meaning": "国际标准书号"
    },
    {
      "name": "publisher",
      "meaning": "出版社"
    },
    {
      "name": "original_name",
      "meaning": "原书名"
    },
    {
      "name": "subtitle",
      "meaning": "副标题"
    },
    {
      "name": "translator",
      "meaning": "译者"
    },
    {
      "name": "publication_date",
      "meaning": "出版日期"
    },
    {
      "name": "no_of_pages",
      "meaning": "页数"
    },
    {
      "name": "cover",
      "meaning": "封面类型"
    },
    {
      "name": "collection",
      "meaning": "系列或丛书"
    },
    {
      "name": "users_rating",
      "meaning": "用户评分"
    },
    {
      "name": "description",
      "meaning": "书籍简介"
    },
    {
      "name": "author_description",
      "meaning": "作者简介"
    },
    {
      "name": "price",
      "meaning": "书籍价格"
    },
    {
      "name": "tags",
      "meaning": "标签"
    },
  ]
}
用户需求：'''
res_prompt = '''你是一个系统助理。请根据数据库中的查询到的书籍信息相关信息，回答用户的问题(请使用编辑人员能够理解的表达方式，不要使用markdown语法)。
(注意：如果SQL语句是空的，或者查询的结果和用户的问题不符合，说明数据库中没有用户想要查询的数据对应的字段或者数据，你需要给一个友好的回复以提示用户，而不是展示错误的结果，同时注意不要使用专业性的语言描述，例如出现SQL这样的关键字，尽可能通俗易懂)。
用户的问题是：{}
查询数据库的SQL语句如下：
{}
查询的结果如下(如果结果为空，说明没有找到相应的数据，此时需要以友好的形式将这种情况反馈给用户，不要编造数据)：
{}
'''
system_prompt = '''请根据数据库中的查询到的书籍信息相关信息，没有数据返回空即可，不要编造数据，以markdown语法整理(尽量使用表格、分点等方式)
(注意：如果SQL语句是空的，或者查询的结果和用户的问题不符合，说明数据库中没有用户想要查询的数据对应的字段或者数据，你需要给一个友好的回复以提示用户，而不是展示错误的结果，同时注意不要使用专业性的语言描述，例如出现SQL这样的关键字，尽可能通俗易懂)。
查询数据库的SQL语句如下：
{}
查询的结果如下：
{}
'''


