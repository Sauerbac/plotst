"""Physical checks for the gallery's independently integrated HS.273 orbit."""

from pathlib import Path
import runpy

import numpy as np
import pytest


def test_hs273_returns_and_preserves_newtonian_invariants() -> None:
    example = runpy.run_path(str(Path(__file__).resolve().parents[1] / "examples" / "three_body_orbit.py"))
    times, states = example["integrate_orbit"]()
    separations, energy = example["diagnostics"](states)
    positions = states[:, :6].reshape(-1, 3, 2)
    velocities = states[:, 6:].reshape(-1, 3, 2)
    angular_momentum = np.sum(positions[:, :, 0] * velocities[:, :, 1]
                              - positions[:, :, 1] * velocities[:, :, 0], axis=1)

    assert times[0] == 0
    assert times[-1] == example["PERIOD"]
    assert np.all(np.diff(times) > 0)
    assert np.all(np.isfinite(states))
    # Check the state, including velocities, rather than artificially closing a curve.
    assert np.linalg.norm(states[-1] - states[0]) < 3e-6
    assert np.max(np.abs((energy - energy[0]) / energy[0])) < 2e-9
    assert np.max(np.abs(positions.mean(axis=1))) < 1e-10
    assert np.max(np.abs(velocities.sum(axis=1))) < 1e-11
    assert np.max(np.abs(angular_momentum)) < 1e-10
    # Independent rounded values from the linked catalogue, not the integrator.
    assert separations.min() == pytest.approx(0.4533, abs=1e-4)
    assert np.linalg.norm(velocities, axis=2).max() == pytest.approx(1.622, abs=1e-3)
