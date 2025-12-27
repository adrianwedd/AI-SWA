# AutoGen Integration Guide

This guide shows how to connect AI-SWA with Microsoft's AutoGen framework using a simple plugin.

## Overview

AutoGen enables multi-agent conversations for complex tasks. By wrapping an AutoGen conversation as a plugin, AI-SWA can trigger it as part of its orchestration cycle.

## Steps

1. **Install AutoGen**
   ```bash
   pip install ag2
   ```
2. **Create a Plugin**
   Write a plugin that constructs an AutoGen `GroupChat` or similar conversation and exposes a `chat` action. See `plugins/examples/autogen_plugin.py` for a reference implementation.

3. **Register the Plugin**
   List the plugin directory in `config.yaml` under `enabled_plugins`.

4. **Use Within Tasks**
   Tasks can call the `chat` action, and the plugin will run the AutoGen conversation, returning its transcript for further steps in the Reflector loop.

## Example Plugin

The sample `autogen_plugin.py` launches two conversable agents that work together to answer a question. The `chat` action returns their final message.

