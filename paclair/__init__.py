import os

REGEX = {
    'domain': r'(?:(?P<domain>(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])(?:(?:\.(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]))+)?(?::[0-9]+)?)/)?',
    'name': r'(?P<name>[a-z0-9]+(?:(?:(?:[._]|__|[-]*)[a-z0-9]+)+)?(?:(?:/[a-z0-9]+(?:(?:(?:[._]|__|[-]*)[a-z0-9]+)+)?)+)?)',
    'tag': r'(:(?P<tag>[\w][\w.-]{0,127}))?'
}

DOCKER_HUB_TOKEN_REQUEST = \
    "https://auth.docker.io/token?client_id=paclair&service=registry.docker.io&scope=repository:{image.name}:pull"
DOCKER_HUB_DOMAIN = "registry.hub.docker.com"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
