#!/bin/sh
set -e
DIR="$(dirname "$0")/certs"
mkdir -p "$DIR"
openssl req -x509 -nodes -newkey rsa:2048 -days 365 \
  -subj "/CN=localhost" \
  -keyout "$DIR/collector.key" -out "$DIR/collector.crt"
cp "$DIR/collector.crt" "$DIR/ca.crt"
cp "$DIR/collector.key" "$DIR/ca.key"
