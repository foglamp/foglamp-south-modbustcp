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

import copy
from datetime import datetime, timezone
import uuid

from pymodbus3.client.sync import ModbusTcpClient

from foglamp.common import logger
from foglamp.plugins.common import utils
from foglamp.services.south import exceptions

__author__ = "Dan Lopez"
__copyright__ = "Copyright (c) 2018 OSIsoft, LLC"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"


""" _DEFAULT_CONFIG with Modbus Entities  Map

    The coils and registers each have a read-only table and read-write table.

        Coil	Read-write	1 bit
        Discrete input	Read-only	1 bit
        Input register	Read-only	16 bits
        Holding register	Read-write	16 bits 
"""

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
    'sourceIPAddress': {
        'description': 'The IP address of the Modbus TCP data source',
        'type':        'string',
        'default':     '127.0.0.1'
    },
    'entitiesMap' : {
        'description' : 'Modbus entities map',
        'type' : 'JSON',
        'default' : {
            'coils' : {},
            'discreteInputs' : {},
            'holdingRegisters' : {
                "temperature" : 7,
                "humidity" : 8
            },
            'inputRegisters' : {}
        }
    }
}



_LOGGER = logger.setup(__name__)
""" Setup the access to the logging system of FogLAMP """

mbus_client = None

def plugin_info():
    """ Returns information about the plugin.

    Args:
    Returns:
        dict: plugin information
    Raises:
    """

    return {
        'name':      'Modbus TCP',
        'version':   '1.3.0',
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
    return copy.deepcopy(config)


def plugin_poll(handle):
    """ Extracts data from the device and returns it in a JSON document as a Python dict.

    Available for poll mode only.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
        returns a reading in a JSON document, as a Python dict, if it is available
        None - If no reading is available
    Raises:
        DataRetrievalError
    """

    try:
        global mbus_client
        if mbus_client is None:
            sourceIP = handle['sourceIPAddress']['value']
            mbus_client = ModbusTcpClient(sourceIP)
            _LOGGER.info('Modbus TCP started on IP %s', sourceIP)

        # TODO:read from the modbus coils, inputs, holding registers and input registers
        # using the API's read coils, read discrete inputs, read holding registers and read input registers
        # use modbus_map = handle['entitiesMap']['value'] dict to read

        # Specify which register number to monitor and how many registers to read
        registerNumber = 0
        numberOfRegistersToRead = 1
        registerValue = (mbus_client.read_holding_registers(registerNumber, numberOfRegistersToRead, unit=1)).registers[0]

        if registerValue is not None:
            time_stamp = str(datetime.now(tz=timezone.utc))
            readings =  {'Register Value': registerValue}
            wrapper = {
                'asset': 'Modbus TCP',
                'timestamp': time_stamp,
                'key': str(uuid.uuid4()),
                'readings': readings
            }

    except Exception as ex:
        raise exceptions.DataRetrievalError(ex)
    else:
        return wrapper


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

    _LOGGER.info("Old config for Modbus TCP plugin {} \n new config {}".format(handle, new_config))

    diff = utils.get_diff(handle, new_config)

    if 'sourceIPAddress' in diff or 'management_host' in diff:
        plugin_shutdown(handle)
        new_handle = plugin_init(new_config)
        new_handle['restart'] = 'yes'
        _LOGGER.info("Restarting  Modbus TCP plugin due to change in configuration keys [{}]".format(', '.join(diff)))
    else:
        new_handle = copy.deepcopy(handle)
        new_handle['restart'] = 'no'

    return new_handle


def plugin_shutdown(handle):
    """ Shutdowns the plugin doing required cleanup, to be called prior to the device service being shut down.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
    Raises:
    """
    try:
        global mbus_client
        if mbus_client is not None:
            mbus_client.close()
    except Exception as ex:
        _LOGGER.exception('Error in shutting down Modbus TCP plugin; %s', ex)
        raise
    else:
        _LOGGER.info('Modbus TCP plugin shut down.')
