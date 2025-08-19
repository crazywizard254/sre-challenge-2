set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

sudo apt-get update -y
sudo apt-get install -y \
  ca-certificates \
  curl \
  gnupg \
  lsb-release \
  apt-transport-https \
  software-properties-common

if [ ! -f /etc/apt/keyrings/docker.gpg ]; then
  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  sudo chmod a+r /etc/apt/keyrings/docker.gpg
fi

UBUNTU_CODENAME=$(lsb_release -cs)
if ! grep -q "download.docker.com" /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null; then
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${UBUNTU_CODENAME} stable" \
    | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
fi

sudo apt-get update -y

sudo apt-get install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

sudo systemctl enable docker
sudo systemctl restart docker

if id -nG vagrant | grep -qw docker; then
  echo "User 'vagrant' already in docker group"
else
  sudo usermod -aG docker vagrant
  echo "Added 'vagrant' to docker group. You may need to log out/in for this to take effect."
fi

if sudo docker version > /dev/null 2>&1; then
  echo "Docker installed successfully."
else
  echo "Docker installed but not yet accessible; a reboot or new login may be required." >&2
fi

# Deploy the base application stack with Docker Compose
COMPOSE_FILE="/vagrant/docker-compose.yml"
if [ -f "$COMPOSE_FILE" ]; then
  echo "Bringing up application stack via compose..."
  # Build and start as the vagrant user (has docker group membership)
  sudo -u vagrant /usr/bin/docker compose -f "$COMPOSE_FILE" pull
  sudo -u vagrant /usr/bin/docker compose -f "$COMPOSE_FILE" up -d --build
  echo "Application stack started."
else
  echo "Compose file $COMPOSE_FILE not found; skipping app deployment" >&2
fi
