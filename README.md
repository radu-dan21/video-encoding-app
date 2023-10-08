# Video encoding app

---

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python: 3.11](https://img.shields.io/badge/Python-3.11-blue)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![CI](https://github.com/radu-dan21/project/actions/workflows/CI.yml/badge.svg)

Web app used for video encoding and comparing the performance of different video software encoders.

The application uses `ffmpeg` and `ffprobe` for all video related operations (encoding, computing metrics, extracting metadata).

---

## Useful commands:

Run the app (then access the application by navigating at http://localhost:8000):

    docker compose up

Run test suite:

    docker compose run --rm test pytest tests/

Create a superuser for Django's admin site (use the following command and follow the instructions):

    docker compose run --rm web python manage.py createsuperuser

Manually run pre-commit hooks for linting and auto-formatting code:

    ./scripts/run_code_checks.sh

----

## Usage

In order to start a new video encoding experiment or examine previous results, navigate at http://localhost:8000/console/home.

By default, the app offers support for a few software encoders and metrics, but it can work with any encoders and metrics that ffmpeg supports.
The apps functionality can be extended by creating new `Codec`, `EncoderSetting`, `InformationFilter`, and `ComparisonFilter` instances in Django's admin site (http://localhost:8000/admin).

---

## Model diagram

![Model diagram](model_diagram.png)
