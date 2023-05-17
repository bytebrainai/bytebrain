FROM node:18-alpine as builder

WORKDIR /app/client

COPY . .

RUN rm -rf node_modules && yarn install --frozen-lockfile

RUN yarn run build

FROM nginx:1.21.0-alpine as production

ENV NODE_ENV production

COPY --from=builder /app/client/build /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
