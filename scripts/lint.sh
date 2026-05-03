#!/usr/bin/env bash

set -e

export DIR_SCRIPT=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export DIR_SOURCE="${DIR_SCRIPT}/.."

python ${DIR_SOURCE}/test/check_order.py
python -m py_compile ${DIR_SOURCE}/bin/aosp_cli.py