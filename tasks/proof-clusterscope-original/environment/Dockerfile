FROM aweaiteam/scaleswe:facebookresearch_clusterscope_pr29
WORKDIR /workspace/clusterscope
RUN git clean -fd -e '*.egg-info' -e '.tox' -e '.venv' && git checkout a53cad948d50780e69d2eb82d94e29ee4792f41e -f && git reset --hard HEAD && git checkout -b scaleswe && git config user.email 'scaleswe@example.com' && git config user.name 'scaleswe-engine' && rm -f .git/packed-refs && find .git/refs/heads -type f ! -name 'scaleswe' -delete && rm -rf .git/refs/tags .git/refs/remotes && git reflog expire --expire=now --all && git gc --prune=now --aggressive
