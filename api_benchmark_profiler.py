# DevOps & Performance Engineering: Benchmarking request execution times, calculating latency statistics, and generating performance metrics

import time
import urllib.request
import urllib.error
import math

class EndpointPerformanceProfiler:
    """
    Executes benchmark test runs against target API endpoints,
    calculates statistical latency metrics (Min, Max, Mean, StdDev),
    and flags degraded network response profiles.
    """
    def __init__(self, target_url, iterations=5):
        self.target_url = target_url
        self.iterations = iterations
        self.latency_records = []

    def run_benchmark(self):
        print("--- Performance Tools: API Endpoint Benchmark Profiler ---")
        print(f"Target URL: {self.target_url}")
        print(f"Executing {self.iterations} benchmark test runs...\n")

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

        for i in range(1, self.iterations + 1):
            start_time = time.time()
            try:
                req = urllib.request.Request(self.target_url, headers=headers)
                with urllib.request.urlopen(req, timeout=5.0) as response:
                    status_code = response.getcode()
                    elapsed_ms = (time.time() - start_time) * 1000
                    self.latency_records.append(elapsed_ms)
                    print(f"Run #{i}: Status {status_code} | Latency: {elapsed_ms:.2f} ms")
            except urllib.error.HTTPError as err:
                elapsed_ms = (time.time() - start_time) * 1000
                self.latency_records.append(elapsed_ms)
                print(f"Run #{i}: HTTP Error {err.code} | Latency: {elapsed_ms:.2f} ms")
            except Exception as err:
                print(f"Run #{i}: Connection Failed ({err})")

        return self.compute_statistics()

    def compute_statistics(self):
        if not self.latency_records:
            print("Error: No latency samples collected.")
            return None

        n = len(self.latency_records)
        min_lat = min(self.latency_records)
        max_lat = max(self.latency_records)
        mean_lat = sum(self.latency_records) / n

        # Standard Deviation calculation
        variance = sum((x - mean_lat) ** 2 for x in self.latency_records) / n
        std_dev = math.sqrt(variance)

        stats = {
            "total_runs": n,
            "min_ms": round(min_lat, 2),
            "max_ms": round(max_lat, 2),
            "mean_ms": round(mean_lat, 2),
            "std_dev_ms": round(std_dev, 2)
        }

        print("\nBenchmark Performance Summary:")
        print("=" * 50)
        print(f"Total Sample Runs : {stats['total_runs']}")
        print(f"Minimum Latency   : {stats['min_ms']} ms")
        print(f"Maximum Latency   : {stats['max_ms']} ms")
        print(f"Mean Latency      : {stats['mean_ms']} ms")
        print(f"Standard Deviation: {stats['std_dev_ms']} ms")
        print("=" * 50)

        if stats['mean_ms'] < 200:
            print("PERFORMANCE VERDICT: Excellent response speed.")
        elif stats['mean_ms'] < 500:
            print("PERFORMANCE VERDICT: Moderate latency observed.")
        else:
            print("PERFORMANCE VERDICT: High latency endpoint. Optimization required.")

        return stats

if __name__ == "__main__":
    # Benchmark a standard public endpoint
    target_api = "https://api.github.com"
    profiler = EndpointPerformanceProfiler(target_api, iterations=5)
    profiler.run_benchmark()