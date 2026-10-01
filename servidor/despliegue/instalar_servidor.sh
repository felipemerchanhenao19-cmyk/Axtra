#!/usr/bin/env bash
# Instala Axtra en un servidor Ubuntu 24.04 nuevo. Uso (como root):
#   curl -fsSL https://raw.githubusercontent.com/... | bash    (o copia este archivo y: bash instalar_servidor.sh)
# Pasos: Docker, llave de solo lectura para GitHub, descarga de Axtra, claves (.env), arranque,
# actualizaciones automáticas cada 10 minutos, copias de seguridad diarias y cortafuegos.
set -euo pipefail
RAMA="${RAMA:-main}"
DIR=/opt/axtra
REPO=git@github-axtra:felipemerchanhenao19-cmyk/Axtra.git

echo "=== Instalando Axtra en este servidor (rama: $RAMA) ==="
apt-get update -q
apt-get install -y -q git curl ufw nano
command -v docker >/dev/null || curl -fsSL https://get.docker.com | sh

# Memoria de respaldo en disco (2 GB): con el plan de 1 GB evita quedarse sin memoria al instalar o actualizar
if ! swapon --show | grep -q .; then
  fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile >/dev/null && swapon /swapfile
  grep -q '^/swapfile ' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
  sysctl -q vm.swappiness=10 && echo 'vm.swappiness=10' > /etc/sysctl.d/99-axtra.conf
fi

# 1) Llave de solo lectura para descargar el repositorio privado
if [ ! -f /root/.ssh/axtra_github ]; then
  mkdir -p /root/.ssh && chmod 700 /root/.ssh
  ssh-keygen -t ed25519 -N "" -C "servidor-axtra" -f /root/.ssh/axtra_github -q
  cat >> /root/.ssh/config <<CFG
Host github-axtra
  HostName github.com
  User git
  IdentityFile /root/.ssh/axtra_github
  IdentitiesOnly yes
CFG
  ssh-keyscan -q github.com >> /root/.ssh/known_hosts
fi
echo
echo "Copia esta llave y agrégala en GitHub: repositorio Axtra -> Settings -> Deploy keys -> Add deploy key"
echo "(título: servidor, SIN marcar 'Allow write access'):"
echo
cat /root/.ssh/axtra_github.pub
echo
read -r -p "Cuando la hayas agregado, presiona Enter... " _

# 2) Descargar Axtra
if [ ! -d "$DIR/.git" ]; then
  git clone -b "$RAMA" "$REPO" "$DIR"
else
  git -C "$DIR" fetch -q && git -C "$DIR" checkout -q "$RAMA" && git -C "$DIR" pull -q --ff-only
fi

# 3) Claves
if [ ! -f "$DIR/servidor/.env" ]; then
  cp "$DIR/servidor/.env.ejemplo" "$DIR/servidor/.env"
  chmod 600 "$DIR/servidor/.env"
  echo
  echo "Ahora se abre el archivo de claves. Pega tus claves (guía: servidor/despliegue/DESPLIEGUE.md)."
  echo "Para guardar: Ctrl+O, Enter. Para salir: Ctrl+X."
  read -r -p "Presiona Enter para abrirlo... " _
  nano "$DIR/servidor/.env"
fi

# 4) Arrancar
cd "$DIR/servidor/despliegue"
docker compose up -d --build

# 5) Actualizaciones automáticas y copias de seguridad
chmod +x "$DIR/servidor/despliegue/"*.sh
cat > /etc/cron.d/axtra <<CRON
*/10 * * * * root RAMA=$RAMA $DIR/servidor/despliegue/actualizar.sh >> /var/log/axtra-actualizar.log 2>&1
30 3 * * * root $DIR/servidor/despliegue/respaldo.sh >> /var/log/axtra-respaldo.log 2>&1
CRON

# 6) Cortafuegos: solo SSH (la app entra por el túnel de Cloudflare, sin puertos abiertos)
ufw allow OpenSSH >/dev/null && ufw --force enable >/dev/null

echo
echo "=== AXTRA INSTALADO ==="
docker compose ps
echo "Revisa en Cloudflare que el túnel aparezca como 'Healthy'. Registros: docker compose logs -f axtra"
