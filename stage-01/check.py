"""练习包自检（给课程作者用）。

参考实现必须全过；起步代码和故障代码必须失败。
任何一条不满足，说明练习包本身有问题。
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
EXPECTATIONS = [("reference", True), ("practice", False), ("broken", False)]

ok = True
for target, should_pass in EXPECTATIONS:
    done = subprocess.run(
        [sys.executable, "test_agent.py", target], cwd=HERE, capture_output=True
    )
    passed = done.returncode == 0
    good = passed == should_pass
    ok = ok and good
    print(
        f"{'通过' if good else '不符'}  {target:<9} "
        f"期望{'全过' if should_pass else '失败'}，实际{'全过' if passed else '失败'}"
    )

sys.exit(0 if ok else 1)
