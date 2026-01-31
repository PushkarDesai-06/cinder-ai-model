# 🎛️ Recommendation System Hyperparameters

This document lists all tunable hyperparameters in the recommendation system and their effects on behavior.

---

## 📍 Location: `backend/recommendation_engine.py`

### 1. **Dislike Penalty Weight** 🚫
**Line 34** in `UserInteractionTracker.compute_preference_vector()`
```python
return liked_vector - 0.5 * disliked_vector
```

**Current Value:** `0.5`

**What it does:**
- Controls how much disliked items push recommendations away from certain styles
- Applied as a penalty when computing user preference vector

**Effect of changing:**
- **Lower (0.0 - 0.3)**: Dislikes have less influence, recommendations focus more on likes only
- **Higher (0.7 - 1.0)**: Dislikes strongly push away similar items, more aggressive avoidance
- **Above 1.0**: Disliked items become more important than liked items (not recommended)

**Use cases:**
- `0.2-0.3`: User is exploring, dislikes are just "not now"
- `0.5`: Balanced (current default)
- `0.8-1.0`: Strong preferences, user really wants to avoid certain styles

---

### 2. **MMR Lambda Parameter** ⚖️
**Line 171** in `_mmr_rerank()`
```python
def _mmr_rerank(self, candidates, query_vector, num_recommendations, lambda_param=0.7):
```

**Current Value:** `0.7`

**What it does:**
- Balances relevance vs diversity in Maximal Marginal Relevance (MMR) algorithm
- Formula: `mmr_score = lambda * relevance - (1 - lambda) * similarity_to_selected`

**Effect of changing:**
- **Higher (0.8 - 1.0)**: More relevance-focused, recommendations are very similar to preferences (less diverse)
- **Lower (0.3 - 0.5)**: More diversity-focused, recommendations vary more in style (less similar to each other)
- **0.5**: Perfect balance between relevance and diversity

**Use cases:**
- `0.9`: "Show me more items EXACTLY like what I liked"
- `0.7`: Balanced (current default) - similar but diverse
- `0.4`: "Show me variety, even if not perfect matches"

---

### 3. **Diverse Recommendations Sampling Step** 📊
**Line 229** in `_get_diverse_recommendations()`
```python
step = max(1, total_vectors // (num_recommendations * 2))
```

**Current Formula:** `total_items / (requested_items * 2)`

**What it does:**
- Controls how spread out diverse recommendations are when user has no interaction history
- Determines the stride when sampling from the product catalog

**Effect of changing the multiplier (currently `2`):**
- **Lower (1)**: Samples from first half of catalog only, less diverse
- **Higher (3-5)**: Samples more evenly across entire catalog, more diverse

**Example:**
If you have 1000 items and request 10 recommendations:
- Current: `step = 1000 / (10 * 2) = 50` → samples items at indices 0, 50, 100, 150...
- With `* 3`: `step = 1000 / (10 * 3) = 33` → samples items at indices 0, 33, 66, 99...
- With `* 5`: `step = 1000 / (10 * 5) = 20` → samples items at indices 0, 20, 40, 60...

**Use cases:**
- `* 1-2`: Quick startup, less diverse initial set
- `* 2-3`: Balanced (current range)
- `* 4-6`: Maximum diversity for cold start

---

### 4. **Number of Recommendations** 🔢
**Line 92** in `get_recommendations()`
```python
def get_recommendations(self, user_id, num_recommendations=10, ...):
```

**Current Default:** `10`

**What it does:**
- Default number of items returned per request
- Can be overridden by API call

**Effect of changing:**
- **Lower (3-5)**: Fewer recommendations, faster processing, less scrolling
- **Higher (20-50)**: More recommendations, user can browse more without refresh

**Configured in:** `backend/api.py` and `frontend/src/App.jsx`
```javascript
// Frontend currently requests:
num_recommendations: 10
```

---

### 5. **FAISS Search Space** 🔍
**Line 109** in `get_recommendations()`
```python
distances, indices = self.index.search(
    np.array([user_preference]), k=self.index.ntotal
)
```

**Current Value:** `k=self.index.ntotal` (searches entire index)

**What it does:**
- Number of nearest neighbors to retrieve from FAISS before filtering and re-ranking
- Currently searches entire catalog

**Effect of changing:**
- **Lower (100-500)**: Faster search, but might miss some good matches
- **Current (ntotal)**: Comprehensive search, slower but finds all possible matches
- Only consider changing if you have 10,000+ items

---

## 🎨 How to Modify Hyperparameters

### Method 1: Direct Code Changes
Edit `backend/recommendation_engine.py` and restart the API:

```python
# Example: Make dislikes stronger
return liked_vector - 0.8 * disliked_vector  # Changed from 0.5

# Example: Prefer diversity over relevance
def _mmr_rerank(self, candidates, query_vector, num_recommendations, lambda_param=0.5):
```

### Method 2: Make Them Configurable (Recommended)
Create a config file or class attributes:

```python
class RecommendationEngine:
    def __init__(self, faiss_index_path, product_metadata_path, config=None):
        # ... existing code ...
        
        # Hyperparameters
        self.dislike_penalty = config.get('dislike_penalty', 0.5)
        self.mmr_lambda = config.get('mmr_lambda', 0.7)
        self.diversity_multiplier = config.get('diversity_multiplier', 2)
```

---

## 📊 Recommended Configurations

### For Maximum Personalization 🎯
```python
dislike_penalty = 0.7           # Strong avoidance
mmr_lambda = 0.85              # Focus on relevance
diversity_multiplier = 2        # Standard diversity
```
**Result:** Very personalized, items closely match user taste

### For Maximum Diversity 🌈
```python
dislike_penalty = 0.3           # Soft avoidance
mmr_lambda = 0.5               # Balance relevance and diversity
diversity_multiplier = 5        # Maximum spread
```
**Result:** Varied recommendations, helps user discover new styles

### For Exploration Mode 🔍
```python
dislike_penalty = 0.2           # Minimal avoidance
mmr_lambda = 0.4               # Favor diversity
diversity_multiplier = 4        # High spread
```
**Result:** Encourages trying new things, less focused on current preferences

### For Refined Taste 💎
```python
dislike_penalty = 0.8           # Strong rejection
mmr_lambda = 0.9               # Maximum relevance
diversity_multiplier = 1        # Less cold-start diversity
```
**Result:** Laser-focused on exact preferences, for users who know what they want

---

## 🧪 A/B Testing Suggestions

Test different configurations with different user segments:

1. **New Users:** Higher diversity, lower penalties
2. **Engaged Users:** Higher relevance, stronger penalties
3. **Power Users:** Very high relevance, very strong penalties

Track metrics:
- Click-through rate
- Time spent browsing
- Number of likes per session
- User retention

---

## ⚠️ Important Notes

1. **Restart Required:** After changing hyperparameters in the code, restart the backend API:
   ```bash
   python backend/api.py
   ```

2. **No User Data Persistence:** Currently, user preferences are stored in memory. They reset when the server restarts.

3. **Testing:** Test changes with different user interaction patterns to see effects.

4. **Balance:** Most hyperparameters work best in the 0.3-0.8 range. Extreme values can cause unexpected behavior.

---

## 🔮 Future Enhancements

Consider making these configurable:
- **Recency weighting**: Give more weight to recent interactions
- **Interaction count threshold**: Minimum likes before switching to personalized mode
- **Exploration rate**: Occasionally show random items even in personalized mode
- **Category/color preference weights**: Learn which attributes matter most to user
