import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';

/**
 * main.jsx — React application entry point.
 *
 * Mounts the App component to the #root div in index.html.
 * StrictMode enables additional development-mode checks and warnings.
 */
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
