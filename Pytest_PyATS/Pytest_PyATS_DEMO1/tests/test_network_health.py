from pyats import aetest
from pathlib import Path
import sys

# =====================================================
# 基本路径
# =====================================================
from pyats import aetest
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"

sys.path.insert(0, str(SRC_DIR))

YAML_DIR = BASE_DIR / "yaml"
DATA_DIR = BASE_DIR / "data"
OPERATIONS_DIR = BASE_DIR / "operations"


# =====================================================
# imports（统一 utils，不再用 src.utils）
# =====================================================
from utils.testbed_loader import load_devices_from_testbed

from utils.check_ospf_bgp_evpn import (
    check_spine_leaf_evpn,
    check_single_node_bgp_underlay,
    check_single_node_ospf_underlay,
)

from utils.load_input_expected import (
    load_expected_yaml,
    load_issue_actions_by_protocol,
    generate_operation_yaml,
)

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
        

    # =====================================================
    # EVPN（只检查 leaf）
    # =====================================================
    @aetest.test
    def evpn_check(self):
        for dev, dev_info in self.devices.items():

            routing_file = (
                DATA_DIR / "routing_summary" / f"routing_summary_{dev}.log"
            )

            evpn_result = check_spine_leaf_evpn(
                device_name=dev,
                routing_summary_file=routing_file,
                #expected_nodes=self.expected_nodes,
                #rules_by_protocol=self.rules_by_protocol,
            )

            if not evpn_result.get("has_issue"):
                #self.logger.info(f"[{dev}] BGP underlay healthy")
                print(f"[{dev}] EVPN underlay healthy: {list(self.devices.keys())}")
                continue

            generate_operation_yaml(
                device_name=dev,
                role=dev_info.get("role"),
                protocol="EVPN",
                issue_summary=list(evpn_result["issue_detail"].values()),
                issue_detail=None,
                affected_peers=list(evpn_result["issue_detail"].keys()),
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

            # generate_operation_yaml(
            #     device_name=dev,
            #     role=dev_info.get("role"),
            #     protocol="BGP",
            #     issue_summary=list(bgp_result["bgp_issues"].values()),
            #     issue_detail=None,
            #     affected_peers=list(bgp_result["bgp_issues"].keys()),
            #     actions=bgp_result["actions"],
            #     schema_path=YAML_DIR / "operation_schema.yaml",
            #     output_dir=OPERATIONS_DIR,
            #     generated_by="pyats_bgp_underlay_check",
            # )
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

            # generate_operation_yaml(
            #     device_name=dev,
            #     role=dev_info.get("role"),
            #     protocol="OSPF",
            #     issue_summary=list(ospf_result["ospf_issues"].values()),
            #     issue_detail=None,
            #     affected_peers=[
            #         k for k in ospf_result["ospf_issues"].keys()
            #         if k != "_log_"
            #     ],
            #     actions=ospf_result.get("actions", []),
            #     schema_path=YAML_DIR / "operation_schema.yaml",
            #     output_dir=OPERATIONS_DIR,
            #     generated_by="pyats_ospf_underlay_check",
            # )
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

