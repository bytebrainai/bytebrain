## ZIO Website Deployment

The `byteBrain-client` module is used to embed the ByteBrain UI in a website that is used to provide a chatbot for
zio.dev documentation. You can find the deployed version [here](https://chat.zio.dev).

To deploy ZIO Chat interface on chat.zio.dev, run following commands:

```shell
git clone https://github.com/bytebrainai/bytebrain.git
cd bytebrain/bytebrain-client
docker-compose up -d
```

Notes:

1. The latest version of bytebrain that is deployed on chat.zio.dev is based on
   this [commit](https://github.com/zivergetech/bytebrain/commit/fb4b0f9b8c1fc72d3ffc015ede7fd6bb2b1ae039).

2. The monitoring dashboard is available on Grafana Cloud console [here](https://ziochat.grafana.net/d/a2d6a23e-5200-44f0-9e50-33d252917386/zio-chat)
