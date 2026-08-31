import sqlite3 #导入sqlite工具


DATABASE = "chat.db"#指定数据库文件名



def get_connection():

    conn = sqlite3.connect(DATABASE)#连接数据库 文件不存在就创建它

    return conn



def init_db():

    conn = get_connection()#连接数据库

    cursor = conn.cursor() #cursor 可以理解为“执行 SQL 命令的工具”。


    cursor.execute(#让数据库执行一条命令
        """
        CREATE TABLE IF NOT EXISTS messages(
        
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        
        user_id INTEGER,
        
        conversation_id INTEGER,
        
        role TEXT,
        
        content TEXT
        
        
        )
        """
    )#""" 这是Python保存的多行字符串  真正的SQL是message（。。。）
    #括号里面是在定义表的列
    conn.commit()
    
    conn.close()
def get_history(user_id, conversation_id):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT role,content
        FROM messages
        WHERE user_id=?
        AND conversation_id=?
        ORDER BY id
        """,#按照消息编号排序，保证聊天顺序。
        (user_id,conversation_id)
    )


    rows = cursor.fetchall()#取出查询到的所有记录。


    conn.close()


    messages=[]


    for row in rows:#for 循环把数据库记录重新整理成大模型需要的格式

        messages.append(
            {
                "role":row[0],
                "content":row[1]
            }
        )


    return messages
def save_message(user_id, conversation_id, role, content):#它的作用是把一条消息写入数据库

    conn=get_connection()

    cursor=conn.cursor()


    cursor.execute(
        """
        INSERT INTO messages
        (user_id,role,content,conversation_id)

        VALUES(?,?,?,?)
        """,#使用 ? 而不是直接拼接字符串，是更安全、更规范的数据库参数传递方式
        (
            user_id,
            role,
            content,
            conversation_id
            
        )
    )


    conn.commit()

    conn.close()

   