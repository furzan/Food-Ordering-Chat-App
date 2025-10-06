from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
import uuid

class Users(SQLModel, table=True):
    username: str = Field(primary_key=True, index=True)
    password: str

    def __repr__(self):
        return f"<User {self.username}>"
