# =====================================================
# 1.basic import library and define different folders
# =====================================================

from pathlib import Path
from pyats import aetest
import sys

# Define the basic locations for the basic files
BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR)) #reset the import root folder

YAML_DIR = BASE_DIR / "yaml"
DATA_DIR = BASE_DIR / "data"
OPERATIONS_DIR = BASE_DIR / "operations"

# =====================================================
# 2.imports function to load testbed
# =====================================================

from utils.testbed_loader import load_devices_from_testbed
# from load_input_expected import (
from utils.load_input_expected import (    
    load_issue_actions_by_protocol,
    load_expected_yaml,
    generate_operation_yaml
)
from src.ai.ai_analyzer import run_ai_analysis



# =====================================================
# 3.imports parser and chcecker functions
# =====================================================

from checkers.bgp import check_single_node_bgp_underlay
from checkers.ospf import check_single_node_ospf_underlay
from checkers.evpn import check_evpn_neighbors
from checkers.interface import check_interfaces



from utils.format_print import print_ospf_neighbors

# =====================================================
# Testcase
# =====================================================
class NetworkHealthTest(aetest.Testcase):

    @aetest.setup
    def setup(self):
        """

        """

        # ---- inventory ----
        self.devices = load_devices_from_testbed("testbed.yaml")

        # ---- rules / expected ----
        self.expected_nodes = load_expected_yaml(
            YAML_DIR / "expected_nodes.yaml"
        )
        self.rules_by_protocol = load_issue_actions_by_protocol(YAML_DIR)

        # self.logger.info(f"Loaded devices: {list(self.devices.keys())}")
        print(f"Loaded devices:: {list(self.devices.keys())}")


    # =====================================================
    # EVPN（checking leaf/spine）
    # =====================================================
    @aetest.test
    def evpn_check(self):
        for dev, dev_info in self.devices.items():

            routing_file = (
                DATA_DIR / "routing_summary" / f"routing_summary_{dev}.log"
            )

            evpn_result = check_evpn_neighbors(
                device_name=dev,
                routing_summary_file=routing_file,
            )

            if not evpn_result.get("has_issue"):
                print(f"[{dev}] EVPN underlay healthy: {list(self.devices.keys())}")
                continue
            #[leaf1] EVPN underlay healthy: ['leaf1', 'leaf2', 'spine1']

            generate_operation_yaml(
                device_name=dev,
                role=dev_info.get("role"),
                protocol="EVPN",
                issue_summary=evpn_result["issue_summary"],
                issue_detail=evpn_result["issue_detail"],
                affected_peers=evpn_result["affected_peers"],
                actions=evpn_result["actions"],
                schema_path=YAML_DIR / "operation_schema.yaml",
                output_dir=OPERATIONS_DIR,
                generated_by="pyats_evpn_underlay_check",
            )


    # =====================================================
    # BGP Underlay（leaf / spine）
    # =====================================================
    @aetest.test
    def bgp_underlay_check(self):
        for dev, dev_info in self.devices.items():
            routing_file = (
                DATA_DIR / "routing_summary" / f"routing_summary_{dev}.log"
            )

            bgp_result = check_single_node_bgp_underlay(
                device_name=dev,
                routing_summary_file=routing_file,

            )

            if not bgp_result["has_issue"]:
                print(f"[{dev}] BGP underlay healthy: {list(self.devices.keys())}")
                continue

            generate_operation_yaml(
                device_name=dev,
                role=dev_info.get("role"),
                protocol=bgp_result["protocol"],              # "BGP"
                issue_summary=bgp_result["issue_summary"],
                issue_detail=bgp_result["issue_detail"],
                affected_peers=bgp_result["affected_peers"],
                actions=bgp_result["actions"],
                schema_path=YAML_DIR / "operation_schema.yaml",
                output_dir=OPERATIONS_DIR,
                generated_by="test_network_health",
            )
    # =====================================================
    # OSPF Underlay（leaf / spine）
    # =====================================================
    @aetest.test
    def ospf_underlay_check(self):
        for dev, dev_info in self.devices.items():

            routing_file = (
                DATA_DIR / "routing_summary" / f"routing_summary_{dev}.log"
            )
            log_file = DATA_DIR / "logs" / f"log_summary_{dev}.log"


            ospf_result = check_single_node_ospf_underlay(
                device_name=dev,
                routing_summary_file=routing_file,

            )


            if not ospf_result["has_issue"]:
                print(f"[{dev}] OSPF underlay healthy: {list(self.devices.keys())}")
                continue


            generate_operation_yaml(
                device_name=dev,
                role=dev_info.get("role"),
                protocol=ospf_result["protocol"],          # "OSPF"
                issue_summary=ospf_result["issue_summary"],
                issue_detail=ospf_result["issue_detail"],
                affected_peers=ospf_result["affected_peers"],
                actions=ospf_result["actions"],
                schema_path=YAML_DIR / "operation_schema.yaml",
                output_dir=OPERATIONS_DIR,
                generated_by="test_network_health",
            )

    # =====================================================
    # INTERFACE (resource / root-cause layer)
    # =====================================================
    @aetest.test
    def interface_check(self):
        for dev, dev_info in self.devices.items():

            # Interface checker uses log file, not routing summary
            log_file = DATA_DIR / "logs" / f"log_summary_{dev}.log"

            interface_result = check_interfaces(
                device_name=dev,
                log_file=log_file,
            )

            if not interface_result["has_issue"]:
                print(f"[{dev}] INTERFACE healthy")
                continue

            generate_operation_yaml(
                device_name=dev,
                role=dev_info.get("role"),
                protocol=interface_result["protocol"],   # "INTERFACE"
                issue_summary=interface_result["issue_summary"],
                issue_detail=interface_result["issue_detail"],
                affected_peers=interface_result["affected_interfaces"],
                actions=interface_result["actions"],
                schema_path=YAML_DIR / "operation_schema.yaml",
                output_dir=OPERATIONS_DIR,
                generated_by="test_network_health",
            )
    # =====================================================
    # AI RCA Analysis (Post-check)
    # =====================================================      
    # class NetworkHealthTest(aetest.Testcase):

    ...

    @aetest.test
    def ai_rca_analysis(self):
        """
        Run AI-based root cause analysis after all protocol checks.
        This step does NOT affect test pass/fail.
        """

        operations_dir = OPERATIONS_DIR
        output_path = OPERATIONS_DIR / "ai_analysis.yaml"

        run_ai_analysis(
            operations_dir=operations_dir,
            output_path=output_path
        )

        print(f"[AI] RCA analysis generated at {output_path}")
