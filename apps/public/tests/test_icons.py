"""Ícone do navegador derivado do peixe da logo."""

import json
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from PIL import Image

ICONS = Path(settings.BASE_DIR) / "static" / "img" / "icons"


class IconFilesTests(SimpleTestCase):
    def test_ico_carries_a_drawing_for_each_tab_size(self):
        with Image.open(ICONS / "favicon.ico") as ico:
            self.assertEqual(ico.ico.sizes(), {(16, 16), (32, 32), (48, 48)})

    def test_png_icons_have_the_declared_sizes(self):
        for name, size in (("apple-touch-icon.png", 180), ("icon-192.png", 192), ("icon-512.png", 512)):
            with Image.open(ICONS / name) as image:
                self.assertEqual(image.size, (size, size), name)

    def test_manifest_points_to_existing_icons(self):
        manifest = json.loads((Path(settings.BASE_DIR) / "static" / "site.webmanifest").read_text(encoding="utf-8"))
        for icon in manifest["icons"]:
            path = Path(settings.BASE_DIR) / icon["src"].lstrip("/")
            self.assertTrue(path.is_file(), icon["src"])

    def test_svg_icon_is_self_contained(self):
        svg = (ICONS / "icon.svg").read_text(encoding="utf-8")
        self.assertTrue(svg.startswith("<svg"))
        self.assertNotIn("<image", svg)
        self.assertNotIn("href", svg)


class IconLinksTests(TestCase):
    def test_every_page_declares_the_icons(self):
        body = self.client.get(reverse("home")).content.decode()
        for fragment in (
            "img/icons/favicon.ico",
            "img/icons/icon.svg",
            "img/icons/apple-touch-icon.png",
            "site.webmanifest",
        ):
            self.assertIn(fragment, body)

    def test_root_favicon_redirects_to_the_static_file(self):
        response = self.client.get("/favicon.ico")
        self.assertEqual(response.status_code, 301)
        self.assertTrue(response["Location"].endswith("img/icons/favicon.ico"))
