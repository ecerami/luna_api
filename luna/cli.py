"""
Luna Command Line Interface (CLI).

Primarily used to add new h5ad data to the database.
"""
import logging
from luna.config.luna_config import LunaConfig
import click
import emoji
from sqlalchemy import exc
from jsonschema.exceptions import ValidationError
from luna.h5ad.h5ad_persist import H5adDb
from luna.vignette.vignette_validator import VignetteValidator
from luna.vignette.vignette_persist import VignetteDb
from luna.h5ad.h5ad_downsample import H5adDownSample
from luna.db.db_util import DbConnection


@click.group()
@click.option("--verbose", is_flag=True, help="Enable verbose mode")
def cli(verbose):
    """Run luna."""
    log_level = logging.FATAL
    if verbose:
        log_level = logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s:%(message)s")


@cli.command()
@click.argument("config_file_name", type=click.Path(exists=True))
def add(config_file_name):
    """Add a new h5ad file to the database."""
    output_header(f"Adding data from config file:  {config_file_name}.")
    luna_config = LunaConfig(config_file_name)

    h5ad = H5adDb(
        luna_config.h5ad_file_name,
        luna_config.h5ad_description,
        luna_config.h5ad_url,
        luna_config.gene_list,
    )
    try:
        h5ad.persist_to_database()
        output_header(emoji.emojize("Done! :beer:", use_aliases=True))
    except exc.IntegrityError as error:
        output_error(f"Cannot add file:  {error.__str__}")

@cli.command()
@click.argument("vignette_file_name", type=click.Path(exists=True))
def add_vignettes(vignette_file_name):
    """Add a new set of vignettes to the database."""
    output_header(f"Adding vignettes file:  {vignette_file_name}.")
    vignette_validator = VignetteValidator(vignette_file_name)
    try:
        vignette_validator.validate()
        vignette_db = VignetteDb(vignette_file_name)
        vignette_db.persist_to_database()
        output_header(emoji.emojize("Done! :beer:", use_aliases=True))
    except ValidationError as error:
        output_error(
            f"File:  {vignette_file_name} is invalid:  {error.message}"
        )


@cli.command()
@click.argument("config_file_name", type=click.Path(exists=True))
@click.argument("output_file_name", type=click.Path())
@click.option("--num_cells", type=click.INT, default=100, help="N cells.")
def downsample(config_file_name, output_file_name, num_cells):
    """Downsample an h5ad file."""
    output_header(f"Using config file:  {config_file_name}.")
    luna_config = LunaConfig(config_file_name)

    down_sampler = H5adDownSample(
        luna_config.h5ad_file_name, num_cells, luna_config.gene_list
    )
    down_sampler.save(output_file_name)
    output_header(f"Writing new data to:  {output_file_name}.")
    output_header(emoji.emojize("Done! :beer:", use_aliases=True))


@cli.command()
def reset():
    """Reset the database."""
    output_header("Resetting database to a clean slate.")
    db_connection = DbConnection()
    db_connection.reset_database()
    output_header(emoji.emojize("Done! :beer:", use_aliases=True))


def output_header(msg):
    """Output header with emphasis."""
    click.echo(click.style(msg, fg="green"))


def output_error(msg):
    """Output error message with emphasis."""
    msg = emoji.emojize(f":warning:  {msg}", use_aliases=True)
    click.echo(click.style(msg, fg="yellow"))
