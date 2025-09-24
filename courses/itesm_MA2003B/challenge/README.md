# Challenge for MA2003B

# Installation

To install the project, you will require a Python 3.x interpreter.
This project was built using Python 3.13, it is recommended to use this version.

## Create a virtual environment

After cloning the repository, you should create a virtual environment and install the dependencies:

```bash
python3.13 -m venv .venv
```

Or

```bash
python -m venv .venv
```

## Activate the virtual environment

To activate the virtual environment:

On macOS/Linux:
```bash
source .venv/bin/activate
```

On Windows PowerShell:
```bash
..\.venv\Scripts\activate.ps1
```

On Windows Command Prompt:
```bash
..venv\Scripts\activate.bat
```

## Install the dependencies

To install the dependencies:

```bash
pip install -r requirements.txt
```

# Process Datasets

In the `scripts` directory, you will find the script `process_datasets.py` that will process the datasets.
To run the script, use the following commands after activating the virtual environment:

First, change the working directory to the `scripts` directory:
```
cd scripts
```

Then, run the script:

```bash
python process_datasets.py
```

You should see an output in `data/processed/` with the name `main_dataframe.csv`
_Note: If you have already processed the datasets, running the script again will overwrite the existing files._
