# ByteBrain

A Chatbot For Your Documentations

## Components

ByteBrain consists of following components:

- **ByteBrain Server**: A server that provides a REST API for chatbot and dashboard
- **ByteBrain UI**: A UI component that can be embedded in any website
- **ByteBrain Dashboard**: A dashboard for creating and managing chatbots


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

Then define following env variables

```shell
export OPENAI_API_KEY=<openai_api_key>
export ZIOCHAT_DOCS_DIR=<docs_dir>
```

After running these steps, we can run any task defined inside `pyproject.toml`, e.g.:

```shell
poetry run webserver
```

It will start a development server on http://localhost:8081

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

Then you can import the `ChatApp` or `ChatPrompt` component from `@bytebrain.ai/bytebrain-ui` and use it in your project, e.g.:


```jsx
<ChatApp
  websocketHost='localhost'
  websocketPort='8081'
  websocketEndpoint='/chat'
/>
```

#### Development Notes

1. To test ui components locally, you can run `yarn run storybook` in `bytebrain-ui` directory and then open http://localhost:6006 in your browser. It will show a list of all components that you can test.

2. To build and publish the package, run following commands:

```shell
cd bytebrain-ui
yarn version --patch
yarn run build-lib
yarn pack
yarn publish
```

## ZIO Website Deployment (chat.zio.dev)

The **ByteBrain Client** module is used to embed the ByteBrain UI in a website that is used to provide a chatbot for zio.dev documentation. You can find the deployed version [here](https://chat.zio.dev).

To deploy client module, run following commands:

```
git clone https://github.com/zivergetech/bytebrain.git
cd bytebrain
docker-compose up -d
cd letsencrypt
./cli.sh up
```
