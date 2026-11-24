#!/bin/bash
# Hidden grader = the dataset's strict grader: the real PR's tests (FAIL_TO_PASS).
mkdir -p /logs/verifier
cd /workspace/clusterscope
git checkout 01a3a6b5811e10fd853b986577fca10ee3ba2d65 -- tests/ 2>/dev/null || \
  curl -fsSL https://raw.githubusercontent.com/facebookresearch/clusterscope/01a3a6b5811e10fd853b986577fca10ee3ba2d65/tests/test_cluster_info.py -o tests/test_cluster_info.py
python -m pytest -q tests/test_cluster_info.py::TestLinuxInfo::test_get_mem_per_node_MB tests/test_cluster_info.py::TestDarwinInfo::test_get_mem_per_node_MB tests/test_cluster_info.py::TestSlurmClusterInfo::test_get_mem_per_node_MB > /logs/verifier/pytest.txt 2>&1
if [ $? -eq 0 ]; then echo 1 > /logs/verifier/reward.txt; else echo 0 > /logs/verifier/reward.txt; fi
tail -5 /logs/verifier/pytest.txt
