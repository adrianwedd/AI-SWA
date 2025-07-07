import grpc
from . import io_service_pb2, io_service_pb2_grpc
from .config import load_config


def ping(message: str, host: str | None = None, port: int | None = None) -> str:
    """Send a ping request to the Node IOService."""
    cfg = load_config()
    host = host or cfg.get("node", {}).get("host", "localhost")
    port = port or cfg.get("node", {}).get("port", 50051)
    channel = grpc.insecure_channel(f"{host}:{int(port)}")
    stub = io_service_pb2_grpc.IOServiceStub(channel)
    response = stub.Ping(io_service_pb2.PingRequest(message=message))
    return response.message
