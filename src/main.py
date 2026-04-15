"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
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

    user_prefs = {
        "genre":        "pop",
        "mood":         "happy",
        "energy":       0.8,
        "play_history": {1: 8, 5: 3},
    }

    k               = 5
    recommendations = recommend_songs(user_prefs, songs, k=k)

    _print_header(user_prefs, len(songs), k)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        _print_rec(rank, song, score, explanation)
    _print_footer(k)

if __name__ == "__main__":
    main()