import faiss
import json
import numpy as np
import os


class UserInteractionTracker:
    def __init__(self):
        self.interactions = []  # List of dicts: {product_id, embedding, rating, weight}
        self.rated_products = set()  # Track which products have been rated

    def add_interaction(self, product_id, embedding, rating):
        """
        Add user interaction with rating-based weighting.
        rating can be: 1-5 (stars) OR 'love' (5), 'like' (4), 'dislike' (2), 'hate' (1)
        """
        # Convert string reactions to numeric ratings for backward compatibility
        rating_map = {
            'love': 5,      # 😍 Super like
            'like': 4,      # 👍 Like (right arrow)
            'dislike': 2,   # 👎 Dislike (left arrow)
            'hate': 1       # 😡 Strong dislike
        }
        
        if isinstance(rating, str):
            rating = rating_map.get(rating, 3)  # Default to neutral if unknown
        
        # Convert rating (1-5) to weight (-1.0 to +1.0)
        # 5 stars → +1.0, 4 stars → +0.5, 3 stars → 0, 2 stars → -0.5, 1 star → -1.0
        weight = (rating - 3) / 2.0
        
        self.interactions.append({
            'product_id': product_id,
            'embedding': embedding,
            'rating': rating,
            'weight': weight
        })
        self.rated_products.add(product_id)
        
        print(f"📊 Interaction recorded: Product {product_id}, Rating: {rating} stars, Weight: {weight:.2f}")

    def compute_preference_vector(self):
        """
        Compute user preference vector as weighted average of rated items.
        Items with higher ratings have more positive influence.
        """
        if not self.interactions:
            return None
        
        # Calculate weighted sum of embeddings
        weighted_sum = np.zeros_like(self.interactions[0]['embedding'])
        total_weight = 0.0
        
        for item in self.interactions:
            weighted_sum += item['weight'] * item['embedding']
            total_weight += abs(item['weight'])  # Use absolute weight for normalization
        
        if total_weight > 0:
            preference = weighted_sum / total_weight
            
            # Normalize the preference vector
            norm = np.linalg.norm(preference)
            if norm > 0:
                preference = preference / norm
            
            print(f"🎯 Computed preference vector from {len(self.interactions)} interactions")
            return preference
        
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

    def record_user_interaction(self, user_id, product_id, rating):
        """
        Record user interaction with rating.
        rating can be: 1-5 (numeric) OR 'love', 'like', 'dislike', 'hate' (string)
        """
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

            # Record interaction with rating
            self.user_trackers[user_id].add_interaction(product_id, embedding, rating)

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
            if product_id in user_tracker.rated_products:
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
                
                # Calculate cosine similarity directly (since embeddings are normalized)
                # This is more meaningful than distance-based similarity
                cosine_similarity = np.dot(user_preference, embedding)
                # Convert from [-1, 1] to [0, 1] range for display
                similarity_score = (cosine_similarity + 1) / 2
                    
                candidates.append({
                    "idx": idx,
                    "key": key,
                    "product_info": product_info,
                    "similarity_score": float(similarity_score),
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
        
        # Debug logging
        if results:
            print(f"🎯 Returning {len(results)} personalized recommendations")
            scores = [f"{r['similarity_score']:.2f}" for r in results[:3]]
            print(f"   Similarity scores: {scores}")
        
        return results

    def _get_diverse_recommendations(
        self, num_recommendations, color_filter=None, category_filter=None
    ):
        """
        Get diverse recommendations by sampling evenly across the entire catalog.
        Increased diversity for cold start experience.
        """
        total_vectors = self.index.ntotal

        # Increase diversity multiplier from 2 to 5 for maximum spread
        step = max(1, total_vectors // (num_recommendations * 5))

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

        print(f"🌈 Returning {len(recommendations)} diverse recommendations (cold start)")
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
