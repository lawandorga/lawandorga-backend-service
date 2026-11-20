import io
from datetime import date, timedelta
from pathlib import Path

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client
from PIL import Image

from core.internal.api.pages import INDEX_PAGE_ARTICLES
from core.internal.models import Article, FeatureArea, RoadmapItem
from core.org.models import Org

pytestmark = pytest.mark.django_db


def png_file(name="image.png"):
    buffer = io.BytesIO()
    Image.new("RGB", (4, 4), "#003C4D").save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


def get_index():
    response = Client().get("/api/internal/pages/index/")
    assert response.status_code == 200
    return response.json()


def make_article(title, days_ago=0, *recipient_orgs):
    article = Article.objects.create(
        title=title,
        preview="Preview",
        date=date(2026, 11, 20) - timedelta(days=days_ago),
        content="Content",
    )
    if recipient_orgs:
        article.recipients.set(recipient_orgs)
    return article


# models


def test_feature_area_requires_alt_text_with_screenshot():
    area = FeatureArea(
        title="Akten",
        description="Text",
        placement=FeatureArea.PLACEMENT_SHOWROOM,
        screenshot=png_file(),
    )
    with pytest.raises(ValidationError) as e:
        area.full_clean()
    assert "screenshot_alt" in e.value.message_dict


def test_feature_area_without_screenshot_needs_no_alt_text():
    area = FeatureArea(
        title="Akten", description="Text", placement=FeatureArea.PLACEMENT_MORE
    )
    area.full_clean()


def test_feature_area_ordering():
    FeatureArea.objects.create(title="m1", description="", placement="more", position=1)
    FeatureArea.objects.create(
        title="s2", description="", placement="showroom", position=2
    )
    FeatureArea.objects.create(title="m0", description="", placement="more", position=0)
    FeatureArea.objects.create(
        title="s1", description="", placement="showroom", position=1
    )
    titles = list(FeatureArea.objects.values_list("title", flat=True))
    assert titles == ["m0", "m1", "s1", "s2"]


def test_roadmap_ordering_status_position_date():
    RoadmapItem.objects.create(
        title="p1", date=date(2026, 1, 1), status="planned", position=1
    )
    RoadmapItem.objects.create(
        title="l-old", date=date(2026, 1, 1), status="live", position=0
    )
    RoadmapItem.objects.create(
        title="l-new", date=date(2026, 9, 1), status="live", position=0
    )
    RoadmapItem.objects.create(
        title="p0", date=date(2026, 1, 1), status="planned", position=0
    )
    titles = list(RoadmapItem.objects.values_list("title", flat=True))
    assert titles == ["l-new", "l-old", "p0", "p1"]


def test_roadmap_benefits_are_split_into_a_list():
    item = RoadmapItem(benefits="  First \n\n Second\r\n  \nThird  ")
    assert item.benefit_list == ["First", "Second", "Third"]


def test_new_roadmap_items_are_unpublished_and_planned():
    item = RoadmapItem.objects.create(title="New", date=date(2026, 1, 1))
    assert item.is_published is False
    assert item.status == RoadmapItem.STATUS_PLANNED


# index endpoint


def test_index_returns_only_published_feature_areas():
    published = FeatureArea.objects.create(
        title="Published", description="Text", placement="showroom", is_published=True
    )
    FeatureArea.objects.create(title="Draft", description="Text", placement="showroom")

    areas = get_index()["feature_areas"]

    assert [a["id"] for a in areas] == [published.pk]
    assert set(areas[0].keys()) == {
        "id",
        "title",
        "description",
        "placement",
        "position",
        "icon_url",
        "screenshot_url",
        "screenshot_alt",
        "screenshot_note",
    }
    assert areas[0]["icon_url"] is None
    assert areas[0]["screenshot_url"] is None


def test_index_returns_image_urls_for_feature_areas():
    FeatureArea.objects.create(
        title="With images",
        description="Text",
        placement="showroom",
        icon=png_file("icon.png"),
        screenshot=png_file("shot.png"),
        screenshot_alt="Alt",
        is_published=True,
    )

    area = get_index()["feature_areas"][0]

    assert "internal/landing/feature_areas/icons/" in area["icon_url"]
    assert "internal/landing/feature_areas/screenshots/" in area["screenshot_url"]
    assert area["screenshot_url"].startswith(("http://", "https://", "/"))


def test_index_returns_only_published_roadmap_items_with_new_fields():
    RoadmapItem.objects.create(
        title="Published",
        date=date(2026, 1, 1),
        status="planned",
        stage="Prototyp",
        benefits="A\nB",
        status_note="Konzept vorhanden.",
        is_published=True,
    )
    RoadmapItem.objects.create(title="Draft", date=date(2026, 1, 1))

    items = get_index()["roadmap_items"]

    assert len(items) == 1
    item = items[0]
    assert item["title"] == "Published"
    assert item["status"] == "planned"
    assert item["stage"] == "Prototyp"
    assert item["benefits"] == ["A", "B"]
    assert item["status_note"] == "Konzept vorhanden."
    assert item["icon_url"] is None
    assert "benefit_list" not in item


def test_index_returns_latest_public_articles_only():
    org = Org.objects.create(name="Some RLC")
    targeted = make_article("Targeted", 0, org)
    public = [make_article("Public {}".format(i), i + 1) for i in range(5)]

    articles = get_index()["articles"]

    ids = [a["id"] for a in articles]
    assert targeted.pk not in ids
    assert ids == [a.pk for a in public[:INDEX_PAGE_ARTICLES]]


# public article list


def test_public_article_list_only_contains_public_articles_newest_first():
    org = Org.objects.create(name="Some RLC")
    older = make_article("Older", 10)
    newer = make_article("Newer", 1)
    targeted = make_article("Targeted", 0, org)

    response = Client().get("/api/internal/pages/articles/")

    assert response.status_code == 200
    ids = [a["id"] for a in response.json()]
    assert ids == [newer.pk, older.pk]
    assert targeted.pk not in ids


# seed command


def test_seed_landing_content_is_idempotent_and_unpublished():
    call_command("seed_landing_content", stdout=io.StringIO())
    call_command("seed_landing_content", stdout=io.StringIO())

    assert FeatureArea.objects.filter(placement="showroom").count() == 6
    assert FeatureArea.objects.filter(placement="more").count() == 3
    assert RoadmapItem.objects.filter(status="live").count() == 7
    assert RoadmapItem.objects.filter(status="planned").count() == 3
    assert not FeatureArea.objects.filter(is_published=True).exists()
    assert not RoadmapItem.objects.filter(is_published=True).exists()

    calendar = RoadmapItem.objects.get(
        title="Kalender mit Freigaben, Erinnerungen und Export"
    )
    assert calendar.date == date(2026, 9, 11)
    signal = RoadmapItem.objects.get(title="Signal-Bridge für den Chat")
    assert signal.date == date(2026, 1, 1)
    stats = FeatureArea.objects.get(title="Statistik")
    assert (
        stats.screenshot_note
        == "Ausschnitte aus der Statistik der Demo-Organisation, neu angeordnet."
    )


def test_seed_landing_content_publish_and_assets(tmp_path: Path):
    icons = tmp_path / "icons"
    screenshots = tmp_path / "screenshots"
    icons.mkdir()
    screenshots.mkdir()
    for name in [
        "ic-akten",
        "ic-tasks",
        "ic-kalender",
        "ic-kommunikation",
        "ic-statistik",
        "ic-dashboard",
        "ic-mail",
        "ic-admin",
        "ic-bell",
        "ic-share",
        "ic-forms",
    ]:
        (icons / "{}.png".format(name)).write_bytes(png_file().read())
    for name in [
        "shot-akten",
        "shot-akte",
        "shot-tasks",
        "shot-kalender",
        "shot-statistik",
        "shot-dashboard",
        "shot-admin",
    ]:
        (screenshots / "{}.png".format(name)).write_bytes(png_file().read())

    call_command(
        "seed_landing_content",
        "--assets",
        str(tmp_path),
        "--publish",
        stdout=io.StringIO(),
    )

    index = get_index()
    showroom = [a for a in index["feature_areas"] if a["placement"] == "showroom"]
    assert [a["title"] for a in showroom] == [
        "Akten",
        "Einzelne Akte",
        "Aufgaben",
        "Kalender",
        "Chat und Signal",
        "Statistik",
    ]
    chat = next(a for a in showroom if a["title"] == "Chat und Signal")
    assert chat["screenshot_url"] is None
    assert chat["icon_url"] is not None
    akten = showroom[0]
    assert akten["screenshot_url"] is not None
    assert akten["screenshot_alt"].startswith("Screenshot: Aktenliste")
    planned = [i for i in index["roadmap_items"] if i["status"] == "planned"]
    assert all(i["icon_url"] for i in planned)
    assert len(planned[0]["benefits"]) == 2
