import click

from giteapy.data import Data


@click.group()
@click.version_option()
def cli():
    '''
    Manage organizations and teams in Gitea
    '''


@cli.command()
@click.option('--file', '-f', type=click.Path(exists=True), help='giteapy config file to manage')
def run(file):
    '''Manage orgs and teams in Gitea
    '''
    if file:
        d = Data(file)
        click.echo('=> Running...')
        d.process()
