// src/pages/HomePage.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css';

const HomePage = () => {
  return (
    <div className="home-page">
      <section className="hero-section">
        <div className="hero-content">
          <h1>GIFs Personalizados para Momentos Especiais</h1>
          <p className="hero-subtitle">
            Crie lindos GIFs de bom dia, boa tarde e boa noite com IA para compartilhar com amigos e familiares.
          </p>
          <div className="hero-actions">
            <Link to="/profile?tab=generator" className="btn btn-primary btn-large">
              Começar a Criar
            </Link>
            <Link to="/plans" className="btn btn-secondary btn-large">
              Ver Planos
            </Link>
          </div>
        </div>
      </section>
     {/* ... outras seções ... */}
    </div>
  );
};

export default HomePage;