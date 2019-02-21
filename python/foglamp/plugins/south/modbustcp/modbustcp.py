# -*- coding: utf-8 -*-

# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END


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


import copy
import uuid
import json
import logging

from pymodbus3.client.sync import ModbusTcpClient

from foglamp.common import logger
from foglamp.plugins.common import utils
from foglamp.services.south import exceptions

""" Plugin for reading data from a Modbus TCP data source

    This plugin uses the pymodbus3 library, to install this perform the following steps:

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

__author__ = "Dan Lopez, Praveen Garg"
__copyright__ = "Copyright (c) 2018 OSIsoft, LLC"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"


""" _DEFAULT_CONFIG with Modbus Entities Map

    The coils and registers each have a read-only table and read-write table.

        Coil	Read-write	1 bit
        Discrete input	Read-only	1 bit
        Input register	Read-only	16 bits
        Holding register	Read-write	16 bits 
"""

_DEFAULT_CONFIG = {
    'plugin': {
        'description': 'Modbus TCP South Service Plugin',
        'type': 'string',
        'default': 'modbustcp',
        'readonly': 'true'
    },
    'assetName': {
        'description': 'Asset name',
        'type': 'string',
        'default': 'Modbus TCP',
        'order': "1",
        'displayName': 'Asset Name'
    },
    'address': {
        'description': 'Address of Modbus TCP server',
        'type': 'string',
        'default': '127.0.0.1',
        'order': '3',
        'displayName': 'TCP Server Address'
    },
    'port': {
        'description': 'Port of Modbus TCP server',
        'type': 'integer',
        'default': '502',
        'order': '4',
        'displayName': 'Port'
    },
    'map': {
        'description': 'Modbus register map',
        'type': 'JSON',
        'default': json.dumps({
            "coils": {},
            "inputs": {},
            "registers": {
                "temperature": 7,
                "humidity": 8
            },
            "inputRegisters": {}
        }),
        'order': '5',
        'displayName': 'Register Map'
    }
}


_LOGGER = logger.setup(__name__, level=logging.INFO)
""" Setup the access to the logging system of FogLAMP """

UNIT = 0x0
"""  The slave unit this request is targeting """

mbus_client = None


def plugin_info():
    """ Returns information about the plugin.

    Args:
    Returns:
        dict: plugin information
    Raises:
    """

    return {
        'name': 'Modbus TCP',
        'version': '1.5.0',
        'mode': 'poll',
        'type': 'south',
        'interface': '1.0',
        'config': _DEFAULT_CONFIG
    }


def plugin_init(config):
    """ Initialise the plugin.

    Args:
        config: JSON configuration document for the plugin configuration category
    Returns:
        handle: JSON object to be used in future calls to the plugin
    Raises:
    """
    return copy.deepcopy(config)


def plugin_poll(handle):
    """ Poll readings from the modbus device and returns it in a JSON document as a Python dict.

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
            try:
                source_address = handle['address']['value']
                source_port = int(handle['port']['value'])
            except Exception as ex:
                e_msg = 'Failed to parse Modbus TCP address and / or port configuration.'
                _LOGGER.error('%s %s', e_msg, str(ex))
                raise ValueError(e_msg)
            try:
                mbus_client = ModbusTcpClient(host=source_address, port=source_port)
            except Exception as ex:
                _LOGGER.warn('Failed to connect! Modbus TCP host %s on port %d', source_address, source_port)
                return ex
            else:
                _LOGGER.info('Modbus TCP Client is connected: %s, %s:%d', mbus_client.connect(), source_address, source_port)

        """ 
        read_coils(self, address, count=1, **kwargs)  
        read_discrete_inputs(self, address, count=1, **kwargs)
        read_holding_registers(self, address, count=1, **kwargs)
        read_input_registers(self, address, count=1, **kwargs)
        
            - address: The starting address to read from
            - count: The number of coils / discrete or registers to read
            - unit: The slave unit this request is targeting
            
            On TCP/IP, the MODBUS server is addressed using its IP address; therefore, the MODBUS Unit Identifier is useless. 

            Remark : The value 0 is also accepted to communicate directly to a MODBUS TCP device.
        """
        unit_id = UNIT
        modbus_map = json.loads(handle['map']['value'])

        readings = {}

        # Read coils
        coils_address_info = modbus_map['coils']

        if len(coils_address_info) > 0:
            for k, address in coils_address_info.items():
                coil_bit_values = mbus_client.read_coils(99 + int(address), 1, unit=unit_id)
                readings.update({k: coil_bit_values.bits[0]})

        # Discrete input
        discrete_input_info = modbus_map['inputs']

        if len(discrete_input_info) > 0:
            for k, address in discrete_input_info.items():
                read_discrete_inputs = mbus_client.read_discrete_inputs(99 + int(address), 1, unit=unit_id)
                readings.update({k:  read_discrete_inputs.bits[0]})

        # Holding registers
        holding_registers_info = modbus_map['registers']

        if len(holding_registers_info) > 0:
            for k, address in holding_registers_info.items():
                register_values = mbus_client.read_holding_registers(99 + int(address), 1, unit=unit_id)
                readings.update({k: register_values.registers[0]})

        # Read input registers
        input_registers_info = modbus_map['inputRegisters']

        if len(input_registers_info) > 0:
            for k, address in input_registers_info.items():
                read_input_reg = mbus_client.read_input_registers(99 + int(address), 1, unit=unit_id)
                readings.update({k: read_input_reg.registers[0] })

        wrapper = {
            'asset': handle['assetName']['value'],
            'timestamp': utils.local_timestamp(),
            'key': str(uuid.uuid4()),
            'readings': readings
        }

    except Exception as ex:
        _LOGGER.error('Failed to read data from modbus device. Got error %s', str(ex))
        raise ex
    else:
        return wrapper


def plugin_reconfigure(handle, new_config):
    """ Reconfigures the plugin

    it should be called when the configuration of the plugin is changed during the operation of the south service.
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

    if 'address' in diff or 'port' in diff:
        plugin_shutdown(handle)
        new_handle = plugin_init(new_config)
        _LOGGER.info("Restarting Modbus TCP plugin due to change in configuration keys [{}]".format(', '.join(diff)))
    else:
        new_handle = copy.deepcopy(new_config)

    return new_handle


def plugin_shutdown(handle):
    """ Shutdowns the plugin doing required cleanup

    To be called prior to the south service being shut down.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
    Raises:
    """
    global mbus_client
    try:
        if mbus_client is not None:
            mbus_client.close()
            _LOGGER.info('Modbus TCP client connection closed.')
    except Exception as ex:
        _LOGGER.exception('Error in shutting down Modbus TCP plugin; %s', str(ex))
        raise ex
    else:
        mbus_client = None
        _LOGGER.info('Modbus TCP plugin shut down.')
