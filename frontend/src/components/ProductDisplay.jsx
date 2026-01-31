import { useState, useEffect } from 'react';

function ProductDisplay({ recommendation, isLoading, loadingText, isProcessing, onLike, onDislike }) {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageLoading, setImageLoading] = useState(false);
  const [similarityWidth, setSimilarityWidth] = useState(0);

  useEffect(() => {
    if (recommendation) {
      setImageLoaded(false);
      setImageLoading(true);
      setSimilarityWidth(0);
    }
  }, [recommendation]);

  const handleImageLoad = () => {
    setImageLoading(false);
    setImageLoaded(true);
    
    // Animate similarity bar - check for similarity_kscore (personalized) or default to 100 (diverse)
    if (recommendation?.similarity_kscore !== undefined) {
      setTimeout(() => {
        setSimilarityWidth(Math.round(recommendation.similarity_kscore * 100));
      }, 400);
    } else {
      setTimeout(() => {
        setSimilarityWidth(100);
      }, 400);
    }
  };

  const handleImageError = () => {
    setImageLoading(false);
  };

  const getSimilarityPercentage = () => {
    if (recommendation?.similarity_kscore !== undefined) {
      return Math.round(recommendation.similarity_kscore * 100) + '%';
    }
    return 'New';
  };

  return (
    <div className="recommendation-container">
      {/* Loading Overlay */}
      <div className={`loading-overlay ${isLoading ? 'active' : ''}`}>
        <div style={{ textAlign: 'center' }}>
          <div className="loader"></div>
          <div className="loading-text">{loadingText}</div>
        </div>
      </div>

      {/* Image Container */}
      {recommendation && (
        <>
          <div className="image-container">
            {imageLoading && (
              <div className="image-loading">
                <div className="spinner"></div>
              </div>
            )}
            <img
              id="recommendedImage"
              className={imageLoaded ? 'loaded' : ''}
              src={recommendation.image_href}
              alt="Recommended Product"
              onLoad={handleImageLoad}
              onError={handleImageError}
            />
          </div>

          {/* Product Info */}
          <div className={`product-info ${imageLoaded ? 'visible' : ''}`}>
            <div className="product-title">
              {recommendation.title || 'Fashion Item'}
            </div>
            <div className="product-details">
              {recommendation.color && recommendation.color !== 'unknown' && (
                <span className="product-tag">🎨 {recommendation.color}</span>
              )}
              {recommendation.category && (
                <span className="product-tag">👗 {recommendation.category}</span>
              )}
              {recommendation.price && (
                <span className="product-tag">💰 ₹{recommendation.price}</span>
              )}
            </div>
          </div>

          {/* Similarity Section */}
          <div className={`similarity-section ${imageLoaded ? 'visible' : ''}`}>
            <div className="similarity-label">
              <span className="similarity-text">Match Confidence</span>
              <span className="similarity-percentage">{getSimilarityPercentage()}</span>
            </div>
            <div className="similarity-bar">
              <div
                className="similarity-indicator"
                style={{ width: `${similarityWidth}%` }}
              ></div>
            </div>
          </div>

          {/* Action Buttons */}
          <div>
            <div className="interaction-buttons">
              <button
                className="btn-action btn-dislike"
                onClick={onDislike}
                disabled={isProcessing}
                title="Dislike"
              >
                👎
              </button>
              <button
                className="btn-action btn-like"
                onClick={onLike}
                disabled={isProcessing}
                title="Like"
              >
                👍
              </button>
            </div>
            <div className="keyboard-hint">
              Keyboard: <kbd>←</kbd> Dislike | <kbd>→</kbd> Like
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default ProductDisplay;
