import sqlite3


DATABASE = "chat.db"



def get_connection():

    conn = sqlite3.connect(DATABASE)

    return conn



def init_db():

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages(
        
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        
        user_id INTEGER,
        
        role TEXT,
        
        content TEXT
        
        )
        """
    )
    conn.commit()
    
    conn.close()
def get_history(user_id):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT role,content
        FROM messages
        WHERE user_id=?
        ORDER BY id
        """,
        (user_id,)
    )


    rows = cursor.fetchall()


    conn.close()


    messages=[]


    for row in rows:

        messages.append(
            {
                "role":row[0],
                "content":row[1]
            }
        )


    return messages
def save_message(user_id, role, content):

    conn=get_connection()

    cursor=conn.cursor()


    cursor.execute(
        """
        INSERT INTO messages
        (user_id,role,content)

        VALUES(?,?,?)
        """,
        (
            user_id,
            role,
            content
        )
    )


    conn.commit()

    conn.close()

   