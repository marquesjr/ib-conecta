import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from smoke_golive import Response, build_checks, run  # noqa: E402

BASE = "https://www.ibsantaleopoldina.com.br"
HTML = {"content-type": "text/html; charset=utf-8", "x-content-type-options": "nosniff"}
FORM = "<main><form method='post'><input name='csrfmiddlewaretoken'></form></main>"


def healthy_site(url: str) -> Response:
    if url == "http://www.ibsantaleopoldina.com.br/":
        return Response(308, {"location": f"{BASE}/"}, "")
    if url == "https://ibsantaleopoldina.com.br/planeje-sua-visita/":
        return Response(301, {"location": f"{BASE}/planeje-sua-visita/"}, "")
    if url.endswith("/healthz/"):
        return Response(200, {"content-type": "application/json"}, '{"status": "ok"}')
    if url.endswith("/area-privada/") or url.endswith("/area-privada/ministerios/"):
        return Response(302, {"location": "/conta/entrar/?next=/area-privada/"}, "")
    if url.endswith("/admin/"):
        return Response(302, {"location": "/admin/login/?next=/admin/"}, "")
    return Response(200, HTML, FORM)


class SmokeGoLiveTests(unittest.TestCase):
    def test_healthy_site_passes_every_check(self) -> None:
        results = run(BASE, fetcher=healthy_site)
        self.assertEqual([r for r in results if r[2]], [])
        self.assertEqual(len(results), len(build_checks(BASE)))

    def test_private_area_open_to_anonymous_fails(self) -> None:
        def leaky(url: str) -> Response:
            if url.endswith("/area-privada/"):
                return Response(200, HTML, FORM)
            return healthy_site(url)

        failures = {name: error for name, _url, error in run(BASE, fetcher=leaky) if error}
        self.assertEqual(list(failures), ["Área privada exige login"])
        self.assertIn("esperado redirect", failures["Área privada exige login"])

    def test_form_without_csrf_fails(self) -> None:
        def no_csrf(url: str) -> Response:
            if url.endswith("/pedido-de-oracao/"):
                return Response(200, HTML, "<main><form></form></main>")
            return healthy_site(url)

        failures = [name for name, _url, error in run(BASE, fetcher=no_csrf) if error]
        self.assertEqual(failures, ["Formulário: pedido de oração"])

    def test_unhealthy_database_fails(self) -> None:
        def db_down(url: str) -> Response:
            if url.endswith("/healthz/"):
                return Response(503, {"content-type": "application/json"}, '{"status": "error"}')
            return healthy_site(url)

        failures = [name for name, _url, error in run(BASE, fetcher=db_down) if error]
        self.assertEqual(failures, ["Health check (app + banco)"])

    def test_local_http_skips_https_and_apex_checks(self) -> None:
        names = [name for name, _url, _check in build_checks("http://localhost:8000")]
        self.assertNotIn("HTTP redireciona para HTTPS", names)
        self.assertNotIn("Apex redireciona para www", names)
        self.assertIn("Login", names)


if __name__ == "__main__":
    unittest.main()
