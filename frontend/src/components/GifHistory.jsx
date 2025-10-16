import React from 'react';
import './GifHistory.css';

const GifHistory = ({ gifs, isLoading }) => {
  if (isLoading) {
    return <p>Carregando histórico...</p>;
  }

  if (gifs.length === 0) {
    return (
      <div className="gif-history-empty">
        <h3>Você ainda não criou nenhum GIF.</h3>
        <p>Use a aba "Criar GIF" para começar a sua coleção!</p>
      </div>
    );
  }

  // Função para limpar o texto extra que a IA adiciona ao prompt
  const cleanPrompt = (text) => {
    return text.replace(', beautiful, high quality, cinematic', '');
  };

  return (
    <div className="gif-history-list">
      {gifs.map((gif) => (
        <div key={gif.id} className="gif-history-card">
          {/* Coluna da Imagem */}
          <div className="gif-image-container">
            <img src={gif.gif_url} alt={gif.prompt} className="gif-history-image" />
          </div>

          {/* Coluna dos Detalhes */}
          <div className="gif-history-details">

            {/* Mostrando o Prompt */}
            <div className="prompt-details">
              <h4>Prompt utilizado:</h4>
              <p>"{cleanPrompt(gif.prompt)}"</p>
            </div>

            <p><strong>Frase:</strong> {gif.overlay_text || 'N/A'}</p>
            <p><strong>Criado em:</strong> {new Date(gif.created_at).toLocaleDateString('pt-BR')}</p>

            {/* Botão de Download */}
            <a
              href={gif.gif_url}
              download={`meu_gif_${gif.id}.gif`}
              className="btn btn-secondary download-btn"
            >
              Download
            </a>
          </div>
        </div>
      ))}
    </div>
  );
};

export default GifHistory;