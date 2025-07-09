# LangChain Integration Guide

This guide demonstrates how to connect AI-SWA with the LangChain framework.

## Overview

LangChain is a popular toolkit for composing LLM-powered applications. AI-SWA can orchestrate LangChain agents through its plugin system. The steps below illustrate a simple integration.

## Steps

1. **Install LangChain**
   ```bash
   pip install langchain
   ```
2. **Create a Plugin**
   Implement a plugin that exposes LangChain chains as callable tools. Place the plugin in the `plugins/` directory with a manifest file describing required permissions.

3. **Register the Plugin**
   Add the plugin to `config.yaml` under `enabled_plugins`. AI-SWA will load it at startup and make its actions available to the Planner and Executor.

4. **Use Within Tasks**
   Tasks can reference the plugin's actions. The Executor will invoke the LangChain chain and return the output for further processing in the Reflector loop.

## Example

A minimal plugin might wrap a LangChain `LLMChain` that summarizes text. The plugin exposes a `summarize` action, which tasks can call by name. See `plugins/examples/langchain_plugin.py` for a reference implementation.

