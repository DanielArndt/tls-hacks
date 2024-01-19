#!/usr/bin/env bash

venv-create() {
    current_python=$(pyenv which python)

    # Check if the .venv directory exists
    if [ -d ".venv" ]; then
        echo "Virtual environment already exists."
        return 1
    fi

    $current_python -m venv .venv
    # shellcheck source=/dev/null
    source .venv/bin/activate
    pip install -r requirements.txt
    pip install -r test-requirements.txt
}
