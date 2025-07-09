try:
    import grpc
except Exception:  # pragma: no cover - optional dependency
    grpc = None
from . import io_service_pb2, io_service_pb2_grpc
from .config import load_config


def ping(message: str, host: str | None = None, port: int | None = None) -> str:
    """Send a ping request to the Node IOService."""
    if grpc is None:
        raise ImportError("grpc is required for ping")
    cfg = load_config()
    host = host or cfg.get("node", {}).get("host", "localhost")
    port = port or cfg.get("node", {}).get("port", 50051)
    channel = grpc.insecure_channel(f"{host}:{int(port)}")
    stub = io_service_pb2_grpc.IOServiceStub(channel)
    response = stub.Ping(io_service_pb2.PingRequest(message=message))
    return response.message


def read_file(path: str, host: str | None = None, port: int | None = None) -> str:
    """Read a file using the Node IOService."""
    if grpc is None:
        raise ImportError("grpc is required for read_file")
    cfg = load_config()
    host = host or cfg.get("node", {}).get("host", "localhost")
    port = port or cfg.get("node", {}).get("port", 50051)
    channel = grpc.insecure_channel(f"{host}:{int(port)}")
    stub = io_service_pb2_grpc.IOServiceStub(channel)
    response = stub.ReadFile(io_service_pb2.FileRequest(path=path))
    return response.content


def write_file(path: str, content: str, host: str | None = None, port: int | None = None) -> bool:
    """Write a file using the Node IOService."""
    if grpc is None:
        raise ImportError("grpc is required for write_file")
    cfg = load_config()
    host = host or cfg.get("node", {}).get("host", "localhost")
    port = port or cfg.get("node", {}).get("port", 50051)
    channel = grpc.insecure_channel(f"{host}:{int(port)}")
    stub = io_service_pb2_grpc.IOServiceStub(channel)
    response = stub.WriteFile(
        io_service_pb2.WriteRequest(path=path, content=content)
    )
    return response.success
