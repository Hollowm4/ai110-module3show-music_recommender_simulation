"""
Command line runner for the Music Recommender Simulation.
"""

from .recommender import load_songs, recommend_songs

_RESET  = "\033[0m";  _BOLD   = "\033[1m";  _DIM    = "\033[2m"
_GREEN  = "\033[32m"; _YELLOW = "\033[33m"; _RED    = "\033[31m"
_CYAN   = "\033[36m"; _WHITE  = "\033[97m"
SCORE_BAR_WIDTH = 24

def _score_colour(score):
    if score >= 3.0: return _GREEN
    if score >= 1.5: return _YELLOW
    return _RED

def _score_bar(score, max_score=6.0):
    filled = max(1, min(round((score / max_score) * SCORE_BAR_WIDTH), SCORE_BAR_WIDTH))
    bar = "█" * filled + "░" * (SCORE_BAR_WIDTH - filled)
    return f"{_score_colour(score)}{bar}{_RESET}"

def _format_reasons(explanation):
    reasons = [r.strip() for r in explanation.split("|") if r.strip()]
    lines = []
    for reason in reasons:
        if "match"     in reason: bullet = f"{_GREEN}▸{_RESET}"
        elif "proximity" in reason: bullet = f"{_CYAN}▸{_RESET}"
        elif "novelty"   in reason: bullet = f"{_GREEN}★{_RESET}"
        elif any(w in reason for w in ("penalty","decay","heard")): bullet = f"{_RED}▾{_RESET}"
        else: bullet = f"{_DIM}·{_RESET}"
        lines.append(f"      {bullet} {_DIM}{reason}{_RESET}")
    return "\n".join(lines)

def _print_header(user_prefs, total_songs, k):
    W = 54
    print(f"\n{_BOLD}{'─'*W}{_RESET}")
    print(f"{_BOLD}  MUSIC RECOMMENDER{_RESET}")
    print(f"{'─'*W}")
    prefs = "  ".join(
        f"{_DIM}{k2}:{_RESET} {_WHITE}{v}{_RESET}"
        for k2,v in user_prefs.items() if k2 != "play_history"
    )
    print(f"  Profile  →  {prefs}")
    print(f"  Catalog  →  {_WHITE}{total_songs}{_RESET} songs   Top  →  {_WHITE}{k}{_RESET}")
    print(f"{'─'*W}\n")

def _print_rec(rank, song, score, explanation):
    colour = _score_colour(score)
    print(f"  {_BOLD}{_WHITE}{rank:>2}.{_RESET}  {_BOLD}{song['title']:<26}{_RESET}{_DIM}{song['artist']}{_RESET}")
    print(f"        {_score_bar(score)}  {colour}{_BOLD}{score:>5.2f}{_RESET}  {_DIM}{song['genre']} · {song['mood']}{_RESET}")
    print(_format_reasons(explanation))
    print()

def _print_footer(k):
    print(f"{'─'*54}")
    print(f"  {_DIM}{k} recommendations ranked highest → lowest score{_RESET}\n")

def main():
    songs = load_songs("data/songs.csv")

    # ------------------------------------------------------------------
    # Adversarial test profiles — set ACTIVE_PROFILE to swap in any one.
    # Set ACTIVE_PROFILE = None to fall through to the real taste profile.
    # ------------------------------------------------------------------
    TEST_PROFILES = {
        "contradiction": {
            "label":        "The Contradiction - high energy + sad mood",
            "genre":        "blues",
            "mood":         "sad",
            "energy":       0.9,
            "acousticness": 0.9,
            "play_history": {},
        },
        "ghost": {
            "label":        "The Ghost - all features disabled",
            "play_history": {},
        },
        "overplayed": {
            "label":        "The Overplayed Superfan - favourite genre played 50x",
            "genre":        "lofi",
            "mood":         "chill",
            "energy":       0.4,
            "play_history": {2: 50, 4: 50, 9: 50},
        },
        "impossible": {
            "label":        "The Impossible Target - all features at midpoint 0.5",
            "energy":       0.5,
            "acousticness": 0.5,
            "valence":      0.5,
            "play_history": {},
        },
        "monopoly": {
            "label":        "The Artist Monopoly - profile matches one artist twice",
            "genre":        "synthwave",
            "mood":         "moody",
            "energy":       0.75,
            "acousticness": 0.22,
            "play_history": {},
        },
        "niche": {
            "label":        "The Niche Hunter - only one catalog match",
            "genre":        "classical",
            "mood":         "melancholic",
            "energy":       0.18,
            "acousticness": 0.97,
            "play_history": {},
        },
    }

    # Change this to any key above to test it, or None for real taste profile
    ACTIVE_PROFILE = None   # e.g. "contradiction" | "ghost" | "overplayed" etc.

    # ------------------------------------------------------------------
    # Taste profile — sourced from taste_profile.py
    # ------------------------------------------------------------------
    taste_profile = {
        "acousticness": {
            "target": 0.50,
            "sigma":  0.30,         # wider gaussian = more tolerant of variation
            "label":  "Balanced mix"
        },
        "valence": {
            "target": None,         # no preference — valence scoring disabled
            "sigma":  None,
            "label":  "No preference"
        },
        "genres": {
            "preferred": [
                "pop", "indie pop", "lofi", "ambient", "rock", "metal",
                "r&b", "hip-hop", "jazz", "blues", "synthwave",
                "electronic", "country", "folk", "funk", "reggae"
            ],
            "bonus": 0.12           # added to score when genre matches
        },
        "moods": {
            "preferred": [],        # no preference — mood scoring disabled
            "bonus":     0.00
        },
        "novelty_boost": {
            "enabled":               True,
            "unheard_multiplier":    1.09,
            "heard_multiplier":      0.85,
            "overplayed_multiplier": 0.40
        },
        "artist_spread": {
            "enabled":           True,
            "duplicate_penalty": 0.35
        }
    }

    # ------------------------------------------------------------------
    # Build user_prefs for recommend_songs() from taste_profile values
    # ------------------------------------------------------------------
    user_prefs = {
        # Acousticness target + custom sigma from profile
        "acousticness": taste_profile["acousticness"]["target"],

        # Valence disabled when target is None
        **({"valence": taste_profile["valence"]["target"]}
           if taste_profile["valence"]["target"] is not None else {}),

        # First preferred genre as primary genre signal (broad match)
        "genre": taste_profile["genres"]["preferred"][0]
                 if taste_profile["genres"]["preferred"] else None,

        # Mood disabled — empty preferred list maps to no mood filter
        "mood": taste_profile["moods"]["preferred"][0]
                if taste_profile["moods"]["preferred"] else None,

        # Novelty multipliers passed through for recommend_songs ranking
        "unheard_multiplier":    taste_profile["novelty_boost"]["unheard_multiplier"],
        "heard_multiplier":      taste_profile["novelty_boost"]["heard_multiplier"],
        "overplayed_multiplier": taste_profile["novelty_boost"]["overplayed_multiplier"],

        # Artist spread penalty passed through for ranking
        "duplicate_penalty": taste_profile["artist_spread"]["duplicate_penalty"],

        # Play history — update this dict with actual listen counts
        "play_history": {1: 8, 5: 3},
    }

    # ------------------------------------------------------------------
    # Route: swap in test profile if ACTIVE_PROFILE is set
    # ------------------------------------------------------------------
    if ACTIVE_PROFILE is not None:
        if ACTIVE_PROFILE not in TEST_PROFILES:
            print(f"Unknown profile '{ACTIVE_PROFILE}'. Choose from: {list(TEST_PROFILES)}")
            return
        test = TEST_PROFILES[ACTIVE_PROFILE].copy()
        label = test.pop("label")
        user_prefs = {k: v for k, v in test.items() if v is not None}
        print(f"\n  {_BOLD}{_YELLOW}[TEST MODE]{_RESET}  {_DIM}{label}{_RESET}")
    else:
        # Remove None-valued keys so score_song skips disabled features
        user_prefs = {k: v for k, v in user_prefs.items() if v is not None}

    k               = 5
    recommendations = recommend_songs(user_prefs, songs, k=k)

    _print_header(user_prefs, len(songs), k)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        _print_rec(rank, song, score, explanation)
    _print_footer(k)

if __name__ == "__main__":
    main()