// src/components/layout/Header.jsx

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Header.css';

export const Header = () => {
  const navigate = useNavigate();
  const authToken = localStorage.getItem('authToken');

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    // Redireciona o usuário para a página de login
    navigate('/login');
  };

  return (
    <header className="main-header">
      <div className="header-container">
<Link to="/" className="logo">
  <img src="/Logo.png" alt="Gerador de GIFs Logo" /><span>Gerador de GIFs ✨</span>
</Link>
        <nav className="main-nav">
          <ul>
            <li>
              <Link to="/profile">Criar GIF</Link>
            </li>
            <li>
              <Link to="/plans">Planos</Link>
            </li>
            {authToken ? (
              // Se o usuário estiver logado, mostra o botão "Sair"
              <li>
                <button onClick={handleLogout} className="nav-button">
                  Sair
                </button>
              </li>
            ) : (
              // Se não estiver logado, mostra o link para "Login"
              <li>
                <Link to="/login" className="nav-button">
                  Entrar
                </Link>
              </li>
            )}
          </ul>
        </nav>
      </div>
    </header>
  );
};