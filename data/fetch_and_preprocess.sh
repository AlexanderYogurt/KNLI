#!/bin/bash
set -e

python download.py
python preprocess_data.py
# python prepare_snli.py