"""
Luna Command Line Interface (CLI).

Primarily used to add new h5ad data to the database.
"""
import logging
import click
import emoji
from configparser import ConfigParser
from luna.h5ad.h5ad_persist import H5adDb
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
def add_h5ad(config_file_name):
    """Add a new h5ad file to the database."""
    output_header("Adding data from config file:  %s." % config_file_name)
    cfg = ConfigParser()
    cfg.read(config_file_name)
    h5ad_file_name = cfg.get("h5ad", "file_name")
    h5ad_description = cfg.get("h5ad", "description")
    h5ad_url = cfg.get("h5ad", "url")

    if cfg.has_section("genes"):
        gene_list = cfg.get("genes", "gene_list", fallback=None)
        gene_list = [x.strip() for x in gene_list.split(",")]
        click.echo("Importing %d genes." % len(gene_list))
    else:
        gene_list = []
        click.echo("Importing all genes.")

    h5ad = H5adDb(h5ad_file_name, h5ad_description, h5ad_url, gene_list)
    h5ad.persist_to_database()
    output_header(emoji.emojize("Done! :beer:", use_aliases=True))


@cli.command()
@click.argument("config_file_name", type=click.Path(exists=True))
@click.argument("output_file_name", type=click.Path())
@click.option("--num_cells", type=click.INT, default=100, help="N cells.")
def downsample_h5ad(config_file_name, output_file_name, num_cells):
    """Downsample an h5ad file."""
    output_header("Using config file:  %s." % config_file_name)
    cfg = ConfigParser()
    cfg.read(config_file_name)
    h5ad_file_name = cfg.get("h5ad", "file_name")
    output_header("Downsampling file:  %s." % h5ad_file_name)
    gene_list = [x.strip() for x in cfg.get("genes", "gene_list").split(",")]

    down_sampler = H5adDownSample(h5ad_file_name, num_cells, gene_list)
    down_sampler.save(output_file_name)
    output_header("Writing new data to:  %s." % output_file_name)
    output_header(emoji.emojize("Done! :beer:", use_aliases=True))


@cli.command()
def reset_db():
    """Reset the database."""
    output_header("Resetting database to a clean slate.")
    db_connection = DbConnection()
    db_connection.reset_database()
    output_header(emoji.emojize("Done! :beer:", use_aliases=True))


def output_header(msg):
    """Output header with emphasis."""
    click.echo(click.style(msg, fg="green"))
