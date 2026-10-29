# data-broker-opt-out-bot

An autonomous Telegram bot and extensible plugin framework that submits and tracks opt-out requests to major data brokers, using a combination of public APIs and headless-browser scraping backed by recorded HTML fixtures.

## Features & Plugin Ecosystem

- **Extensible Architecture**: Load community adapters via setuptools entry points (`optout_bot.adapters`).
- **Auto-Discovery**: Installing `optout-broker-xyz` via `pip install` automatically registers the adapter with the core bot engine.
- **Developer & Contributor Template**: Reference implementation and plugin creation template in [`examples/sample-plugin`](examples/sample-plugin).

## Quickstart

### Installation

```bash
pip install -e .
```

### Community Adapters

To install a community adapter plugin (e.g. `optout-broker-xyz`):

```bash
pip install optout-broker-xyz
```

Upon installation, `optout_bot` will auto-discover and enable the adapter.

### Developing Plugins

Refer to the [Plugin Marketplace Guide](docs/PLUGINS.md) for entry-point specifications, adapter guidelines, and creation instructions.

## Testing

Run pytest across core engine and installed plugins:

```bash
pytest
```
