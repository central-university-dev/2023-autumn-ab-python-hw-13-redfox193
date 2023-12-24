from datetime import date

from app.db.database import execute_read_query, execute_query
from app.db.schemas import User, Todo


def get_user_id_by_username(connection, username: str) -> int | None:
    query = '''
        SELECT * FROM users
        WHERE username = %s;
    '''
    user = execute_read_query(connection, query, [username, ])
    if user:
        return user[0][0]
    return None


def get_user_by_username(connection, username) -> User | None:
    query = '''
        SELECT * FROM users
        WHERE username = %s;
    '''
    user = execute_read_query(connection, query, [username, ])
    if user:
        return User(id=user[0][0], username=user[0][1], is_admin=user[0][2], hashed_password=user[0][3])
    return None


def get_todo_list_by_username(connection, username) -> list[Todo]:
    query = '''
        SELECT todos.id, todos.content, todos.owner_id
        FROM todos
        JOIN users ON todos.owner_id = users.id
        WHERE users.username = %s;
    '''
    todo_rows = execute_read_query(connection, query, [username, ])

    todo_list = []
    for todo_data in todo_rows:
        todo = Todo(id=todo_data[0], content=todo_data[1], owner_id=todo_data[2])
        todo_list.append(todo)

    return todo_list


def get_all_usernames(connection) -> list[str]:
    query = '''
        SELECT username FROM users;
    '''
    result = execute_read_query(connection, query)

    usernames = [row[0] for row in result]
    return usernames


def add_user(connection, username: str, is_admin: bool, hashed_password: str) -> None:
    query = '''
        INSERT INTO users (username, is_admin, hashed_password)
        VALUES (%s, %s, %s);
    '''
    execute_query(connection, query, [username, is_admin, hashed_password],
                  success_message=f"User '{username}' added successfully")


def add_todo_by_user_id(connection, owner_id, content) -> None:
    query = '''
        INSERT INTO todos (content, owner_id)
        VALUES (%s, %s);
    '''
    execute_query(connection, query, [content, owner_id],
                  success_message=f"Todo added successfully for user with ID {owner_id}")


def update_todo_content_by_id(connection, todo_id, new_content) -> None:
    query = '''
        UPDATE todos
        SET content = %s
        WHERE id = %s;
    '''
    execute_query(connection, query, [new_content, todo_id],
                  success_message=f"Todo with ID {todo_id} content updated successfully")


def delete_todo_by_id(connection, todo_id) -> None:
    query = '''
        DELETE FROM todos
        WHERE id = %s;
    '''
    execute_query(connection, query, [todo_id, ],
                  success_message=f"Todo with ID {todo_id} deleted successfully")


def delete_user_with_todos_by_username(connection, username) -> None:
    user_query = '''
        SELECT id FROM users
        WHERE username = %s;
    '''
    user_id_result = execute_read_query(connection, user_query, [username, ])

    if user_id_result:
        user_id = user_id_result[0][0]

        delete_todos_query = '''
            DELETE FROM todos
            WHERE owner_id = %s;
        '''
        execute_query(connection, delete_todos_query, [user_id, ],
                      success_message=f"Todos for user '{username}' deleted successfully")

        delete_user_query = '''
            DELETE FROM users
            WHERE id = %s;
        '''
        execute_query(connection, delete_user_query, [user_id, ],
                      success_message=f"User '{username}' and associated todos deleted successfully")
    else:
        print(f"No user found with username '{username}'.")
