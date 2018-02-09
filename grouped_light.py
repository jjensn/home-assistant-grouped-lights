import logging

# Import the device class from the component that you want to support
from homeassistant.components import light
from homeassistant.const import (STATE_OFF, STATE_ON, SERVICE_TURN_ON,
                                 SERVICE_TURN_OFF, ATTR_ENTITY_ID)
from homeassistant.components.light import (SUPPORT_BRIGHTNESS,
                                            SUPPORT_RGB_COLOR,
                                            SUPPORT_COLOR_TEMP,
                                            SUPPORT_TRANSITION)

CONF_NAME = 'name'
CONF_ENTITIES = 'entities' #

_LOGGER = logging.getLogger(__name__)

SUPPORT_GROUP_LIGHT = (SUPPORT_BRIGHTNESS | SUPPORT_RGB_COLOR |
                       SUPPORT_COLOR_TEMP | SUPPORT_TRANSITION)

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Initialize grouped light platform."""
    name = config.get(CONF_NAME)
    entity_ids = config.get(CONF_ENTITIES)

    if name is None or entity_ids is None or len(entity_ids) == 0:
        _LOGGER.error('Invalid config. Excepted %s and %s', CONF_NAME, CONF_ENTITIES)
        return False

    add_devices([GroupedLight(hass, name, entity_ids)])


class GroupedLight(light.Light):
    """Represents an Grouped Light in Home Assistant."""

    def __init__(self, hass, name, entity_ids):
        """Initialize a Grouped Light."""
        self.hass = hass
        self._name = name
        self._entity_ids = entity_ids

    @property    
    def name(self):
        return self._name
        
    @property
    def brightness(self):
        """Brightness of the light group"""   
        brightness = 0
        for state in self._light_states():
            if not 'brightness' in state.attributes:
                return None
            brightness += state.attributes.get('brightness')
        brightness = brightness / float(len(self._entity_ids))
        return brightness

    @property
    def color_temp(self):
        """Return the CT color value."""
        for state in self._light_states():
            if not 'color_temp' in state.attributes:
                return None
            return state.attributes.get('color_temp')

    @property
    def xy_color(self):
        """Return the XY color value."""
        for state in self._light_states():
            if not 'xy_color' in state.attributes:
                return None
            #return the first value we get since merging color values does not make sense
            return state.attributes.get('xy_color')

    @property
    def rgb_color(self):
        """Return the RGB color value."""
        for state in self._light_states():
            if not 'rgb_color' in state.attributes:
                return None
            #return the first value we get since merging color values does not make sense
            return state.attributes.get('rgb_color')

    @property
    def is_on(self):
        """If light is on."""
        for state in self._light_states():
            if state.state == STATE_ON:
                return True
        return False

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_GROUP_LIGHT

    def _light_states(self):
        """The states that the group is tracking."""
        states = []

        for entity_id in self._entity_ids:
            state = self.hass.states.get(entity_id)
            if state is not None:
                states.append(state)

        return states

    def turn_on(self, **kwargs):
        """Forward the turn_on command to all lights in the group"""
        for entity_id in self._entity_ids:
            kwargs[ATTR_ENTITY_ID] = entity_id
            self.hass.services.call('light', SERVICE_TURN_ON, kwargs, blocking=True)

    def turn_off(self, **kwargs):
        """Forward the turn_off command to all lights in the group"""
        for entity_id in self._entity_ids:
            kwargs[ATTR_ENTITY_ID] = entity_id
            self.hass.services.call('light', SERVICE_TURN_OFF, kwargs, blocking=True)
            
