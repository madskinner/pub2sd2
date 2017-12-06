#!/bin/bash

if [[ $TRAVIS_OS_NAME == 'osx' ]]; then

    # Install some custom requirements on OS X
    # e.g. brew install pyenv-virtualenv

    case "${TOXENV}" in
        py34)
            # Install some custom Python 3.4 requirements on OS X
           pip install .
           pip install -r requirements.txt
            ;;
        py35)
            # Install some custom Python 3.5 requirements on OS X
           pip install .
           pip install -r requirements.txt
            ;;
        py36)
            # Install some custom Python 3.6 requirements on OS X
            pip install .
            pip install -r requirements.txt
            ;;
    esac
else
    # Install some custom requirements on Linux
    pip install .
    pip install -r requirements.txt
fi