# Introduction

 Exporter that receives data from the Fibaro Home Center device (Smart Home HUB Z-Wave) and publishes it in prometheus format

# Installation

Pull the latest version of the image from the docker.

```
docker pull sonaton/fibaro_hc_exporter
```

Alternately you can build the image yourself.

```
docker build -t sonaton/fibaro_hc_exporter https://github.com/sonaton/fibaro_hc_exporter.git
```

# Start

Run the image

```
docker run -d --name fibaro_hc_exporter \
   --env 'hub_url=http://url' \
   --env 'hub_user=user' \
   --env 'hub_password=password' \
   --publish 8000:8000 \
   sonaton/fibaro_hc_exporter
```

Base variables:
- hub_url: url of fibaro hub
- hub_user: hub user
- hub_password: user password

Additional variables:
- update_interval: update time in seconds (default: "60")
- enabled: export only enabled devices (default: "True")
- visible: export only visible devices (default: "True")
