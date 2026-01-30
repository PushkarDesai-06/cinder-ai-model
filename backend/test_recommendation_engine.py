"""Lightweight smoke test for RecommendationEngine without requiring faiss.
It creates a dummy index object with the minimal API used by RecommendationEngine:
- ntotal
- reconstruct(i) -> vector
- search(query_array, k) -> (distances, indices)

It also writes a tiny product metadata file and runs through record_user_interaction and get_recommendations.
"""
import numpy as np
import json
import os

from recommendation_engine import RecommendationEngine, UserInteractionTracker


class DummyIndex:
    def __init__(self, vectors):
        self.vectors = np.asarray(vectors, dtype=np.float32)
        self.ntotal = self.vectors.shape[0]

    def reconstruct(self, i):
        return self.vectors[int(i)]

    def search(self, query_array, k):
        # cosine similarity as dot product (assume normalized)
        q = np.asarray(query_array, dtype=np.float32)
        if q.ndim == 1:
            q = q[None, :]
        sims = q.dot(self.vectors.T)
        # return fake 'distances' as 1 - similarity
        idx = np.argsort(-sims, axis=1)[:, :k]
        dists = 1.0 - np.take_along_axis(sims, idx, axis=1)
        return dists, idx


def write_small_metadata(path, n=20, dim=32):
    meta = {}
    colors = ["black", "red", "blue", "green", "navy blue", "white"]
    cats = ["Above the Knee", "Below the Knee", "Midi"]
    for i in range(n):
        meta[str(i)] = {
            "id": f"product_{i}",
            "affiliate_href": f"https://example.com/p/{i}",
            "category": np.random.choice(cats),
            "title": f"Product {i}",
            "price": int(100 + i * 10),
            "color": np.random.choice(colors),
            "image_href": "",
        }
    with open(path, "w") as f:
        json.dump(meta, f)


def run_smoke_test():
    tmp_meta = "./backend/tmp_processed.json"
    write_small_metadata(tmp_meta, n=100, dim=64)

    # random normalized vectors
    rng = np.random.RandomState(0)
    vecs = rng.randn(100, 64).astype(np.float32)
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)

    # create engine but monkeypatch the index
    eng = RecommendationEngine(faiss_index_path="./backend/image_vectors.index", product_metadata_path=tmp_meta)
    eng.index = DummyIndex(vecs)

    user_id = "test_user"

    # like a couple of items of different colors to ensure diversity isn't just color-based
    eng.record_user_interaction(user_id, "product_1", "like")
    eng.record_user_interaction(user_id, "product_5", "like")
    eng.record_user_interaction(user_id, "product_10", "dislike")

    recs = eng.get_recommendations(user_id, num_recommendations=5)
    print("Recommendations (no filters):")
    for r in recs:
        print(r["id"], r.get("color"), r.get("similarity_score", None))

    recs_color = eng.get_recommendations(user_id, num_recommendations=5, color_filter=["black", "navy blue"])
    print("\nRecommendations (color filter navy/black):")
    for r in recs_color:
        print(r["id"], r.get("color"), r.get("similarity_score", None))

    # clean up
    os.remove(tmp_meta)


if __name__ == "__main__":
    run_smoke_test()
