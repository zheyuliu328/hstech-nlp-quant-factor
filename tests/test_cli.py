import os, subprocess, sys
import pytest

def run(args, env=None):
    env = {**os.environ, **(env or {})}
    p = subprocess.run([sys.executable, "src/data_pipe.py"] + args,
                       env=env, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr

@pytest.mark.skipif(os.getenv("ER_API_KEY") is None, reason="ER_API_KEY not set")
def test_estimate_only_ok():
    code, out = run(["--symbols","0700.HK","--recent_pages","2","--estimate_only"])
    assert code == 0
    assert "Estimated" in out

@pytest.mark.skipif(os.getenv("ER_API_KEY") is None, reason="ER_API_KEY not set")
def test_token_cap_stops():
    code, out = run(["--symbols","0700.HK","--years","2024","2023","--archive_pages","3","--token_cap","10"])
    assert code != 0
    assert "token_cap" in out

@pytest.mark.skipif(os.getenv("ER_API_KEY") is None, reason="ER_API_KEY not set")
def test_env_missing_fails():
    env = dict(os.environ)
    env.pop("ER_API_KEY", None)
    # 临时移除 .env 文件的影响
    env["ER_API_KEY"] = ""
    code, out = run(["--symbols","0700.HK","--recent_pages","1"], env=env)
    assert code != 0 and "ER_API_KEY" in out
