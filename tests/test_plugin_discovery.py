import pytest
from optout_bot.adapters.base import BaseAdapter
from optout_bot.adapters.registry import AdapterRegistry


class DummyAdapter(BaseAdapter):
    @property
    def broker_id(self) -> str:
        return "dummy_broker"

    @property
    def name(self) -> str:
        return "Dummy Broker"

    def submit_opt_out(self, user_data):
        return {"status": "submitted", "confirmation_id": "dummy-123"}

    def check_status(self, confirmation_id):
        return {"status": "completed"}


def test_registry_manual_registration():
    registry = AdapterRegistry()
    registry.register(DummyAdapter)

    assert "dummy_broker" in registry.list_adapters()
    adapter_cls = registry.get_adapter_class("dummy_broker")
    assert adapter_cls is DummyAdapter

    instance = adapter_cls()
    assert instance.broker_id == "dummy_broker"
    assert instance.name == "Dummy Broker"
    res = instance.submit_opt_out({"email": "test@example.com"})
    assert res["status"] == "submitted"
    assert res["confirmation_id"] == "dummy-123"


def test_registry_invalid_registration():
    registry = AdapterRegistry()

    class NotAnAdapter:
        pass

    with pytest.raises(TypeError):
        registry.register(NotAnAdapter)  # type: ignore


def test_plugin_discovery_integration():
    registry = AdapterRegistry()
    registry.discover_plugins()
    # Check if sample plugin optout_broker_xyz is discovered after installation
    adapters = registry.list_adapters()
    assert "optout_broker_xyz" in adapters
    adapter_cls = registry.get_adapter_class("optout_broker_xyz")
    assert adapter_cls is not None

    adapter = adapter_cls()
    assert adapter.name == "XYZ Data Broker"
    sub_res = adapter.submit_opt_out({"email": "user@example.com"})
    assert sub_res["status"] == "submitted"
    assert "xyz-optout-user@example.com-12345" in sub_res["confirmation_id"]

    status_res = adapter.check_status(sub_res["confirmation_id"])
    assert status_res["status"] == "processed"
