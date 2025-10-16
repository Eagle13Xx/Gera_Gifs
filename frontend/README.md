# Gerador de GIFs ✨ - Frontend (React + Vite)

![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)

Esta pasta contém todo o código-fonte para a interface de usuário (frontend) do projeto Gerador de GIFs com IA. A aplicação é construída com **React** e **Vite**, e é responsável por toda a interação do usuário, comunicando-se com a API do backend Django para executar as funcionalidades.

## 🚀 Tecnologias Utilizadas

* **React 18:** Biblioteca principal para a construção da interface de usuário.
* **Vite:** Ferramenta de build e servidor de desenvolvimento extremamente rápido.
* **React Router:** Para o gerenciamento de rotas e navegação entre as páginas.
* **JavaScript (ES6+):** Linguagem base para toda a lógica do frontend.
* **CSS:** Para a estilização dos componentes e páginas.
* **Fetch API:** Para realizar as requisições HTTP para o backend.

## ✨ Funcionalidades do Frontend

* **Autenticação:**
    * Página de Login e Cadastro com formulários interativos.
    * Exibição de mensagens de erro de validação específicas para cada campo (ex: "Usuário já existe").
    * Gerenciamento de token de autenticação no `localStorage` para manter o usuário logado.

* **Páginas Públicas:**
    * `HomePage`: A landing page da aplicação.
    * `PlansPage`: Exibe os planos de assinatura disponíveis e destaca o plano atual do usuário, se logado.

* **Área do Usuário (`ProfilePage`):**
    * Um painel centralizado com navegação por abas.
    * **Aba "Meu Plano":** Exibe o status da assinatura (Ativa, Inativa, Cancelada), os detalhes do plano, a data de validade e o **contador de uso de GIFs** (`gerados/limite`).
    * **Gerenciamento de Assinatura:** Permite que o usuário solicite o cancelamento da renovação. A interface se atualiza para refletir o estado de "cancelamento agendado", mostrando a data de expiração.
    * **Aba "Criar GIF":** Contém o formulário principal para a geração de GIFs. Bloqueia o acesso se o usuário não tiver uma assinatura ativa e exibe uma mensagem de erro específica se o limite de GIFs for atingido.
    * **Aba "Histórico de GIFs":** Uma galeria que exibe todos os GIFs previamente gerados pelo usuário, com o prompt utilizado, a data de criação e um botão para download.

* **Fluxo de Pagamento:**
    * `PaymentStatusPage`: Uma página de "aguarde" que verifica o status da assinatura em segundo plano ("polling") após o usuário retornar do gateway de pagamento, proporcionando uma experiência de usuário fluida e sem a necessidade de recarregar a página manualmente.

## 📁 Estrutura do Projeto

A estrutura de pastas principal dentro de `src/` é organizada da seguinte forma:

* **`/components`**: Contém componentes reutilizáveis que são usados em várias páginas.
    * `/layout`: Componentes estruturais como `Header` e `Footer`.
    * `GifGenerator.jsx`: O formulário para criar GIFs.
    * `GifHistory.jsx`: A galeria de GIFs gerados.

* **`/pages`**: Contém os componentes principais que representam cada página da aplicação.
    * `HomePage.jsx`
    * `LoginPage.jsx`
    * `PlansPage.jsx`
    * `ProfilePage.jsx`
    * `PaymentStatusPage.jsx`

* **`/services`**: Centraliza toda a comunicação com a API do backend.
    * `api.js`: Contém todas as funções (`loginUser`, `getGifHistory`, etc.) que realizam as chamadas `fetch` para o servidor Django.

## ⚙️ Configuração e Instalação Local

Siga os passos abaixo para rodar o frontend em um ambiente de desenvolvimento.

### Pré-requisitos
* Node.js (versão 18 ou superior).
* O servidor do **backend Django** deve estar rodando.

### Passos

1.  **Navegue até a pasta do frontend:**
    ```bash
    cd frontend
    ```

2.  **Instale as dependências:**
    Este comando irá baixar todas as bibliotecas listadas no `package.json`.
    ```bash
    npm install
    ```

3.  **Configure as Variáveis de Ambiente:**
    * Crie um arquivo chamado `.env` na raiz da pasta `frontend`.
    * Adicione a seguinte linha, apontando para a URL do seu backend.
    ```env
    VITE_API_URL=[http://127.0.0.1:8000/api](http://127.0.0.1:8000/api)
    ```

4.  **Inicie o Servidor de Desenvolvimento:**
    ```bash
    npm run dev
    ```
    A aplicação estará disponível em `http://localhost:5173`. O servidor de desenvolvimento possui *hot-reloading*, o que significa que as alterações no código serão refletidas no navegador instantaneamente.

5.  **Build para Produção:**
    Quando for fazer o deploy da aplicação, o seguinte comando irá gerar uma versão otimizada e minificada dos seus arquivos na pasta `dist/`.
    ```bash
    npm run build
    ```
