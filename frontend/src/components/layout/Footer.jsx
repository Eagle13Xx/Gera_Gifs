// src/components/layout/Footer.jsx

import React from 'react';
import './Footer.css';

export const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="main-footer">
      <p>&copy; {currentYear} Gerador de GIFs. Todos os direitos reservados.</p>
      <p>Feito com carinho para todas as idades.</p>
        <p>Entre em contato com suporte pelo numero: (99) 9999-9999</p>
        <p>ou no Email geragif@gmail.com</p>
        <div className="django-badge">
          <a href="https://www.djangoproject.com/" target="_blank" rel="noopener noreferrer">
            <img
              src="https://www.djangoproject.com/m/img/badges/djangomade124x25.gif"
              alt="Made with Django."
              style={{ border: 'none' }} // Garante que a imagem não tenha bordas
            />
          </a>
        </div>
    </footer>
  );
};