import csv
import math
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Scoring constants (ported from hybrid recommender)
# ---------------------------------------------------------------------------

GENRE_MATCH_BONUS = 2.0     # flat bonus for exact genre match
MOOD_MATCH_BONUS  = 1.5     # flat bonus for exact mood match
ENERGY_SIGMA      = 0.22    # Gaussian width for energy proximity
ACOUSTIC_SIGMA    = 0.22    # Gaussian width for acousticness proximity
VALENCE_SIGMA     = 0.22    # Gaussian width for valence proximity
ENERGY_WEIGHT     = 1.0     # max contribution from energy Gaussian
ACOUSTIC_WEIGHT   = 0.8     # max contribution from acousticness Gaussian
VALENCE_WEIGHT    = 0.8     # max contribution from valence Gaussian


def _gaussian(value: float, target: float, sigma: float) -> float:
    """
    Gaussian proximity — 1.0 when value == target, decays toward 0.
    Same formula used in the hybrid recommender pipeline.
    """
    return math.exp(-((value - target) ** 2) / (2 * sigma ** 2))

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    songs = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    print(f"Loaded {len(songs)} songs from {csv_path}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Returns (score, reasons) where reasons is a human-readable list
    explaining each contribution to the final score.

    Scoring components (ported from hybrid recommender):
      1. Genre match          — flat +2.0 bonus
      2. Mood match           — flat +1.5 bonus
      3. Energy proximity     — Gaussian, weighted x1.0
      4. Acousticness proximity — Gaussian, weighted x0.8 (if pref supplied)
      5. Valence proximity    — Gaussian, weighted x0.8 (if pref supplied)
    """
    score   = 0.0
    reasons = []

    # ------------------------------------------------------------------ #
    # 1. Genre match — exact string comparison, case-insensitive
    # ------------------------------------------------------------------ #
    user_genre = user_prefs.get("genre", "")
    if user_genre and song["genre"].lower() == user_genre.lower():
        score += GENRE_MATCH_BONUS
        reasons.append(f"genre match (+{GENRE_MATCH_BONUS})")

    # ------------------------------------------------------------------ #
    # 2. Mood match — exact string comparison, case-insensitive
    # ------------------------------------------------------------------ #
    user_mood = user_prefs.get("mood", "")
    if user_mood and song["mood"].lower() == user_mood.lower():
        score += MOOD_MATCH_BONUS
        reasons.append(f"mood match (+{MOOD_MATCH_BONUS})")

    # ------------------------------------------------------------------ #
    # 3. Energy proximity — Gaussian centred on user's target energy
    # ------------------------------------------------------------------ #
    if "energy" in user_prefs:
        energy_score = _gaussian(song["energy"], user_prefs["energy"], ENERGY_SIGMA)
        contribution = round(energy_score * ENERGY_WEIGHT, 3)
        score += contribution
        reasons.append(f"energy proximity (+{contribution:.2f})")

    # ------------------------------------------------------------------ #
    # 4. Acousticness proximity (optional pref)
    # ------------------------------------------------------------------ #
    if "acousticness" in user_prefs:
        ac_score     = _gaussian(song["acousticness"], user_prefs["acousticness"], ACOUSTIC_SIGMA)
        contribution = round(ac_score * ACOUSTIC_WEIGHT, 3)
        score += contribution
        reasons.append(f"acousticness proximity (+{contribution:.2f})")

    # ------------------------------------------------------------------ #
    # 5. Valence proximity (optional pref)
    # ------------------------------------------------------------------ #
    if "valence" in user_prefs:
        val_score    = _gaussian(song["valence"], user_prefs["valence"], VALENCE_SIGMA)
        contribution = round(val_score * VALENCE_WEIGHT, 3)
        score += contribution
        reasons.append(f"valence proximity (+{contribution:.2f})")

    # If nothing matched at all, say so explicitly
    if not reasons:
        reasons.append("no matching preferences found")

    return round(score, 4), reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Score every song in the catalog, apply hybrid ranking rules,
    and return the top-k results sorted highest → lowest score.

    Pipeline (mirrors hybrid recommender):
      1. score_song()        — content-based score + reasons for each song
      2. Repeat decay        — continuous penalty: 1.18 / (1 + 0.20 * plays)
      3. Artist spread       — ×0.35 penalty if artist already in top-5 window
      4. Sort + slice        — sorted by final_score descending, return top k

    Returns:
        List of (song_dict, final_score, explanation_string) tuples
    """
    play_history: Dict[int, int] = user_prefs.get("play_history", {})

    # ------------------------------------------------------------------
    # Step 1 — score every song and attach ranking metadata
    # ------------------------------------------------------------------
    scored = []
    for song in songs:
        base_score, reasons = score_song(user_prefs, song)

        # Step 2 — repeat decay (ported from hybrid recommender)
        # Formula: 1.18 / (1 + 0.20 * play_count)
        # 0 plays → ×1.18 (novelty boost)   8 plays → ×0.45 (heavy decay)
        play_count   = play_history.get(song["id"], 0)
        decay        = 1.18 / (1 + 0.20 * play_count)
        final_score  = round(base_score * decay, 4)

        if play_count == 0:
            reasons.append("novelty boost (unheard)")
        elif play_count >= 5:
            reasons.append(f"repeat decay ×{decay:.2f} ({play_count} plays)")
        else:
            reasons.append(f"heard ×{decay:.2f} ({play_count} plays)")

        scored.append({
            "song":        song,
            "base_score":  base_score,
            "final_score": final_score,
            "reasons":     reasons,
            "play_count":  play_count,
        })

    # ------------------------------------------------------------------
    # Step 3 — sort descending by final_score before artist spread check
    # ------------------------------------------------------------------
    scored.sort(key=lambda x: x["final_score"], reverse=True)

    # ------------------------------------------------------------------
    # Step 4 — artist spread (positional dampening, top-5 window)
    # Mirrors hybrid recommender: duplicate artist within top-5 → ×0.35
    # ------------------------------------------------------------------
    ARTIST_SPREAD_WINDOW = 5
    seen_artists: List[str] = []

    for item in scored:
        artist = item["song"]["artist"]
        if artist in seen_artists:
            first_idx = seen_artists.index(artist)
            if first_idx < ARTIST_SPREAD_WINDOW:
                item["final_score"] = round(item["final_score"] * 0.35, 4)
                item["reasons"].append("artist spread penalty (×0.35)")
        seen_artists.append(artist)

    # ------------------------------------------------------------------
    # Step 5 — final sort and slice to top k
    # ------------------------------------------------------------------
    scored.sort(key=lambda x: x["final_score"], reverse=True)
    top_k = scored[:k]

    # ------------------------------------------------------------------
    # Step 6 — format output as (song_dict, score, explanation)
    # ------------------------------------------------------------------
    return [
        (item["song"], item["final_score"], " | ".join(item["reasons"]))
        for item in top_k
    ]