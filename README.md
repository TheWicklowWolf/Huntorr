![Build Status](https://github.com/TheWicklowWolf/Huntorr/actions/workflows/main.yml/badge.svg)
![Docker Pulls](https://img.shields.io/docker/pulls/thewicklowwolf/huntorr.svg)


<img src="https://raw.githubusercontent.com/TheWicklowWolf/Huntorr/main/src/static/huntorr.png" alt="huntorr">


Web GUI for manually finding torrents and adding them to qBittorrent.


## Run using docker-compose

```yaml
version: "2.1"
services:
  huntorr:
    image: thewicklowwolf/huntorr:latest
    container_name: huntorr
    environment:
      - torrenter_username=user
      - torrenter_password=password
      - torrenter_ip=192.168.1.2
      - torrenter_port=5002
      - media_server_addresses=Plex:http://192.168.1.2:32400, Jellyfin:http://192.168.1.2:8096
      - media_server_tokens=Plex:abc, Jellyfin:def
      - media_server_library_name=Movies
    ports:
      - 5000:5000
    restart: unless-stopped
```

---

<img src="https://raw.githubusercontent.com/TheWicklowWolf/Huntorr/main/src/static/light.png" alt="light">

---

<img src="https://raw.githubusercontent.com/TheWicklowWolf/Huntorr/main/src/static/dark.png" alt="dark">

---

https://hub.docker.com/r/thewicklowwolf/huntorr
