# Installation Guide

This document outlines the steps for installing ImageDreamer-QT-QUICK-MVC using various methods. Choose the one that best fits your environment.

## Conda Installation (Recommended)

1. Clone the repo: `git clone https://github.com/illescasDaniel/ImageDreamer-QT-QUICK-MVC.git` and `cd ImageDreamer-QT-QUICK-MVC`.
2. Install Conda if not already installed: [Anaconda](https://www.anaconda.com/download) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html).
3. Execute the install script based on your OS:
   - Ubuntu/macOS: `./install.sh`
   - Windows (**Anaconda Powershell Prompt**, outside of VSCode): `.\install.ps1`
4. Activate the new environment: `conda activate ImageDreamer`
5. Run the app: `invoke run`

## Pip Installation

**Note**: Issues may occur on Windows.

1. Clone the repo and navigate into the directory.
2. Create a virtual environment: `python3 -m venv imagedreamer-env`
3. Activate the environment: `source imagedreamer-env/bin/activate` (`deactivate` to exit)
4. Install dependencies: `pip3 install -r requirements.txt`
5. Run the app: `python3 src/main.py` or `invoke run`.

## UV Installation

1. Ensure `uv` is installed: `pip install uv` (if not already installed)
2. Clone the repo and navigate into the directory.
3. Create a virtual environment with `uv`: `uv venv`
4. Activate the environment: `source .venv/bin/activate`
5. Install dependencies: `uv pip install -r requirements.txt`
6. Run the app: `python3 src/main.py` or `invoke run`.

[Back to main README](../README.md)
