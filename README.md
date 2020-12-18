# Luna API

Luna API for serving up single cell matrix data.

# Installation

To install the Luna API, you must install the ```luna``` Python package and set up a Postgres database.

For the python package, first make sure you are running Python 3.6 or above.

```
python --version
```

Next, it is recommended that you create a virtual environment:

```
cd luna_api
python -m venv .venv
```

To activate the virtual environment, run:

```
source .venv/bin/activate
```

You are now ready to install the package:

```
python setup.py install
```

## PostgreSQL

The Luna API requires a running instance of PostgreSQL.  You can find many tutorials on installing PostgreSQL, including this one on [installing PostgreSQL to Ubuntu](https://www.linode.com/docs/guides/how-to-install-postgresql-on-ubuntu-16-04/).

Once you have verified that your PostgresSQL server is running, you need to set a ```LUNA_DB_CONNECT``` string.  Use the following pattern:

```
postgresql+psycopg2://username:password@localhost/luna
```

For example:

```
export LUNA_DB_CONNECT=postgresql+psycopg2://postgres:XXXXXXX@localhost/luna
```

For convenience, you may want to consider adding ```LUNA_DB_CONNECT``` to your ```.bash_profile``` or ```.bashrc.```

# Command Line Usage

To run the ```luna``` command line tool, make sure you have first activated your virtual environment:

```
source .venv/bin/activate
```

Then, type:

```
luna
```

As output, you should see:

```
Usage: luna [OPTIONS] COMMAND [ARGS]...

  Run luna.

Options:
  --verbose  Enable verbose mode
  --help     Show this message and exit.

Commands:
  add-h5ad         Add a new h5ad file to the database.
  downsample-h5ad  Downsample an h5ad file.
  reset-db         Reset the database.
```

# Example Data

The examples folder includes a [mini h5ad](/examples/tabula_muris_mini.h5ad) file that you can use to test things out.  This is a downsampled version of the [CZI tabula muris data set](https://tabula-muris.ds.czbiohub.org/) that only contains data on 3 genes and 100 cells.

To download the full tabula muris data set run:

```
wget https://cellxgene-example-data.czi.technology/tabula-muris.h5ad
```

# Loading Data

To load an h5ad file, you must first create an ```.ini``` configuration file.  Here is an [example configuration file](examples/tabula_muris_mini.ini) for loading the [mini h5ad](/examples/tabula_muris_mini.h5ad) file.  In the config file, you can specify a ```genes``` section with specific genes to imported;  if you remove the ```genes``` section, all genes in the h5ad file will be imported.

To import the data, you then run:

```
luna add-h5ad examples/tabula_muris_mini.ini
```

If you want verbose output, use:

```
luna --verbose add-h5ad examples/tabula_muris_mini.ini
```

# Running the API

To the Luna API, run:

```
make run_api
```

By default, this will start an API on port 8000.  Interactive Swagger API docs will be located at 8000/docs.

To run the Luna API in production, run:

```
make run_api_prod
```

# Downsampling h5ad Files

By their very nature, h5ad files tend to be quite large, as they may cover tens of thousands of cells and tens of thousands of genes.  As I was developing Luna, I realized I needed to generate smaller h5ad files that I could use for unit testing and quick examples.  To that end, the Luna CLI includes an option for downsampling h5ad files.

To downsample an existing h5ad file, you first need to download the full h5ad file.  For example, to download the [CZI tabula muris data set](https://tabula-muris.ds.czbiohub.org/):

```
wget https://cellxgene-example-data.czi.technology/tabula-muris.h5ad
```

You then specify an .ini file with:

* the path to an existing h5ad file.
* list of genes you want to extract.

[Example here](examples/tabula_muris_downsample.ini).

Then run:

```
luna --verbose downsample-h5ad examples/tabula_muris_downsample.ini examples/tabula-muris-mini.h5ad
```

By default, this will create a new ```tabula_muris_mini.h5ad``` with only 100 cells and 3 genes.  To specify more cells, use the ```--num_cells``` option.

# Additional Make Commands

The Make file includes a few additional commands that might be useful for developers, including running tests, linting code, etc.

# License

MIT License

Copyright (c) ecerami

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.