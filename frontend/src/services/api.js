// src/services/api.js

// Usando import.meta.env.VITE_API_URL para compatibilidade com Vite,
// ou um fallback para localhost em desenvolvimento.
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

/**
 * Função utilitária para fazer requisições HTTP para a API.
 * Gerencia a URL base, token de autenticação e tratamento de erros.
 * @param {string} endpoint - O caminho do endpoint da API (ex: '/users/login/').
 * @param {Object} options - Opções de configuração da requisição (method, body, headers, etc.).
 * @returns {Promise<Object>} - Uma Promise que resolve com os dados JSON da resposta.
 * @throws {Error} - Lança um erro se a requisição não for bem-sucedida ou se houver erro de rede.
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = localStorage.getItem('authToken');

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Token ${token}`;
  }

  const config = { ...options, headers };

  // O 'try...catch' foi removido daqui, pois a função 'async' já lida com os erros.
  const response = await fetch(url, config);
  const data = await response.json();

  if (!response.ok) {
    const error = new Error('A requisição da API falhou.');
    error.data = data;
    error.status = response.status;
    throw error;
  }

  return data;
}

// --- Funções de Autenticação e Perfil ---

/**
 * Realiza o login de um usuário.
 * @param {Object} credentials - Objeto com username e password.
 * @returns {Promise<Object>} - Dados do usuário logado e token.
 */
export const loginUser = (credentials) => {
  return request('/users/login/', {
    method: 'POST',
    body: JSON.stringify(credentials),
  });
};

/**
 * Registra um novo usuário.
 * @param {Object} userData - Dados do usuário para registro (username, password, email, first_name, taxId, cellphone).
 * @returns {Promise<Object>} - Dados do usuário registrado.
 */
export const registerUser = (userData) => {
    return request('/users/register/', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
};

/**
 * Obtém o perfil do usuário autenticado.
 * @returns {Promise<Object>} - Dados do perfil do usuário.
 */
export const getUserProfile = () => {
  return request('/users/profile/');
};


// --- Funções de Assinatura ---

/**
 * Obtém a lista de planos de assinatura disponíveis.
 * @returns {Promise<Array>} - Uma lista de objetos de planos.
 */
export const getPlans = () => {
    return request('/subscriptions/plans/');
};

/**
 * Inicia o processo de criação de uma nova assinatura para um plano.
 * @param {number} planId - O ID do plano selecionado.
 * @returns {Promise<Object>} - Um objeto contendo a URL de pagamento.
 */
export const createSubscription = (planId) => {
    return request('/subscriptions/create-subscription/', {
        method: 'POST',
        body: JSON.stringify({ plan_id: planId }),
    });
};

/**
 * Obtém os detalhes da assinatura ativa do usuário autenticado.
 * @returns {Promise<Object>} - Detalhes da assinatura (plan_name, status, end_date, etc.).
 */
export const getUserSubscriptionDetails = async () => {
  return request('/subscriptions/my-subscription/', {
    method: 'GET',
  });
};

/**
 * Solicita o cancelamento da assinatura ativa do usuário.
 * @returns {Promise<Object>} - Mensagem de confirmação do cancelamento.
 */
export const cancelUserSubscription = async () => {
  return request('/subscriptions/cancel-subscription/', {
    method: 'POST', // O endpoint de cancelamento no backend é POST
  });
};


// --- Funções de Geração de GIF ---

/**
 * Envia um prompt para a IA gerar uma imagem e animar um GIF.
 * @param {Object} promptData - Objeto contendo 'prompt' (descrição da imagem) e 'text' (texto para sobrepor).
 * @returns {Promise<Object>} - Um objeto contendo a URL do GIF gerado.
 */
export const generateAiImage = (promptData) => {
  const endpoint = '/gif/generate-image/';
  return request(endpoint, {
    method: 'POST',
    body: JSON.stringify(promptData),
  });
};
/**
 * Obtém o histórico de GIFs gerados pelo usuário autenticado.
 * @returns {Promise<Array>} - Uma lista de objetos de GIFs.
 */
export const getGifHistory = () => {
  return request('/gif/history/');
};