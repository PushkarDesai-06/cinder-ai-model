import { useState, useEffect } from 'react';

function ProductDisplay({ recommendation, isLoading, loadingText, isProcessing, onRate }) {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageLoading, setImageLoading] = useState(false);
  const [similarityWidth, setSimilarityWidth] = useState(0);
  const [isTitleExpanded, setIsTitleExpanded] = useState(false);

  useEffect(() => {
    if (recommendation) {
      setImageLoaded(false);
      setImageLoading(true);
      setSimilarityWidth(0);
      setIsTitleExpanded(false); // Reset title expansion for new recommendation
      
      // Fallback timeout: if image doesn't load in 10 seconds, show it anyway
      const timeout = setTimeout(() => {
        console.log('⏰ Image load timeout - forcing display');
        setImageLoading(false);
        setImageLoaded(true);
      }, 10000);
      
      return () => clearTimeout(timeout);
    }
  }, [recommendation]);

  const handleImageLoad = () => {
    console.log('🖼️ Image loaded successfully');
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

  const handleImageError = (e) => {
    console.log('❌ Image failed to load:', e.target.src);
    setImageLoading(false);
    setImageLoaded(true); // Set to true to show the rest of the UI even if image fails
  };

  const getSimilarityPercentage = () => {
    if (recommendation?.similarity_kscore !== undefined) {
      return Math.round(recommendation.similarity_kscore * 100) + '%';
    }
    return 'New';
  };

  // Debug logging
  console.log('🎨 ProductDisplay render:', {
    hasRecommendation: !!recommendation,
    isLoading,
    isProcessing,
    imageLoaded,
    imageLoading
  });

  return (
    <div className="recommendation-container">
      {/* Loading Overlay */}
      <div className={`loading-overlay ${isLoading ? 'active' : ''}`}>
        <div style={{ textAlign: 'center' }}>
          <div className="loader"></div>
          <div className="loading-text">{loadingText}</div>
        </div>
      </div>

      {/* Show content when we have a recommendation */}
      {recommendation ? (
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
              ref={(img) => {
                if (img) {
                  console.log('🖼️ Image element created:', {
                    src: img.src,
                    complete: img.complete,
                    naturalWidth: img.naturalWidth,
                    naturalHeight: img.naturalHeight
                  });
                  // If image is already loaded (cached), trigger onLoad manually
                  if (img.complete && img.naturalWidth > 0) {
                    console.log('✅ Image was already cached/loaded - triggering onLoad');
                    handleImageLoad();
                  }
                }
              }}
            />
          </div>

          {/* Product Info */}
          <div className={`product-info ${imageLoaded ? 'visible' : ''}`}>
            <div 
              className={`product-title ${isTitleExpanded ? 'expanded' : ''}`}
              onClick={() => setIsTitleExpanded(!isTitleExpanded)}
              title="Click to expand/collapse"
            >
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

          {/* Rating Buttons - Emoji Based */}
          <div>
            <div className="rating-section">
              <div className="rating-title">How do you feel about this?</div>
              <div className="rating-buttons">
                <button
                  className="btn-rating btn-hate"
                  onClick={() => onRate(1)}
                  disabled={isProcessing}
                  title="Hate It (1 star)"
                >
                  😡
                </button>
                <button
                  className="btn-rating btn-dislike"
                  onClick={() => onRate(2)}
                  disabled={isProcessing}
                  title="Dislike (2 stars)"
                >
                  👎
                </button>
                <button
                  className="btn-rating btn-like"
                  onClick={() => onRate(4)}
                  disabled={isProcessing}
                  title="Like (4 stars)"
                >
                  👍
                </button>
                <button
                  className="btn-rating btn-love"
                  onClick={() => onRate(5)}
                  disabled={isProcessing}
                  title="Love It! (5 stars)"
                >
                  �
                </button>
              </div>
              <div className="rating-labels">
                <span className="rating-label">Hate It</span>
                <span className="rating-label">Dislike</span>
                <span className="rating-label">Like</span>
                <span className="rating-label">Love It!</span>
              </div>
            </div>
            <div className="keyboard-hint">
              Quick Actions: <kbd>↓</kbd> Hate | <kbd>←</kbd> Dislike | <kbd>→</kbd> Like | <kbd>↑</kbd> Love
            </div>
          </div>
        </>
      ) : !isLoading && (
        // Show empty state only if not loading and no recommendation
        <div className="empty-state">
          <div className="empty-state-icon">👗</div>
          <div className="empty-state-text">Getting your recommendations ready...</div>
        </div>
      )}
    </div>
  );
}

export default ProductDisplay;
