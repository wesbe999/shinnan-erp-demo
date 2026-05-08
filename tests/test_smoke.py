import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.main import app


BASE_URL = "http://127.0.0.1:8050"


def get_url(path):
    request = Request(BASE_URL + path, headers={"User-Agent": "shinnan-smoke-test"})
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, response.headers.get("content-type", ""), response.read()
    except HTTPError as exc:
        return exc.code, exc.headers.get("content-type", ""), exc.read()
    except URLError as exc:
        raise unittest.SkipTest(f"local server unavailable: {exc}")


class SmokeTests(unittest.TestCase):
    def test_no_duplicate_method_path_routes(self):
        seen = set()
        duplicates = []

        for route in app.routes:
            if not hasattr(route, "methods"):
                continue

            key = (tuple(sorted(route.methods)), route.path)
            if key in seen:
                duplicates.append(key)
            else:
                seen.add(key)

        self.assertEqual([], duplicates)

    def test_admin_pages_respond(self):
        paths = [
            "/admin/buildings",
            "/admin/sales",
            "/admin/sales/managers",
            "/admin/customers",
            "/admin/customers/billing",
            "/admin/ticket-customer-link",
            "/admin/import",
        ]

        for path in paths:
            with self.subTest(path=path):
                status, content_type, _ = get_url(path)
                self.assertEqual(200, status)
                self.assertIn("text/html", content_type)

    def test_admin_apis_respond_with_json(self):
        paths = [
            "/api/admin/buildings",
            "/api/admin/buildings/status",
            "/api/admin/sales/business-records",
            "/api/admin/sales/managers",
            "/api/admin/customers",
            "/api/admin/employees",
            "/api/admin/ticket-customer-candidates",
            "/api/admin/ticket-customer-candidates/search-customers?q=test",
        ]

        for path in paths:
            with self.subTest(path=path):
                status, content_type, _ = get_url(path)
                self.assertEqual(200, status)
                self.assertIn("application/json", content_type)

    def test_missing_customer_billing_detail_returns_404(self):
        status, content_type, _ = get_url("/api/admin/customers/billing?customer_no=__missing__")

        self.assertEqual(404, status)
        self.assertIn("application/json", content_type)


if __name__ == "__main__":
    unittest.main()
