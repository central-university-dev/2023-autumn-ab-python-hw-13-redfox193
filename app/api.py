import enum
import json

from app.util import get_password_hash
from app.db import crud
from app.db import database
from app.db import schemas
from http_exceptions import HTTPException


class Api:
    def __init__(self):
        connection = database.create_connection(database.connection_data)
        database.create_tables(connection)
        connection.close()

        self.api_roots = {
            '/add_user': {'method_type': 'PUT', 'body_model': schemas.UserCreate, 'func': self.add_user},
            '/add_todo': {'method_type': 'PUT', 'body_model': schemas.TodoCreate, 'func': self.add_todo},
        }
        pass

    async def send_responce(self, send, status_code: int, headers: list[tuple], body: bytes):
        await self.send_start(send, status_code, headers)
        await self.send_body(send, body)

    async def send_start(self, send, status_code: int, headers: list[tuple]):
        await send({
            'type': 'http.response.start',
            'status': status_code,
            'headers': headers
        })

    async def send_body(self, send, body: bytes):
        await send({
            'type': 'http.response.body',
            'body': body,
        })

    async def process_request(self, method: str, path: str, body: dict, send) -> None:
        path_list = path.split('/')[1:]
        try:
            if path in self.api_roots:
                if method == self.api_roots[path]['method_type']:
                    await self.api_roots[path]['func'](send, body)
                else:
                    raise HTTPException.from_status_code(405)
            else:
                raise HTTPException.from_status_code(405)
        except HTTPException as http:
            await self.send_responce(send,
                                     status_code=http.status_code,
                                     headers=[(b'content-type', b'application/json')],
                                     body=str.encode(http.message)
                                     )

    async def add_user(self, send, body: dict) -> None:
        try:
            new_user = schemas.UserCreate.model_validate(body)
        except Exception as e:
            raise HTTPException.from_status_code(422)
        hashed_password = get_password_hash(new_user.password)

        connection = database.create_connection(database.connection_data)
        try:
            crud.add_user(connection, new_user.username, new_user.is_admin, hashed_password)
            added_user = crud.get_user_by_username(connection, new_user.username)
            connection.close()
        except Exception as e:
            connection.close()
            raise HTTPException.from_status_code(400)

        await self.send_responce(send,
                                 status_code=200,
                                 headers=[(b'content-type', b'application/json')],
                                 body=added_user.model_dump_json().encode())

    async def add_todo(self, send, body):
        try:
            new_todo = schemas.TodoCreate.model_validate(body)
        except Exception as e:
            raise HTTPException.from_status_code(422)

        connection = database.create_connection(database.connection_data)
        try:
            owner_id = crud.get_user_id_by_username(connection, new_todo.owner_username)
            connection.close()

            connection = database.create_connection(database.connection_data)
            crud.add_todo_by_user_id(connection, owner_id, new_todo.content)
            connection.close()

            connection = database.create_connection(database.connection_data)
            todo_list = crud.get_todo_list_by_username(connection, new_todo.owner_username)
            connection.close()
        except Exception as e:
            print(e)
            connection.close()
            raise HTTPException.from_status_code(400)

        await self.send_responce(send,
                                 status_code=200,
                                 headers=[(b'content-type', b'application/json')],
                                 body=json.dumps([model.model_dump() for model in todo_list]).encode())


api = Api()
