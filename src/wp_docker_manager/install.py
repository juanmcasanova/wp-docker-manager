import os
import shutil

import docker


def install_environment():
    # This should get "check" results to ensure we recreate anything that don't 100% comply
    # with our requirements (and so it doesn't file when some things exist but other don't)
    docker_client = docker.from_env()

    shutil.copyfile(f'{os.path.dirname(os.path.abspath(__file__))}/resources/haproxy.cfg', '/opt/wp-docker-manager/haproxy.cfg')

    docker_client.networks.list()
    docker_client.networks.create('wpdm-services')
    docker_client.networks.create('wpdm-proxy')

    docker_client.containers.run(
        image='haproxy:3.4-alpine',
        detach=True,
        name='wpdm-haproxy',
        volumes=['/opt/wp-docker-manager/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro'],
        ports={'80/tcp': 80},
        restart_policy={"Name": 'always'},
        network='wpdm-proxy'
    )
    docker_client.containers.run(
        image='mariadb:13.0',
        detach=True,
        name='wpdm-mariadb',
        volumes=['/opt/wp-docker-manager/mariadb:/var/lib/mysql:Z'],
        ports={'3306/tcp': 3306},
        restart_policy={"Name": 'always'},
        network='wpdm-services',
        # TODO: Obviously, change this!
        environment={'MARIADB_ROOT_PASSWORD': 'root'}
    )
