import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class DuplicateDetector:

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def prepare_text(self, df):
        df = df.copy()

        df["Work_Description_Clean"] = (
            df["Work_Description"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.strip()
        )

        return df

    def generate_embeddings(self, df):
        texts = df["Work_Description_Clean"].tolist()

        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            normalize_embeddings=True
        )

        return embeddings

    def find_similar_projects(self, df, threshold=0.80):

        df = self.prepare_text(df)

        results = []

        grouped = df.groupby(
            ["State", "Work_Category"],
            dropna=False
        )

        for (state, category), group in grouped:

            if len(group) < 2:
                continue

            embeddings = self.generate_embeddings(group)

            similarity_matrix = cosine_similarity(embeddings)

            n = len(group)

            for i in range(n):

                for j in range(i + 1, n):

                    similarity = similarity_matrix[i][j]

                    if similarity >= threshold:

                        results.append({
                            "Work_ID_A": group.iloc[i]["Work_ID"],
                            "Work_ID_B": group.iloc[j]["Work_ID"],
                            "State": state,
                            "Work_Category": category,

                            "Description_A":
                                group.iloc[i]["Work_Description"],

                            "Description_B":
                                group.iloc[j]["Work_Description"],

                            "Semantic_Similarity":
                                round(float(similarity), 4),

                            "Sanction_Amount_A":
                                group.iloc[i]["Sanction_Amount"],

                            "Sanction_Amount_B":
                                group.iloc[j]["Sanction_Amount"],

                            "Sanction_Date_A":
                                group.iloc[i]["Sanction_Date"],

                            "Sanction_Date_B":
                                group.iloc[j]["Sanction_Date"],
                        })

        return pd.DataFrame(results)

    def calculate_overlap_score(self, candidates):

        candidates = candidates.copy()

        # --------------------------------
        # 1. TEXT SIMILARITY
        # --------------------------------

        text_score = (
            candidates["Semantic_Similarity"] * 100
        )

        # --------------------------------
        # 2. COST SIMILARITY
        # --------------------------------

        amount_a = pd.to_numeric(
            candidates["Sanction_Amount_A"],
            errors="coerce"
        )

        amount_b = pd.to_numeric(
            candidates["Sanction_Amount_B"],
            errors="coerce"
        )

        max_amount = pd.concat(
            [amount_a, amount_b],
            axis=1
        ).max(axis=1)

        cost_difference = (
            (amount_a - amount_b).abs()
            / max_amount
        ) * 100

        cost_similarity = (
            100 - cost_difference
        ).clip(lower=0)

        candidates["Cost_Similarity"] = cost_similarity

        # --------------------------------
        # 3. DATE PROXIMITY
        # --------------------------------

        date_a = pd.to_datetime(
            candidates["Sanction_Date_A"],
            errors="coerce"
        )

        date_b = pd.to_datetime(
            candidates["Sanction_Date_B"],
            errors="coerce"
        )

        days_difference = (
            date_a - date_b
        ).abs().dt.days

        # Within 30 days = strongest signal
        # Gradually decreases until 365 days

        date_similarity = (
            100 * (1 - days_difference / 365)
        ).clip(lower=0)

        # Missing dates should not receive a similarity score
        date_similarity = date_similarity.where(
            date_a.notna() & date_b.notna()
        )

        candidates["Date_Similarity"] = date_similarity

        # --------------------------------
        # 4. OVERALL SCORE
        # --------------------------------

        # Prototype weights:
        #
        # Text  = 60%
        # Cost  = 25%
        # Date  = 15%
        #
        # Location will be added later.

        candidates["Overlap_Score"] = (
            text_score * 0.60
            + candidates["Cost_Similarity"].fillna(0) * 0.25
            + candidates["Date_Similarity"].fillna(0) * 0.15
        )

        candidates["Overlap_Score"] = (
            candidates["Overlap_Score"]
            .round(2)
        )

        # --------------------------------
        # 5. REVIEW CATEGORY
        # --------------------------------

        candidates["Review_Category"] = "Low"

        candidates.loc[
            candidates["Overlap_Score"] >= 60,
            "Review_Category"
        ] = "Medium"

        candidates.loc[
            candidates["Overlap_Score"] >= 75,
            "Review_Category"
        ] = "High"

        candidates.loc[
            candidates["Overlap_Score"] >= 90,
            "Review_Category"
        ] = "Critical"

        return candidates