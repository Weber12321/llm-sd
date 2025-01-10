from pydantic import BaseModel


class PromptItem(BaseModel):
    name: str  # name of the prompt, e.g. "查詢結果"
    content: str  # the prompt, e.g. "請問我要查詢什麼？"
    order: int  # the order of the prompt, e.g. 1
    need_parse: bool  # whether the prompt needs to be parsed, e.g. True
    placehold: bool  # whether the prompt needs to be replaced when saved, e.g. True
