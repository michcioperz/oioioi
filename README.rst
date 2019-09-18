======
OIOIOI
======

SIO2 is a free platform for carrying out algorithmic contests and OIOIOI is its
main component — the web interface.

Installation
------------

Vagrant (for development)
~~~~~~~~~~~~~~~~~~~~~~~~~

You can easily start development and run oioioi out of the box with `vagrant`_.
Just enter the directory where Vagrantfile and this README are placed, and type::

  vagrant up

It will create an instance of virtual machine with web server and judges running.

You can specify configuration in `vagrant.yml` (if you don't have such file,
create it in the same directory as Vagrantfile).
Supported configuration options (with example)::

  port: 8001  # run oioioi on port 8001 instead of the default 8000
  runserver_cmd: runserver_plus  # use manage.py runserver_plus instead of manage.py runserver

.. _vagrant: https://www.vagrantup.com/docs/

Don't forget to create the superuser. In order to do so,
you should login into virtual machine created by Vagrant (default password is "vagrant")::

  ssh 127.0.0.1 -p 2222 -l vagrant

and run::

  cd deployment
  python manage.py createsuperuser

Docker (for deployment)
~~~~~~~~~~~~~~~~~~~~~~~

Additionally, there are available docker files to create images containing our services. We do not recommend this method of running OIOIOI. Please inspect Docker files and startup scripts before using in production.

To run the infrastructure simply::

  docker-compose up

Make sure to change default superuser password. To do that:
   1. Login to the superuser with default credentials (username:admin, password:admin)
   2. Click username ("admin") in upper-right corner of the webpage.
   3. Click "Change password"
   4. Fill and submit password change form

To start additional number of workers::

  docker-compose scale worker=<number>

as described `in Docker docs`_.

.. _in Docker docs: https://docs.docker.com/compose/reference/scale/

Docker (for development)
~~~~~~~~~~~~~~~~~~~~~~~

It is possible to develop using docker images, but this we do not recommend it.
Better use Vagrant or install OIOIOI manually, as described in the next section.

Working directory should be the repository root.

First prepare the image with::

    OIOIOI_UID=$(id -u) docker-compose -f docker-compose-dev.yml build

Create config files and logs folder on host::

    id=$(docker create oioioi-dev)  #Create oioioi container
    docker cp $id:/sio2/logs logs  #Copy initial logs folder from oioioi container
    docker cp $id:/sio2/deployment deployment  #Copy initial deployment config from oioioi contanier
    docker rm -v $id  #Remove unneeded container

Then you can start oioioi with::

    OIOIOI_UID=$(id -u) docker-compose -f docker-compose-dev.yml up

to start the infrastructure in development mode. Current dirrectory with source
code will be binded to /sio2/oioioi/ inside running container, and logs from
services will be availible outside of the container in ./logs/.

In both cases, oioioi web interface will be availible at localhost:8000, and the user
admin with password admin will be created. If you are using docker installation
in production encvironment remember to change the password.

Manual installation
~~~~~~~~~~~~~~~~~~~

See `INSTALL`_ for instructions.

.. _INSTALL: INSTALL.rst

Upgrading
---------

See `UPGRADING`_ for instructions.

.. _UPGRADING: UPGRADING.rst

For developers
--------------

Documentation for developers:

* `Developer's Guide`_
* `Developer's Reference`_

.. _Developer's Guide: https://sio2project.mimuw.edu.pl/display/DOC/SIO2+Developer%27s+Guide
.. _Developer's Reference: http://oioioi.readthedocs.io/en/latest/

Testing
-------

OIOIOI has a big suite of unit tests. You can run them in following way:

* ``test.sh`` - a simple test runner, use from virtualenv
* ``test_selenium.sh`` - long selenium tests, use from virtualenv
* ``tox [path/to/module[::TestClass[::test_method]]] [-- arg1 arg2 ...]`` - runs pytest in isolated environemnt

Supported args:

* ``-n NUM`` - run tests using NUM CPUs
* ``-v`` - increase verbosity
* ``-q`` - decrease verbosity
* ``-x`` - exit after first failure
* ``-lf`` - runs only tests that failed last time
* ``--runslow`` - runs also tests marked as slow

Usage
-----

Well, we don't have a full-fledged User's Guide, but feel free to propose
what should be added here.

Creating task packages
~~~~~~~~~~~~~~~~~~~~~~

To run a contest, you obviously need some tasks. To add a task to a contest in
OIOIOI, you need to create an archive, called task package. Here are some
pointers, how it should look like:

* `example task packages`_ used by our tests,
* `a rudimentary task package format specification`_.

.. _example task packages: https://github.com/sio2project/oioioi/tree/master/oioioi/sinolpack/files
.. _a rudimentary task package format specification: http://sio2project.mimuw.edu.pl/display/DOC/Preparing+Task+Packages

Contact us
------------

Here are some useful links:

* `our mailing list`_
* `GitHub issues system`_ (English only)

.. _our mailing list: sio2-project@googlegroups.com
.. _GitHub issues system: http://github.com/sio2project/oioioi/issues
