#codecloud.web.att.com
#vi /etc/resolve.conf
#nameserver 135.207.142.20
#nameserver 135.207.142.21
#nameserver 135.207.255.13

docker build -t api api/
docker build -t controller controller/
docker build -t data data/
docker build -t solver solver/
docker build -t reservation reservation/
