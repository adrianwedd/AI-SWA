# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: io_service.proto
# Protobuf Python Version: 6.31.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
try:
    pass
except Exception:
    pass
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10io_service.proto\x12\x05\x61iswa\"\x1e\n\x0bPingRequest\x12\x0f\n\x07message\x18\x01 \x01(\t\"\x1c\n\tPingReply\x12\x0f\n\x07message\x18\x01 \x01(\t\"\x1b\n\x0b\x46ileRequest\x12\x0c\n\x04path\x18\x01 \x01(\t\"\x1c\n\tFileReply\x12\x0f\n\x07\x63ontent\x18\x01 \x01(\t\"-\n\x0cWriteRequest\x12\x0c\n\x04path\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\t\"\x1d\n\nWriteReply\x12\x0f\n\x07success\x18\x01 \x01(\x08\x32\xa6\x01\n\tIOService\x12.\n\x04Ping\x12\x12.aiswa.PingRequest\x1a\x10.aiswa.PingReply\"\x00\x12\x32\n\x08ReadFile\x12\x12.aiswa.FileRequest\x1a\x10.aiswa.FileReply\"\x00\x12\x35\n\tWriteFile\x12\x13.aiswa.WriteRequest\x1a\x11.aiswa.WriteReply\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'io_service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_PINGREQUEST']._serialized_start=27
  _globals['_PINGREQUEST']._serialized_end=57
  _globals['_PINGREPLY']._serialized_start=59
  _globals['_PINGREPLY']._serialized_end=87
  _globals['_FILEREQUEST']._serialized_start=89
  _globals['_FILEREQUEST']._serialized_end=116
  _globals['_FILEREPLY']._serialized_start=118
  _globals['_FILEREPLY']._serialized_end=146
  _globals['_WRITEREQUEST']._serialized_start=148
  _globals['_WRITEREQUEST']._serialized_end=193
  _globals['_WRITEREPLY']._serialized_start=195
  _globals['_WRITEREPLY']._serialized_end=224
  _globals['_IOSERVICE']._serialized_start=227
  _globals['_IOSERVICE']._serialized_end=393
# @@protoc_insertion_point(module_scope)
