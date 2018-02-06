# Paclair

Paclair is a Python3 Cli tool to interact with Coreos's Clair (https://github.com/coreos/clair).

Features:
  - No need to have docker installed since Paclair interacts directly with the registries.
  - Compatible with all registries.
  - Simple to use.
  - Easy integration in a CI job thanks to a lightweight output mode.

## Getting Started

### Prerequisites

All requirements are specified in requirements.txt

```
pip install -r requirements.txt
```

### Installing

```
python setup.py install
```

### Configuration

An example configuration file is available in the conf directory

```
General:
  clair_url: 'https://localhost:6060'
  verify: "/etc/ssl/certs/my_custom_ca.crt"
Plugins:
  Docker:
    class: paclair.plugin.docker_plugin.DockerPlugin
    registries:
      registry.gitlab.domain.com:
        auth:
          - "*****"
          - "*****"
        verify: "/etc/ssl/certs/ca-certificates.crt"
```

Plugins are dynamically loaded during execution. That's why you have to specify the class of the plugins you want to use.

We have various plugins to interact with different sources (ex: docker registry, Elasticsearch) because we use a custom variant of Clair which can analyse more than Docker images.

If you want to use Paclair only to analyse docker images, don't bother with others plugins.

Config Option | Description |
|---|---|
| General::clair_url | url of the Clair Server
| General::verify | Either a boolean, in which case it controls whether we verify the server's TLS certificate, or a string, in which case it must be a path to a CA bundle to use. 
| Plugins | List of plugins to use. If you only want to analyse docker images, keep the default configuration | 
| Plugins::Docker::class | Class for the docker plugin |
| Plugins::Docker::registries | You can specify configuration for registries (authentification, ...) if needed|
| Plugins::Docker::registries::registry1::auth | login/password |
| Plugins::Docker::registries::registry1::verify | Either a boolean, in which case it controls whether we verify the server's TLS certificate, or a string, in which case it must be a path to a CA bundle to use. |
| Plugins::Docker::registries::registry1::protocol | Protocol to use (http or https). Default to https |

## Running the tests

```
nosetests -v paclair_tests/
```


## Usage

```
paclair --help
usage: main.py [-h] [--debug] [--syslog] [--conf CONF]
               plugin hosts [hosts ...] {push,analyse} ...

positional arguments:
  plugin          Plugin to launch
  hosts           Image/hostname to analyse
  {push,analyse}  Command to launch
    push          Push images/hosts to Clair
    analyse       Analyse images/hosts already pushed to Clair

optional arguments:
  -h, --help      show this help message and exit
  --debug         Debug mode
  --syslog        Log to syslog
  --conf CONF     Conf file

```

### Example

Push ubuntu image to Clair

```
paclair --conf conf/conf.yml Docker ubuntu push
Pushed ubuntu to Clair.
```

Analyse ubuntu image

```
paclair --conf conf/conf.yml Docker ubuntu analyse --statistics
Medium: 3
```

You can have the full json if you don't specify --statistics

## Contributing

Feel free to contribute.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Yebinama** - *Initial work* - [Yebinama](https://github.com/yebinama)

