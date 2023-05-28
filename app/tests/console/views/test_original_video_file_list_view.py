import pytest

from bs4 import BeautifulSoup
from django.test import Client
from django.urls import reverse

from video_coding.entities.models import OriginalVideoFile


@pytest.mark.django_db
def test_home_page(ovf: OriginalVideoFile):
    client = Client()
    response = client.get(reverse("console:home"))
    soup = BeautifulSoup(response.content, "html.parser")

    table_body = soup.find("tbody")
    ovfs = table_body.find_all("tr")

    assert len(ovfs) == 1
    assert ovf.name in str(next(iter(ovfs)))
