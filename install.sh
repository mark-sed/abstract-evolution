# Run using: sh install.sh
#
# This script checks if all needed tools are installed
# It also installs needed Python packages

# Check for Python 3
if ! command -v python3 &>/dev/null
then
    # No python3 command, check for python command version
    if ! python -V | cut -d. -f1 | grep -w 'Python 3' &>/dev/null
    then
        printf "ERROR: Python 3 is not installed. Please install it using your packaging manager or from the official website: https://www.python.org/downloads/\n"
        exit 0
    fi
fi

# Check for pip
if ! command -v pip3 &>/dev/null
then
    # No pip3 command check for pip command
    if ! command -v pip &>/dev/null
    then
        # pip is not installed install it
        printf "ERROR: Pip is not installed. Please install it.\n"
        exit 0
    fi
fi

# Install python requirements
# No fail check because pip was checked before
pip3 install -r requirements.txt || pip install -r requirements.txt
