# Dockerfile-weaviate
FROM semitechnologies/weaviate:1.21.5

ARG USER_ID
ARG GROUP_ID

RUN addgroup -g weaviate && \
    adduser -u $USER_ID -G weaviate -D weaviate

USER weaviate

