try:
    import grpc
except Exception:  # pragma: no cover - optional dependency
    grpc = None
from . import bridge_pb2, bridge_pb2_grpc
from .config import load_config


def reverse(text: str, host: str | None = None, port: int | None = None) -> str:
    """Call the Rust Bridge service to reverse a string."""
    if grpc is None:
        raise ImportError("grpc is required for bridge client")
    cfg = load_config()
    host = host or cfg.get("rust_bridge", {}).get("host", "localhost")
    port = port or cfg.get("rust_bridge", {}).get("port", 50052)
    channel = grpc.insecure_channel(f"{host}:{int(port)}")
    stub = bridge_pb2_grpc.BridgeStub(channel)
    response = stub.Reverse(bridge_pb2.ReverseRequest(text=text))
    return response.text
