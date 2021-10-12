import click

from ocrd.decorators import ocrd_cli_options, ocrd_cli_wrap_processor
from .doxa_binarize import DoxaBinarize

@click.command()
@ocrd_cli_options
def ocrd_doxa_binarize(*args, **kwargs):
    return ocrd_cli_wrap_processor(DoxaBinarize, *args, **kwargs)

