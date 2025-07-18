# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings
import os

from . import plugin_marketplace_pb2 as plugin__marketplace__pb2

GRPC_GENERATED_VERSION = '1.73.1'
GRPC_VERSION = grpc.__version__ if not os.environ.get("DISABLE_GRPC_VERSION_CHECK") else GRPC_GENERATED_VERSION
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except Exception:
    _version_not_supported = False

if _version_not_supported:
    warnings.warn(
        'gRPC version mismatch: ' + GRPC_VERSION + ' expected ' + GRPC_GENERATED_VERSION,
        RuntimeWarning,
    )


class PluginMarketplaceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ListPlugins = channel.unary_unary(
                '/aiswa.PluginMarketplace/ListPlugins',
                request_serializer=plugin__marketplace__pb2.Empty.SerializeToString,
                response_deserializer=plugin__marketplace__pb2.PluginList.FromString,
                _registered_method=True)
        self.DownloadPlugin = channel.unary_unary(
                '/aiswa.PluginMarketplace/DownloadPlugin',
                request_serializer=plugin__marketplace__pb2.PluginRequest.SerializeToString,
                response_deserializer=plugin__marketplace__pb2.PluginData.FromString,
                _registered_method=True)
        self.SubmitReview = channel.unary_unary(
                '/aiswa.PluginMarketplace/SubmitReview',
                request_serializer=plugin__marketplace__pb2.SubmitReviewRequest.SerializeToString,
                response_deserializer=plugin__marketplace__pb2.Empty.FromString,
                _registered_method=True)
        self.ListReviews = channel.unary_unary(
                '/aiswa.PluginMarketplace/ListReviews',
                request_serializer=plugin__marketplace__pb2.ReviewRequest.SerializeToString,
                response_deserializer=plugin__marketplace__pb2.ReviewList.FromString,
                _registered_method=True)


class PluginMarketplaceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ListPlugins(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DownloadPlugin(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SubmitReview(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListReviews(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_PluginMarketplaceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ListPlugins': grpc.unary_unary_rpc_method_handler(
                    servicer.ListPlugins,
                    request_deserializer=plugin__marketplace__pb2.Empty.FromString,
                    response_serializer=plugin__marketplace__pb2.PluginList.SerializeToString,
            ),
            'DownloadPlugin': grpc.unary_unary_rpc_method_handler(
                    servicer.DownloadPlugin,
                    request_deserializer=plugin__marketplace__pb2.PluginRequest.FromString,
                    response_serializer=plugin__marketplace__pb2.PluginData.SerializeToString,
            ),
            'SubmitReview': grpc.unary_unary_rpc_method_handler(
                    servicer.SubmitReview,
                    request_deserializer=plugin__marketplace__pb2.SubmitReviewRequest.FromString,
                    response_serializer=plugin__marketplace__pb2.Empty.SerializeToString,
            ),
            'ListReviews': grpc.unary_unary_rpc_method_handler(
                    servicer.ListReviews,
                    request_deserializer=plugin__marketplace__pb2.ReviewRequest.FromString,
                    response_serializer=plugin__marketplace__pb2.ReviewList.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'aiswa.PluginMarketplace', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('aiswa.PluginMarketplace', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class PluginMarketplace(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ListPlugins(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/aiswa.PluginMarketplace/ListPlugins',
            plugin__marketplace__pb2.Empty.SerializeToString,
            plugin__marketplace__pb2.PluginList.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def DownloadPlugin(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/aiswa.PluginMarketplace/DownloadPlugin',
            plugin__marketplace__pb2.PluginRequest.SerializeToString,
            plugin__marketplace__pb2.PluginData.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SubmitReview(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/aiswa.PluginMarketplace/SubmitReview',
            plugin__marketplace__pb2.SubmitReviewRequest.SerializeToString,
            plugin__marketplace__pb2.Empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ListReviews(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/aiswa.PluginMarketplace/ListReviews',
            plugin__marketplace__pb2.ReviewRequest.SerializeToString,
            plugin__marketplace__pb2.ReviewList.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
