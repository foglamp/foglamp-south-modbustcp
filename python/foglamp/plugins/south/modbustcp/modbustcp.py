# -*- coding: utf-8 -*-

# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END

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

import copy
import uuid
import json

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

__author__ = "Dan Lopez"
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
        'default': 'modbustcp'
    },
    'pollInterval': {
        'description': 'The interval between poll calls to the device poll routine, expressed in milliseconds.',
        'type': 'integer',
        'default': '1000'
    },
    'sourceIpAddress': {
        'description': 'The IP address of the Modbus TCP data source',
        'type': 'string',
        'default': '127.0.0.1'
    },
    'sourcePort': {
        'description': 'The port of the Modbus TCP data source',
        'type': 'integer',
        'default': '502'
    },
    'entitiesMap': {
        'description': 'Modbus entities map',
        'type': 'JSON',
        'default': json.dumps({
            "coils": {},
            "discreteInputs": {},
            "holdingRegisters": {
                "temperature": 7,
                "humidity": 8
            },
            "inputRegisters": {}
        })
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
        'name': 'Modbus TCP',
        'version': '1.3.0',
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
    """ Extracts data from the modbus device and returns it in a JSON document as a Python dict.

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
                source_ip = handle['sourceIpAddress']['value']
                source_port = int(handle['sourcePort']['value'])
            except:
                raise ValueError

            mbus_client = ModbusTcpClient(host=source_ip, port=source_port)
            _LOGGER.info('Modbus TCP started on IP %s', source_ip)

        """ 
        read_coils(self, address, count=1, **kwargs)  
        read_discrete_inputs(self, address, count=1, **kwargs)
        read_holding_registers(self, address, count=1, **kwargs)
        read_input_registers(self, address, count=1, **kwargs)

            - address: The starting address to read from
            - count: The number of coils / discrete or registers to read
            - unit: The slave unit this request is targeting

            On TCP/IP, the MODBUS server is addressed using its IP address; therefore, the MODBUS Unit Identifier is useless. 
            The value 0xFF has to be used. When addressing a MODBUS server connected directly to a TCP/IP network, it’s 
            recommended not using a significant MODBUS slave address in the "Unit Identifier" field.  
            In the event of a re-allocation of the IP addresses within an automated system and if a IP address previously
            assigned to a MODBUS server is then assigned to a gateway, using a significant slave address may cause trouble
            because of a bad routing by the gateway. Using a non-significant slave address, the gateway will simply discard
            the MODBUS PDU with no trouble. 0xFF is recommended for the "Unit Identifier" as non-significant value. 

            Remark : The value 0 is also accepted to communicate directly to a MODBUS TCP device.

        """
        unit_id = 0
        modbus_map = json.loads(handle['entitiesMap']['value'])
        readings = {}

        # Read coils
        coils_address_info = modbus_map['coils']
        number_of_coils_to_read = 1
        if len(coils_address_info) > 0:
            for k, address in coils_address_info.items():
                coil = mbus_client.read_coils(address, number_of_coils_to_read, unit_id)
                readings.update(coil.registers[0])

        # Discrete input
        discrete_input_info = modbus_map['discreteInputs']
        number_of_registers_to_read = 1
        if len(discrete_input_info) > 0:
            for k, address in discrete_input_info.items():
                read_discrete_inputs = mbus_client.read_discrete_inputs(address, number_of_registers_to_read, unit_id)
                readings.update(read_discrete_inputs.registers[0])

        # Holding registers
        holding_registers_info = modbus_map['holdingRegisters']
        number_of_holding_registers_to_read = 1
        if len(holding_registers_info) > 0:
            for k, address in holding_registers_info.items():
                register_values = mbus_client.read_holding_registers(address, number_of_holding_registers_to_read, unit_id)
                readings.update(register_values.registers[0])

        # Read input registers
        input_registers_info = modbus_map['inputRegisters']
        number_of_input_registers_to_read = 1
        if len(input_registers_info) > 0:
            for k, address in input_registers_info.items():
                read_input_reg = mbus_client.read_input_registers(address, number_of_input_registers_to_read, unit_id)
                readings.update(read_input_reg.registers[0])

        if len(readings) > 0:
            wrapper = {
                'asset': 'Modbus TCP',
                'timestamp': utils.local_timestamp(),
                'key': str(uuid.uuid4()),
                'readings': readings
            }

    except Exception as ex:
        raise exceptions.DataRetrievalError(ex)
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

    if 'sourceIpAddress' in diff or 'sourcePort' in diff or 'management_host' in diff:
        plugin_shutdown(handle)
        new_handle = plugin_init(new_config)
        new_handle['restart'] = 'yes'
        _LOGGER.info("Restarting  Modbus TCP plugin due to change in configuration keys [{}]".format(', '.join(diff)))
    else:
        new_handle = copy.deepcopy(handle)
        new_handle['restart'] = 'no'

    return new_handle


def _plugin_stop(handle):
    """ Stops the plugin doing required cleanup

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
    Raises:
    """
    _LOGGER.info('Stopping Modbus TCP plugin...')
    try:
        global mbus_client
        if mbus_client is not None:
            mbus_client.close()
    except Exception as ex:
        _LOGGER.exception('Error in shutting down Modbus TCP plugin; %s', ex)
        raise


def plugin_shutdown(handle):
    """ Shutdowns the plugin doing required cleanup

    To be called prior to the south service being shut down.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
    """
    _plugin_stop(handle)
    _LOGGER.info('Modbus TCP plugin shut down.')
