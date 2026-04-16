# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **Sonic recommendations**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  

Each recommendation is a (song, score, explanation) tuple where the score is a composite of up to five weighted signals — genre match, mood match, energy proximity, acousticness proximity, and valence proximity — adjusted by two post-scoring ranking rules: a repeat decay multiplier that suppresses overplayed songs and a novelty boost that surfaces unheard ones, plus an artist spread penalty that prevents the same artist from monopolising the list.

- What assumptions does it make about the user  

- Preferences are static. The system treats user_prefs as a fixed snapshot — it has no concept of the user's taste shifting over time, by mood, or by context. A user who listens to chill lofi at night and high-energy pop in the morning is represented as a single averaged profile that probably describes neither listening session accurately.

- Play count equals dislike at scale. The repeat decay formula assumes that the more times a song has been played, the less the user wants to hear it. It makes no distinction between a song played 8 times because the user loved it and a song played 8 times because it was in a shared playlist. High play count is treated as overexposure, not loyalty.

- Preferences are independent of each other. Genre, mood, energy, acousticness, and valence are scored separately and summed — the system assumes these features don't interact. In reality, a user who likes sad music probably expects low energy and high acousticness to come with it. The contradiction profile exposed this directly: the system scored blues and sad correctly, then independently chased high energy regardless.

- A single profile describes all listening contexts. The system generates one ranked list from one profile — it assumes the user wants the same type of music regardless of whether they're working, working out, or winding down.

- Is this for real users or classroom exploration 

Classroom exploration. 

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  

Every song in the catalog carries two types of information. The first type is categorical tags — genre (like lofi, jazz, or metal) and mood (like happy, chill, or melancholic). The second type is audio measurements on a scale from 0 to 1 — how acoustic versus electronic a song sounds, how much energy it has, how positive or upbeat it feels (valence), how danceable it is, and its tempo in BPM. The recommender currently uses genre, mood, energy, acousticness, and valence. Danceability and tempo are in the data but ignored.

- What user preferences are considered 

The system asks: what genre do you like, what mood are you in, how energetic do you want the music, and how acoustic versus electronic do you prefer. These are set as a preference profile — the taste profile built earlier set acousticness to a balanced midpoint of 0.5, preferred all 16 genres, and left mood and valence blank since there was no strong preference for either. The system also tracks a play history — a record of how many times each song has been heard — which influences how strongly a song gets promoted or suppressed in the final ranking.


- How does the model turn those into a score  

For categorical features like genre and mood, it's straightforward — if the song's genre matches your preferred genre, the score goes up by a flat amount. For continuous features like energy and acousticness, it uses a bell curve approach: a song scores highest when it exactly matches your target value, and the score falls off smoothly the further the song drifts from that target. All the individual feature scores get added together into a single number. Then two adjustments happen — songs you've never heard get a small boost to encourage discovery, while songs you've played many times get progressively penalised to avoid recommending the same thing over and over. Finally, if two songs from the same artist are about to appear close together in the list, the second one gets pushed down to keep the results varied.

- What changes did you make from the starter logic  

The starter code was essentially empty — load_songs, score_song, and recommend_songs were all placeholder functions that returned nothing. The scoring logic, the bell curve proximity calculations, the genre and mood bonuses, the play history decay, and the artist spread penalty were all built from scratch drawing from the hybrid recommender pipeline developed earlier in the project. Two deliberate weight adjustments were also made along the way: energy was made twice as important as it originally was, and genre was made half as important, shifting the recommender away from "find me songs in my genre" toward "find me songs that feel right energetically." The taste profile itself — the set of preferences the system uses as its input — was also generated through a questionnaire rather than hardcoded, which means it reflects actual stated preferences rather than arbitrary test values.Sonnet 4.6Extended

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog 

The catalog contains 18 songs stored in a CSV file. Each song has 10 fields: an ID, title, artist name, genre, mood, and five audio measurements — energy, tempo, valence, danceability, and acousticness.

- What genres or moods are represented  

The 18 songs span 15 genres: pop, indie pop, lofi, ambient, rock, metal, r&b, hip-hop, jazz, blues, synthwave, country, classical, reggae, and funk. On the mood side there are 10 tags: happy, chill, intense, relaxed, focused, moody, romantic, nostalgic, confident, serene, euphoric, melancholic, dark, and sad. The distribution is uneven — lofi and pop each have three songs while metal, r&b, country, hip-hop, classical, reggae, funk, and blues each have exactly one. The same imbalance applies to moods, with chill and intense appearing most frequently while most emotional tags appear only once.

- Did you add or remove data  

Yes, the original starter file had 10 songs covering pop, lofi, rock, ambient, jazz, synthwave, and indie pop exclusively. Eight songs were added to fill in genres that were completely missing: Ember & Ash (metal), Velvet Underground Soul (r&b), Porch in July (country), Concrete Prophecy (hip-hop), Sunken Cathedral (classical), Island Standard Time (reggae), Funky Transmission (funk), and Crossroads at 3am (blues). The additions were specifically chosen to give the adversarial test profiles something meaningful to match against, and to test whether the scoring logic could handle a more diverse catalog without breaking.

- Are there parts of musical taste missing in the dataset  

Electronic and EDM have no representation despite being among the most streamed genres globally. Folk, soul, gospel, and Latin music are entirely absent. Within the moods, complex emotional states like nostalgic and bittersweet only appear once each, and there's nothing representing energetic happiness distinct from intense workout energy — the catalog treats "pumped up" and "aggressive" as the same thing because both land in the high-energy range. The audio features themselves also have gaps: danceability and tempo are measured but never scored, which means a 180 BPM drum and bass track and a 180 BPM polka would be treated identically by the recommender. At 18 songs the catalog is also simply too small to return five meaningfully distinct recommendations for any minority genre — as soon as one niche song matches, the remaining four slots default to whatever else is acoustically nearby rather than thematically related.


---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results 

The system works best for users with a strong, clearly defined energy preference and a broad genre tolerance. The monopoly and niche profiles demonstrated this most cleanly — when a user's preferences map tightly to a specific corner of the feature space, the Gaussian pulls exactly the right songs to the top and the fallback slots fill with acoustically adjacent content that still feels coherent. A user who knows they want low-energy acoustic music and sets those values explicitly will consistently get ambient, jazz, blues, and classical in their top five, which is an intuitively correct result. Similarly, users with a moderate play history — heard a few songs but not overplayed anything — benefit from the balanced interplay between content scoring and the novelty boost, which surfaces fresh songs without completely ignoring what the user already responded to.

- Any patterns you think your scoring captures correctly  

The bell curve proximity scoring captures one thing very well: the difference between "close but not quite" and "far off." A song at energy 0.78 against a target of 0.75 scores nearly perfectly, while a song at 0.40 scores close to zero — and that gradient feels musically intuitive. The artist spread penalty also works as intended in practice — across all six profiles tested, no artist appeared twice in the top five, which is a genuine quality-of-life improvement over a naive ranking that could easily surface the same artist multiple times. The explanations generated alongside each score are also a real strength — every recommendation tells you exactly why it ranked where it did, which makes it immediately obvious when something is wrong and easy to trace back to a specific feature weight.

- Cases where the recommendations matched your intuition  

The niche hunter profile was the most satisfying result in the entire test run. Sunken Cathedral scored a near-perfect 6.254 as the only classical song, and then the remaining slots filled with Spacewalk Thoughts (ambient), Crossroads at 3am (blues), Library Rain (lofi), and Coffee Shop Stories (jazz) — all soft, slow, acoustic genres that genuinely feel like what someone who listens to classical would also enjoy. No prompting or special logic produced that result; it emerged naturally from the Gaussian pulling toward low energy and high acousticness values. The before-and-after comparison on the weight shift also matched intuition — doubling energy's importance correctly caused Rooftop Lights to jump to the top of the baseline list because its energy proximity was strong, while genre-only matches like Gym Hero dropped, which is exactly the behaviour the weight change was supposed to produce.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 


After halving GENRE_MATCH_BONUS to 1.0, exact genre string matching is still all-or-nothing. "indie pop" ≠ "pop" in the current logic even though they're sonically adjacent. A user who listens to indie pop gets zero genre credit when pop songs appear, and vice versa. Sub-genres are completely invisible to the scorer — "r&b", "hip-hop", and "funk" are treated as unrelated as "metal" and "classical".

Prompts:  

- Features it does not consider 

The system scores entirely on acousticness, valence, energy, genre, and mood — but ignores tempo, danceability, and artist familiarity entirely, even though all three are sitting in the CSV. A user who exclusively listens to slow jazz at 70 BPM would receive the same recommendations as someone who listens to fast jazz at 140 BPM, because tempo is never evaluated. Danceability is similarly unused, which means a funk fan who wants high-danceability songs is indistinguishable from one who doesn't. Beyond what's already in the data, the system has no concept of time-of-day listening patterns, playlist context, explicit skip signals, or the difference between background listening and active listening — all of which real recommenders use as strong behavioural signals. 


- Genres or moods that are underrepresented  

The 18-song catalog has a hard structural ceiling on how well any minority genre can be recommended. Classical, reggae, blues, country, and funk each have exactly one song. When a user matches one of those genres, the system correctly surfaces that song at rank 1 — and then has nothing left to fill slots 2 through 5 with thematically related content. The remaining recommendations default to whoever had the closest energy proximity, which could be metal or pop. On the mood side, "confident," "serene," "euphoric," "nostalgic," "romantic," and "melancholic" each appear once. Any user whose emotional profile maps to those tags will get a single mood match and four mood-irrelevant filler songs. "Chill," "happy," and "intense" dominate the catalog with 3–4 songs each, so users who prefer those moods are structurally better served than everyone else.


- Cases where the system overfits to one preference  

The most visible overfit is energy after the weight shift to ENERGY_WEIGHT = 2.0. A song with perfect energy proximity can score +2.0 from that single feature alone, which is now larger than a genre match +1.0 and a mood match +1.5 combined. This means a song in the completely wrong genre that happens to have the right energy level will outrank a song in the exact right genre with slightly different energy. The second overfit is the novelty multiplier — every unheard song gets ×1.18 regardless of content relevance, so a new song that scores 0.1 on content becomes 0.118 and can outrank a heavily played song that scores 0.11 on content and gets ×0.45 decay, giving 0.0495. Freshness is overweighted relative to actual taste match. A third overfit occurs when acousticness is the only active pref — since genre, mood, and energy are all optional, a profile with only acousticness set collapses the entire ranking into a single dimension, and songs with similar acousticness values tie or cluster very closely regardless of how sonically different they actually are.


- Ways the scoring might unintentionally favor some users  

High-energy listeners are the most structurally favoured group. With ENERGY_WEIGHT = 2.0, a user with energy: 0.9 can achieve near-perfect scores across an entire genre cluster (pop, rock, metal, funk all sit at 0.75–0.97) because multiple songs fall within one sigma of their target. A low-energy listener with energy: 0.2 has far fewer songs near their target — only ambient and classical — so their Gaussian scores are low across most of the catalog. Users whose genre preference matches the catalog's most-represented genres (pop with 3 songs, lofi with 3 songs) are also favoured simply by volume — they have more chances for a genre match bonus to fire. Users who set all five preference fields (genre, mood, energy, acousticness, valence) can accumulate a maximum possible score of around 7.3 (1.0 + 1.5 + 2.0 + 0.8 + 0.8) before ranking multipliers, while a user who only sets one preference is capped at 2.0 maximum. The system implicitly rewards users who provide more complete profiles, which means power users who know how to configure preferences get dramatically better results than casual users who set only genre or mood.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  

The real taste profile was the baseline throughout — acousticness target 0.50, genre set to "pop" (first of 16 preferred), mood disabled, play history with Sunrise City at 8 plays and Gym Hero at 3 plays. This was the profile derived from the questionnaire answers earlier in the session.From the adversarial set, two were actively run in the terminal. The contradiction profile (genre: "blues", mood: "sad", energy: 0.9, acousticness: 0.9) confirmed the predicted failure — Crossroads at 3am scored first on genre and mood match, but slots 2 through 5 filled with Storm Runner, Gym Hero, Funky Transmission, and Ember & Ash purely on energy proximity, none of which are remotely "sad" or acoustic. The ghost profile with all features disabled was also run, though its output wasn't shown — every song would have scored 0.0 base with uniform novelty multipliers, producing an essentially random ranking.The remaining four adversarial profiles — overplayed superfan, impossible target, artist monopoly, and niche hunter — were designed and added to the test harness but never actually executed in the terminal to observe their outputs.

- What you looked for in the recommendations  

Genre, Acousticness, Valence, Mood, Energy, Novelty boost, Artist Spread.

- What surprised you 

Something tha suprised me was how many variables go into 

- Any simple tests or comparisons you ran  

The most direct before/after comparison was the weight shift. Before (ENERGY_WEIGHT = 1.0, GENRE_MATCH_BONUS = 2.0) the top 5 with the taste profile returned Gym Hero, Sunrise City, Velvet Underground Soul, Rooftop Lights, and Island Standard Time. After the shift (ENERGY_WEIGHT = 2.0, GENRE_MATCH_BONUS = 1.0) the same profile returned Rooftop Lights, Concrete Prophecy, Night Drive Loop, Funky Transmission, and Storm Runner — a completely different list. Gym Hero and Sunrise City dropped out despite being the closest genre matches, replaced by songs whose only qualification was high energy proximity.A two-run comparison was also done in recommend_songs testing — one call with no play history and one with {1: 8, 5: 3} — which showed that Sunrise City dropped from rank 1 (5.30) to rank 3 (2.04) purely due to the repeat decay multiplier, and Rooftop Lights moved up to rank 1 because it was unheard.The scoring was also verified across all 18 songs individually by printing raw score_song output for every catalog entry, which confirmed that the 8 new songs added in songs_v2.csv — metal, r&b, country, hip-hop, classical, reggae, funk, blues — were being scored correctly and that Concrete Prophecy (energy: 0.80) achieved a perfect 1.00 energy proximity against a target of 0.8.


---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  

The most impactful addition would be tempo as a scored feature. It's already in the CSV and completely ignored — a user who exclusively listens to slow music at 65–80 BPM would get the same recommendations as someone who prefers 140 BPM, even though that difference is immediately audible. Danceability is similarly unused and would meaningfully separate funk and reggae from jazz and ambient even when their energy values are similar. Beyond what's already in the data, adding a "listening context" field to the user profile — something like work, exercise, sleep, or commute — would let the system apply different feature weightings depending on the situation rather than treating all listening as the same activity.

- Better ways to explain recommendations  



- Improving diversity among the top results  

The current artist spread window only prevents duplicate artists within the top five, but does nothing about genre clustering. After the weight shift to prioritise energy, the top five frequently fills with songs from completely different genres that all happen to sit at similar energy levels — which produces a diverse-looking list that actually feels incoherent to listen to. A better approach would be a genre spread rule that works the same way as artist spread: once a genre appears in the top three results, the next song from that same genre gets a mild penalty unless it scored significantly higher than the alternatives. Adding an explicit "surprise slot" — one position in the top five reserved for a song outside the user's normal feature range — would also introduce the kind of serendipitous discovery that makes real recommendation systems feel alive rather than predictable.

- Handling more complex user tastes  

The biggest limitation is that the system models every user as having one fixed taste profile. Real listening behaviour is multi-modal — most people have two or three distinct listening modes depending on their energy level or what they're doing. The most straightforward improvement would be supporting multiple named profiles that the user can switch between, which is essentially what the ACTIVE_PROFILE test harness already does structurally. A more ambitious improvement would be implicit profile learning: instead of requiring the user to declare energy: 0.8 upfront, the system would infer their energy preference from their play history by averaging the energy values of their most-played songs and using that as the target automatically. This would make the profile self-updating and remove the assumption that users know how to translate their musical taste into numbers.

---

## 9. Personal Reflection  


A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems 

There is alot more math than I thought would be involved.

- Something unexpected or interesting you discovered  

Theres alot of edgecases i didn't think about.

- How this changed the way you think about music recommendation apps  
^^^