import yaml,re
from pathlib import Path
def load_expected_yaml(path:Path,keyword: str|None=None)->dict:
    if not path.exists():
        raise FileNotFoundError(f"Yaml file not found: {path}")
    
    with open(path,"r") as f:
        data = yaml.safe_load(f)
        #print(data)
        #print(type(data))

    if not data:
        raise ValueError(f"Yaml file is empty!")
    
    if keyword:
        if keyword not in data:
            raise KeyError(f"keyword is '{keyword}' not find in data.keys()")
        # print(data[keyword])
        # print(type(data[keyword]))

        if not isinstance(data[keyword], dict):
            raise TypeError(
                f"Expected '{keyword}' to be dict, got {type(data[keyword]).__name__}"
            )
        return data[keyword]
    return data   
    
def write_expected_yaml(filename: str, data:dict):

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

    print(f"Operation YAML written to: {filename}")    

def build_operation_from_schema(
    *,
    schema_path: Path,
    device: str,
    role: str,
    protocol: str,
    result: dict,
    generated_by: str,
) -> dict:
    """
    Build operation dict strictly based on YAML schema.
    Schema defines structure, Python only fills values.
    """

    # 1. load schema (structure comes from YAML)
    operation_schema = load_expected_yaml(schema_path)

    # 2. shallow copy schema
    operation = operation_schema.copy()

    # 3. fill basic info
    operation["device"] = device
    operation["role"] = role

    # 4. fill issue section
    operation["issue"]["protocol"] = protocol
    operation["issue"]["summary"] = list(result["evpn_issues"].values())
    operation["issue"]["detail"] = result["evpn_detail_issue"]
    operation["issue"]["affected_peers"] = list(result["evpn_issues"].keys())

    # 5. fill actions
    operation["actions"] = result.get("actions", [])

    # 6. metadata
    operation["metadata"]["generated_by"] = generated_by

    return operation   

def load_issue_actions_by_protocol(issue_yaml_dir:Path)->dict: # load the all issues as a dict
    if not issue_yaml_dir.exists():
        raise FileNotFoundError(f"Issue Yaml folder not found: {issue_yaml_dir}")
    
    issue_rules={}
    issues = ["bgp","evpn","interface","ospf"]

    for issue in issues:
        issue_path=issue_yaml_dir/f"issue_actions_{issue}.yaml"
        issue_rules[issue]=load_expected_yaml(issue_path)
    
    return issue_rules   


def match_issue_and_actions(protocol: str, facts: dict, rules_by_protocol: dict):# from protocol to generate dict based on the whole rules.
    """
    Given protocol + facts, return (issue_name, actions)
    If no issue matched, return (None, [])
    """
    rules = rules_by_protocol.get(protocol, {})#get a dict of single rule

    for issue_name, rule in rules.items():
        match = rule.get("match", {})
        matched = True

        for key, expected in match.items():
            if key == "log_error":#if the error is belong to "log error" then compare the log appear in the yaml log_error
                log_text = facts.get("log", "")
                if not re.search(expected, log_text, re.I):
                    matched = False
                    break
            else:
                if facts.get(key) != expected:
                    matched = False
                    break

        if matched:
            # if not isinstance(actions, list):
            #     actions = [str(actions)]
            return issue_name, rule.get("actions", [])

    return None, []

def generate_operation_yaml(
    *,
    device_name: str,
    role: str,
    protocol: str,
    issue_summary: list,
    issue_detail: str | None,
    affected_peers: list,
    actions: list,
    schema_path: Path,
    output_dir: Path,
    generated_by: str,
):
    """
    Generate operation yaml based on operation_schema.yaml
    """

    with open(schema_path, "r") as f:
        operation = yaml.safe_load(f)

    operation["device"] = device_name
    operation["role"] = role

    operation["issue"]["protocol"] = protocol
    operation["issue"]["summary"] = issue_summary
    operation["issue"]["detail"] = issue_detail
    operation["issue"]["affected_peers"] = affected_peers

    operation["actions"] = actions
    operation["metadata"]["generated_by"] = generated_by

    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{device_name}_{protocol.lower()}_operation.yaml"

    with open(out_file, "w") as f:
        yaml.safe_dump(operation, f, sort_keys=False)

    return out_file

def write_exec_yaml(
    *,
    device_name: str,
    role: str,
    evpn_result: dict | None,
    bgp_result: dict | None,
    ospf_result: dict | None,
    output_dir: Path,
):
    """
    只生成【执行用】YAML：
    - 汇总所有 actions
    - 无 issue 不生成
    """

    actions = []

    for result in (evpn_result, bgp_result, ospf_result):
        if result and result.get("actions"):
            actions.extend(result["actions"])

    # 没有任何 action，就不生成文件
    if not actions:
        return None

    exec_yaml = {
        "device": device_name,
        "role": role,
        "actions": sorted(set(actions)),
        "generated_by": "check_ospf_bgp_evpn.py",
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{device_name}_exec.yaml"

    with open(out_file, "w") as f:
        yaml.safe_dump(exec_yaml, f, sort_keys=False)

    return out_file