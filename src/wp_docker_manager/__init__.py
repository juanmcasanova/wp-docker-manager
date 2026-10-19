import click

from wp_docker_manager.check import check_environment
from wp_docker_manager.install import install_environment


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
    check_environment()

@main.command('install')
def install() -> None:
    """
    Configures everything missing to ensure the environment is right.
    """
    install_environment()

if __name__ == '__main__':
    main()
