import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ProductDisplay from './components/ProductDisplay';
import Toast from './components/Toast';
import './App.css';

function App() {
  const [currentUserId] = useState(() => {
    let userId = localStorage.getItem('userId');
    if (!userId) {
      userId = 'user_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('userId', userId);
    }
    return userId;
  });

  const [currentProductId, setCurrentProductId] = useState(null);
  const [recommendationQueue, setRecommendationQueue] = useState([]);
  const [colors, setColors] = useState([]);
  const [categories, setCategories] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingText, setLoadingText] = useState('Finding perfect matches...');
  const [currentRecommendation, setCurrentRecommendation] = useState(null);
  const [toast, setToast] = useState({ show: false, message: '', icon: '' });

  // Console greeting
  useEffect(() => {
    console.log('%c✨ CINDER Fashion Discovery ✨', 'font-size: 20px; color: #667eea; font-weight: bold;');
    console.log('%cUser ID: ' + currentUserId, 'color: #764ba2;');
    console.log('%c⌨️  Keyboard shortcuts:', 'color: #95a5a6; font-weight: bold;');
    console.log('%c  ← Left Arrow: 👎 Dislike (2 stars)', 'color: #95a5a6;');
    console.log('%c  → Right Arrow: 👍 Like (4 stars)', 'color: #95a5a6;');
    console.log('%c  ↑ Up Arrow: 😍 Love It (5 stars)', 'color: #95a5a6;');
    console.log('%c  ↓ Down Arrow: 😡 Hate It (1 star)', 'color: #95a5a6;');
  }, [currentUserId]);

  // Auto-fetch recommendations on mount
  useEffect(() => {
    fetchRecommendations();
  }, []);

  // Debug: Log loading state changes
  useEffect(() => {
    console.log('🔄 Loading state changed:', isLoading);
  }, [isLoading]);

  // Debug: Log when recommendation changes
  useEffect(() => {
    console.log('🎯 Current recommendation:', currentRecommendation?.id || 'none');
  }, [currentRecommendation]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (!currentProductId || isProcessing) return;
      
      if (event.key === 'ArrowRight') {
        event.preventDefault();
        handleUserInteraction(4);  // Like (4 stars) - 👍
      } else if (event.key === 'ArrowLeft') {
        event.preventDefault();
        handleUserInteraction(2);  // Dislike (2 stars) - 👎
      } else if (event.key === 'ArrowUp') {
        event.preventDefault();
        handleUserInteraction(5);  // Super like (5 stars) - 😍
      } else if (event.key === 'ArrowDown') {
        event.preventDefault();
        handleUserInteraction(1);  // Strong dislike (1 star) - 😡
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [currentProductId, isProcessing]);

  const showToast = (message, icon = '✅') => {
    setToast({ show: true, message, icon });
    setTimeout(() => {
      setToast({ show: false, message: '', icon: '' });
    }, 3000);
  };

  const fetchRecommendations = async () => {
    if (isProcessing) {
      console.log('⏸️ Already processing, skipping fetch');
      return;
    }
    
    setIsLoading(true);
    setLoadingText('Analyzing your preferences...');
    
    console.log('🚀 Starting fetch recommendations...');
    
    try {
      const response = await fetch('http://localhost:8000/get-recommendations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: currentUserId,
          colors: colors,
          categories: categories,
          num_recommendations: 20  // Increased from 10 to 20
        })
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      const recommendations = data.recommendations;

      // Console log the fetched recommendations
      console.log('📦 Fetched Recommendations:', recommendations);
      console.log(`📊 Total count: ${recommendations.length}`);
      if (recommendations.length > 0) {
        console.table(recommendations.map(rec => ({
          id: rec.id,
          title: rec.title,
          color: rec.color,
          category: rec.category,
          price: rec.price,
          similarity: rec.similarity_kscore ? `${Math.round(rec.similarity_kscore * 100)}%` : 'N/A (diverse mode)'
        })));
      }

      if (recommendations.length > 0) {
        showToast(`Found ${recommendations.length} perfect matches!`, '🎉');
        console.log('🎬 Setting first recommendation:', recommendations[0].id);
        // Set all states together - React 18 will batch these automatically
        setCurrentRecommendation(recommendations[0]);
        setCurrentProductId(recommendations[0].id);
        setRecommendationQueue(recommendations.slice(1));
        setIsLoading(false);
        setIsProcessing(false);  // Clear processing flag
        console.log('✅ States updated, loading hidden, processing cleared');
      } else {
        console.log('⚠️ No recommendations received');
        showToast('No more recommendations available. You\'ve seen them all! 🎊', '✨');
        setIsProcessing(false);
        setIsLoading(false);
      }
    } catch (error) {
      console.error('❌ Error fetching recommendations:', error);
      showToast('Failed to fetch recommendations. Check if server is running!', '❌');
      setIsLoading(false);
      setIsProcessing(false);
    }
  };

  const handleUserInteraction = async (rating) => {
    if (!currentUserId || !currentProductId || isProcessing) {
      showToast('Please fetch recommendations first', '⚠️');
      return;
    }

    setIsProcessing(true);

    // Map ratings to emoji feedback
    const feedbackMap = {
      1: { icon: '💔', message: 'Got it, we\'ll avoid similar items!' },
      2: { icon: '👎', message: 'Noted your preference!' },
      4: { icon: '👍', message: 'Added to your favorites!' },
      5: { icon: '😍', message: 'Amazing! We\'ll find more like this!' }
    };
    
    const feedback = feedbackMap[rating] || { icon: '✅', message: 'Thanks for the feedback!' };
    showToast(feedback.message, feedback.icon);

    try {
      await fetch('http://localhost:8000/record-interaction', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: currentUserId,
          product_id: currentProductId,
          rating: rating  // Now sending rating instead of reaction
        })
      });

      if (recommendationQueue.length > 0) {
        const nextRecommendation = recommendationQueue[0];
        setCurrentRecommendation(nextRecommendation);
        setCurrentProductId(nextRecommendation.id);
        setRecommendationQueue(recommendationQueue.slice(1));
        setIsProcessing(false);
      } else {
        setLoadingText('Finding more matches...');
        setIsLoading(true);
        await fetchRecommendations();
        setIsProcessing(false);
      }
    } catch (error) {
      console.error('Error:', error);
      showToast('Failed to process interaction', '❌');
      setIsProcessing(false);
    }
  };

  return (
    <>
      {/* Background particles */}
      <div className="bg-particle"></div>
      <div className="bg-particle"></div>
      <div className="bg-particle"></div>

      <div className="app-container">
        <Sidebar
          colors={colors}
          setColors={setColors}
          categories={categories}
          setCategories={setCategories}
          onRefresh={fetchRecommendations}
          isLoading={isLoading}
        />

        <div className="main-content">
          <ProductDisplay
            recommendation={currentRecommendation}
            isLoading={isLoading}
            loadingText={loadingText}
            isProcessing={isProcessing}
            onRate={handleUserInteraction}
          />
        </div>
      </div>

      <Toast
        show={toast.show}
        message={toast.message}
        icon={toast.icon}
      />
    </>
  );
}

export default App;
