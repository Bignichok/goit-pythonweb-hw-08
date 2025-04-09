.. goit-hw-08 documentation master file, created by
   sphinx-quickstart on Wed Apr  9 14:30:16 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Contact Management API documentation!
============================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules/auth
   modules/contacts
   modules/models
   modules/schemas

Introduction
------------

This is a FastAPI-based REST API for managing contacts with user authentication, email verification, and rate limiting.

Features
--------

* User authentication with JWT tokens
* Email verification (optional in development)
* Rate limiting (optional in development)
* Contact management (CRUD operations)
* Contact search and filtering
* Upcoming birthdays tracking
* User avatars with Cloudinary integration
* Email notifications
* Redis caching (optional in development)

Installation
-----------

1. Clone the repository::

    git clone <repository-url>
    cd contact-management-api

2. Create and activate a virtual environment::

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies::

    pip install poetry
    poetry install

4. Create a `.env` file with required configuration.

5. Initialize the database::

    poetry run python -m app.core.database

6. Start the development server::

    poetry run uvicorn app.main:app --reload

API Documentation
---------------

Authentication
^^^^^^^^^^^^^

.. automodule:: app.api.auth
   :members:
   :undoc-members:
   :show-inheritance:

Contacts
^^^^^^^

.. automodule:: app.api.contacts
   :members:
   :undoc-members:
   :show-inheritance:

Models
^^^^^^

.. automodule:: app.models.user
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: app.models.contact
   :members:
   :undoc-members:
   :show-inheritance:

Schemas
^^^^^^^

.. automodule:: app.schemas.auth
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: app.schemas.contact
   :members:
   :undoc-members:
   :show-inheritance:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

