"""
data_processing.py  (Member 1 - Dataset & Movie Explorer)
Loads the CSV with Pandas, cleans it, and provides search / filter helpers.
"""

import os
import re
import pandas as pd

# Different CSVs name their columns differently; map common names to ours.
COLUMN_ALIASES = {
    "title":   ["title", "name", "movie_title", "movie", "original_title"],
    "genre":   ["genre", "genres", "listed_in", "category"],
    "year":    ["year", "release_year", "released", "startyear"],
    "runtime": ["runtime", "duration", "runtime_minutes", "runtimeminutes"],
    "rating":  ["rating", "imdb_rating", "averagerating", "average_rating", "vote_average", "score"],
    "votes":   ["votes", "numvotes", "num_votes", "vote_count"],
}

REQUIRED_COLUMNS = ["title", "genre", "year", "rating"]


def load_data(path):
    """Load the CSV file into a DataFrame and standardise column names."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    rename_map = {}
    for standard, aliases in COLUMN_ALIASES.items():
        if standard in df.columns:
            continue
        for alias in aliases:
            if alias in df.columns:
                rename_map[alias] = standard
                break
    df = df.rename(columns=rename_map)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"CSV is missing required columns: {missing}. Found: {list(df.columns)}"
        )

    print(f"[OK] Loaded {len(df)} rows and {len(df.columns)} columns from '{path}'")
    return df


def _to_number(series):
    """Convert things like '1,234' or '120 min' to numbers (invalid -> NaN)."""
    cleaned = series.astype(str).str.replace(",", "", regex=False)
    extracted = cleaned.str.extract(r"(\d+\.?\d*)")[0]
    return pd.to_numeric(extracted, errors="coerce")


def clean_data(df):
    """Remove duplicates, handle missing values and fix data types."""
    df = df.copy()
    start_rows = len(df)

    # Trim whitespace in text columns
    for col in ["title", "genre"]:
        df[col] = df[col].astype(str).str.strip().replace({"nan": None, "": None})

    # Numeric columns
    for col in ["year", "rating", "runtime", "votes"]:
        if col in df.columns:
            df[col] = _to_number(df[col])

    # Duplicates (same title + year)
    df = df.drop_duplicates(subset=["title", "year"], keep="first")
    dup_removed = start_rows - len(df)

    # Rows missing essential info cannot be used
    df = df.dropna(subset=["title", "year", "rating"])

    # Fill the rest
    df["genre"] = df["genre"].fillna("Unknown")
    if "runtime" in df.columns:
        df["runtime"] = df["runtime"].fillna(df["runtime"].median())
    if "votes" in df.columns:
        df["votes"] = df["votes"].fillna(0).astype(int)

    df["year"] = df["year"].astype(int)
    df = df.reset_index(drop=True)

    print(f"[OK] Cleaning done: {dup_removed} duplicates removed, "
          f"{start_rows - dup_removed - len(df)} incomplete rows dropped, "
          f"{len(df)} rows remain")
    return df


def split_genres(genre_text):
    """'Action, Drama' or 'Action|Drama' -> ['Action', 'Drama']"""
    return [g.strip() for g in re.split(r"[,|]", str(genre_text)) if g.strip()]


def get_all_genres(df):
    """Return a sorted list of all unique genres in the dataset."""
    genres = set()
    for value in df["genre"]:
        genres.update(split_genres(value))
    return sorted(genres)


def search_movie(df, query):
    """Case-insensitive search of movie titles (partial match allowed)."""
    mask = df["title"].str.contains(query.strip(), case=False, regex=False, na=False)
    return df[mask]


def filter_by_genre(df, genre):
    """Return movies whose genre text contains the given genre."""
    mask = df["genre"].str.contains(genre.strip(), case=False, regex=False, na=False)
    return df[mask]


def filter_by_year(df, start_year, end_year=None):
    """Return movies released between start_year and end_year (inclusive)."""
    if end_year is None:
        end_year = start_year
    if start_year > end_year:
        start_year, end_year = end_year, start_year
    return df[(df["year"] >= start_year) & (df["year"] <= end_year)]


def display_movie_details(df, limit=10):
    """Print movie details in a readable table. Uses tuples for fixed details."""
    if df.empty:
        print("  No movies found.")
        return

    print(f"\n  Showing {min(limit, len(df))} of {len(df)} result(s)\n")
    print(f"  {'No':<4}{'Title':<38}{'Year':<7}{'Rating':<8}{'Genre'}")
    print("  " + "-" * 85)
    for i, (_, row) in enumerate(df.head(limit).iterrows(), start=1):
        details = (row["title"], int(row["year"]), float(row["rating"]))  # tuple
        title = details[0] if len(details[0]) <= 36 else details[0][:33] + "..."
        print(f"  {i:<4}{title:<38}{details[1]:<7}{details[2]:<8}{row['genre']}")

    extras = []
    if "runtime" in df.columns:
        extras.append("runtime")
    if "votes" in df.columns:
        extras.append("votes")
    if extras and len(df) == 1:
        row = df.iloc[0]
        print("\n  " + " | ".join(f"{c}: {row[c]}" for c in extras))
