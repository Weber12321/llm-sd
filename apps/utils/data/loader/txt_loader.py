import html
from dataclasses import dataclass

from .base_loader import BaseLoader


@dataclass
class TxtLoaderInput:
    file_path: str


@dataclass
class TxtLoaderOutput:
    document: str


class TxtLoader(BaseLoader):
    def __init__(self) -> None:
        super().__init__()

    @property
    def input_class(self):
        return TxtLoaderInput

    @property
    def output_class(self):
        return TxtLoaderOutput

    def execute(self, inputs: TxtLoaderInput) -> TxtLoaderOutput:
        file_path = inputs.file_path
        with open(file_path, "r") as f:
            document = f.read()
        document_html = html.escape(document).replace("\n", "<br>")
        document_html = f"<p>{document_html}</p>"
        return TxtLoaderOutput(document=document_html)
