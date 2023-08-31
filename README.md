# project

App used for comparing the performance of various video codecs

Run command:

    docker compose up


Access the application by navigating at:

    http://localhost:8000


Test command:

    docker compose run --rm test pytest tests/

In order to create a superuser for Django's admin site, use the following command and follow the instructions:

    docker compose run --rm python manage.py createsuperuser
