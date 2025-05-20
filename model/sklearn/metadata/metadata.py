from pydantic import BaseModel, Field
from typing import List
import pathlib


class FAQPipelineConfig(BaseModel):
    file_path: pathlib.Path = Field(..., description="Path to the FAQ file")
    col_names: List[str] = Field(..., description="Column names to be used")
    stopwords_path: pathlib.Path = Field(
        "resources/stopwords.json", description="Path to the stopwords file"
    )
    use_sentence_transformer: bool = Field(
        True, description="Whether to use the Sentence Transformer"
    )
