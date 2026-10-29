# Community Adapter Template: `optout-broker-xyz`

This directory serves as a reference template for building community adapters for the Data Broker Opt-Out Bot.

## How to use this template

1. Copy this directory to create your own adapter repository (e.g. `optout-broker-yourbroker`).
2. Update `pyproject.toml` with your package details and entry point definition:
   ```toml
   [project.entry-points."optout_bot.adapters"]
   your_broker = "optout_broker_yourbroker.adapter:YourBrokerAdapter"
   ```
3. Subclass `BaseAdapter` from `optout_bot.adapters` and implement `broker_id`, `name`, `submit_opt_out`, and `check_status`.
4. Install your plugin package locally (`pip install -e .`) or publish to PyPI.
5. `data-broker-opt-out-bot` will automatically discover and register your adapter upon startup!
