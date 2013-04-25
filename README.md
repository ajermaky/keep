# Installing Dependencies

Make sure the following dependencies are installed:

- MongoDB ( http://www.mongodb.org )
- MySQL ( http://www.mysql.com )
- Python 2.7 ( http://www.python.org )


# Setting up your Python Dev Environment


Make sure you have the following Python modules installed:

- pip ( http://pypi.python.org/pypi/pip )
- virtualenv ( http://pypi.python.org/pypi/virtualenv )
- virtualenvwrapper ( http://www.doughellmann.com/projects/virtualenvwrapper )

Ensure that virtualenvwrapper is correctly setup. You should be able to run mkvirtualenv_help from the command line.


## Create your development workspace

    mkvirtualenv dhlab_backend
    pip install -r deps.txt

## Initializing Submodules

    git submodule init
    git submodule update

## Startup MongoDB

Run mongod to ensure MongoDB is running

    mongod

## Setting up the Databases

    python dhlab_backend/manage.py syncdb
    fab restore_db

## Running the Django server

    python dhlab_backend/manage.py runserver

## Logging In

You may now log in to the system using the following credentials.

**Username:** admin

**Password:** test

