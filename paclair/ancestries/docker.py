# -*- coding: utf-8 -*-
from paclair.ancestries.generic import GenericAncestry, Layer


class DockerAncestry(GenericAncestry):
    """
    Construct an ancestry from a docker image
    """

    def __init__(self, name, docker_image):
        """
        Constructor

        :param name: image name
        :param docker_image:  docker image
        """
        super().__init__("Docker", name)

        # headers
        headers ={'Authorization': "Bearer {}".format(docker_image.token)}
        partial_path = docker_image.registry.get_blobs_url(docker_image, '{digest}')

        # Create layers
        parent = ""
        for layer in docker_image.get_layers():
            self.layers.append(Layer("{}_{}".format(layer, docker_image.short_sha), layer,
                                     partial_path.format(digest=layer), headers, parent))
            parent = layer
