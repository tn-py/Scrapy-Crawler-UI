
# Build stage
FROM node:18-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./

ENV NODE_OPTIONS=--openssl-legacy-provider
RUN npm install

COPY . .

RUN npm run build

# Production stage
FROM nginx:stable-alpine

COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
