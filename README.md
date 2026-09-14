# ByteBrain
<div align="center" style="display: flex; align-items: center; justify-content: center;">
  <img src="logo.svg" alt="ByteBrain Logo" width="20%" height="20%">
</div>

ByteBrain is an AI-powered chatbot used to onboard and support developers with new frameworks, languages, and libraries.

## Features

ByteBrain offers a range of powerful features:

1. **AI-Powered Chatbot:** Utilizes advanced artificial intelligence algorithms to provide assistance to users.

2. **Framework, Language, and Library Support:** Assists developers in getting acquainted with new frameworks, languages, and libraries. It supports a wide range of programming languages.

3. **Multiple Chat Interfaces:** Provides flexibility with two chat interfaces:
    - Web Interface: Integrates seamlessly into websites via a customizable widget.
    - Discord: Interacts directly within Discord channels for easy communication.

4. **Document Indexing:** Supports indexing documents from various sources including websites, webpages, GitHub repositories, and YouTube videos.

5. **Customizable Via Prompt Templates:** Allows customization of conversation prompts to align with specific needs and preferences.

## Components

ByteBrain consists of following components:

- **ByteBrain Server**: A server that provides a REST API for chatbot and dashboard. Currently, this component supports
  two chat frontends:
    - Websocket ChatBot
    - Discord ChatBot
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
AUTH_SECRET_KEY=<auth_secret_key>
```

To generate `AUTH_SECRET_KEY` please run the `openssl rand -hex 32` command.

After running these steps, we can run any task defined inside `pyproject.toml`, e.g.:

```shell
poetry run webserver
```

It will start a development server on http://localhost:8081 and the swagger documentation is available on http://localhost:8081/docs

#### Development Notes

1. Currently, some tables in this module are stored in a separate database, which is not ideal. We need to integrate
   these tables in one database.
2. The customization of chatbot's prompt template not completed yet and needs more work.

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

## Contribution Guide

We're thrilled that you're interested in contributing to ByteBrain project. This guide will help you understand how you can get involved and the contribution process. 

If you want to fix a bug or add a new feature, please follow the following steps:

1. **Fork the Repository**: Start by forking the ByteBrain repository to your GitHub account. This will create a copy of the repository under your account.

2. **Clone the Repository**: Clone the forked repository to your local machine using the following command:

```bash
git clone https://github.com/your-username/bytebrain.git
```

3. **Install Dependencies**: Follow the installation instructions in the project's README file to set up the development environment.

4. **Branching Strategy**: Create a new branch for your contribution. It's recommended to name your branch descriptively, indicating the feature or fix you're working on:

```shell
git checkout -b new-feature
```

5. **Code and Document**: Implement your changes or additions to the project. Update documentation, including README files, comments within the code, or any other relevant documentation affected by your changes.

6. **Commit**: Once you've made your changes, commit them to your branch:

```shell
git add .
git commit -m "Brief description of your changes"
```

7. **Push**: Push your changes to your forked repository:

```shell
git push origin new-feature
```

8. **Pull Request**: Go to the original ByteBrain repository on GitHub and create a Pull Request (PR) from your forked branch. Provide a descriptive title and detailed description of your changes in the PR.

## Demo

### Dashboard

![ByteBrain Dashboard](https://github.com/bytebrainai/bytebrain/assets/235974/38253456-e1b9-4169-a51f-c50167c1788f)

### WebUI Chat Component

![ByteBrain UI](https://github-production-user-asset-6210df.s3.amazonaws.com/235974/303415209-bd763189-5554-4ebb-a48a-149fb8c824c4.gif?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAVCODYLSA53PQK4ZA%2F20240208%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20240208T183609Z&X-Amz-Expires=300&X-Amz-Signature=702184602f38c4afa176d6d2543a5dcdea5083912cc965b33a1101bb2c757598&X-Amz-SignedHeaders=host&actor_id=235974&key_id=0&repo_id=648111122)

### Discord Chat Component

![Discord ChatBot](https://github.com/bytebrainai/bytebrain/assets/235974/912f80ef-3acc-4805-a5b3-4dcdbbcbdc92)
