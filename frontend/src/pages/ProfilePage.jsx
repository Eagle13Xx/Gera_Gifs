import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { getUserProfile, getUserSubscriptionDetails, cancelUserSubscription } from '../services/api';
import ImageGenerator from '../components/GifGenerator';
import './ProfilePage.css';

import { getGifHistory } from '../services/api'; //
import GifHistory from '../components/GifHistory';

const ProfilePage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialTab = searchParams.get('tab') || 'generator';
  const [activeTab, setActiveTab] = useState(initialTab);
  const [user, setUser] = useState(null);
  const [subscriptionDetails, setSubscriptionDetails] = useState(null);
  const [subscriptionError, setSubscriptionError] = useState('');
  const [isCanceling, setIsCanceling] = useState(false);
  const [gifHistory, setGifHistory] = useState([]); // 3. Adicione o novo state
  const [isHistoryLoading, setIsHistoryLoading] = useState(true);

  useEffect(() => {
    const fetchAllData = async () => {
      try {
        // Busca os dados do perfil e da assinatura em paralelo
        const [profileData, subDetails] = await Promise.all([
          getUserProfile(),
          getUserSubscriptionDetails().catch(() => null)
        ]);
        setUser(profileData);
        setSubscriptionDetails(subDetails);

        // Busca o histórico de GIFs
        try {
          const historyData = await getGifHistory();
          setGifHistory(historyData);
        } catch (historyErr) {
          console.error("Falha ao carregar o histórico de GIFs:", historyErr);
        }

      } catch (error) {
        localStorage.removeItem('authToken');
        navigate('/login');
      } finally {
        setIsHistoryLoading(false); // Marca o loading do histórico como concluído
      }
    };
    fetchAllData();
  }, [navigate]);

    const handleCancelSubscription = async () => {
        if (!window.confirm('Tem certeza que deseja agendar o cancelamento da sua assinatura? Seu acesso continuará ativo até o final do período pago.')) {
          return;
        }
        setIsCanceling(true);
        setSubscriptionError('');
        try {
          // Se o cancelamento for bem-sucedido, a API retorna o objeto atualizado
          const updatedSubscriptionDetails = await cancelUserSubscription();
          setSubscriptionDetails(updatedSubscriptionDetails);
        } catch (err) {
          // Verifica se o objeto de erro (err.data) contém nossa chave 'error'
          if (err.data && err.data.error) {
            // Se sim, usa a mensagem de erro específica vinda do backend
            setSubscriptionError(err.data.error);
          } else {
            // Se não, usa uma mensagem genérica
            setSubscriptionError('A requisição da API falhou. Tente novamente.');
          }
        } finally {
          setIsCanceling(false);
        }
      };


  const isSubscribed = subscriptionDetails && subscriptionDetails.status === 'active';

  if (!user) {
    return <div>Carregando perfil...</div>;
  }

  const subscriptionStatus = isSubscribed ? 'Ativa' :
                             subscriptionDetails?.status === 'canceled' ? 'Cancelada' : 'Inativa';
  const statusClass = isSubscribed ? 'active' :
                      subscriptionDetails?.status === 'canceled' ? 'canceled' : 'inactive';

  return (
    <div className="container">
      <div className="profile-header">
        <h1>👋 Olá, {user.first_name || user.username}!</h1>
      </div>

      <nav className="profile-tabs">
        <button
          onClick={() => setActiveTab('generator')}
          className={`tab-button ${activeTab === 'generator' ? 'active' : ''}`}
        >
          Criar GIF
        </button>

        <button
          onClick={() => setActiveTab('history')}
          className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
        >
          Histórico de GIFs
        </button>
        <button
          onClick={() => setActiveTab('plan')}
          className={`tab-button ${activeTab === 'plan' ? 'active' : ''}`}
        >
          Meu Plano
        </button>
      </nav>

      <div className="tab-content">
        {activeTab === 'generator' && (
          <ImageGenerator subscriptionActive={isSubscribed} />
        )}

        {activeTab === 'history' && (
          <GifHistory gifs={gifHistory} isLoading={isHistoryLoading} />
        )}
        {activeTab === 'plan' && (
          <div className="plan-status-card">
            <h2>Status do Plano</h2>
            <p>
              Sua assinatura está:
              <span className={`status-badge ${statusClass}`}>
                {subscriptionStatus}
              </span>
            </p>

            {isSubscribed ? (
                <>
                    <p>
                        <strong>Plano:</strong> {subscriptionDetails.plan_name} <br />
                        <strong>Preço:</strong> {(subscriptionDetails.plan_price / 100).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}/{subscriptionDetails.plan_cycle === 'MONTHLY' ? 'mês' : 'ano'} <br />
                        <strong>Válida até:</strong> {new Date(subscriptionDetails.end_date).toLocaleDateString('pt-BR')}<br />
                        <strong>Uso de GIFs este mês:</strong> {subscriptionDetails.gif_count} / {subscriptionDetails.plan_gif_limit}
                    </p>

                    {subscriptionDetails.cancellation_requested ? (
                      <p className="cancellation-pending-message" style={{ fontWeight: 'bold', color: '#6c757d' }}>
                        Sua assinatura foi cancelada e expira em {new Date(subscriptionDetails.end_date).toLocaleDateString('pt-BR')}.
                      </p>
                    ) : (
                      <button
                          className="btn btn-danger"
                          onClick={handleCancelSubscription}
                          disabled={isCanceling}
                      >
                          {isCanceling ? 'Agendando cancelamento...' : 'Cancelar Assinatura'}
                      </button>
                    )}
                </>
            ) : (
                <>
                  <p>Você não possui um plano ativo no momento.</p>
                  <button className="btn btn-primary" onClick={() => navigate('/plans')}>
                    Ver Planos
                  </button>
                </>
            )}

            {subscriptionError && <div className="error-message">{subscriptionError}</div>}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfilePage;