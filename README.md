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

![Huntorr_Light](https://github.com/TheWicklowWolf/Huntorr/assets/111055425/6c852963-7bb7-4eca-b5c2-65becb2e7fd2)

---

![Huntorr](https://github.com/TheWicklowWolf/Huntorr/assets/111055425/a3ab3f53-6857-42a4-995f-fbada2718fd3)

---

https://hub.docker.com/r/thewicklowwolf/huntorr
