from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors


class DuplicateDetector:
    """
    Detects potentially overlapping MPLADS projects using
    semantic similarity plus financial/date signals.

    IMPORTANT:
    A candidate is a screening signal only.
    It does NOT establish that two projects are duplicates,
    fraudulent, or improperly funded.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        self.model = SentenceTransformer(model_name)

    # =====================================================
    # TEXT PREPARATION
    # =====================================================

    @staticmethod
    def prepare_text(
        df: pd.DataFrame
    ) -> pd.DataFrame:

        df = df.copy()

        if "Work_Description" not in df.columns:

            df["Work_Description"] = ""

        df["Work_Description_Clean"] = (
            df["Work_Description"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

        return df

    # =====================================================
    # DISTRICT EXTRACTION
    # =====================================================

    @staticmethod
    def add_district(
        df: pd.DataFrame
    ) -> pd.DataFrame:

        df = df.copy()

        if "district" in df.columns:

            df["district"] = (
                df["district"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            return df

        if "IDA" in df.columns:

            ida = (
                df["IDA"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            district = (
                ida
                .str.split(
                    "(",
                    n=1
                )
                .str[0]
                .str.strip()
            )

            # Mumbai City special case
            district = district.where(
                ~ida.str.contains(
                    "MUMBAI CITY_IDA",
                    case=False,
                    na=False
                ),
                "Mumbai City"
            )

            df["district"] = district

        else:

            df["district"] = ""

        return df

    # =====================================================
    # EMBEDDINGS
    # =====================================================

    def generate_embeddings(
        self,
        df: pd.DataFrame,
    ) -> np.ndarray:

        texts = (
            df["Work_Description_Clean"]
            .tolist()
        )

        if not texts:

            return np.empty(
                (0, 384),
                dtype=np.float32
            )

        return self.model.encode(
            texts,
            show_progress_bar=True,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

    # =====================================================
    # FIND SIMILAR PROJECTS
    # =====================================================

    def find_similar_projects(
        self,
        df: pd.DataFrame,
        threshold: float = 0.80,
        max_neighbors: int = 30,
    ) -> pd.DataFrame:

        df = self.prepare_text(df)
        df = self.add_district(df)

        # -------------------------------------------------
        # Required columns
        # -------------------------------------------------

        required = [
            "Work_ID",
            "Work_Description",
            "State",
            "Work_Category",
        ]

        missing = [
            column
            for column in required
            if column not in df.columns
        ]

        if missing:

            raise ValueError(
                "Duplicate detection requires "
                f"these columns: {missing}"
            )

        # -------------------------------------------------
        # Remove records without meaningful text
        # -------------------------------------------------

        usable = df[
            df["Work_Description_Clean"].str.len() >= 10
        ].copy()

        if usable.empty:

            return pd.DataFrame()

        # -------------------------------------------------
        # Normalize blocking columns
        # -------------------------------------------------

        usable["_state_block"] = (
            usable["State"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
        )

        usable["_category_block"] = (
            usable["Work_Category"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # Do NOT put missing State/Category into one enormous
        # comparison group.
        usable = usable[
            (usable["_state_block"] != "")
            & (usable["_category_block"] != "")
        ].copy()

        if usable.empty:

            return pd.DataFrame()

        results: List[dict] = []

        # =================================================
        # BLOCK BY STATE + CATEGORY
        # =================================================

        grouped = usable.groupby(
            [
                "_state_block",
                "_category_block",
            ],
            sort=False,
        )

        for (
            state_block,
            category_block,
        ), group in grouped:

            if len(group) < 2:
                continue

            group = group.reset_index(
                drop=True
            )

            # ---------------------------------------------
            # Generate embeddings
            # ---------------------------------------------

            embeddings = self.generate_embeddings(
                group
            )

            if len(embeddings) < 2:
                continue

            # ---------------------------------------------
            # Radius search instead of full NxN matrix
            #
            # Cosine distance = 1 - cosine similarity
            # ---------------------------------------------

            radius = 1.0 - threshold

            neighbors_model = NearestNeighbors(
                metric="cosine",
                radius=radius,
                algorithm="brute",
                n_jobs=-1,
            )

            neighbors_model.fit(
                embeddings
            )

            distances, indices = (
                neighbors_model.radius_neighbors(
                    embeddings,
                    return_distance=True,
                    sort_results=True,
                )
            )

            for i in range(len(group)):

                for distance, j in zip(
                    distances[i],
                    indices[i],
                ):

                    # Skip self
                    if i >= j:
                        continue

                    similarity = (
                        1.0 - float(distance)
                    )

                    if similarity < threshold:
                        continue

                    row_a = group.iloc[i]
                    row_b = group.iloc[j]

                    results.append(
                        {
                            "Work_ID_A":
                                row_a["Work_ID"],

                            "Work_ID_B":
                                row_b["Work_ID"],

                            "State":
                                row_a["State"],

                            "Work_Category":
                                row_a["Work_Category"],

                            "district":
                                row_a["district"],

                            "Description_A":
                                row_a["Work_Description"],

                            "Description_B":
                                row_b["Work_Description"],

                            "Semantic_Similarity":
                                round(
                                    similarity,
                                    4
                                ),

                            "Sanction_Amount_A":
                                row_a.get(
                                    "Sanction_Amount",
                                    np.nan
                                ),

                            "Sanction_Amount_B":
                                row_b.get(
                                    "Sanction_Amount",
                                    np.nan
                                ),

                            "Sanction_Date_A":
                                row_a.get(
                                    "Sanction_Date",
                                    pd.NaT
                                ),

                            "Sanction_Date_B":
                                row_b.get(
                                    "Sanction_Date",
                                    pd.NaT
                                ),
                        }
                    )

        return pd.DataFrame(results)

    # =====================================================
    # CALCULATE OVERLAP SCORE
    # =====================================================

    def calculate_overlap_score(
        self,
        candidates: pd.DataFrame,
    ) -> pd.DataFrame:

        candidates = candidates.copy()

        if candidates.empty:

            return candidates

        # -------------------------------------------------
        # TEXT SIMILARITY
        # -------------------------------------------------

        text_score = (
            pd.to_numeric(
                candidates[
                    "Semantic_Similarity"
                ],
                errors="coerce",
            )
            .fillna(0)
            * 100
        )

        # -------------------------------------------------
        # COST SIMILARITY
        # -------------------------------------------------

        amount_a = pd.to_numeric(
            candidates[
                "Sanction_Amount_A"
            ],
            errors="coerce",
        )

        amount_b = pd.to_numeric(
            candidates[
                "Sanction_Amount_B"
            ],
            errors="coerce",
        )

        max_amount = pd.concat(
            [
                amount_a,
                amount_b,
            ],
            axis=1,
        ).max(axis=1)

        cost_difference = (
            (amount_a - amount_b).abs()
            / max_amount.replace(
                0,
                np.nan
            )
        ) * 100

        cost_similarity = (
            100 - cost_difference
        ).clip(
            lower=0,
            upper=100,
        )

        # If either amount is unavailable,
        # do not pretend the cost signal exists.
        cost_similarity = cost_similarity.where(
            amount_a.notna()
            & amount_b.notna()
            & max_amount.notna()
        )

        candidates[
            "Cost_Similarity"
        ] = cost_similarity

        # -------------------------------------------------
        # DATE PROXIMITY
        # -------------------------------------------------

        date_a = pd.to_datetime(
            candidates[
                "Sanction_Date_A"
            ],
            errors="coerce",
        )

        date_b = pd.to_datetime(
            candidates[
                "Sanction_Date_B"
            ],
            errors="coerce",
        )

        days_difference = (
            date_a - date_b
        ).abs().dt.days

        date_similarity = (
            100
            * (
                1
                - days_difference / 365
            )
        ).clip(
            lower=0,
            upper=100,
        )

        date_similarity = date_similarity.where(
            date_a.notna()
            & date_b.notna()
        )

        candidates[
            "Date_Similarity"
        ] = date_similarity

        # -------------------------------------------------
        # OVERALL SCORE
        # -------------------------------------------------

        # Text: 60%
        # Cost: 25%
        # Date: 15%
        #
        # Missing secondary signals are excluded from
        # the numerator and their weight is redistributed.
        # This prevents missing data from automatically
        # reducing the score.

        text_component = (
            text_score * 0.60
        )

        cost_component = (
            candidates[
                "Cost_Similarity"
            ].fillna(0)
            * 0.25
        )

        date_component = (
            candidates[
                "Date_Similarity"
            ].fillna(0)
            * 0.15
        )

        available_weight = (
            0.60
            + candidates[
                "Cost_Similarity"
            ].notna().astype(float) * 0.25
            + candidates[
                "Date_Similarity"
            ].notna().astype(float) * 0.15
        )

        raw_score = (
            text_component
            + cost_component
            + date_component
        )

        candidates[
            "Overlap_Score"
        ] = (
            raw_score
            / available_weight
        ).clip(
            0,
            100,
        ).round(2)

        # -------------------------------------------------
        # REVIEW CATEGORY
        # -------------------------------------------------

        candidates[
            "Review_Category"
        ] = "Low"

        candidates.loc[
            candidates[
                "Overlap_Score"
            ] >= 60,
            "Review_Category",
        ] = "Medium"

        candidates.loc[
            candidates[
                "Overlap_Score"
            ] >= 75,
            "Review_Category",
        ] = "High"

        candidates.loc[
            candidates[
                "Overlap_Score"
            ] >= 90,
            "Review_Category",
        ] = "Critical"

        return candidates