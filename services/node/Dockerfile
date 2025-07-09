FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev && addgroup -S app && adduser -S app -G app
COPY io_server.js ./
EXPOSE 50051
USER app
CMD ["node", "io_server.js"]
