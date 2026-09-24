# Guia Completo de Deploy na Oracle Cloud Infrastructure (OCI)

Este guia orienta passo a passo o provisionamento e o deploy do **NexusDocs AI** na Oracle Cloud Infrastructure (OCI), utilizando os recursos gratuitos (**Always Free**) e Docker Compose.

---

## 🏗️ Arquitetura no Deploy

Ao final do deploy, sua máquina na nuvem estará executando três serviços integrados em contêineres:

1. **NexusDocs Web (Streamlit)**: Interface interativa de chat RAG com fontes e pontuações de relevância (Porta `8501` e Porta `80`).
2. **NexusDocs API (FastAPI)**: Backend com documentação interativa Swagger UI (Porta `8000`).
3. **Qdrant**: Banco de dados vetorial de alta performance (Porta `6333` interna).

---

## 📋 Passo 1: Criar a Máquina Virtual (Compute Instance) na OCI

1. Acesse o console da Oracle Cloud: [cloud.oracle.com](https://cloud.oracle.com)
2. No menu lateral esquerdo, vá em **Compute** > **Instances** (Instâncias).
3. Clique no botão azul **Create Instance** (Criar Instância).
4. Configure os campos:
   - **Name**: `nexusdocs-server` (ou outro nome de sua preferência).
   - **Placement**: Mantenha o padrão.
   - **Image and shape**:
     - Clique em **Edit** (Editar).
     - **Image**: Selecione **Canonical Ubuntu** (versão `24.04 Minimal` ou `22.04`).
     - **Shape**:
       - *Opção Recomendada (Always Free ARM)*: **Ampere (VM.Standard.A1.Flex)** com 2 a 4 OCPUs e 8 a 16 GB de RAM.
       - *Opção Alternativa (Always Free AMD)*: **VM.Standard.E2.1.Micro** (1 OCPU, 1 GB RAM). O script de setup configurará automaticamente 2GB de Swap para suportar os embeddings sem travamento.
   - **Networking** (Rede):
     - Escolha **Create new virtual cloud network** (Criar nova VCN) ou use a sua existente.
     - Certifique-se de marcar: **Assign a public IPv4 address** (Atribuir endereço IPv4 público).
   - **Add SSH keys**:
     - Selecione **Generate a key pair for me** (Gerar par de chaves).
     - **MUITO IMPORTANTE:** Clique em **Save private key** (`.key` ou `.pem`) e salve no seu computador. Sem essa chave você não conseguirá acessar a VM!
5. Clique em **Create** (Criar) no final da página.
6. Aguarde alguns minutos até que o status mude para **Running** (verde). Anote o **Public IP Address** (Endereço IP Público).

---

## 🔓 Passo 2: Liberar as Portas na OCI (Security List)

Por padrão, a OCI bloqueia conexões externas exceto SSH (porta 22). Precisamos liberar as portas do NexusDocs.

1. Na página da sua Instância, na seção **Instance details**, clique no link da **Virtual cloud network** (VCN).
2. Na página da VCN, clique no menu lateral em **Security Lists** (Listas de Segurança) e clique na **Default Security List for...**.
3. Clique em **Add Ingress Rules** (Adicionar Regras de Entrada) e preencha:
   - **Source Type**: `CIDR`
   - **Source CIDR**: `0.0.0.0/0`
   - **IP Protocol**: `TCP`
   - **Destination Port Range**: `80,8000,8501`
   - **Description**: `Permitir HTTP, FastAPI Swagger e Streamlit`
4. Clique em **Add Ingress Rules**.

---

## 💻 Passo 3: Conectar à Máquina via SSH

No seu computador local (Windows), abra o **PowerShell**:

1. Caso tenha salvo a chave privada, por exemplo em `C:\Users\moabm\Downloads\ssh-key.key`, ajuste as permissões para evitar avisos do OpenSSH:
   ```powershell
   icacls.exe "C:\Users\moabm\Downloads\ssh-key.key" /reset
   icacls.exe "C:\Users\moabm\Downloads\ssh-key.key" /grant:r "$($env:USERNAME):(R)"
   icacls.exe "C:\Users\moabm\Downloads\ssh-key.key" /inheritance:r
   ```

2. Conecte-se à instância (substitua pelo caminho da sua chave e pelo IP público da VM):
   ```powershell
   ssh -i "C:\Users\moabm\Downloads\ssh-key.key" ubuntu@<SEU_IP_PUBLICO>
   ```

---

## ⚙️ Passo 4: Configurar o Ambiente na VM com o Script Automatizado

Já dentro do terminal da VM na OCI:

1. Clone o repositório do projeto:
   ```bash
   git clone https://github.com/moabdev/nexusdocs-ai.git
   cd nexusdocs-ai
   ```

2. Execute o script de configuração inicial que preparamos no projeto:
   ```bash
   bash scripts/setup_oci.sh
   ```
   *Este script instala o Docker, o Docker Compose v2, cria 2GB de Swap e libera as portas 80, 8000 e 8501 no firewall interno do Ubuntu.*

3. Aplique as permissões do Docker na sua sessão atual:
   ```bash
   newgrp docker
   ```

---

## 🔑 Passo 5: Configurar Variáveis de Ambiente

Crie o arquivo `.env` a partir do modelo:

```bash
cp .env.example .env
nano .env
```

Insira sua chave da API do Google Gemini no campo `GEMINI_API_KEY`:
```env
GEMINI_API_KEY=AIzaSy...sua_chave_aqui...
```
*(Para salvar no nano: pressione `Ctrl + O`, depois `Enter`, e `Ctrl + X` para sair).*

---

## 🚀 Passo 6: Subir os Contêineres

Inicie a aplicação com o Docker Compose:

```bash
docker compose up -d --build
```

Verifique se todos os contêineres estão saudáveis e rodando:
```bash
docker compose ps
```

Você verá:
- `nexusdocs-qdrant` (Up)
- `nexusdocs-api` (Up)
- `nexusdocs-web` (Up)

---

## 📚 Passo 7: Ingestão da Base de Conhecimento no Qdrant

Para que o RAG consiga responder com os documentos da Velox Logistics, execute o script de ingestão diretamente no contêiner da API:

```bash
docker compose exec api python scripts/ingest.py
```

Você verá a saída indexando cada documento markdown (`technology-platform-handbook.md`, `customer-service-faq.md`, `shipping-policy-v3.md`, etc.), gerando os embeddings e salvando os pontos no Qdrant!

---

## 📸 Passo 8: Coletar as Evidências do Deploy

Abra o seu navegador web no seu computador e acesse os links públicos:

### 1. Interface Web do Streamlit
- **URL Pública**: `http://<SEU_IP_PUBLICO>:8501` ou `http://<SEU_IP_PUBLICO>`
- **O que testar**:
  Faça perguntas como:
  - *"Como o sistema deve lidar com eventos duplicados do Kafka?"*
  - *"Qual é a política de reembolso e prazos de contestação?"*
  - *"Para que o Redis é utilizado na plataforma?"*
- **Evidência**: Tire um print da tela inteira (incluindo a barra de endereços com o IP público) mostrando a resposta fundamentada com as fontes consultadas abertas.

### 2. Documentação da API FastAPI (Swagger UI)
- **URL Pública**: `http://<SEU_IP_PUBLICO>:8000/docs`
- **O que testar**:
  - Teste o endpoint `GET /health` clicando em **Try it out** > **Execute** (deve retornar `{"status":"healthy","service":"nexusdocs-api"}`).
  - Teste o endpoint `POST /query` enviando um JSON com uma pergunta.
- **Evidência**: Tire um print mostrando o Swagger UI carregado no IP público e a resposta 200 do `/health`.

### 3. Painel da Oracle Cloud (OCI Console)
- Tire um print da página de detalhes da instância na OCI mostrando o status **Running**, o nome `nexusdocs-server` e o **Public IP**.
