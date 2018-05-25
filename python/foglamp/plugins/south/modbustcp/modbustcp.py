""" 
# ***********************************************************************
# * DISCLAIMER:
# *
# * All sample code is provided by OSIsoft for illustrative purposes only.
# * These examples have not been thoroughly tested under all conditions.
# * OSIsoft provides no guarantee nor implies any reliability,
# * serviceability, or function of these programs.
# * ALL PROGRAMS CONTAINED HEREIN ARE PROVIDED TO YOU "AS IS"
# * WITHOUT ANY WARRANTIES OF ANY KIND. ALL WARRANTIES INCLUDING
# * THE IMPLIED WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY
# * AND FITNESS FOR A PARTICULAR PURPOSE ARE EXPRESSLY DISCLAIMED.
# ************************************************************************
"""
""" Plugin for reading data from a Modbus TCP data source

    This plugin uses the pymodbus3 library, to install this perform
    the following steps:

        pip install pymodbus3

    You can learn more about this library here:
        https://pypi.org/project/pymodbus3/
    The library is licensed under the BSD License (BSD).

    As an example of how to use this library:

        from pymodbus3.client.sync import ModbusTcpClient
        client = ModbusTcpClient('127.0.0.1')
        value = (client.read_holding_registers(0, 1, unit=1)).registers[0]
        print(value)
        client.close()

    """

from datetime import datetime, timezone
from pymodbus3.client.sync import ModbusTcpClient
import uuid
import copy

from foglamp.common import logger
from foglamp.services.south import exceptions

__author__ = "Dan Lopez"
__copyright__ = "Copyright (c) 2018 OSIsoft, LLC"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_DEFAULT_CONFIG = {
    'plugin': {
        'description': 'Python module name of the plugin to load',
        'type':        'string',
        'default':     'modbustcp'
    },
    'pollInterval': {
        'description': 'The interval between poll calls to the device poll routine expressed in milliseconds.',
        'type':        'integer',
        'default':     '1000'
    },
    #'gpiopin': {
    'sourceipaddress': {
        'description': 'The IP address of the Modbus TCP data source',
        'type':        'string',
        'default':     '127.0.0.1'
    }

}

_LOGGER = logger.setup(__name__)
""" Setup the access to the logging system of FogLAMP """

def plugin_info():
    """ Returns information about the plugin.

    Args:
    Returns:
        dict: plugin information
    Raises:
    """

    return {
        'name':      'Modbus TCP',
        'version':   '1.0',
        'mode':      'poll',
        'type':      'south',
        'interface': '1.0',
        'config':    _DEFAULT_CONFIG
    }


def plugin_init(config):
    """ Initialise the plugin.

    Args:
        config: JSON configuration document for the device configuration category
    Returns:
        handle: JSON object to be used in future calls to the plugin
    Raises:
    """

    #handle = config['gpiopin']['value']
    # handle = config['sourceipaddress']['value']
    return copy.deepcopy(config)


def plugin_poll(handle):
    """ Extracts data from the sensor and returns it in a JSON document as a Python dict.

    Available for poll mode only.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
        returns a sensor reading in a JSON document, as a Python dict, if it is available
        None - If no reading is available
    Raises:
        DataRetrievalError
    """

    try:
        #humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, handle)
        # Open a new Modbus TCP client; in this case, the handle is already set to the source IP address
        client = ModbusTcpClient(handle['sourceipaddress']['value'])
        # Specify which register number to monitor and how many registers to read
        registerNumber = 0
        numberOfRegistersToRead = 1
        registerValue = (client.read_holding_registers(registerNumber, numberOfRegistersToRead, unit=1)).registers[0]
        #if humidity is not None and temperature is not None:
        if registerValue is not None:
            time_stamp = str(datetime.now(tz=timezone.utc))
            #readings =  { 'temperature': temperature , 'humidity' : humidity }
            readings =  { 'Register Value': registerValue }
            wrapper = {
                    #'asset':     'dht11',
                    'asset':     'Modbus TCP Source',
                    'timestamp': time_stamp,
                    'key':       str(uuid.uuid4()),
                    'readings':  readings
            }
            # Close the modbus client
            client.close()
            return wrapper
        else:
            return None

    except Exception as ex:
        raise exceptions.DataRetrievalError(ex)

    return None


def plugin_reconfigure(handle, new_config):
    """ Reconfigures the plugin, it should be called when the configuration of the plugin is changed during the
        operation of the device service.
        The new configuration category should be passed.

    Args:
        handle: handle returned by the plugin initialisation call
        new_config: JSON object representing the new configuration category for the category
    Returns:
        new_handle: new handle to be used in the future calls
    Raises:
    """

    #new_handle = new_config['gpiopin']['value']
    new_handle = new_config['sourceipaddress']['value']
    return new_handle


def plugin_shutdown(handle):
    """ Shutdowns the plugin doing required cleanup, to be called prior to the device service being shut down.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
    Raises:
    """
