import pandas as pd
from datetime import datetime
import numpy as np

# load data
df = pd.read_csv('spotify-streaming-top-50-world.csv')
print(df.columns)
print(df.describe())
print(df.shape)
print(df.info())
print(df['total_tracks'])
# Cleaning data
    # kolom date
df['date'] = pd.to_datetime(df['date'])
df['month_year'] = df['date'].dt.to_period('M')
year = df['date'].dt.year
month = df['date'].dt.to_period('M').view(dtype = 'int64')
    # kolom release date & kolom song age
df['release_date_raw'] = df['release_date'].astype(str).str.strip()

    # kondisi
is_full = df['release_date_raw'].str.len() == 10  #format YYYY-MM-DD
is_month = df['release_date_raw'].str.len() == 7  #format YYYY-MM
is_year = df['release_date_raw'].str.len() == 4  #format YYYY

    # eksekusi
val_full = (df['date'] - pd.to_datetime(df['release_date'], errors='coerce')).dt.days / 365

release_to_month = pd.to_datetime(df['release_date_raw'], errors='coerce').dt.to_period('M').view(dtype='int64')
val_month = (month - release_to_month)/12

val_year = year - pd.to_numeric(df['release_date_raw'], errors='coerce')

df['umur_final'] = np.select(
    [is_full, is_month, is_year],
    [val_full, val_month, val_year],
    default=0
)
df['song_age'] = df['umur_final'].round().clip(lower=0).astype('int64')
# df['song_age'] = df['song_age'].astype('int64')
# print('ini mv:', df['song_age'])

bins = [-1,1,2,3,5,10,20,40,60,85]
labels = ['0–1','1–2','2–3','3–5','5–10','10–20','20–40','40–60','60+']

# bin NUMERIC (buat sorting)
df['umur_bin_num'] = pd.cut(
    df['song_age'],
    bins=bins,
    labels=range(len(bins)-1),
    right=False
).astype('Int64')

# bin LABEL (buat ditampilin)
df['umur_bin_label'] = pd.cut(
    df['song_age'],
    bins=bins,
    labels=labels,
    right=False
)
print(df[['month_year', 'umur_bin_label', 'song_age']])
print(df.info())
    # kolom duration
df['duration_ms'] = df['duration_ms']/60000
df['duration_bucket'] = pd.cut(df['duration_ms'], bins = [0,2,3,4,5,np.inf], labels=['<2 min', '2-3 min', '3-4 min', '4-5 min', '>5 min'])
    # kolom position
df['position_group'] = pd.cut(df['position'], bins = [0,10,20,30,40,50], labels=['Top 10', '11-20', '21-30', '31-40', '41-50'])
    # kolom artist, song
df['artist'] = df['artist'].str.strip()
df['song'] = df['song'].str.strip()
    # kolom is_explicit (labeling)
df['is_explicit'] = df['is_explicit'].map({True : 'Explicit', False : 'Non-Explicit'})
    # drop kolom url
df.drop(columns=['album_cover_url'], inplace=True)

# Dataset artis dominan
artist_sum = df.groupby('artist').agg(
    total_song = ('song', 'nunique'),
    avg_popularity = ('popularity', 'mean'),
    chart_appear = ('song', 'count')
).reset_index()
# print(artist_sum.head())

# Dataset lagu dominan
song_sum = df.groupby('song').agg(
    artist = ('artist', 'first'),
    avg_position = ('position', 'mean'),
    max_popularity = ('popularity', 'max'),
    appearances = ('song', 'count')
).reset_index()
# print(song_sum.head())

song_level = df.groupby('song').agg(
    avg_popularity = ('popularity', 'mean'),
    avg_song_age_days = ('song_age', 'mean'),
    appearances = ('song', 'count')
).reset_index()

album_prop = df.groupby('album_type').agg(
    avg_popularity = ('popularity', 'mean')
).reset_index()

duration_analysis = df.groupby('duration_bucket').agg(
    avg_popularity=('popularity', 'mean'),
    song_count=('song', 'count')
).reset_index()

# Export
duration_analysis.to_csv('duration_analysis.csv', index=False)
# artist_sum.to_csv('spotify_artist_summary.csv', index = False)
# song_sum.to_csv('spotify_song_summary.csv', index = False)

print(song_sum[['avg_position', 'max_popularity']])

