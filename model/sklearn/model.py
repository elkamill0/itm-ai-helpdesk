import pandas as pd
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin
from metadata.metadata import FAQPipelineConfig


class SentenceTransformerWrapper(BaseEstimator, TransformerMixin):
    def __init__(self, model_name="paraphrase-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return self.model.encode(X, convert_to_tensor=True).cpu().detach().numpy()


class TfidfWrapper(BaseEstimator, TransformerMixin):
    def __init__(self, stopwords=None):
        self.vectorizer = TfidfVectorizer(stop_words=stopwords)

    def fit(self, X, y=None):
        self.vectorizer.fit(X)
        return self

    def transform(self, X):
        return self.vectorizer.transform(X)


class FAQPipeline:
    def __init__(self, config: FAQPipelineConfig):
        self.use_sentence_transformer = config.use_sentence_transformer
        self.faq_data, self.combined_column = self.__load_faq(
            config.file_path, *config.col_names
        )
        self.stopwords = self.__load_stopwords(config.stopwords_path)
        self.pipeline = self.__create_pipeline()
        if self.use_sentence_transformer:
            self.faq_embeddings = self.pipeline.named_steps[
                "sentence_transformer"
            ].transform(self.combined_column.tolist())

        self.tfidf_matrix = self.pipeline.named_steps["tfidf"].fit_transform(
            self.combined_column.tolist()
        )

    def __load_faq(self, file_path: str, *col_names: str) -> pd.DataFrame:
        df = pd.read_excel(file_path)
        df.dropna(subset=col_names, inplace=True)
        df["combined"] = df[col_names[0]]

        for col in col_names[1:]:
            df["combined"] += " " + df[col]

        combined_column = df["combined"]
        df.drop(columns=["combined"], inplace=True)
        return df, combined_column

    def __load_stopwords(self, file_path: str) -> list:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def __create_pipeline(self) -> Pipeline:
        steps = [("tfidf", TfidfWrapper(stopwords=self.stopwords))]
        if self.use_sentence_transformer:
            steps.append(("sentence_transformer", SentenceTransformerWrapper()))
        return Pipeline(steps)

    def __calculate_tfidf_similarity(self, user_tfidf: csr_matrix) -> np.ndarray:
        return cosine_similarity(user_tfidf, self.tfidf_matrix).flatten()

    def __calculate_sentence_similarity(self, user_question: str) -> np.ndarray:
        user_embedding = self.pipeline.named_steps["sentence_transformer"].transform(
            [user_question]
        )
        similarities = cosine_similarity(user_embedding, self.faq_embeddings).flatten()
        return similarities

    def __calculate_combined_similarity(self, user_question: str) -> np.ndarray:
        user_tfidf = self.pipeline.named_steps["tfidf"].transform([user_question])
        tfidf_similarities = self.__calculate_tfidf_similarity(user_tfidf)
        sentence_similarities = self.__calculate_sentence_similarity(user_question)
        return (tfidf_similarities + sentence_similarities) / 2

    def find_top_answers(
        self, user_question: str, top_n: int = 5, similarity_metric: str = "tfidf"
    ) -> list:
        user_tfidf = self.pipeline.named_steps["tfidf"].transform([user_question])

        if similarity_metric == "tfidf":
            similarities = self.__calculate_tfidf_similarity(user_tfidf)
        elif similarity_metric == "sentence_transformer":
            similarities = self.__calculate_sentence_similarity(user_question)
        elif similarity_metric == "combined":
            similarities = self.__calculate_combined_similarity(user_question)
        else:
            raise ValueError(f"Unknown similarity metric: {similarity_metric}")

        top_indices = similarities.argsort()[-top_n:][::-1]
        top_answers = [
            self.faq_data.iloc[i].tolist() + [similarities[i] * 100]
            for i in top_indices
        ]
        return top_answers


if __name__ == "__main__":
    config = FAQPipelineConfig(
        file_path="resources/Szablon_HD_AI.xlsx",
        col_names=["Nazwa Błędu", "Opis Błędu"],
        use_sentence_transformer=True,
    )

    model = FAQPipeline(config=config)
    user_question = "Mam błąd refifo"
    print(model.find_top_answers(user_question, similarity_metric="tfidf", top_n=1))
    print(
        model.find_top_answers(
            user_question, similarity_metric="sentence_transformer", top_n=1
        )
    )
    print(model.find_top_answers(user_question, similarity_metric="combined", top_n=1))
