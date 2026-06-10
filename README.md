# VeritasAI Frontend

Interface web da aplicação VeritasAI. Este projeto é o front-end em React que permite ao usuário enviar conteúdos para análise de veracidade em quatro modos:

- `Texto`: cola uma afirmação ou notícia para checagem
- `Link`: envia uma URL para extração e análise do conteúdo
- `Imagem`: faz upload de uma imagem para análise multimodal
- `Histórico`: lista as verificações anteriores salvas no backend

O front se comunica com a API do projeto backend e exibe o veredito, a confiança, o resumo e a análise detalhada retornados pelo servidor.

## Tecnologias

- React 18
- Vite
- React Icons

## Requisitos

- Node.js 18 ou superior
- npm
- Backend do VeritasAI em execução, ou acesso ao endpoint publicado

## Configuração

Por padrão, o front usa a API publicada em:

```bash
https://back-veritasai.onrender.com
```

Se quiser apontar para uma API local, crie um arquivo `.env` na raiz deste projeto com:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Instalação

```bash
npm install
```

## Como rodar

### Ambiente de desenvolvimento

```bash
npm run dev
```

O Vite vai subir a aplicação normalmente em `http://localhost:5173`.

### Build de produção

```bash
npm run build
```

### Pré-visualizar a build

```bash
npm run preview
```

## Como funciona

O fluxo da interface é simples:

1. O usuário escolhe o tipo de conteúdo.
2. O front envia os dados para o backend em uma das rotas:
   - `POST /verify/text`
   - `POST /verify/url`
   - `POST /verify/image`
3. A resposta é exibida com veredito e detalhes da análise.
4. Na aba `Histórico`, o front chama `GET /history`.

## Estrutura principal

- `src/App.jsx`: lógica principal da interface
- `src/main.jsx`: ponto de entrada do React
- `src/index.css`: estilos da aplicação
- `vite.config.js`: configuração do Vite

## Observações

- O upload de imagem usa o nome de campo `file`, exatamente como o backend espera.
- Se a API estiver em outro domínio, verifique se o CORS do backend está liberado.
