import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import './components/AdminPreview.css';

class AppErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error('Error al renderizar ESSAID:', error, info.componentStack);
  }

  render() {
    if (!this.state.error) return this.props.children;
    return (
      <main className="app-error-page" role="alert">
        <section className="app-error-card">
          <p className="eyebrow">ERROR DE LA APLICACIÓN</p>
          <h1>No se pudo cargar el panel</h1>
          <p>Ocurrió un error al mostrar esta página. Recarga e inténtalo de nuevo.</p>
          <details>
            <summary>Detalles técnicos</summary>
            <code>{this.state.error.message}</code>
          </details>
          <button className="primary-button" type="button" onClick={() => window.location.reload()}>Recargar</button>
        </section>
      </main>
    );
  }
}

const root = document.getElementById('root');
if (root) {
  createRoot(root).render(
    <React.StrictMode>
      <AppErrorBoundary><App /></AppErrorBoundary>
    </React.StrictMode>,
  );
}

