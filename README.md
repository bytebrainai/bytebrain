# ByteBrain

A Chatbot For Your Documentations

## Components

ByteBrain consists of following components:

- **ByteBrain Server**: A server that provides a REST API for chatbot and dashboard. Currently, this component supports
  two chat frontends:
    - Websocket ChatBot
    - Discord ChatBot
- **ByteBrain UI**: A UI component that can be embedded in any website
- **ByteBrain Dashboard**: A dashboard for creating and managing chatbots

## ZIO Website Deployment (chat.zio.dev)

The `byteBrain-client` module is used to embed the ByteBrain UI in a website that is used to provide a chatbot for
zio.dev documentation. You can find the deployed version [here](https://chat.zio.dev).

To deploy ZIO Chat interface on chat.zio.dev, run following commands:

```shell
git clone https://github.com/zivergetech/bytebrain.git
cd bytebrain
docker-compose up -d
```

Note: The latest version of bytebrain that is deployed on chat.zio.dev is based on
this [commit](https://github.com/zivergetech/bytebrain/commit/fb4b0f9b8c1fc72d3ffc015ede7fd6bb2b1ae039).

## Install Development Environment

### ByteBrain Server

Run the following steps:

```shell
nix-shell shell.nix
cd bytebrain-server
python -m venv .venv
source .venv/bin/activate
pip install poetry
poetry install
```

Then define following env variables in .env file:

```shell
OPENAI_API_KEY=<openai_api_key>
DISCORD_BOT_TOKEN=<discord_token>
PROMETHEUS_REMOTE_WRITE_URL=<prometheus_url>
PROMETHEUS_REMOTE_WRITE_USERNAME=<prometheus_username>
PROMETHEUS_REMOTE_WRITE_PASSWORD=<prometheus_password>
GOOGLE_API_KEY=<google_api_key>
GITHUB_CLIENT_ID=<github_client_id>
GITHUB_CLIENT_SECRET=<github_secret>
```

After running these steps, we can run any task defined inside `pyproject.toml`, e.g.:

```shell
poetry run webserver
```

It will start a development server on http://localhost:8081

#### Development Notes

1. The current implementation of ByteBrain Server depends on modified version of Langchain AI which enables us to have
   Multi-tenancy support. I've created a pull request for this
   change [here](https://github.com/langchain-ai/langchain/pull/14174).
2. Currently, the some tables in this module are stored in a separate database, which is not ideal. We need to integrate
   theses tables in one database.
3.T  he customization of chatbot's prompt template not completed yet and needs
   more work.

### ByteBrain Dashboard

Run the following steps:

```shell
nix-shell shell.nix
cd bytebrain-dashboard
yarn install
yarn run dev
```

It will start a development server on http://localhost:5173

### ByteBrain UI

The ByteBrain UI is a React component that can be embedded in any website. To install it, run the following steps on the root of your React project:

```shell
npm i @bytebrain.ai/bytebrain-ui
```

Then you can import the `ChatApp` or `ChatPrompt` component from `@bytebrain.ai/bytebrain-ui` and use it in your
project, e.g.:

```jsx
<ChatApp
  websocketHost='localhost'
  websocketPort='8081'
  websocketEndpoint='/chat'
/>
```

#### Development Notes

1. To test ui components locally, you can run `yarn run storybook` in `bytebrain-ui` directory and then
   open http://localhost:6006 in your browser. It will show a list of all components that you can test.

2. To build and publish the package, run following commands:

```shell
cd bytebrain-ui
yarn version --patch
yarn run build-lib
yarn pack
yarn publish
```

3. The current implementation of ByteBrain UI contains support for API Keys. But it is not published to npm registry
   yet.