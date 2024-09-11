from pydantic import BaseModel

class CreateTableRequest(BaseModel):
    table_name: str


class SearchRequest(BaseModel):
    query: str
    table: str
    
    
class ChatRequest(BaseModel):
    query: str
    use_rag: bool
    rag_table: str