
from pathlib import Path
import spiceypy as spice

KERNEL_DIR = Path("data/kernels")

KERNELS = [
    "naif0012.tls",
    "pck00011.tpc",
    "moon_de440_250416.tf",
    "moon_pa_de440_200625.bpc",
    "de440s.bsp",
]


def test_all_kernels_exist():
    for filename in KERNELS:
        path = KERNEL_DIR / filename
        assert path.exists(), f"Missing kernel: {filename}"
        assert path.stat().st_size > 0


def test_spice_can_load_kernels():
    spice.kclear()

    try:
        for filename in KERNELS:
            spice.furnsh(str(KERNEL_DIR / filename))

        assert spice.ktotal("ALL") == 5

    finally:
        spice.kclear()
