import { useState } from 'react';

function Sidebar({ colors, setColors, categories, setCategories, onRefresh, isLoading }) {
  const [colorInput, setColorInput] = useState('');
  const [categoryInput, setCategoryInput] = useState('');

  const handleColorChange = (e) => {
    setColorInput(e.target.value);
    const parsedColors = e.target.value
      .split(',')
      .map(color => color.trim())
      .filter(color => color !== '');
    setColors(parsedColors);
  };

  const handleCategoryChange = (e) => {
    setCategoryInput(e.target.value);
    const parsedCategories = e.target.value
      .split(',')
      .map(category => category.trim())
      .filter(category => category !== '');
    setCategories(parsedCategories);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      onRefresh();
    }
  };

  return (
    <div className="sidebar">
      <div className="app-header">
        <div className="app-logo">
          <span>CINDER</span>
        </div>
        <div className="app-tagline">Discover Fashion That Matches Your Style</div>
      </div>

      <div className="sidebar-card">
        <div className="sidebar-title">🎯 Preferences</div>
        <div className="filter-container">
          <div className="filter-group">
            <label htmlFor="colorFilter">🎨 Colors</label>
            <input
              type="text"
              id="colorFilter"
              placeholder="e.g., blue, green, red"
              value={colorInput}
              onChange={handleColorChange}
              onKeyPress={handleKeyPress}
            />
          </div>
          <div className="filter-group">
            <label htmlFor="categoryFilter">👗 Categories</label>
            <input
              type="text"
              id="categoryFilter"
              placeholder="e.g., Below the Knee"
              value={categoryInput}
              onChange={handleCategoryChange}
              onKeyPress={handleKeyPress}
            />
          </div>
          <button
            className="btn-get-recs"
            onClick={onRefresh}
            disabled={isLoading}
          >
            {isLoading ? '⏳ Loading...' : '🔄 Refresh Matches'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
