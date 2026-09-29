from validation.mixed_system_validation import (
    validate_mixed_equilibrium,
    validate_mixed_perturbation,
)


def test_mixed_system_steady_dae_operating_point():
    validate_mixed_equilibrium(verbose=False)


def test_mixed_system_recovers_after_small_perturbation():
    validate_mixed_perturbation(verbose=False)
