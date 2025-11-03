
set -e

echo "🔥 Apagando TUDO do Docker (containers, volumes, imagens e redes)..."

# Para e remove todos os containers
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm -f $(docker ps -aq) 2>/dev/null || true

# Remove todas as imagens
docker rmi -f $(docker images -aq) 2>/dev/null || true

# Remove todos os volumes
docker volume rm -f $(docker volume ls -q) 2>/dev/null || true

# Remove todas as redes (exceto as padrão)
docker network rm $(docker network ls | grep -vE "bridge|host|none" | awk '{print $1}') 2>/dev/null || true

# Faz uma limpeza final
docker system prune -af --volumes

echo "✅ Tudo foi removido com sucesso!"
