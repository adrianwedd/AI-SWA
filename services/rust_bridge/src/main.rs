use tonic::{transport::Server, Request, Response, Status};

pub mod bridge {
    tonic::include_proto!("aiswa");
}
use bridge::bridge_server::{Bridge, BridgeServer};
use bridge::{ReverseReply, ReverseRequest};

#[derive(Default)]
struct MyBridge;

#[tonic::async_trait]
impl Bridge for MyBridge {
    async fn reverse(
        &self,
        request: Request<ReverseRequest>,
    ) -> Result<Response<ReverseReply>, Status> {
        let text = request.into_inner().text;
        let reversed: String = text.chars().rev().collect();
        Ok(Response::new(ReverseReply { text: reversed }))
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let addr = "0.0.0.0:50052".parse()?;
    let svc = MyBridge::default();
    Server::builder()
        .add_service(BridgeServer::new(svc))
        .serve(addr)
        .await?;
    Ok(())
}
