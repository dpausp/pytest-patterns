import subprocess

def run_pytest(
    test_code: str, *args: str, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]: ...
