# NexusDocs AI

> Enterprise Knowledge Intelligence Platform powered by Agentic RAG, hybrid retrieval, vector search and LLMs.

NexusDocs AI é uma plataforma corporativa de inteligência de conhecimento voltada para transformar documentos corporativos e dados não-estruturados em respostas seguras, rastreáveis e fundamentadas em evidências com citações de fontes.

---

## 🌐 Deploy em Produção (Oracle Cloud Infrastructure)

A aplicação está provisionada e ativa na **Oracle Cloud Infrastructure (OCI)** utilizando Docker e Docker Compose:

| Serviço | URL Pública | Descrição |
| :--- | :--- | :--- |
| **Interface Web (Streamlit)** | [http://168.138.130.251](http://168.138.130.251) | Chat RAG interativo com pontuações de relevância e citações de fontes |
| **Interface Alternativa** | [http://168.138.130.251:8501](http://168.138.130.251:8501) | Porta direta do Streamlit |
| **FastAPI Swagger UI** | [http://168.138.130.251:8000/docs](http://168.138.130.251:8000/docs) | Documentação OpenAPI interativa dos endpoints da API |
| **Health Check** | [http://168.138.130.251:8000/health](http://168.138.130.251:8000/health) | Endpoint de integridade do serviço |

> 📖 **Guia Completo de Deploy**: Consulte o passo a passo detalhado em [`docs/deployment/OCI_DEPLOY.md`](docs/deployment/OCI_DEPLOY.md).

---

<p align="center">
  <img width="100%" alt="NexusDocs AI Architecture & Interface" src="https://github.com/user-attachments/assets/e6a9df17-8628-40b8-a83a-f9ec8bd4bd37" />
</p>

---

## 🏗️ Arquitetura do Sistema

```
                      ┌──────────────────────────────────────────┐
                      │             Cliente / Navegador          │
                      └─────────────────────┬────────────────────┘
                                            │
                      ┌─────────────────────┴────────────────────┐
                      ▼                                          ▼
           Porta 80 / 8501                            Porta 8000
    ┌───────────────────────────────┐          ┌───────────────────────────────┐
    │    NexusDocs Web (Streamlit)  │ ───────> │     NexusDocs API (FastAPI)   │
    └───────────────────────────────┘          └──────────────┬────────────────┘
                                                              │
                                       ┌──────────────────────┴──────────────────────┐
                                       ▼                                             ▼
                        ┌───────────────────────────────┐             ┌───────────────────────────────┐
                        │    Qdrant Vector Database     │             │     Google Gemini (LLM)       │
                        │    (Busca Semântica / RAG)    │             │   (Geração Fundamentada)      │
                        └───────────────────────────────┘             └───────────────────────────────┘
```

### Componentes Principais:
1. **NexusDocs Web (Streamlit)**: Interface conversacional para perguntas em linguagem natural, exibição de respostas fundamentadas e visualização detalhada dos trechos recuperados.
2. **NexusDocs API (FastAPI)**: Orquestrador do pipeline de RAG (Retrieval-Augmented Generation), expondo endpoints REST padronizados (`/query`, `/health`).
3. **Qdrant Vector Store**: Banco de dados vetorial de alta performance executando como serviço dedicado, indexando chunks com metadados estruturados.
4. **FastEmbed**: Gerador de embeddings multilíngues (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`), otimizado para inferência veloz com ONNX Runtime.
5. **Google Gemini**: Modelo de fundação responsável pela síntese de respostas estritamente baseadas nos trechos recuperados (*anti-hallucination*).

---

## 📚 Base de Conhecimento (Velox Logistics)

A plataforma conta com uma base de conhecimento corporativa completa da empresa **Velox Logistics** localizada em [`knowledge-base/velox-logistics`](knowledge-base/velox-logistics):

- **Políticas de Envio**: Histórico de versões v1.0, v2.0 e a versão vigente v3.0 (`KB-001`, `KB-002`, `KB-003`).
- **Política de Reembolso e Indenizações**: Prazos, SLA e regras de disputa (`KB-004`).
- **Manual de Operações e Rastreamento**: Códigos de status, exceções e SLA operacional (`KB-005`).
- **FAQ de Atendimento ao Cliente**: Procedimentos para suporte e SAC (`KB-006`).
- **Handbook de Engenharia e Tecnologia**: Diretrizes de arquitetura de microsserviços, Kafka, Redis e Postgres (`KB-007`).

---

## 🚀 Como Executar Localmente

### Pré-requisitos
- Python 3.12+
- Gerenciador de pacotes [`uv`](https://docs.astral.sh/uv/)
- Docker e Docker Compose

### 1. Clonar o repositório
```bash
git clone https://github.com/moabdev/nexusdocs-ai.git
cd nexusdocs-ai
```

### 2. Configurar variáveis de ambiente
```bash
cp .env.example .env
```
Edite o arquivo `.env` e configure sua chave da API do Google Gemini (`GEMINI_API_KEY`).

### 3. Subir os contêineres com Docker Compose
```bash
docker compose up -d --build
```

### 4. Executar a ingestão dos documentos
```bash
docker compose exec api python scripts/ingest.py
```

Acesse:
- **Web App**: [http://localhost](http://localhost) ou [http://localhost:8501](http://localhost:8501)
- **API Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: Python 3.12
- **Gerenciamento de Dependências**: [uv](https://github.com/astral-sh/uv)
- **Backend API**: [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- **Frontend / Web UI**: [Streamlit](https://streamlit.io/)
- **Banco Vetorial**: [Qdrant](https://qdrant.tech/)
- **Embeddings**: [FastEmbed](https://github.com/qdrant/fastembed) (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`)
- **LLM**: Google Gemini API (`google-genai`)
- **Infraestrutura**: Docker, Docker Compose, Oracle Cloud Infrastructure (OCI Always Free)

---

## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE).