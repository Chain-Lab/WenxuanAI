from core import Agent, Message, PromptTemplate
import sqlite3
system_instructions = \
"""
你是一位SQL专家，擅长将自然语言查询转换为SQL语句。
"""
core_instructions = \
"""
请根据用户的查询和表结构，生成一条正确的SQL查询语句。确保只生成一条SQL语句，不要生成多条。
你的任务是生成SQL语句，你在选择下一个Agent时，必须默认已经按照你给出的SQL查询到了需要的结果。

# 数据库表结构
表名为：data。

# 表字段
表字段为如下:
表字段为：[{"id": "INT UNSIGNED AUTO_INCREMENT PRIMARY KEY", "description": "唯一标识符"}, {"title": "VARCHAR(255) NOT NULL", "description": "书名"}, {"author": "VARCHAR(150) NOT NULL", "description": "作者"}, {"isbn": "CHAR(13) UNIQUE NOT NULL", "description": "定长ISBN"}, {"publisher": "VARCHAR(100) NOT NULL", "description": "出版社"}, {"publish_date": "DATE", "description": "出版日期"}, {"price": "DECIMAL(8,2) UNSIGNED", "description": "价格"}, {"page_count": "SMALLINT UNSIGNED", "description": "页数"}, {"category": "VARCHAR(50) NOT NULL DEFAULT '未知'", "description": "分类（从tags提取或默认）"}, {"language": "CHAR(2) DEFAULT 'CN'", "description": "语言代码(ISO标准)"}, {"desc": "TEXT", "description": "图书描述"}, {"stock": "INT UNSIGNED DEFAULT 0", "description": "库存数量"}, {"created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "description": "创建时间"}, {"updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP", "description": "更新时间"}]"""

data_fields = \
"""
"sql": "string"    // 生成一条正确的SQL查询语句
"""

def get_book_info(sql):
    conn = sqlite3.connect('./books.db')
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

class SqlAgent(Agent):
    def __init__(self):
        super().__init__(
            name="sql_agent",
            description="专门用于查询图书数据库，可以获取图书信息、作者、出版详情等。该Agent会根据用户的查询生成SQL语句，并自动执行查询，将结果返回给用户。",
            handles=["图书信息查询", "图书检索", "书籍查询", "出版社查询", "作者查询"],
            parameters={
                "demand": "用户的查询需求",
            }
        )
        self.prompt_template = PromptTemplate(
            system_instructions=system_instructions,
            available_agents=None,
            core_instructions=core_instructions,
            data_fields=data_fields
        )

    def run(self, message:Message) -> Message:
        sql = message.data.get("sql", "")
        # print(f"---------------------SQL: {sql}")
        data = get_book_info(sql)
        message.data = {
            **message.data,
            "result": data
        }
        return message