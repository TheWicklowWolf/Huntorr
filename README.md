![Build Status](https://github.com/TheWicklowWolf/Huntorr/actions/workflows/main.yml/badge.svg)
![Docker Pulls](https://img.shields.io/docker/pulls/thewicklowwolf/huntorr.svg)

<p align="center">
  
![huntorr](https://github.com/TheWicklowWolf/Huntorr/assets/111055425/792f991c-b202-436c-a6d9-4f8244e24c17)

</p>


Web GUI for manually finding torrents and adding them to qBittorrent.


## Run using docker-compose

```yaml
version: "2.1"
services:
  huntorr:
    image: thewicklowwolf/huntorr:latest
    container_name: huntorr
    environment:
      - torrenter_username=admin
      - torrenter_password=raspberry
      - torrenter_ip=192.168.1.123
      - torrenter_port=5002
    ports:
      - 5000:5000
    restart: unless-stopped
```


---


https://github.com/TheWicklowWolf/Huntorr/assets/111055425/c3984c80-3abb-4333-accc-36760117c5c7


---

https://hub.docker.com/r/thewicklowwolf/huntorr

