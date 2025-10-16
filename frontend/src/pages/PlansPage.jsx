// src/pages/PlansPage.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPlans, createSubscription, getUserSubscriptionDetails } from '../services/api';

const PlansPage = () => {
  const [plans, setPlans] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isSubscribingId, setIsSubscribingId] = useState(null);
  const [activeSubscription, setActiveSubscription] = useState(null);

  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // 1. Busca os planos primeiro (chamada pública)
        const plansData = await getPlans();
        setPlans(plansData);

        // 2. Verifica se o usuário está logado (pela existência do token)
        const token = localStorage.getItem('authToken');
        if (token) {
          // 3. Se estiver logado, busca os detalhes da assinatura
          try {
            const subscriptionData = await getUserSubscriptionDetails();
            setActiveSubscription(subscriptionData);
          } catch (subError) {
            // Ignora o erro 404 (sem assinatura), mas trata outros erros
            if (!subError.message.includes('404')) {
              console.error("Erro ao buscar detalhes da assinatura:", subError);
            }
          }
        }
      } catch (err) {
        // Este catch só será acionado se a busca de planos falhar (ex: API offline)
        setError(err.message || 'Não foi possível carregar os planos.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleSubscribe = async (planId) => {
    // Verifica se o usuário está logado ANTES de tentar assinar
    const token = localStorage.getItem('authToken');
    if (!token) {
      navigate('/login');
      return;
    }

    if (activeSubscription && activeSubscription.status === 'active') {
      setError('Você já possui uma assinatura ativa. Gerencie-a na sua página de perfil.');
      return;
    }

    setIsSubscribingId(planId);
    setError('');
    try {
      const response = await createSubscription(planId);
      if (response.payment_url) {
        window.location.href = response.payment_url;
      }
    } catch (err) {
      setError(`Erro ao iniciar o processo de assinatura: ${err.message}`);
    } finally {
      setIsSubscribingId(null);
    }
  };

  // O resto do componente continua o mesmo...
  if (isLoading) {
    return <div className="loading-message">Carregando planos...</div>;
  }

  if (error) {
    return <div style={{ color: 'red' }}>{error}</div>;
  }

  return (
    <div className="plans-page">
      <div className="plans-header">
        <h1>Escolha seu Plano</h1>
        <p>Acesso ilimitado para criar e compartilhar mensagens de carinho.</p>
      </div>

      {activeSubscription && activeSubscription.status === 'active' && (
        <div className="active-subscription-message">
          <p>Você já possui o plano "{activeSubscription.plan_name}" ativo.</p>
          <p>Próxima cobrança: {new Date(activeSubscription.next_billing_date).toLocaleDateString('pt-BR')}.</p>
          <button className="btn btn-secondary" onClick={() => navigate('/profile?tab=plan')}>
            Gerenciar Minha Assinatura
          </button>
        </div>
      )}

      <div className="plans-comparison">
        {plans.length > 0 ? (
          plans.map((plan) => {
            const isCurrentPlan = activeSubscription && activeSubscription.plan_name === plan.name;
            const buttonDisabled = isCurrentPlan || (isSubscribingId === plan.id);

            return (
              <div key={plan.id} className={`plan-card ${isCurrentPlan ? 'plan-card-active' : ''}`}>
                <div className="plan-header">
                  <h3>{plan.name}</h3>
                  <div className="plan-price">
                    <span className="price-amount">
                      {(plan.price / 100).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                    </span>
                      <span className="price-period">
                        /{plan.cycle === 'MONTHLY' ? 'mês' : 'ano'}
                      </span>
                  </div>
                </div>

                <ul className="plan-features">
                  <li>✓ {plan.description}</li>
                </ul>

                <div className="plan-actions">
                  <button
                    className={`btn ${isCurrentPlan ? 'btn-tertiary' : 'btn-primary'}`}
                    onClick={() => handleSubscribe(plan.id)}
                    disabled={buttonDisabled}
                  >
                    {isCurrentPlan ? 'Seu Plano Atual' : (isSubscribingId === plan.id ? 'Processando...' : 'Assinar Agora')}
                  </button>
                </div>
              </div>
            );
          })
        ) : (
          <p className="no-plans-message">Nenhum plano disponível no momento.</p>
        )}
      </div>
    </div>
  );
};

export default PlansPage;