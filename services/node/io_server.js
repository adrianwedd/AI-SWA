const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const client = require('prom-client');
const express = require('express');
const path = require('path');
const fs = require('fs');
const yaml = require('js-yaml');

function loadConfig() {
  const cfgPath = process.env.CONFIG_FILE || path.join(__dirname, '../../config.yaml');
  try {
    const data = fs.readFileSync(cfgPath, 'utf8');
    return yaml.load(data) || {};
  } catch (err) {
    console.warn(`Failed to load config: ${err}`);
    return {};
  }
}

const config = loadConfig();

const packageDef = protoLoader.loadSync(path.join(__dirname, '../../proto/io_service.proto'));
const proto = grpc.loadPackageDefinition(packageDef).aiswa;

const requestCounter = new client.Counter({
  name: 'io_requests_total',
  help: 'Total number of RPC requests',
  labelNames: ['method'],
});

const latencyHistogram = new client.Histogram({
  name: 'io_request_duration_seconds',
  help: 'Duration of RPC requests in seconds',
  labelNames: ['method'],
  buckets: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5],
});

function ping(call, callback) {
  const end = latencyHistogram.startTimer({ method: 'Ping' });
  requestCounter.labels('Ping').inc();
  callback(null, { message: 'pong:' + call.request.message });
  end();
}

function readFile(call, callback) {
  const end = latencyHistogram.startTimer({ method: 'ReadFile' });
  requestCounter.labels('ReadFile').inc();
  fs.readFile(call.request.path, 'utf8', (err, data) => {
    if (err) {
      callback(err, null);
    } else {
      callback(null, { content: data });
    }
    end();
  });
}

function writeFile(call, callback) {
  const end = latencyHistogram.startTimer({ method: 'WriteFile' });
  requestCounter.labels('WriteFile').inc();
  fs.writeFile(call.request.path, call.request.content, 'utf8', (err) => {
    if (err) {
      callback(err, null);
    } else {
      callback(null, { success: true });
    }
    end();
  });
}

function startHttpServer(port) {
  client.collectDefaultMetrics();
  const app = express();
  app.get('/metrics', async (_req, res) => {
    res.set('Content-Type', client.register.contentType);
    res.end(await client.register.metrics());
  });
  app.get('/health', (_req, res) => {
    res.json({ status: 'ok', uptime: process.uptime() });
  });
  app.listen(port, () => {
    console.log(`HTTP server running on ${port}`);
  });
}

function main() {
  const server = new grpc.Server();
  server.addService(proto.IOService.service, {
    Ping: ping,
    ReadFile: readFile,
    WriteFile: writeFile,
  });
  const port = process.env.PORT || '50051';
  const metricsPort = process.env.METRICS_PORT ||
    (config.worker && config.worker.metrics_port) || '9100';
  server.bindAsync('0.0.0.0:' + port, grpc.ServerCredentials.createInsecure(), () => {
    server.start();
    console.log(`IOService running on ${port}`);
  });
  startHttpServer(metricsPort);
}

if (require.main === module) {
  main();
}

module.exports = { ping };
