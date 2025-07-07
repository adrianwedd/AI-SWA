FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev
COPY io_server.js ./
EXPOSE 50051
CMD ["node", "io_server.js"]
