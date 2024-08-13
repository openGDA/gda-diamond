from reduction import (
    load_angular_calibration,
    ModuleAngularCalibration,
    get_single_angular_calibration,
    BEAMLINE_OFFSET_DEGREES,
    get_angular_calibrations,
    mask_bad_channel_counts,
    get_bins,
    calculate_bin_centres,
    apply_flatfield_correction,
    mask_and_histogram,
)
from unittest.mock import patch, mock_open
import pytest
import numpy as np


def test_parse_angular_calibration_file():
    data = "module 0 center 6.400E+02 +- 0.00E+00 conversion 6.5559E-05 +- 6.86E-09 offset 0.00000 +- 0.00014"
    with patch("builtins.open", mock_open(read_data=data)):
        assert load_angular_calibration("")[0] == ModuleAngularCalibration(
            centre=pytest.approx(640),
            conversion=pytest.approx(6.5559e-05),
            conversion_err=pytest.approx(6.86e-09),
            offset=pytest.approx(0.0),
            offset_err=pytest.approx(0.00014),
        )


def test_get_single_angular_calibration():
    calib = ModuleAngularCalibration(
        centre=640,
        conversion=1e-4,
        conversion_err=0,
        offset=90,
        offset_err=0,
    )

    fake_encoder_position = 12.3456

    result = get_single_angular_calibration(calib, fake_encoder_position)

    # If we're interested in the "central" module, then conversion should
    # be irrelevant, should just return the offset (+beamline offset)
    assert result[640] == pytest.approx(
        90 + BEAMLINE_OFFSET_DEGREES + fake_encoder_position
    )

    # TODO: is there a useful test we can do with non-central modules that doesn't
    # just repeat the formula in the code?


def test_get_angular_calibrations():
    with patch("reduction.get_single_angular_calibration") as mock_get_single_calib:
        mock_get_single_calib.side_effect = lambda mod, *a, **k: np.array(
            [mod], dtype=np.int64
        )

        # 5 possible modules in the calibration file, but only 4 modules present
        # (missing module id 2)
        result = get_angular_calibrations({i: i for i in range(5)}, [0, 1, 3, 4], 0.0)
        assert (result == np.array([0, 1, 3, 4])).all()


def test_mask_bad_channel_counts():
    data = np.array([100, 200, 300, 400, 500, 600, 700, 800])
    bad_channels = [1, 3, 7]
    result = mask_bad_channel_counts(data, bad_channels)
    assert np.allclose(result, np.array([100, 0, 300, 0, 500, 600, 700, 0]))


def test_get_bins():
    angles = np.array([0.05, 0.2, 0.4, 0.55])
    result = get_bins(angles, 0.1)
    assert np.allclose(result, np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]))


def test_calculate_bin_centres():
    bins = np.array([0, 0.1, 0.2, 0.5, 0.6])
    result = calculate_bin_centres(bins)
    assert np.allclose(result, np.array([0.05, 0.15, 0.35, 0.55]))


def test_apply_flatfield_correction():
    data = np.array([100, 200, 300, 0, 700, 0, 0, 0, 0, 0])
    flat_field = np.array(
        [1, 2, 1, 0, 0, 1, 0, 0, 0, 5]
    )  # Mean = 1 is important for this test

    result = apply_flatfield_correction(data, flat_field)

    assert np.allclose(result, np.array([100, 100, 300, 0, 0, 0, 0, 0, 0, 0]))


def test_apply_flatfield_correction_scaling():
    # Total counts: 1500
    data = np.array([100, 200, 300, 400, 500])

    # Dummy test setup: "sensitive" bins count 3x more events than "insensitive" ones
    # during a flat-field image
    insensitive = 5
    average = 10
    sensitive = 15

    flat_field = np.array([insensitive, sensitive, insensitive, sensitive, average])

    assert flat_field.mean() == pytest.approx(average)

    result = apply_flatfield_correction(data, flat_field)

    assert np.allclose(
        result,
        np.array(
            [
                # Counted 100 events in an insensitive bin (5), if this was a bin
                # with mean sensitivity (10) it would have counted 200 events.
                200,
                133.333333,
                600,
                266.666666,
                # Bin with precisely average sensitivity shouldn't have "counts" changed.
                500,
            ]
        ),
    )

    # Note that the total counts across the entire image may be different after flat-field correction
    assert data.sum() == pytest.approx(1500)
    assert result.sum() == pytest.approx(1700)


def test_mask_and_histogram():
    bad_channels = [2]
    counts = np.array([100, 200, 300, 400, 500])
    angles = np.array([1.001, 1.002, 3.001, 3.002, 5.001])
    bins = np.array([0, 1, 2, 3, 4, 5, 6])
    result = mask_and_histogram(counts, angles, bad_channels, bins)
    assert np.allclose(result, np.array([0, 300, 0, 400, 0, 500]))
