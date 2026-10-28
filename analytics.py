"""
analytics.py  (Member 2 - Data Analytics & Visualization)
NumPy statistics + Matplotlib / Seaborn charts.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # save charts to files (no GUI window needed)
import matplotlib.pyplot as plt
import seaborn as sns

from data_processing import split_genres

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHARTS_DIR = os.path.join(BASE_DIR, "charts")

sns.set_theme(style="whitegrid")


def _prepare_path(save_path, default_name):
    if save_path is None:
        save_path = os.path.join(CHARTS_DIR, default_name)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    return save_path


def calculate_statistics(df, column="rating"):
    """Mean, median, std, variance, min, max and percentiles using NumPy."""
    values = df[column].dropna().to_numpy(dtype=float)
    if values.size == 0:
        return {}
    return {
        "count": int(values.size),
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "std_dev": float(np.std(values)),
        "variance": float(np.var(values)),
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "percentile_25": float(np.percentile(values, 25)),
        "percentile_50": float(np.percentile(values, 50)),
        "percentile_75": float(np.percentile(values, 75)),
        "percentile_90": float(np.percentile(values, 90)),
    }


def get_top_movies(df, n=10, min_votes=0):
    """Top-n rated movies (optionally only those with enough votes)."""
    data = df
    if "votes" in df.columns and min_votes > 0:
        data = df[df["votes"] >= min_votes]
    sort_cols = ["rating"] + (["votes"] if "votes" in data.columns else [])
    return data.sort_values(sort_cols, ascending=False).head(n)


def analyze_genres(df):
    """Return a dictionary {genre: number_of_movies}, highest first."""
    counts = {}
    for value in df["genre"]:
        for g in split_genres(value):
            counts[g] = counts.get(g, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))


def genre_average_rating(df):
    """Return a dictionary {genre: average_rating}, highest first."""
    totals = {}
    for _, row in df.iterrows():
        for g in split_genres(row["genre"]):
            totals.setdefault(g, []).append(row["rating"])
    averages = {g: float(np.mean(v)) for g, v in totals.items()}
    return dict(sorted(averages.items(), key=lambda kv: kv[1], reverse=True))


def yearly_trend(df):
    """Movie count and average rating per release year."""
    grouped = df.groupby("year")["rating"].agg(["count", "mean"]).round(2)
    grouped.columns = ["movie_count", "avg_rating"]
    return grouped


def plot_rating_distribution(df, save_path=None):
    path = _prepare_path(save_path, "rating_distribution.png")
    plt.figure(figsize=(9, 5))
    sns.histplot(df["rating"], bins=15, kde=True, color="#e50914")
    plt.axvline(df["rating"].mean(), color="black", linestyle="--",
                label=f"Mean = {df['rating'].mean():.2f}")
    plt.title("Rating Distribution")
    plt.xlabel("Rating")
    plt.ylabel("Number of Movies")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_top_movies(df, n=10, save_path=None):
    path = _prepare_path(save_path, "top_rated_movies.png")
    top = get_top_movies(df, n).iloc[::-1]
    plt.figure(figsize=(10, 6))
    plt.barh(top["title"], top["rating"], color="#e50914")
    for y, r in enumerate(top["rating"]):
        plt.text(r + 0.02, y, f"{r:.1f}", va="center")
    plt.title(f"Top {len(top)} Rated Movies")
    plt.xlabel("Rating")
    plt.xlim(0, max(10, top["rating"].max() + 0.5))
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_genre_distribution(df, top_n=12, save_path=None):
    path = _prepare_path(save_path, "genre_distribution.png")
    counts = list(analyze_genres(df).items())[:top_n]
    genres = [c[0] for c in counts]
    values = [c[1] for c in counts]
    plt.figure(figsize=(10, 6))
    sns.barplot(x=values, y=genres, hue=genres, palette="rocket", legend=False)
    plt.title("Genre-wise Movie Count")
    plt.xlabel("Number of Movies")
    plt.ylabel("Genre")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_yearly_trend(df, save_path=None):
    path = _prepare_path(save_path, "yearly_trend.png")
    trend = yearly_trend(df)
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.bar(trend.index, trend["movie_count"], color="#b3b3b3", label="Movie count")
    ax1.set_xlabel("Release Year")
    ax1.set_ylabel("Number of Movies")
    ax2 = ax1.twinx()
    ax2.plot(trend.index, trend["avg_rating"], color="#e50914", marker="o",
             label="Average rating")
    ax2.set_ylabel("Average Rating")
    ax2.grid(False)
    plt.title("Year-wise Movie Trend")
    fig.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def generate_all_charts(df):
    """Create every chart and return the list of saved file paths."""
    return [
        plot_rating_distribution(df),
        plot_top_movies(df),
        plot_genre_distribution(df),
        plot_yearly_trend(df),
    ]
