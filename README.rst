Paclair
=======

Paclair is a Python3 Cli tool to interact with `Coreos's Clair <https://github.com/coreos/clair>`_.

Features:

- Now compatible with Clair V3 (delete is not available)
- No need to have docker installed since Paclair interacts directly with the registries.
- Compatible with all registries.
- Simple to use.
- Easy integration in a CI job thanks to a lightweight output mode.

Installation
------------

To install Paclair, simply use `pip` (or pipenv):

.. code-block:: bash

    $ pip install paclair
    ✨🍰✨

Voilà!

Configuration
-------------

Example
~~~~~~~

An example configuration file is available in the conf directory

::

  General:
    clair_url: 'https://localhost:6060'
    # clair_api_version: 3
    # Whitelist known CVE's not to shown in html report
    # cve_whitelist:
    #   - CVE-2016-9843
    #   - CVE-2016-9840
    #   - CVE-2016-6313
  Plugins:
    Docker:
      class: paclair.plugins.docker_plugin.DockerPlugin
      registries:
        artifactory.registry.com:
          token_url: "https://artifactory.registry.com/api/docker/{image.repository}/v2/token?service=artifactory.registry.com"
          protocol: 'http'
          api_prefix: '/api/docker/{image.repository}'
        registry.gitlab.domain.com:
          auth:
            - "*****"
            - "*****"
        # Example for a private gitlab server
        gitlab.example.com:4567:
          # If using https with an internal CA, ensure verify is pointing to it
          protocol: 'https'
          verify: "/etc/ssl/certs/ca-certificates.crt"
          auth:
            - "*****"
            - "*****"
        # Example for ECR Docker Repository
        xxxxxxxxxxxxxxxx.dkr.ecr.eu-west-1.amazonaws.com:
          token: "" # Execute this command to get token aws ecr get-authorization-token --output text --query 'authorizationData[].authorizationToken'
          protocol: 'https'
          token_type: Basic

Plugins are dynamically loaded during execution. That's why you have to specify the class of the
plugins you want to use.

We have various plugins to interact with different sources (ex: docker registry, Elasticsearch)
because we use a custom variant of Clair which can analyse more than Docker images.

If you want to use Paclair only to analyse docker images, don't bother with others plugins.

Options
~~~~~~~

+-----------------------------------+-----------------------------------+
| Config Option                     | Description                       |
+===================================+===================================+
| General::clair_url                | url of the Clair Server.          |
+-----------------------------------+-----------------------------------+
| General::verify                   | Either a boolean, in which case   |
|                                   | it controls whether we verify the |
|                                   | server’s TLS certificate, or a    |
|                                   | string, in which case it must be  |
|                                   | a path to a CA bundle to use.     |
+-----------------------------------+-----------------------------------+
| General::clair_api_version        | Clair Api Version.                |
|                                   | If different from 3, will be set  |
|                                   | to default.                       |
|                                   | Default to 1.                     |
+-----------------------------------+-----------------------------------+
| General::html_template            | Html template.                    |
|                                   | You can use a custom html template|
|                                   | when using html output.           |
+-----------------------------------+-----------------------------------+
| General::cve_whitelist            | CVE vulnerability list not to be  |
|                                   | included in the report post       |
|                                   | analysis (stats or html).         |
+-----------------------------------+-----------------------------------+
| Plugins                           | List of plugins to use. If you    |
|                                   | only want to analyse docker       |
|                                   | images, keep the default          |
|                                   | configuration.                    |
+-----------------------------------+-----------------------------------+
| Plugins::Docker::class            | Class for the docker plugin       |
+-----------------------------------+-----------------------------------+
| Plugins::Docker::registries       | You can specify configuration for |
|                                   | registries (authentification, …)  |
|                                   | if needed.                        |
+-----------------------------------+-----------------------------------+
| Plugins::Docker::registries::regi | login/password                    |
| stry1::auth                       |                                   |
+-----------------------------------+-----------------------------------+
| Plugins::Docker::registries::regi | Either a boolean, in which case   |
| stry1::verify                     | it controls whether we verify the |
|                                   | server’s TLS certificate, or a    |
|                                   | string, in which case it must be  |
|                                   | a path to a CA bundle to use.     |
+-----------------------------------+-----------------------------------+
| Plugins::Docker::registries::regi | Protocol to use (http or https).  |
| stry1::protocol                   | Default to https.                 |
+-----------------------------------+-----------------------------------+
| Plugins::Docker::registries::token| You can specify an authentication |
|                                   | token (use with token_type).      |
|                                   | Default to None.                  |
+-----------------------------------+-----------------------------------+
| Plugins::Docker::registries::token| Specify the token type.           |
| _type                             | Default to Bearer.                |
+-----------------------------------+-----------------------------------+

Running the tests
-----------------

Launch tox.

.. code-block:: bash

    $ tox

Usage
-----

.. code-block:: bash

    usage: paclair [-h] [--debug] [--syslog] [--conf CONF]
                   plugin hosts [hosts ...] {push,delete,analyse} ...

    positional arguments:
      plugin                Plugin to launch
      hosts                 Image/hostname to analyse
      {push,delete,analyse}
                            Command to launch
        push                Push images/hosts to Clair
        delete              Delete images/hosts from Clair
        analyse             Analyse images/hosts already pushed to Clair

    optional arguments:
      -h, --help            show this help message and exit
      --debug               Debug mode
      --syslog              Log to syslog
      --conf CONF           Conf file

Analyse command usage
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    usage: paclair plugin hosts [hosts ...] analyse [-h]
                                                [--output-format {stats,html}]
                                                [--output-report {file,term}]
                                                [--output-dir OUTPUT_DIR]
                                                [--delete]

    optional arguments:
      -h, --help            show this help message and exit
      --output-format {stats,html}
                            Change default output format (default: json)
      --output-report {file,term}
                            Change report location (default: logger)
      --output-dir OUTPUT_DIR
                            Change output directory (default: current)
      --delete              Delete after analyse

Examples
~~~~~~~~

Push ubuntu image to Clair

.. code-block:: bash

    $ paclair --conf conf/conf.yml Docker ubuntu push
    Pushed ubuntu to Clair.

Analyse ubuntu image (stats only show fixable CVE)

.. code-block:: bash

    $ paclair --conf conf/conf.yml Docker ubuntu analyse --output-format stats
    Medium: 3

You can have the full json if you don't specify --output-format stats.


Analyse ubuntu image and get a html report in directory /tmp

.. code-block:: bash

    $ paclair --conf conf/conf.yml Docker ubuntu analyse --output-format html --output-dir /tmp

Delete ubuntu image

.. code-block:: bash

    $ paclair --conf conf/conf.yml Docker ubuntu delete
    ubuntu was deleted from Clair.

Contributing
------------

Feel free to contribute.

Authors
-------

-  **Yebinama** - *Initial work* - `Yebinama <https://github.com/yebinama>`__
