import importlib
import os
import sys
from pathlib import Path

if not os.environ.get("_DFL_NVIDIA_LIBS_READY"):
    _NVIDIA_PACKAGES = [
        "nvidia.cublas",
        "nvidia.cuda_runtime",
        "nvidia.cudnn",
        "nvidia.cufft",
        "nvidia.curand",
        "nvidia.cusolver",
        "nvidia.cusparse",
    ]

    _lib_dirs = []
    for _pkg in _NVIDIA_PACKAGES:
        _spec = importlib.util.find_spec(_pkg)
        if _spec and _spec.origin:
            _lib_dir = Path(_spec.origin).parent / "lib"
            if _lib_dir.is_dir():
                _lib_dirs.append(str(_lib_dir))
                if _pkg == "nvidia.cusolver":
                    _so10 = _lib_dir / "libcusolver.so.10"
                    _so11 = _lib_dir / "libcusolver.so.11"
                    if not _so10.exists() and _so11.exists():
                        _so10.symlink_to("libcusolver.so.11")

    if _lib_dirs:
        _nvidia_path = ":".join(_lib_dirs)

        for _sys_dir in [
            "/usr/lib/wsl/lib",
            "/usr/lib/x86_64-linux-gnu",
            "/usr/lib64",
            "/usr/lib",
            "/usr/local/cuda/lib64",
        ]:
            if Path(_sys_dir, "libcuda.so").exists():
                _nvidia_path += ":" + _sys_dir
                break

        _existing = os.environ.get("LD_LIBRARY_PATH", "")
        os.environ["LD_LIBRARY_PATH"] = _nvidia_path + (":" + _existing if _existing else "")
        os.environ["_DFL_NVIDIA_LIBS_READY"] = "1"
        os.execve(sys.executable, [sys.executable, sys.argv[0]] + sys.argv[1:], os.environ)
