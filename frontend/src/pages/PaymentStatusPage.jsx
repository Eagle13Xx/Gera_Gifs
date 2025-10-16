// src/pages/PaymentStatusPage.jsx
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getUserSubscriptionDetails } from '../services/api';
import './PaymentStatusPage.css';

const PaymentStatusPage = () => {
  const navigate = useNavigate();
  const [statusMessage, setStatusMessage] = useState('Confirmando seu pagamento, por favor aguarde...');

  useEffect(() => {
    // Inicia um "poller" que vai verificar o status a cada 3 segundos
    const intervalId = setInterval(async () => {
      try {
        // Tenta buscar os detalhes da assinatura
        await getUserSubscriptionDetails();

        // Se a chamada ACIMA foi bem-sucedida (não deu erro 404), significa que a assinatura está ativa!
        setStatusMessage('Pagamento confirmado com sucesso! Redirecionando...');
        clearInterval(intervalId); // Para o poller

        // Redireciona para a página de perfil após 2 segundos
        setTimeout(() => {
          navigate('/profile?tab=plan');
        }, 2000);

      } catch (error) {
        // Se der erro 404, continua esperando. O erro é esperado.
        // Se for outro erro, podemos informar o usuário.
        if (!error.message.includes('404')) {
          setStatusMessage('Ocorreu um erro ao verificar seu pagamento. Por favor, contate o suporte.');
          clearInterval(intervalId);
        }
      }
    }, 3000); // Verifica a cada 3 segundos

    // Limpa o intervalo se o componente for desmontado
    return () => clearInterval(intervalId);
  }, [navigate]);

  return (
    <div className="payment-status-container">
      <div className="spinner"></div>
      <h1>Processando...</h1>
      <p>{statusMessage}</p>
    </div>
  );
};

export default PaymentStatusPage;