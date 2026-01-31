# Cinder Frontend - React Migration

## 🎉 Successfully Migrated to React!

The frontend has been migrated from vanilla HTML/JavaScript to **React** using **Vite** as the build tool.

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Sidebar.jsx          # Filter sidebar component
│   │   ├── ProductDisplay.jsx   # Main product display component
│   │   └── Toast.jsx            # Toast notification component
│   ├── App.jsx                  # Main app component with state management
│   ├── App.css                  # All styles (preserved from original)
│   ├── index.css                # Global styles and font import
│   └── main.jsx                 # React entry point
├── index.html                   # Vite HTML template
├── package.json                 # Dependencies
└── vite.config.js              # Vite configuration
```

## 🚀 Getting Started

### Install Dependencies

```bash
cd frontend
npm install
```

### Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173/`

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## ✨ What Changed?

### Technology Stack

- **Build Tool**: Vite (modern, fast, with HMR)
- **Framework**: React 18
- **State Management**: React Hooks (useState, useEffect)
- **Styling**: Same CSS preserved in separate file

### Component Architecture

The app is now organized into logical React components:

1. **App.jsx** - Main container with:
   - User ID management
   - Recommendation fetching logic
   - User interaction handling
   - Keyboard shortcuts
   - State management

2. **Sidebar.jsx** - Filter controls:
   - Color filter input
   - Category filter input
   - Refresh button
   - Filter parsing

3. **ProductDisplay.jsx** - Product presentation:
   - Image display with loading states
   - Product information
   - Similarity score visualization
   - Like/Dislike buttons

4. **Toast.jsx** - Notifications:
   - Success/error messages
   - Auto-dismissal

### Features Preserved

✅ All original functionality maintained:

- User ID persistence in localStorage
- Recommendation fetching with filters
- Interactive like/dislike buttons
- Keyboard shortcuts (← for dislike, → for like)
- Loading animations
- Toast notifications
- Similarity score visualization
- Responsive design
- Background particle animations

### Design

🎨 **Identical visual design** - All CSS has been preserved exactly as it was, ensuring the look and feel remains the same.

## 🔌 Backend Integration

The app connects to the backend at `http://localhost:8000`:

- `POST /get-recommendations` - Fetch recommendations
- `POST /record-interaction` - Record user likes/dislikes

Make sure your backend API is running before starting the frontend.

## 🛠 Development

### Hot Module Replacement (HMR)

Vite provides instant hot reloading - changes to your components will reflect immediately without losing state.

### Adding New Features

- Add new components in `src/components/`
- Update state management in `App.jsx`
- Add styles to `App.css`

## 📦 Dependencies

```json
{
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "vite": "^7.3.1"
}
```

## 🎯 Benefits of React Migration

1. **Better Code Organization** - Separated concerns into reusable components
2. **Improved Maintainability** - Easier to update and debug
3. **State Management** - Cleaner state handling with hooks
4. **Developer Experience** - HMR, better debugging, React DevTools
5. **Scalability** - Easy to add new features and components
6. **Modern Tooling** - Vite provides lightning-fast builds
7. **Type Safety Ready** - Easy to migrate to TypeScript if needed

## 🔄 Migration Notes

- All functionality tested and working
- No breaking changes to the API contract
- Same user experience maintained

---

**Note**: The backend API must be running at `http://localhost:8000` for the frontend to work properly.
