const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const client = require('prom-client');
const http = require('http');
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

function startMetricsServer(port) {
  client.collectDefaultMetrics();
  http
    .createServer(async (req, res) => {
      if (req.url === '/metrics') {
        res.setHeader('Content-Type', client.register.contentType);
        res.end(await client.register.metrics());
      } else {
        res.statusCode = 404;
        res.end();
      }
    })
    .listen(port, () => {
      console.log(`Metrics server running on ${port}`);
    });
}

function main() {
  const server = new grpc.Server();
  server.addService(proto.IOService.service, { Ping: ping });
  const port = process.env.PORT || '50051';
  const metricsPort = process.env.METRICS_PORT ||
    (config.worker && config.worker.metrics_port) || '9100';
  server.bindAsync('0.0.0.0:' + port, grpc.ServerCredentials.createInsecure(), () => {
    server.start();
    console.log(`IOService running on ${port}`);
  });
  startMetricsServer(metricsPort);
}

if (require.main === module) {
  main();
}

module.exports = { ping };
