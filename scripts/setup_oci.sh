#!/usr/bin/env bash
set -e

echo "NexusDocs AI - Configuração Inicial OCI"

# 1. Update system packages
echo "==> Atualizando pacotes do sistema..."
sudo apt-get update && sudo apt-get upgrade -y

# 2. Configure Swap (4GB) to prevent OOM during embedding generation and container builds
if [ ! -f /swapfile ]; then
    echo "==> Configurando 4GB de memória Swap..."
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "Swap configurado com sucesso!"
else
    echo "==> Swap já existente."
fi

# 3. Install Docker & Docker Compose
echo "==> Instalando Docker e Docker Compose..."
sudo apt-get install -y docker.io docker-compose-v2 git curl iptables-persistent netfilter-persistent
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"

# 4. Open ports on OS Firewall (Ubuntu iptables / ufw)
echo "==> Liberando portas 80, 8000 e 8501 no firewall do sistema..."
sudo iptables -I INPUT 1 -p tcp --dport 80 -j ACCEPT || true
sudo iptables -I INPUT 1 -p tcp --dport 8000 -j ACCEPT || true
sudo iptables -I INPUT 1 -p tcp --dport 8501 -j ACCEPT || true
sudo netfilter-persistent save || true

if command -v ufw >/dev/null 2>&1; then
    sudo ufw allow 80/tcp || true
    sudo ufw allow 8000/tcp || true
    sudo ufw allow 8501/tcp || true
fi

echo "Ambiente OCI preparado com sucesso!"