from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str | None = None

class ItemCreate(Item):
    pass

class ItemUpdate(Item):
    pass

