// src/components/GifGenerator.jsx

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { generateAiImage } from '../services/api';
import './GifGenerator.css';

const GifGenerator = ({ subscriptionActive }) => {
  const [prompt, setPrompt] = useState('');
  const [overlayText, setOverlayText] = useState('');
  const [generatedGifUrl, setGeneratedGifUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  // Se o usuário não tiver assinatura ativa, exibe uma mensagem e um botão para ver planos
  if (!subscriptionActive) {
    return (
      <div className="container upgrade-prompt">
        <h2>Assinatura Necessária ✨</h2>
        <p>
          Você precisa de um plano ativo para criar GIFs personalizados com IA.
        </p>
        <button className="btn btn-primary" onClick={() => navigate('/plans')}>
          Ver Planos
        </button>
      </div>
    );
  }

      // Função para lidar com a geração do GIF pela IA
      const handleGenerate = async () => {
        if (!prompt.trim()) {
          setError('Por favor, descreva o gif que você quer criar.');
          return;
        }

        setIsLoading(true);
        setError('');
        setGeneratedGifUrl(null);

        try {
          const response = await generateAiImage({
            prompt: prompt,
            text: overlayText,
          });
          setGeneratedGifUrl(response.gif_url);
        } catch (err) {
          // Verifica se o status do erro é 403 (Limite Atingido)
          // e se existe uma mensagem de erro específica no objeto 'data'.
          if (err.status === 403 && err.data?.error) {
            setError(err.data.error); // Usa a mensagem vinda do backend
          } else {
            // Para todos os outros erros, usa uma mensagem mais genérica.
            setError(err.message || 'A requisição da API falhou. Tente novamente mais tarde.');
          }
        } finally {
          setIsLoading(false);
        }
      };


  //FUNÇÃO: Compartilhar o GIF no WhatsApp
  const handleShareWhatsapp = () => {
    if (generatedGifUrl) {
      // Mensagem padrão que acompanhará o GIF no WhatsApp
      const shareText = encodeURIComponent("Confira este GIF animado que criei com a IA!");
      // A URL do GIF também é codificada para ser segura em links
      const shareUrl = encodeURIComponent(generatedGifUrl);

      // Constrói a URL de compartilhamento do WhatsApp
      // `wa.me/?text=...` permite pré-preencher a mensagem
      // `%0A` é uma quebra de linha
      // `&url=...` anexa a URL do GIF
      const whatsappLink = `https://wa.me/?text=${shareText}%0A${shareUrl}`;

      // Abre o link em uma nova aba/janela, que tentará abrir o WhatsApp
      window.open(whatsappLink, '_blank');
    } else {
      setError('Por favor, gere um GIF antes de tentar compartilhar.');
    }
  };

  return (
    <div className="image-generator-card">
      <h2>Gerador de Gifs com IA</h2>

      <div className="form-group">
        <label htmlFor="prompt">
          1. Descreva o gif que você deseja que a IA crie:
        </label>
        <textarea
          id="prompt"
          placeholder="Ex: Jardim florido ao amanhecer, com um sol radiante, estilo aquarela"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={3}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="overlayText">
          2. Digite uma frase para o Gif (opcional):
        </label>
        <textarea
          id="overlayText"
          placeholder="Ex: Que seu dia seja iluminado!"
          value={overlayText}
          onChange={(e) => setOverlayText(e.target.value)}
          maxLength={40}
          rows={2}
        />
      </div>

      <button
        onClick={handleGenerate}
        disabled={isLoading}
        className="btn btn-primary submit-btn"
      >
        {isLoading ? 'Criando seu gif, aguarde...' : '✨ Gerar Gif Mágico'}
      </button>

      {error && <div className="error-message">{error}</div>}

      {/* Exibe o resultado quando 'generatedGifUrl' tiver um valor */}
      {generatedGifUrl && (
        <div className="image-preview">
          <h3>Seu GIF animado está pronto!</h3>
          <img
            src={generatedGifUrl}
            alt="GIF animado personalizado gerado por IA"
          />
          <div className="image-actions">
            {/* Botão de Download: "Baixar GIF" */}
            <a
              href={generatedGifUrl}
              download="meu-gif-animado.gif"
              className="btn btn-secondary" // Mantém o estilo secundário
            >
              📥 Baixar GIF
            </a>
            {/* Botão de Compartilhar no WhatsApp */}
            <button
              onClick={handleShareWhatsapp}
              className="btn btn-primary"
            >
              🔗 Compartilhar no WhatsApp
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default GifGenerator;