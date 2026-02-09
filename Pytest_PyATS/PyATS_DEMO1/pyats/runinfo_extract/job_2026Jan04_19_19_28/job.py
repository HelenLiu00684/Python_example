from pyats.easypy import run

def main(runtime):
    run(
        testscript="tests/test_network_health.py",
        runtime=runtime,
    )
