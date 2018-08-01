=======================
foglamp-south-modbustcp
=======================

FogLAMP South Plugin for Modbus TCP


Installation
============


Create Debian Package
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    $ ./make_deb help
    make_deb help [clean|cleanall]
    This script is used to create the Debian package of foglamp modbustcp

    Arguments:
     help     - Display this help text
     clean    - Remove all the old versions saved in format .XXXX
     cleanall - Remove all the versions, including the last one

``./make_deb`` will create the debian package inside ``packages/build/``.


Install Debian Package
~~~~~~~~~~~~~~~~~~~~~~

Make sure FogLAMP is installed and running.

.. code-block:: console

  $ sudo systemctl status foglamp.service


Once you have created the debian package, install it using the ``apt`` command. Move the package to the apt cache directory
i.e. ``/var/cache/apt/archives``.

.. code-block:: console

  $ sudo cp foglamp-south-modbustcp-1.3.0.deb /var/cache/apt/archives/.
  $ sudo apt install /var/cache/apt/archives/foglamp-south-modbustcp-1.3.0.deb


Check the newly installed package:

.. code-block:: console

  $ sudo dpkg -l | grep foglamp-south-modbustcp
  ii  foglamp-south-modbustcp    1.3.0    all    South plugin for the modbustcp


Check foglamp service status for foglamp-south-modbustcp, it should list it as a south service:

.. code-block:: console

  $ sudo systemctl status foglamp.service
  ...
  ...
  CGroup: /system.slice/foglamp.service
           |- ....
           ├─/bin/sh services/south --port= --address=127.0.0.1 --name=Modbus TCP
           └─python3 -m foglamp.services.south --port= --address=127.0.0.1 --name=Modbus TCP
