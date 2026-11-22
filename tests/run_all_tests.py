"""
TITAN Master Test Suite & System Verification Orchestrator.
Runs all 6 test batteries, records hardware telemetry, timings, and outputs an audit report.
"""

import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.telemetry import telemetry

def run_all():
    print("=" * 75)
    print("           T.I.T.A.N. COMPREHENSIVE VERIFICATION BATTERY")
    print("=" * 75)

    t0 = time.time()
    tel = telemetry.get_full_telemetry()
    gpu = tel["gpu"]
    cpu = tel["cpu"]
    ram = tel["ram"]
    battery = tel["battery"]

    print(f"Timestamp    : {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"GPU Hardware : {gpu['name']} | VRAM: {gpu['vram_used_mb']}/{gpu['vram_total_mb']} MB ({gpu['vram_percent']}%) | Temp: {gpu['temperature_c']}C")
    print(f"CPU Hardware : AMD Ryzen ({cpu['cores']} Threads) | Frequency: {cpu['frequency_mhz']} MHz | Load: {cpu['percent']}%")
    print(f"RAM Hardware : {ram['used_gb']} / {ram['total_gb']} GB ({ram['percent']}%)")
    print(f"Power State  : {battery['percent']}% ({'Connected to AC Power' if battery['power_plugged'] else 'On Battery'})")
    print("-" * 75)

    test_modules = [
        "tests.test_coding_agent",
        "tests.test_advanced_autonomous_features",
        "tests.test_professional_features",
        "tests.test_openjarvis_parity",
        "tests.test_a_to_z_capabilities",
        "tests.test_full_system",
    ]

    results = []
    total_ran = 0
    total_failed = 0
    total_errors = 0

    loader = unittest.TestLoader()

    for mod_name in test_modules:
        suite_start = time.time()
        suite = loader.loadTestsFromName(mod_name)
        runner = unittest.TextTestRunner(verbosity=1)
        res = runner.run(suite)
        dur = round(time.time() - suite_start, 3)

        ran = res.testsRun
        failed = len(res.failures)
        err = len(res.errors)

        total_ran += ran
        total_failed += failed
        total_errors += err

        status = "PASS" if res.wasSuccessful() else "FAIL"
        results.append({
            "module": mod_name.replace("tests.", ""),
            "tests": ran,
            "status": status,
            "duration": dur,
            "failures": failed,
            "errors": err
        })

    total_dur = round(time.time() - t0, 3)

    print("\n" + "=" * 75)
    print("                    SUBSYSTEM TEST EXECUTION AUDIT")
    print("=" * 75)
    print(f"{'STATUS':<8} | {'SUBSYSTEM TEST SUITE':<38} | {'TESTS':<6} | {'TIME'}")
    print("-" * 75)
    for r in results:
        print(f"[{r['status']}]   | {r['module']:<38} | {r['tests']:<6} | {r['duration']}s")
    print("-" * 75)
    print(f"TOTAL EXECUTION AUDIT: {total_ran} tests in {total_dur}s | Failures: {total_failed} | Errors: {total_errors}")
    print("=" * 75)

    return {
        "total_tests": total_ran,
        "failures": total_failed,
        "errors": total_errors,
        "total_duration": total_dur,
        "telemetry": tel,
        "breakdown": results
    }

if __name__ == "__main__":
    run_all()
