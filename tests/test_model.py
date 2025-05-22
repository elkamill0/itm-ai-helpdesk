import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from model.sklearn.model import FAQPipeline, FAQPipelineConfig


@pytest.fixture
def mock_config(tmp_path):
    stopwords_path = tmp_path / "stopwords.json"
    stopwords_path.write_text('["a", "b", "c"]', encoding="utf-8")

    file_path = tmp_path / "faq.xlsx"
    df = pd.DataFrame(
        {"Nazwa Błędu": ["Błąd A", "Błąd B"], "Opis Błędu": ["Opis A", "Opis B"]}
    )
    df.to_excel(file_path, index=False)

    return FAQPipelineConfig(
        file_path=str(file_path),
        col_names=["Nazwa Błędu", "Opis Błędu"],
        stopwords_path=str(stopwords_path),
        use_sentence_transformer=False,
    )


def test_pipeline_initialization(mock_config):
    model = FAQPipeline(config=mock_config)
    assert isinstance(model.faq_data, pd.DataFrame)
    assert model.pipeline is not None
    assert model.tfidf_matrix.shape[0] == 2


def test_find_top_answers_tfidf(mock_config):
    model = FAQPipeline(config=mock_config)
    result = model.find_top_answers("Błąd A", top_n=1, similarity_metric="tfidf")
    assert isinstance(result, list)
    assert len(result[0]) == len(mock_config.col_names) + 1
    assert result[0][-1] >= 0


def test_invalid_similarity_metric(mock_config):
    model = FAQPipeline(config=mock_config)
    with pytest.raises(ValueError):
        model.find_top_answers("Błąd A", similarity_metric="unknown")


@patch("model.sklearn.model.SentenceTransformerWrapper")
def test_pipeline_with_sentence_transformer(mock_st, mock_config):
    mock_config.use_sentence_transformer = True
    mock_instance = MagicMock()
    mock_instance.transform.return_value = np.array([[0.1, 0.2]])
    mock_st.return_value = mock_instance

    model = FAQPipeline(config=mock_config)
    result = model.find_top_answers("Błąd A", similarity_metric="combined")
    assert isinstance(result, list)
