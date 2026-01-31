# Cinder AI Model - Fashion Recommendation System

A modern fashion discovery platform powered by AI that provides personalized clothing recommendations based on visual similarity and user preferences.

## 🌟 Features

- **AI-Powered Visual Recommendations**: Uses Facebook's DINO ViT model for image embedding and similarity search
- **Personalized User Tracking**: Learns from user interactions (love, like, dislike, hate) to refine recommendations
- **Real-time Updates**: Interactive swipe-based interface with keyboard shortcuts
- **Filter Options**: Filter by colors and categories
- **FAISS Vector Search**: Fast and efficient similarity search using Facebook's FAISS library

## 🏗️ Architecture

### Backend (Python/FastAPI)

- **FastAPI**: Modern web framework for building APIs
- **FAISS**: Vector similarity search for finding similar fashion items
- **DINO ViT**: Vision Transformer model for generating image embeddings
- **User Tracking**: Personalized recommendation engine that learns from user interactions

### Frontend (React/Vite)

- **React 19**: Modern UI library
- **Vite**: Fast build tool and dev server
- **Swipe Interface**: Interactive product browsing with keyboard shortcuts
- **Toast Notifications**: User feedback for interactions

## 📋 Prerequisites

- **Python 3.8+** (Python 3.9 or 3.10 recommended)
- **Node.js 16+** and **npm/yarn**
- **Git**
- **CUDA-compatible GPU** (optional, for faster model training)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/PushkarDesai-06/cinder-ai-model.git
cd cinder-ai-model
```

### 2. Backend Setup

#### Navigate to Backend Directory

```bash
cd backend
```

#### Create Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Verify Required Files

Make sure these files exist in the `backend/` directory:

- `image_vectors.index` - FAISS index file
- `processed_data.json` - Product metadata

If these files don't exist, you'll need to run the model training (see [Model Training](#model-training) section).

#### Start the Backend Server

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`

You can view the API documentation at `http://localhost:8000/docs`

### 3. Frontend Setup

#### Open a New Terminal and Navigate to Frontend Directory

```bash
cd frontend
```

#### Install Dependencies

```bash
npm install
```

#### Start the Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173` (or another port if 5173 is in use)

### 4. Access the Application

Open your browser and navigate to `http://localhost:5173`

## 🎮 How to Use

### Keyboard Shortcuts

- **← Left Arrow**: 👎 Dislike (2 stars)
- **→ Right Arrow**: 👍 Like (4 stars)
- **↑ Up Arrow**: 😍 Love It (5 stars)
- **↓ Down Arrow**: 😡 Hate It (1 star)

### Filters

- Use the sidebar to filter by colors and categories
- Click "Get Recommendations" to apply filters

### User Tracking

The app automatically creates a unique user ID stored in your browser's localStorage. Your preferences are tracked server-side to provide increasingly personalized recommendations.

## 🧠 Implementation Details

### Backend Architecture

#### 1. Recommendation Engine (`recommendation_engine.py`)

```python
class RecommendationEngine:
    - Manages FAISS index for vector similarity search
    - Tracks user interactions with UserInteractionTracker
    - Computes personalized preference vectors
    - Filters recommendations by color and category
```

**Key Features:**

- **Cold Start**: Initial recommendations based on color/category filters or random selection
- **Personalization**: After user interactions, computes weighted preference vectors
- **Rating System**: Converts reactions (love/like/dislike/hate) to numerical weights
- **Diversity**: Ensures variety by avoiding duplicate recommendations

#### 2. FastAPI Server (`api.py`)

```python
Endpoints:
- POST /get-recommendations: Get personalized product recommendations
- POST /record-interaction: Record user reactions (love/like/dislike/hate)
```

**Request/Response Models:**

- `RecommendationRequest`: User ID, color/category filters, number of recommendations
- `UserInteractionRequest`: User ID, product ID, rating (1-5 or string reaction)

#### 3. CORS Configuration

Allows cross-origin requests from the frontend running on a different port.

### Frontend Architecture

#### 1. App Component (`App.jsx`)

**State Management:**

- `currentUserId`: Unique user identifier stored in localStorage
- `recommendationQueue`: Array of products to display
- `currentRecommendation`: Currently displayed product
- `colors/categories`: Active filters
- `isLoading`: Loading state for fetching recommendations

**Key Functions:**

- `fetchRecommendations()`: Fetches products from backend API
- `handleReaction()`: Records user interaction and shows next product
- `preloadImages()`: Preloads next images for smooth transitions

#### 2. Components

- **ProductDisplay**: Shows product image, name, price, and action buttons
- **Sidebar**: Filter controls for colors and categories
- **Toast**: Notification system for user feedback

### Model Architecture

#### Image Embedding Pipeline (`model/model.py`)

1. **Model**: Facebook DINO ViT-S/16 (Vision Transformer)
2. **Preprocessing**: Resize to 224x224, normalize with ImageNet statistics
3. **Embedding**: 384-dimensional feature vectors
4. **Storage**: FAISS IndexFlatL2 for efficient similarity search

**Process Flow:**

```
Image URL → Download → PIL Image → Preprocessing →
ViT Model → Embedding Vector → FAISS Index
```

### Data Pipeline

#### Scraper (`scraper/`)

1. **get_hrefs.py**: Scrapes product URLs from e-commerce site
2. **get_products.py**: Extracts product details (name, price, image, colors, categories)
3. **process_data.py**: Cleans and structures data for model consumption

#### Data Files

- `href_data.json`: Raw product URLs
- `product_data.json`: Raw product information
- `processed_data.json`: Cleaned and structured product data

### Algorithm: Preference Vector Computation

```
For each user interaction:
  - Convert rating to weight: (rating - 3) / 2.0
  - Multiply embedding by weight
  - Sum weighted embeddings
  - Normalize by total absolute weights
  - Return normalized preference vector

Similarity Search:
  - Query FAISS index with preference vector
  - Get top N most similar items
  - Filter out already-rated products
  - Apply color/category filters
  - Return diverse set of recommendations
```

### Performance Optimizations

1. **GPU Acceleration**: Model runs on CUDA if available
2. **FAISS Index**: O(log n) search complexity for large product catalogs
3. **Image Preloading**: Frontend preloads next 2 images for smooth UX
4. **Batch Processing**: Model processes images in batches during training
5. **Caching**: Product metadata loaded once at startup

## 🔧 Model Training

If you need to regenerate the FAISS index and embeddings:

### 1. Scrape Product Data

```bash
cd scraper
python get_hrefs.py      # Get product URLs
python get_products.py   # Extract product details
python process_data.py   # Clean and structure data
```

### 2. Generate Embeddings

```bash
cd model
python model.py
```

This will:

- Load the DINO ViT model
- Process all product images
- Generate 384-dimensional embeddings
- Create FAISS index
- Save `image_vectors.index` and `image_embeddings.json`

### 3. Copy Files to Backend

```bash
cp model/image_vectors.index backend/
cp scraper/data/processed_data.json backend/
```

## 📁 Project Structure

```
cinder-ai-model/
├── backend/                   # FastAPI backend
│   ├── api.py                # API endpoints
│   ├── recommendation_engine.py  # Core recommendation logic
│   ├── requirements.txt      # Python dependencies
│   ├── image_vectors.index   # FAISS index
│   └── processed_data.json   # Product metadata
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── App.jsx          # Main app component
│   │   ├── components/      # Reusable components
│   │   └── assets/          # Static assets
│   ├── package.json         # Node dependencies
│   └── vite.config.js       # Vite configuration
├── model/                     # ML model training
│   ├── model.py             # Embedding generation
│   └── model.ipynb          # Jupyter notebook
├── scraper/                   # Data collection
│   ├── get_hrefs.py         # URL scraping
│   ├── get_products.py      # Product data extraction
│   └── process_data.py      # Data cleaning
└── mdfiles/                   # Documentation
    ├── HYPERPARAMETERS.md   # Model configuration
    └── INTEGRATION_STATUS.md # Integration docs
```

## 🐛 Troubleshooting

### Backend Issues

**Error: "Recommendation engine not initialized"**

- Ensure `image_vectors.index` and `processed_data.json` exist in `backend/`
- Run model training to generate these files

**FAISS Installation Issues**

```bash
# On Windows, you might need to install FAISS via conda
conda install -c pytorch faiss-cpu
```

**Port 8000 Already in Use**

```bash
# Change port in uvicorn command
uvicorn api:app --reload --port 8001
# Update frontend API URL in App.jsx
```

### Frontend Issues

**Error: "Cannot connect to backend"**

- Verify backend is running at `http://localhost:8000`
- Check CORS configuration in `api.py`
- Open browser console for detailed error messages

**npm install Fails**

```bash
# Clear npm cache and try again
npm cache clean --force
npm install
```

## 📊 API Endpoints

### POST `/get-recommendations`

Get personalized product recommendations

**Request Body:**

```json
{
  "user_id": "user_abc123",
  "colors": ["black", "white"],
  "categories": ["tops", "dresses"],
  "num_recommendations": 20
}
```

**Response:**

```json
{
  "recommendations": [
    {
      "id": "product_123",
      "name": "Product Name",
      "price": "$29.99",
      "image": "https://...",
      "colors": ["black"],
      "category": "tops"
    }
  ],
  "is_tracked": true,
  "total_interactions": 5
}
```

### POST `/record-interaction`

Record user interaction with a product

**Request Body:**

```json
{
  "user_id": "user_abc123",
  "product_id": "product_123",
  "rating": "love"
}
```

**Rating Values:**

- `"love"` or `5`: Love it! (5 stars)
- `"like"` or `4`: Like it (4 stars)
- `3`: Neutral (3 stars)
- `"dislike"` or `2`: Dislike (2 stars)
- `"hate"` or `1`: Hate it (1 star)

**Response:**

```json
{
  "message": "Interaction recorded successfully",
  "total_interactions": 6
}
```

## 🔐 Environment Variables (Optional)

Create a `.env` file in the backend directory for configuration:

```env
# Backend Configuration
PORT=8000
HOST=0.0.0.0

# FAISS Configuration
FAISS_INDEX_PATH=image_vectors.index
METADATA_PATH=processed_data.json

# Model Configuration
DEVICE=cuda  # or cpu
```

## 🚢 Production Deployment

### Backend

```bash
# Use production ASGI server
pip install gunicorn
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend

```bash
# Build for production
npm run build

# Files will be in dist/ directory
# Serve with any static file server (nginx, vercel, netlify, etc.)
```

## 📝 License

This project is licensed under the MIT License.

## 👥 Contributors

- Pushkar Desai ([@PushkarDesai-06](https://github.com/PushkarDesai-06))

## 🙏 Acknowledgments

- **Facebook DINO**: Vision Transformer model for image embeddings
- **FAISS**: Efficient similarity search library
- **FastAPI**: Modern Python web framework
- **React & Vite**: Fast and modern frontend development

---

**Built with ❤️ using AI and Computer Vision**
