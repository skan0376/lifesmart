import subprocess
import urllib.request
import json
import time
import hashlib
import logging
from . import LifeSmartDevice


from homeassistant.components.scene import (
    Scene,
)

from homeassistant.components.switch import (
    ENTITY_ID_FORMAT,
)

_LOGGER = logging.getLogger(__name__)

CON_AI_TYPE_SCENE = "scene"
CON_AI_TYPE_AIB = "aib"
CON_AI_TYPE_GROUP = "grouphw"
CON_AI_TYPES = [
    CON_AI_TYPE_SCENE,
    CON_AI_TYPE_AIB,
    CON_AI_TYPE_GROUP,
]
AI_TYPES = ["ai"]


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Find and return lifesmart switches."""
    if discovery_info is None:
        return
    dev = discovery_info.get("dev")
    param = discovery_info.get("param")
    devices = []
    if dev["devtype"] in AI_TYPES:
        print(dev)
        devices.append(LifeSmartScene(dev, "s", dev["me"] + dev["desc"], param))
    else:
        for idx in dev["data"]:
            if idx in ["L1", "L2", "L3", "P1", "P2", "P3"]:
                devices.append(LifeSmartScene(dev, idx, dev["data"][idx], param))
    async_add_entities(devices)
    return True


class LifeSmartScene(LifeSmartDevice, Scene):
    def __init__(self, dev, idx, val, param):
        """Initialize the switch."""
        super().__init__(dev, idx, val, param)
        print(val)
        self.entity_id = ENTITY_ID_FORMAT.format(
            (
                dev["devtype"] + "_" + dev["agt"][:-3] + "_" + dev["me"] + "_" + idx
            ).lower())

    async def async_added_to_hass(self):
        """Call when entity is added to hass."""

    def _get_state(self):
        """get lifesmart switch state."""
        return self._state

    async def activate(self, **kwargs):
        """Turn the device on."""
        if self._devtype in AI_TYPES:
            if await super().async_lifesmart_sceneset(self, None, None) == 0:
                self.activate = True
                self.async_schedule_update_ha_state()

    @property
    def unique_id(self):
        """A unique identifier for this entity."""
        return self.entity_id
