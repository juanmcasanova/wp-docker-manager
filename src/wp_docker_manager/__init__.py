import os
import shutil

import click
import docker


@click.group()
def main() -> None:
    """
    CLI application to manage WordPress instances in a shared Docker environment
    """

@main.command('check')
def check() -> None:
    """
    Checks the current environment to ensure everything is right.
    """
    # TODO: All errors should be displayed at the same time, not one at a time
    docker_client = docker.from_env()

    # Get Docker version (minimal check to ensure Docker is installed and reachable)
    click.echo(f'Docker version: {docker_client.version()['Version']}')

    # Check if both networks exist
    missing_networks = ['wpdm-services', 'wpdm-proxy']
    for network in docker_client.networks.list(names=missing_networks):
        if network.name in missing_networks:
            missing_networks.pop(missing_networks.index(network.name))
    if missing_networks:
        click.echo(click.style(f'The following networks weren\'t found: {missing_networks}. Run `wp-docker-manager install` to create them.', fg='yellow'))
        click.get_current_context().exit(1)

    # Check if the HAProxy configuration file exists
    if not os.path.isfile('/opt/wp-docker-manager/haproxy.cfg'):
        click.echo(click.style('No HAProxy configuration file was found, run `wp-docker-manager install` to create it.', fg='yellow'))
        click.get_current_context().exit(1)

    # Get a list of available containers to know if we already have everything configured
    missing_containers=['wpdm-haproxy', 'wpdm-mariadb']
    for container in docker_client.containers.list(filters={'name': missing_containers}, all=True):
        if container.name in missing_containers:
            missing_containers.pop(missing_containers.index(container.name))
    if missing_containers:
        click.echo(click.style(f'The following containers weren\'t found: {missing_containers}. Run `wp-docker-manager install` to create them.', fg='yellow'))
        click.get_current_context().exit(1)

    click.echo(click.style('Everything seems right!', fg='green'))

@main.command('install')
def install() -> None:
    """
    Configures everything missing to ensure the environment is right.
    """
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

if __name__ == '__main__':
    main()
