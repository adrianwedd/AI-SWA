# CrewAI Integration Guide

This short tutorial demonstrates how to run CrewAI agent teams within AI-SWA's plugin system.

## Overview

CrewAI orchestrates multi-agent workflows using a role-based model. By exposing a CrewAI crew as a plugin, AI-SWA can schedule its actions alongside native tasks.

## Steps

1. **Install CrewAI**
   ```bash
   pip install crewai
   ```
2. **Create a Plugin**
   Implement a plugin that configures a CrewAI crew and exposes crew actions as callable tools. See `plugins/examples/crewai_plugin.py` for a minimal reference.

3. **Register the Plugin**
   Add the plugin path to `config.yaml` under `enabled_plugins` so the Planner can load it at runtime.

4. **Use Within Tasks**
   Define tasks that call the plugin's actions. AI-SWA will invoke the crew and process the returned results within the Reflector loop.

## Example Plugin

The `crewai_plugin.py` example spins up a simple crew with two agents and provides a `run_mission` action. Tasks call `run_mission` by name, which returns the crew's final output.

