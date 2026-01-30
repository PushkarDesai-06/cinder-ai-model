import faiss
import json
import numpy as np
import os


class UserInteractionTracker:
    def __init__(self):
        self.liked_products = set()
        self.disliked_products = set()
        self.interaction_embeddings = {"liked": [], "disliked": []}

    def add_interaction(self, product_id, embedding, reaction):
        if reaction == "like":
            self.liked_products.add(product_id)
            self.interaction_embeddings["liked"].append(embedding)
        else:
            self.disliked_products.add(product_id)
            self.interaction_embeddings["disliked"].append(embedding)

    def compute_preference_vector(self):
        liked_vector = (
            np.mean(self.interaction_embeddings["liked"], axis=0)
            if self.interaction_embeddings["liked"]
            else None
        )
        disliked_vector = (
            np.mean(self.interaction_embeddings["disliked"], axis=0)
            if self.interaction_embeddings["disliked"]
            else None
        )

        if liked_vector is not None and disliked_vector is not None:
            return liked_vector - 0.5 * disliked_vector
        elif liked_vector is not None:
            return liked_vector
        elif disliked_vector is not None:
            return -disliked_vector
        return None


class RecommendationEngine:
    def __init__(self, faiss_index_path, product_metadata_path):
        # Get script directory for relative paths
        script_dir = os.path.dirname(os.path.abspath(__file__))
        faiss_index_path = os.path.join(script_dir, faiss_index_path)
        product_metadata_path = os.path.join(script_dir, product_metadata_path)
        
        self.index = faiss.read_index(faiss_index_path)

        with open(product_metadata_path, "r") as f:
            self.product_metadata = json.load(f)

        # Sort product keys to ensure consistent ordering with FAISS index
        self.product_keys_ordered = sorted(self.product_metadata.keys(), key=lambda x: int(x))
        
        # Map FAISS index to product metadata key
        self.faiss_id_to_key = {i: key for i, key in enumerate(self.product_keys_ordered)}
        self.key_to_faiss_id = {key: i for i, key in enumerate(self.product_keys_ordered)}
        
        # Map product ID (e.g., "product_1") to metadata key (e.g., "1")
        self.product_id_to_key = {
            self.product_metadata[key]["id"]: key 
            for key in self.product_keys_ordered
        }

        self.user_trackers = {}

    def record_user_interaction(self, user_id, product_id, reaction="like"):
        if user_id not in self.user_trackers:
            self.user_trackers[user_id] = UserInteractionTracker()

        # Convert product_id to metadata key
        key = self.product_id_to_key.get(product_id)
        if key is None:
            print(f"Warning: Product ID {product_id} not found")
            return
            
        faiss_idx = self.key_to_faiss_id.get(key)
        if faiss_idx is not None:
            embedding = self.index.reconstruct(faiss_idx)
            
            # Normalize the embedding
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm

            # Record interaction
            self.user_trackers[user_id].add_interaction(product_id, embedding, reaction)

    def get_recommendations(
        self, user_id, num_recommendations=10, color_filter=None, category_filter=None
    ):
        user_tracker = self.user_trackers.get(user_id, UserInteractionTracker())

        user_preference = user_tracker.compute_preference_vector()

        if user_preference is None:
            return self._get_diverse_recommendations(
                num_recommendations, color_filter, category_filter
            )

        # Normalize user preference vector
        norm = np.linalg.norm(user_preference)
        if norm > 0:
            user_preference = user_preference / norm

        distances, indices = self.index.search(
            np.array([user_preference]), k=self.index.ntotal  # Search entire index
        )

        indices = indices[0]
        distances = distances[0]

        # Collect candidates for MMR re-ranking
        candidates = []
        for i, idx in enumerate(indices):
            idx = int(idx)  # Convert to Python int
            if idx >= len(self.product_keys_ordered):
                continue

            key = self.faiss_id_to_key[idx]
            product_info = self.product_metadata[key]
            product_id = product_info["id"]

            # Skip already interacted products
            if (
                product_id in user_tracker.liked_products
                or product_id in user_tracker.disliked_products
            ):
                continue

            # Apply filters
            color_match = not color_filter or product_info.get("color", "").lower() in [
                c.lower() for c in color_filter
            ]
            category_match = not category_filter or product_info.get(
                "category", ""
            ).lower() in [c.lower() for c in category_filter]

            if color_match and category_match:
                embedding = self.index.reconstruct(idx)
                # Normalize embedding
                norm_emb = np.linalg.norm(embedding)
                if norm_emb > 0:
                    embedding = embedding / norm_emb
                    
                candidates.append({
                    "idx": idx,
                    "key": key,
                    "product_info": product_info,
                    "similarity_score": 1 / (1 + distances[i]),
                    "embedding": embedding
                })

        # Apply MMR re-ranking for diversity
        filtered_recommendations = self._mmr_rerank(
            candidates, 
            user_preference, 
            num_recommendations
        )

        return filtered_recommendations

    def _mmr_rerank(self, candidates, query_vector, num_recommendations, lambda_param=0.7):
        """
        Apply Maximal Marginal Relevance (MMR) re-ranking for diversity.
        lambda_param: balance between relevance (1.0) and diversity (0.0)
        """
        if not candidates:
            return []
        
        selected = []
        remaining = candidates.copy()
        
        while len(selected) < num_recommendations and remaining:
            if not selected:
                # Select most relevant item first
                best_idx = max(range(len(remaining)), 
                             key=lambda i: remaining[i]["similarity_score"])
            else:
                # Compute MMR scores
                mmr_scores = []
                for candidate in remaining:
                    # Relevance to query
                    relevance = np.dot(query_vector, candidate["embedding"])
                    
                    # Max similarity to already selected items
                    max_sim = max(
                        np.dot(candidate["embedding"], s["embedding"])
                        for s in selected
                    )
                    
                    # MMR formula
                    mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim
                    mmr_scores.append(mmr_score)
                
                best_idx = max(range(len(mmr_scores)), key=lambda i: mmr_scores[i])
            
            selected.append(remaining.pop(best_idx))
        
        # Format results
        results = []
        for item in selected:
            result = {
                "similarity_score": float(item["similarity_score"]),  # Convert numpy to Python float
                **item["product_info"]
            }
            results.append(result)
        
        return results

    def _get_diverse_recommendations(
        self, num_recommendations, color_filter=None, category_filter=None
    ):
        total_vectors = self.index.ntotal

        step = max(1, total_vectors // (num_recommendations * 2))

        recommendations = []
        for i in range(0, total_vectors, step):
            key = self.faiss_id_to_key[i]
            product_info = self.product_metadata[key]

            color_match = not color_filter or product_info.get("color", "").lower() in [
                c.lower() for c in color_filter
            ]
            category_match = not category_filter or product_info.get(
                "category", ""
            ).lower() in [c.lower() for c in category_filter]

            if color_match and category_match:
                recommendations.append({**product_info})

                if len(recommendations) >= num_recommendations:
                    break

        return recommendations


def main():
    rec_engine = RecommendationEngine(
        faiss_index_path="image_vectors.index",
        product_metadata_path="processed_data.json",
    )

    user_id = "user_001"

    # Simulate liking a black dress
    print("=== User likes a black dress ===")
    rec_engine.record_user_interaction(user_id, "product_3", "like")  # Assuming this is black

    print("\n=== Recommendations (should show diverse colors, not just black) ===")
    recommendations = rec_engine.get_recommendations(
        user_id,
        num_recommendations=10
    )

    # Count colors to show diversity
    color_counts = {}
    for i, rec in enumerate(recommendations, 1):
        color = rec.get('color', 'unknown')
        color_counts[color] = color_counts.get(color, 0) + 1
        
        print(f"\n{i}. {rec.get('title', 'N/A')[:60]}")
        print(f"   Color: {color}")
        print(f"   Category: {rec.get('category', 'N/A')}")
        print(f"   Price: {rec.get('price', 'N/A')}")
        print(f"   Similarity: {rec.get('similarity_score', 0):.4f}")
    
    print(f"\n=== Color Distribution (showing diversity) ===")
    for color, count in sorted(color_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{color}: {count}")


if __name__ == "__main__":
    main()
