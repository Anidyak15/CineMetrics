"""
main.py  (Member 3 - integrates every module)
Run:  python main.py                 -> uses data/movie_recommendation_sample.csv
      python main.py path/to/file.csv
"""

import os
import sys

from data_processing import (load_data, clean_data, search_movie, filter_by_genre,
                             filter_by_year, get_all_genres, display_movie_details)
from analytics import (calculate_statistics, get_top_movies, analyze_genres,
                       genre_average_rating, generate_all_charts)
from recommendation import recommend_movies, display_menu, save_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV = os.path.join(BASE_DIR, "data", "movie_recommendation_sample.csv")


def ask_int(prompt, default=None):
    while True:
        text = input(prompt).strip()
        if text == "" and default is not None:
            return default
        try:
            return int(text)
        except ValueError:
            print("  Please enter a whole number.")


def ask_float(prompt, default=None):
    while True:
        text = input(prompt).strip()
        if text == "" and default is not None:
            return default
        try:
            return float(text)
        except ValueError:
            print("  Please enter a number.")


def show_statistics(df):
    stats = calculate_statistics(df)
    print("\n  RATING STATISTICS")
    print("  " + "-" * 30)
    for key, value in stats.items():
        print(f"  {key:<14}: {value:.2f}" if isinstance(value, float)
              else f"  {key:<14}: {value}")


def show_genre_analysis(df):
    counts = analyze_genres(df)
    averages = genre_average_rating(df)
    print(f"\n  {'Genre':<20}{'Movies':<10}{'Avg Rating'}")
    print("  " + "-" * 42)
    for genre, count in counts.items():
        print(f"  {genre:<20}{count:<10}{averages.get(genre, 0):.2f}")


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV

    try:
        df = clean_data(load_data(csv_path))
    except (FileNotFoundError, ValueError) as err:
        print(f"[ERROR] {err}")
        return
    if df.empty:
        print("[ERROR] No usable rows in dataset after cleaning.")
        return

    last_recommendations = None

    while True:
        choice = display_menu()

        if choice == "1":
            query = input("Enter movie title (or part of it): ")
            display_movie_details(search_movie(df, query))

        elif choice == "2":
            print("\n  Available genres:", ", ".join(get_all_genres(df)))
            genre = input("Enter genre: ")
            result = filter_by_genre(df, genre).sort_values("rating", ascending=False)
            display_movie_details(result, limit=15)

        elif choice == "3":
            start = ask_int("From year: ")
            end = ask_int("To year (press Enter for same year): ", default=start)
            result = filter_by_year(df, start, end).sort_values("rating", ascending=False)
            display_movie_details(result, limit=15)

        elif choice == "4":
            print("\n  Available genres:", ", ".join(get_all_genres(df)))
            genre = input("Preferred genre (Enter for any): ").strip() or None
            min_rating = ask_float("Minimum rating (default 0): ", default=0.0)
            top_n = ask_int("How many recommendations? (default 10): ", default=10)
            last_recommendations = recommend_movies(df, genre, min_rating, top_n=top_n)
            display_movie_details(last_recommendations, limit=top_n)

        elif choice == "5":
            show_statistics(df)

        elif choice == "6":
            n = ask_int("How many top movies? (default 10): ", default=10)
            display_movie_details(get_top_movies(df, n), limit=n)

        elif choice == "7":
            show_genre_analysis(df)

        elif choice == "8":
            print("\n  Generating charts...")
            for path in generate_all_charts(df):
                print(f"  Saved: {path}")

        elif choice == "9":
            for path in save_report(df, last_recommendations):
                print(f"  Saved: {path}")

        elif choice == "0":
            print("\nThank you for using the Movie Recommendation System. Goodbye!")
            break

        else:
            print("  Invalid choice. Please select 0-9.")


if __name__ == "__main__":
    main()
