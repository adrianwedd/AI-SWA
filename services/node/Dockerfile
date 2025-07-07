FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev
COPY . .
COPY config.yaml ./
EXPOSE 50051
EXPOSE 9100
CMD ["node", "io_server.js"]
