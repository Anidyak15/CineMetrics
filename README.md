# Movie Recommendation & Analysis

Menu-driven Python project (no Machine Learning) using Pandas, NumPy, Matplotlib, Seaborn and file handling.

## Folder structure
```
Movie_Recommendation_Project/
├── data/            -> put your CSV here
├── reports/         -> analysis_report.txt, recommendations.csv
├── charts/          -> generated PNG graphs
├── main.py                (Member 3) menu + integration
├── data_processing.py     (Member 1) load, clean, search, filter
├── analytics.py           (Member 2) statistics + graphs
├── recommendation.py      (Member 3) recommendations, menu, report saving
└── requirements.txt
```

## Setup
```
pip install -r requirements.txt
python main.py                          # uses data/movie_recommendation_sample.csv
python main.py data/your_dataset.csv    # use another CSV
```

## Expected CSV columns
`title, genre, year, rating` (required) and `runtime, votes` (optional).
Common alternative names (e.g. `release_year`, `imdb_rating`, `listed_in`, `duration`) are detected automatically.
Genres may be comma-separated, e.g. `Action, Drama`.

## Team split
| Member | Files | Functions |
|---|---|---|
| 1 | data_processing.py | load_data, clean_data, search_movie, filter_by_genre, filter_by_year |
| 2 | analytics.py | calculate_statistics, get_top_movies, analyze_genres, plot_rating_distribution, plot_top_movies |
| 3 | recommendation.py, main.py | recommend_movies, display_menu, save_report, main |
