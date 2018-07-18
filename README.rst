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
    make_deb {arm|x86} [clean|cleanall]
    This script is used to create the Debian package of foglamp modbustcp

    Arguments:
     arm      - Build an armv7l package
     x86      - Build an x86_64 package
     clean    - Remove all the old versions saved in format .XXXX
     cleanall - Remove all the versions, including the last one

``./make_deb arm`` will create the debian package inside ``packages/Debian/build/``.


Install Debian Package
~~~~~~~~~~~~~~~~~~~~~~

Make sure FogLAMP is installed and running.

.. code-block:: console

  $ sudo systemctl status foglamp.service


Once you have created the debian package, install it using the ``apt`` command. Move the package to the apt cache directory
i.e. ``/var/cache/apt/archives``.

.. code-block:: console

  $ sudo cp foglamp-south-modbustcp-1.3.0-armhf.deb /var/cache/apt/archives/.
  $ sudo apt install /var/cache/apt/archives/foglamp-south-modbustcp-1.3.0-armhf.deb


Check the newly installed package:

.. code-block:: console

  $ sudo dpkg -l | grep foglamp-south-modbustcp


Check foglamp service status for foglamp-south-modbustcp, it should list it as a south service:

.. code-block:: console

  $ sudo systemctl status foglamp.service
  ...
  ...
  CGroup: /system.slice/foglamp.service
           |- ....
           └─python3 -m foglamp.services.south --port=43927 --address=127.0.0.1 --name=modbustcp

