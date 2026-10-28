"""
recommendation.py  (Member 3 - Recommendation & File Handling)
Recommendation logic, the menu, and saving reports to TXT / CSV.
"""

import os
from datetime import datetime

from data_processing import filter_by_genre, filter_by_year
from analytics import (calculate_statistics, get_top_movies,
                       analyze_genres, genre_average_rating)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")


def recommend_movies(df, genre=None, min_rating=0.0, year_from=None,
                     year_to=None, top_n=10):
    """Return movies matching the preferences, sorted by rating (best first)."""
    result = df
    if genre:
        result = filter_by_genre(result, genre)
    if year_from is not None:
        result = filter_by_year(result, year_from, year_to if year_to else 9999)
    result = result[result["rating"] >= min_rating]

    sort_cols = ["rating"] + (["votes"] if "votes" in result.columns else [])
    return result.sort_values(sort_cols, ascending=False).head(top_n)


def display_menu():
    """Print the main menu and return the user's choice as a string."""
    print("\n" + "=" * 52)
    print("      MOVIE RECOMMENDATION & ANALYSIS SYSTEM")
    print("=" * 52)
    print(" 1. Search movie by title")
    print(" 2. Browse movies by genre")
    print(" 3. Filter movies by release year")
    print(" 4. Get movie recommendations")
    print(" 5. Statistical analysis (NumPy)")
    print(" 6. Top rated movies")
    print(" 7. Genre analysis")
    print(" 8. Generate charts (PNG)")
    print(" 9. Save analysis report (TXT + CSV)")
    print(" 0. Exit")
    print("-" * 52)
    return input("Enter your choice: ").strip()


def save_report(df, recommendations=None, filename="analysis_report.txt"):
    """Write statistics, top movies, genre summary and recommendations to files."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    txt_path = os.path.join(REPORTS_DIR, filename)

    stats = calculate_statistics(df)
    top = get_top_movies(df, 10)
    genre_counts = analyze_genres(df)
    genre_avg = genre_average_rating(df)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("MOVIE ANALYSIS REPORT\n")
        f.write(f"Generated on: {datetime.now():%Y-%m-%d %H:%M:%S}\n")
        f.write("=" * 60 + "\n\n")

        f.write(f"Total movies analysed: {len(df)}\n\n")

        f.write("RATING STATISTICS\n" + "-" * 60 + "\n")
        for key, value in stats.items():
            f.write(f"  {key:<14}: {value:.2f}\n" if isinstance(value, float)
                    else f"  {key:<14}: {value}\n")

        f.write("\nTOP 10 RATED MOVIES\n" + "-" * 60 + "\n")
        for i, (_, row) in enumerate(top.iterrows(), start=1):
            f.write(f"  {i:>2}. {row['title']} ({int(row['year'])}) - {row['rating']}\n")

        f.write("\nGENRE COUNTS\n" + "-" * 60 + "\n")
        for g, c in genre_counts.items():
            f.write(f"  {g:<18}: {c} movies (avg rating {genre_avg.get(g, 0):.2f})\n")

        if recommendations is not None and not recommendations.empty:
            f.write("\nLATEST RECOMMENDATIONS\n" + "-" * 60 + "\n")
            for i, (_, row) in enumerate(recommendations.iterrows(), start=1):
                f.write(f"  {i:>2}. {row['title']} ({int(row['year'])}) - "
                        f"{row['rating']} - {row['genre']}\n")

    saved = [txt_path]
    if recommendations is not None and not recommendations.empty:
        csv_path = os.path.join(REPORTS_DIR, "recommendations.csv")
        recommendations.to_csv(csv_path, index=False)
        saved.append(csv_path)
    return saved
