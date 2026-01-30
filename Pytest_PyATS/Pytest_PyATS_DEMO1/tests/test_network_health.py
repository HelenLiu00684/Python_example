# =====================================================
# basic packet input
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
# imports（use documents under utils to import packets）
# =====================================================
from utils.testbed_loader import load_devices_from_testbed

from utils.check_ospf_bgp_evpn import (
    #check_spine_leaf_evpn,
    check_single_node_bgp_underlay,
    check_single_node_ospf_underlay,
)

from utils.load_input_expected import (
    load_expected_yaml,
    load_issue_actions_by_protocol,
    generate_operation_yaml,
)

# =====================================================
# imports different files for checking files
# =====================================================
from checkers.evpn import check_evpn_neighbors


# =====================================================
# Testcase
# =====================================================
class NetworkHealthTest(aetest.Testcase):

    @aetest.setup
    def setup(self):
        """
        路线 1：
        - pyATS 只做 runner
        - inventory 由我们自己加载
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
        # self.devices == {
        #     "leaf1":  {"role": "leaf"},
        #     "leaf2":  {"role": "leaf"},
        #     "spine1": {"role": "spine"},
        #     }

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
    # BGP Underlay（leaf / spine 都检查）
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
                #expected_nodes=self.expected_nodes,
                #rules_by_protocol=self.rules_by_protocol,
            )

            if not bgp_result["has_issue"]:
                #self.logger.info(f"[{dev}] BGP underlay healthy")
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
    # OSPF Underlay（leaf / spine 都检查）
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
                #log_summary_file=log_file,
                #expected_nodes=self.expected_nodes,
                #rules_by_protocol=self.rules_by_protocol,
            )

            if not ospf_result["has_issue"]:
                #self.logger.info(f"[{dev}] OSPF underlay healthy")
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

