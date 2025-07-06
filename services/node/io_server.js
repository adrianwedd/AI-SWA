const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const client = require('prom-client');
const http = require('http');
const path = require('path');

const packageDef = protoLoader.loadSync(path.join(__dirname, '../../proto/io_service.proto'));
const proto = grpc.loadPackageDefinition(packageDef).aiswa;

function ping(call, callback) {
  callback(null, { message: 'pong:' + call.request.message });
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
  const metricsPort = process.env.METRICS_PORT || '9100';
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
