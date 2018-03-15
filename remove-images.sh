echo "Removing data containers and images !!!"
docker rm $(docker ps -a -q  --filter ancestor=data)
docker rmi -f $(docker images -a | grep "data" | awk '{print $3}')

echo "Removing controller containers and images !!!"
docker rm $(docker ps -a -q  --filter ancestor=controller)
docker rmi -f $(docker images -a | grep "controller" | awk '{print $3}')

echo "Removing api containers and images !!!"
docker rm $(docker ps -a -q  --filter ancestor=api)
docker rmi -f $(docker images -a | grep "api" | awk '{print $3}')

echo "Removing solver containers and images !!!"
docker rm $(docker ps -a -q  --filter ancestor=solver)
docker rmi -f $(docker images -a | grep "solver" | awk '{print $3}')

echo "Removing reservation containers and images !!!"
docker rm $(docker ps -a -q  --filter ancestor=reservation)
docker rmi -f $(docker images -a | grep "reservation" | awk '{print $3}')

