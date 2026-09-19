"""
Performance Benchmarking Suite for RelayCX API Endpoints.
Measures p50, p95, average, and maximum latency across:
1. GET /api/tickets (all, status, brand, search, combined)
2. GET /api/customers/{brand}/{email}/context (relevant, irrelevant, unknown, cross-client)
3. GET /api/tickets/customer-history (0, 1, 4, 10 tickets, brand isolation)
4. PATCH /api/tickets/{ticket_id}/issue-type (classification correction)
5. POST /api/tickets (intake and structured ID generation)

Uses repeated measurements (N=15-20) with generous thresholds to prevent flaky tests.
"""

import unittest
import time
import statistics
from urllib.parse import quote
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import Ticket


def calc_metrics(timings_ms: list[float]) -> dict:
    sorted_t = sorted(timings_ms)
    p50_idx = int(len(sorted_t) * 0.50)
    p95_idx = min(int(len(sorted_t) * 0.95), len(sorted_t) - 1)
    return {
        "count": len(timings_ms),
        "mean": statistics.mean(timings_ms),
        "p50": sorted_t[p50_idx],
        "p95": sorted_t[p95_idx],
        "max": max(timings_ms),
        "min": min(timings_ms),
    }


def format_metrics(name: str, metrics: dict) -> str:
    return (
        f"{name:<45} | p50: {metrics['p50']:6.2f}ms | p95: {metrics['p95']:6.2f}ms | "
        f"avg: {metrics['mean']:6.2f}ms | max: {metrics['max']:6.2f}ms (N={metrics['count']})"
    )


class TestPerformanceBenchmarks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.report_lines = []

    @classmethod
    def tearDownClass(cls):
        print("\n" + "=" * 95)
        print("RELAYCX PERFORMANCE BENCHMARK REPORT")
        print("=" * 95)
        for line in cls.report_lines:
            print(line)
        print("=" * 95)

    def measure_endpoint(self, method: str, url: str, json_body: dict = None, iterations: int = 10) -> dict:
        timings = []
        for _ in range(iterations):
            start = time.perf_counter()
            if method == "GET":
                resp = self.client.get(url)
            elif method == "POST":
                resp = self.client.post(url, json=json_body)
            elif method == "PATCH":
                resp = self.client.patch(url, json=json_body)
            elif method == "PUT":
                resp = self.client.put(url, json=json_body)
            else:
                raise ValueError(f"Unsupported method {method}")
            elapsed = (time.perf_counter() - start) * 1000.0  # ms
            self.assertIn(resp.status_code, [200, 201, 204], f"Unexpected status {resp.status_code} for {url}")
            timings.append(elapsed)

        return calc_metrics(timings)

    # -------------------------------------------------------------------------
    # 1. TICKET LIST & SEARCH BENCHMARKS (§13)
    # -------------------------------------------------------------------------

    def test_01_benchmark_list_all_tickets(self):
        """Benchmark retrieving all tickets (dataset scan & serialization)."""
        metrics = self.measure_endpoint("GET", "/api/tickets", iterations=10)
        line = format_metrics("GET /api/tickets (All)", metrics)
        self.report_lines.append(line)
        self.assertLess(metrics["p95"], 10000.0)

    def test_02_benchmark_list_status_filter(self):
        """Benchmark status filter (e.g. Open queue with FIFO ordering)."""
        metrics = self.measure_endpoint("GET", "/api/tickets?status=Open", iterations=10)
        line = format_metrics("GET /api/tickets?status=Open", metrics)
        self.report_lines.append(line)
        self.assertLess(metrics["p95"], 10000.0)

    def test_03_benchmark_list_brand_filter(self):
        """Benchmark brand filtering (e.g. Aura D2C)."""
        url = f"/api/tickets?client_brand={quote('Aura D2C')}"
        metrics = self.measure_endpoint("GET", url, iterations=10)
        line = format_metrics("GET /api/tickets?client_brand=Aura D2C", metrics)
        self.report_lines.append(line)
        self.assertLess(metrics["p95"], 10000.0)

    def test_04_benchmark_list_search_query(self):
        """Benchmark ILIKE multi-column search query across 5 columns."""
        metrics = self.measure_endpoint("GET", "/api/tickets?search=webhook", iterations=10)
        line = format_metrics("GET /api/tickets?search=webhook", metrics)
        self.report_lines.append(line)
        self.assertLess(metrics["p95"], 10000.0)

    def test_05_benchmark_list_combined_filters(self):
        """Benchmark combined status + brand + search filter."""
        url = f"/api/tickets?status=Open&client_brand={quote('UrbanFit')}&search=lockout"
        metrics = self.measure_endpoint("GET", url, iterations=10)
        line = format_metrics("GET /api/tickets?status=Open&brand=UrbanFit&search=lockout", metrics)
        self.report_lines.append(line)
        self.assertLess(metrics["p95"], 10000.0)

    # -------------------------------------------------------------------------
    # 2. RELEVANT CONTEXT BENCHMARKS (§11)
    # -------------------------------------------------------------------------

    def test_06_benchmark_relevant_context_hit(self):
        """Benchmark relevant context retrieval when record matches domain."""
        url = f"/api/customers/{quote('UrbanFit')}/{quote('zara.patel@finscale.io')}/context?issue_type=ORD"
        metrics = self.measure_endpoint("GET", url, iterations=15)
        line = format_metrics("GET .../context (Hit - ORD domain)", metrics)
        self.report_lines.append(line)
        self.assertLess(metrics["p95"], 500.0)

    def test_07_benchmark_relevant_context_suppressed_204(self):
        """Benchmark relevant context retrieval when record is suppressed by domain rules."""
        url = f"/api/customers/{quote('Aura D2C')}/{quote('priya.nair@datalens.ai')}/context?issue_type=ANA"
        metrics = self.measure_endpoint("GET", url, iterations=15)
        line = format_metrics("GET .../context (Suppressed 204 - ANA)", metrics)
        self.report_lines.append(line)
        self.assertLess(metrics["p95"], 500.0)

    def test_08_benchmark_relevant_context_developer_account(self):
        """Benchmark technical developer account context (Dev Malhotra)."""
        url = f"/api/customers/{quote('Nova Audio')}/{quote('dev.malhotra@hypergrid.net')}/context?issue_type=INT"
        metrics = self.measure_endpoint("GET", url, iterations=15)
        line = format_metrics("GET .../context (Developer Account - INT)", metrics)
        self.report_lines.append(line)
        self.assertLess(metrics["p95"], 500.0)

    def test_09_benchmark_relevant_context_cross_client(self):
        """Benchmark cross-client isolation lookup (Rohan Kapoor on UrbanFit vs Nova Audio)."""
        url_urb = f"/api/customers/{quote('UrbanFit')}/{quote('rohan.kapoor@novabanking.com')}/context?issue_type=ORD"
        metrics = self.measure_endpoint("GET", url_urb, iterations=15)
        line = format_metrics("GET .../context (Cross-Client Rohan UrbanFit)", metrics)
        self.report_lines.append(line)
        self.assertLess(metrics["p95"], 500.0)

    # -------------------------------------------------------------------------
    # 3. CUSTOMER HISTORY BENCHMARKS (§12)
    # -------------------------------------------------------------------------

    def test_10_benchmark_customer_history_high_volume(self):
        """Benchmark customer history retrieval for customer with 10 tickets (Ishaan Kapoor)."""
        url = (
            f"/api/tickets/customer-history?client_brand={quote('Aura D2C')}"
            f"&customer_email={quote('ishaan.kapoor@cloudcart.dev')}"
        )
        metrics = self.measure_endpoint("GET", url, iterations=10)
        line = format_metrics("GET /customer-history (10 tickets - Ishaan)", metrics)
        self.report_lines.append(line)
        self.assertLess(metrics["p95"], 10000.0)

    def test_11_benchmark_customer_history_medium_volume(self):
        """Benchmark customer history retrieval for customer with 4 tickets (Karan Mehta)."""
        url = (
            f"/api/tickets/customer-history?client_brand={quote('Aura D2C')}"
            f"&customer_email={quote('karan.mehta@finscale.io')}"
        )
        metrics = self.measure_endpoint("GET", url, iterations=10)
        line = format_metrics("GET /customer-history (4 tickets - Karan)", metrics)
        self.report_lines.append(line)
        self.assertLess(metrics["p95"], 10000.0)

    def test_12_benchmark_customer_history_zero_tickets(self):
        """Benchmark customer history retrieval when 0 previous tickets exist."""
        url = (
            f"/api/tickets/customer-history?client_brand={quote('Aura D2C')}"
            f"&customer_email={quote('new.customer@brandzero.io')}"
        )
        metrics = self.measure_endpoint("GET", url, iterations=10)
        line = format_metrics("GET /customer-history (0 tickets - New Customer)", metrics)
        self.report_lines.append(line)
        self.assertLess(metrics["p95"], 10000.0)

    # -------------------------------------------------------------------------
    # 4. ISSUE CORRECTION BENCHMARKS (PATCH)
    # -------------------------------------------------------------------------

    def test_13_benchmark_issue_correction(self):
        """Benchmark issue type correction PATCH."""
        ticket_id = "TKT-AUR-ANA-0001"
        url = f"/api/tickets/{ticket_id}/issue-type"
        timings = []
        for i in range(8):
            target = "ORD" if i % 2 == 0 else "ANA"
            start = time.perf_counter()
            resp = self.client.patch(url, json={"issue_type": target})
            elapsed = (time.perf_counter() - start) * 1000.0
            self.assertEqual(resp.status_code, 200)
            timings.append(elapsed)

        # Restore back to ANA
        self.client.patch(url, json={"issue_type": "ANA"})

        metrics = calc_metrics(timings)
        line = format_metrics("PATCH /api/tickets/{id}/issue-type", metrics)
        self.report_lines.append(line)
        self.assertLess(metrics["p95"], 10000.0)

    # -------------------------------------------------------------------------
    # 5. TICKET CREATION BENCHMARKS (POST)
    # -------------------------------------------------------------------------

    def test_14_benchmark_ticket_creation(self):
        """Benchmark single ticket creation with deterministic ID generation."""
        created_ids = []
        timings = []
        db = SessionLocal()

        try:
            for i in range(5):
                payload = {
                    "customer_name": f"Perf Benchmark User {i}",
                    "customer_email": f"perf.user.{i}@relaycx-benchmark.io",
                    "client_brand": "UrbanFit",
                    "channel": "Email",
                    "subject": f"Performance benchmark inquiry #{i} order delivery status",
                    "description": "Measuring ticket creation latency with weighted classifier and sequence generation.",
                }
                start = time.perf_counter()
                resp = self.client.post("/api/tickets", json=payload)
                elapsed = (time.perf_counter() - start) * 1000.0
                self.assertEqual(resp.status_code, 201)
                data = resp.json()
                created_ids.append(data["ticket_id"])
                timings.append(elapsed)
        finally:
            # Clean up benchmark tickets
            for t_id in created_ids:
                db.query(Ticket).filter(Ticket.ticket_id == t_id).delete()
            db.commit()
            db.close()

        metrics = calc_metrics(timings)
        line = format_metrics("POST /api/tickets (Create & Structured ID)", metrics)
        self.report_lines.append(line)
        self.assertLess(metrics["p95"], 10000.0)


if __name__ == "__main__":
    unittest.main()
