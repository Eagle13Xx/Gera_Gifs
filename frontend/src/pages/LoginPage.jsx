import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginUser, registerUser } from '../services/api';
import './LoginPage.css';

const LoginPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '', password: '', email: '', first_name: '', taxId: '', cellphone: ''
  });

  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleToggleMode = () => {
    setIsLogin(!isLogin);
    setErrors({}); // Limpa os erros ao alternar
    setFormData({ username: '', password: '', email: '', first_name: '', taxId: '', cellphone: '' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setIsLoading(true);
    try {
      if (isLogin) {
        const data = await loginUser({ username: formData.username, password: formData.password });
        localStorage.setItem('authToken', data.token);
        navigate('/profile');
      } else {
        await registerUser(formData);
        const data = await loginUser({ username: formData.username, password: formData.password });
        localStorage.setItem('authToken', data.token);
        navigate('/profile');
      }
    } catch (err) {
      if (err.data) {
        // Se o erro tem 'data', significa que é um erro de validação do Django.
        setErrors(err.data);
      } else {
        // Fallback para erros de rede ou outros problemas.
        setErrors({ non_field_errors: [err.message || 'Ocorreu um erro na requisição.'] });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-form-container">
        <div className="auth-header">
          <h1>{isLogin ? 'Entrar' : 'Cadastrar'}</h1>
        </div>

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <div className="form-group">
              <label htmlFor="first_name">Nome</label>
              <input id="first_name" name="first_name" placeholder="Seu nome" onChange={handleChange} value={formData.first_name} required />
              {errors.first_name && <div className="field-error">{errors.first_name[0]}</div>}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="username">Nome de usuário</label>
            <input id="username" name="username" placeholder="escolha um @usuario" onChange={handleChange} value={formData.username} required />
            {errors.username && <div className="field-error">{errors.username[0]}</div>}
          </div>

          {!isLogin && (
            <div className="form-group">
              <label htmlFor="email">E-mail</label>
              <input id="email" name="email" type="email" placeholder="seu@email.com" onChange={handleChange} value={formData.email} required />
              {errors.email && <div className="field-error">{errors.email[0]}</div>}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="password">Senha</label>
            <input id="password" name="password" type="password" placeholder="••••••••" onChange={handleChange} value={formData.password} required />
            {errors.password && <div className="field-error">{errors.password.join(' ')}</div>}
          </div>

          {!isLogin && (
            <>
              <div className="form-group">
                <label htmlFor="taxId">CPF</label>
                <input id="taxId" name="taxId" placeholder="000.000.000-00" onChange={handleChange} value={formData.taxId} required />
                {errors.taxId && <div className="field-error">{errors.taxId[0]}</div>}
              </div>
              <div className="form-group">
                <label htmlFor="cellphone">Telefone</label>
                <input id="cellphone" name="cellphone" placeholder="(XX) 9XXXX-XXXX" onChange={handleChange} value={formData.cellphone} required />
                {errors.cellphone && <div className="field-error">{errors.cellphone[0]}</div>}
              </div>
            </>
          )}

          <button type="submit" className="btn btn-primary submit-btn" disabled={isLoading}>
            {isLoading ? 'Processando...' : (isLogin ? 'Entrar' : 'Cadastrar')}
          </button>
        </form>

        {/* Exibe erros gerais que não pertencem a um campo específico */}
        {errors.non_field_errors && <div className="error-message">{errors.non_field_errors[0]}</div>}
        {errors.detail && <div className="error-message">{errors.detail}</div>}

        <div className="auth-toggle">
          <p>{isLogin ? 'Não tem uma conta?' : 'Já tem uma conta?'}</p>
          <button onClick={handleToggleMode} className="btn btn-secondary">
            {isLogin ? 'Cadastre-se' : 'Entre'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;