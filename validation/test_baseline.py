from validation.baseline_validations import validate_sg, validate_gfm, validate_gfl


def test_sg_infinite_bus_exact_equilibrium():
    validate_sg(verbose=False)


def test_gfm_infinite_bus_exact_equilibrium():
    validate_gfm(verbose=False)


def test_gfl_infinite_bus_pll_and_current_injection():
    validate_gfl(verbose=False)
