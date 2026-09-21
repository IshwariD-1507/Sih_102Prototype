import re
import pandas as pd


def extract_district_from_ida(ida):
    """
    Extract the district name from the IDA field.

    Example:
    DHARWAD(DEPUTY COMMISSIONER DHARWAR_IDA)
    -> DHARWAD
    """

    if pd.isna(ida):
        return ""

    ida = str(ida).strip()

    if not ida:
        return ""

    district = ida.split("(", 1)[0].strip()

    return district


def extract_place_from_description(description):
    """
    Extract a place name only when the description contains
    a reasonably explicit place/village pattern.

    Romanized regional-language descriptions are left unresolved
    rather than being incorrectly treated as place names.
    """

    if pd.isna(description):
        return ""

    description = str(description).strip()

    if not description:
        return ""

    patterns = [
        # Example:
        # "at Uppinbetageri Village"
        # "at Nulvi Vilage"
        r"\bat\s+([A-Za-z][A-Za-z'-]{2,40})\s+(?:Village|Vilage)\b",

        # Example:
        # "village Bijal"
        r"\b(?:Village|Vilage)\s+([A-Za-z][A-Za-z'-]{2,40})\b",

        # Example:
        # "Neerlgudda village Shiggava TQ"
        # We take the word immediately before "village"
        r"\b([A-Za-z][A-Za-z'-]{2,40})\s+(?:village|vilage)\b",
    ]

    invalid_places = {
        "pry",
        "ward",
        "no",
        "number",
        "colony",
        "block",
        "tq",
        "taluk",
        "tehsil",
        "district",
        "road",
        "near",
        "house",
        "school",
        "college",
        "temple",
        "mandir",
        "math",
        "continued",
        "work",
    }

    for pattern in patterns:
        match = re.search(
            pattern,
            description,
            flags=re.IGNORECASE
        )

        if not match:
            continue

        place = match.group(1).strip(" .,;-")
        place_lower = place.lower()

        if place_lower in invalid_places:
            continue

        # Reject obvious administrative/reference phrases.
        if place_lower in {"tq", "taluk", "tehsil"}:
            continue

        return place

    return ""

def determine_location_confidence(district, place):
    """
    Assign a simple confidence level based on the amount of
    location information explicitly available.
    """
    has_district = bool(str(district).strip())
    has_place = bool(str(place).strip())

    if has_district and has_place:
        return "High"

    if has_district or has_place:
        return "Medium"

    return "Low"


def create_location_features(df):
    """
    Create location-related features from the existing MPLADS data.

    Uses:
        - IDA
        - Work_Description
        - State
        - Constituency

    This module does not generate latitude/longitude.
    """

    df = df.copy()

    # District information from the structured IDA field.
    df["Extracted_District"] = df["IDA"].apply(
        extract_district_from_ida
    )

    # Explicit place information from the work description.
    df["Extracted_Place"] = df["Work_Description"].apply(
        extract_place_from_description
    )

    # Confidence based only on information actually extracted.
    df["Location_Confidence"] = df.apply(
        lambda row: determine_location_confidence(
            row["Extracted_District"],
            row["Extracted_Place"]
        ),
        axis=1
    )

    # Record where the location information came from.
    def determine_source(row):
        has_district = bool(str(row["Extracted_District"]).strip())
        has_place = bool(str(row["Extracted_Place"]).strip())

        if has_district and has_place:
            return "IDA + Description"

        if has_district:
            return "IDA"

        if has_place:
            return "Description"

        return "None"

    df["Location_Source"] = df.apply(
        determine_source,
        axis=1
    )

    return df