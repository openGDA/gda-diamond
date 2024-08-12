import h5py
import numpy as np
import math
from dataclasses import dataclass
from time import perf_counter
from contextlib import contextmanager
import argparse
from typing import Optional

# Each module is divided into this many pixels.
STRIPS_PER_MODULE = 1280

# Beamline-specific offset. Determined experimentally I believe. Constant for all modules.
# TODO: determine what it is for the new Mythen3 on i11.
BEAMLINE_OFFSET_DEGREES = 0.0

# Default rebinning step size.
DEFAULT_BIN_STEP = 0.004

# If modules are not specified on command line, assume the detector is fully functional
# and made up of 28 modules, in order.
DEFAULT_NUM_MODULES = 28
DEFAULT_MODULES = np.arange(DEFAULT_NUM_MODULES, dtype=np.int64)

DEFAULT_COUNTER = 0


@contextmanager
def timing(name):
    start = perf_counter()
    try:
        yield
    finally:
        end = perf_counter()
        print(f"[{name}] took {(end - start)*1000.0:.3f} ms")


def load_raw_data(
    file_path: str,
    flatfield_not_data: bool,
    raw_data_limits: tuple[Optional[int], Optional[int]],
) -> np.ndarray:
    low_limit, high_limit = raw_data_limits

    with h5py.File(file_path, "r") as f:
        # Note: [()] causes data to be copied to a numpy array rather than just referencing
        # a h5py dataset (which goes out of scope after the context manager exits)
        # Axes at this level are:
        #     x_dim: always 1
        #     y_dim: CHANNELS_PER_MODULE * NUM_MODULES
        #     counters: (always 3 counters).
        # Note: do not just sum the counters. The 3 counters can be used in different ways.
        # - Short-term hack: just use the first counter
        # - TODO: Medium-term: add a CLI option to this script to select the counter to use (0, 1 or 2)
        # - TODO: Long-term: in discussion with scientists, implement the different modes
        #                    which the counters can be used in.
        if flatfield_not_data:
            return f["flatfield"][low_limit:high_limit][()]

        return f["entry"]["data"]["data"][0, low_limit:high_limit, DEFAULT_COUNTER][()]


@dataclass
class ModuleAngularCalibration:
    centre: float  # Central module index
    conversion: float
    conversion_err: float
    offset: float  # Degrees
    offset_err: float


def load_angular_calibration(filepath: str) -> dict[int, ModuleAngularCalibration]:
    """
    Returns a mapping channel_id -> ModuleAngularCalibration
    """
    calibrations = {}
    with open(filepath) as f:
        for line in f:
            if line := line.strip():
                elements = line.split()

                # Format:
                # module 9 offset 22.999546717106472 conv -6.562536956058939e-05 center 673.1167192524566
                calib = ModuleAngularCalibration(
                    centre=float(elements[7]),
                    conversion=float(elements[5]),
                    conversion_err=0.0,
                    offset=float(elements[3]),
                    offset_err=0.0,
                )

                calibrations[int(elements[1])] = calib

    return calibrations


def load_bad_channels(
        filepath: str,
        modules: np.ndarray,
        raw_data_limits: tuple[Optional[int], Optional[int]],
        ) -> np.ndarray:
    """
    File format is either
        one module per line, with module identifier followed by filepath to the bad channels file
        or a combined bad channels file with one line per bad channel
    """
    try:
        bad_chan_filepath_from_module_id = {}
        with open(filepath) as f:
            for line in f:
                module_id, bad_chan_filepath = line.split()
                bad_chan_filepath_from_module_id[int(module_id)] = bad_chan_filepath
    except:
        return load_int_array_from_file(filepath)

    print("modules", modules)
    bad_channels = []
    # If a module isn't in the module list, it's channels won't be in the data file either, so
    # calculate channel numbers by the modules in use, not the module_id
    for module, module_id in enumerate(modules):
        if module_id in bad_chan_filepath_from_module_id.keys():
            new_bad_channels = load_int_array_from_file(bad_chan_filepath_from_module_id[module_id])
            if len(new_bad_channels) > 0:
                aligned_bad_channels = new_bad_channels + module*STRIPS_PER_MODULE
                bad_channels.append(aligned_bad_channels)

    all_bad_channels = np.concatenate((bad_channels))
    low_limit, high_limit = raw_data_limits
    return all_bad_channels[
        (all_bad_channels >= low_limit if low_limit else True) &
        (all_bad_channels < high_limit if high_limit else True)]


def get_single_angular_calibration(
    calib: ModuleAngularCalibration, encoder: float
) -> np.ndarray:
    """
    Given a set of calibration parameters, return a numpy array
    describing the angle, in degrees, of each pixel in that module

    Ref:
    section 1.1 of "Angular conversion 1-D" by A. Cervellino (ANGCONV_2024.pdf).
    """

    module_conversions = np.arange(STRIPS_PER_MODULE, dtype=np.int64).astype(np.float64)
    module_conversions -= calib.centre
    module_conversions *= calib.conversion
    module_conversions = np.arctan(module_conversions)
    module_conversions = np.rad2deg(module_conversions)

    return module_conversions + calib.offset + BEAMLINE_OFFSET_DEGREES + encoder


def get_angular_calibrations(
    angular_calibration_data: dict[int, ModuleAngularCalibration],
    modules: np.ndarray,
    encoder: float,
) -> np.ndarray:
    """
    Concatenate all angular calibrations into a single array with the same shape as the raw data.

    Need to take care that the angles for each module get concatenated in the same order as specified
    in modules (which will generally be their natural order, but this is not guaranteed,
    and may have gaps for bad modules).
    """
    return np.concatenate(
        [
            get_single_angular_calibration(angular_calibration_data[mod], encoder)
            for mod in modules
        ]
    )


def load_int_array_from_file(filepath: str) -> np.ndarray:
    """
    File format is just a list of integers in a text file, one integer per line.
    """
    return np.loadtxt(filepath, dtype=np.int64, comments="#", usecols=0, ndmin=1)


def mask_bad_channel_counts(
    raw_counts: np.ndarray, bad_channels: np.ndarray
) -> np.ndarray:
    # Copy unnecessary in principle, but seems cleaner to not mutate the input array.
    masked = raw_counts.copy()
    masked[bad_channels] = 0.0
    return masked


def get_bins(angles: np.ndarray, rebin_step) -> np.ndarray:
    """
    Return a suitable set of bin edges for histogramming this data.

    To match old GDA mythen2 behaviour, want start and stop to align with "multiples" of rebin step
    (as far as f.p. arithmetic allows this...).
    """
    start = math.floor(angles.min() / rebin_step) * rebin_step
    stop = math.ceil(angles.max() / rebin_step) * rebin_step
    return np.arange(start=start, stop=stop, step=rebin_step, dtype=np.float64)


def calculate_bin_centres(bin_edges: np.ndarray) -> np.ndarray:
    """
    Returned array has dimensionality one less than the input (edges) array.
    """
    return (bin_edges[1:] + bin_edges[:-1]) / 2.0


def apply_flatfield_correction(
    raw_counts: np.ndarray, raw_flatfield_counts: np.ndarray
) -> np.ndarray:
    """
    Divide raw counts by flatfield counts to get scaled counts.
    Where the flatfield counts are zero, return zero. Then rescale
    by the mean value of flatfield counts to get back to a unit of
    counts.
    """
    return np.divide(
        raw_counts * raw_flatfield_counts.mean(),
        raw_flatfield_counts,
        where=raw_flatfield_counts != 0,
        out=np.zeros(raw_counts.shape),
    )


def mask_and_histogram(
    raw_counts: np.ndarray,
    angles: np.ndarray,
    bad_channels: np.ndarray,
    bins: np.ndarray,
) -> np.ndarray:
    counts = mask_bad_channel_counts(raw_counts, bad_channels)
    histogram, _ = np.histogram(angles, bins, weights=counts)
    return histogram


def load_and_histogram(
    filepath: str,
    flatfield_not_data: bool,
    angles: np.ndarray,
    bad_channels: np.ndarray,
    bins: np.ndarray,
    raw_data_limits: tuple[Optional[int], Optional[int]],
) -> np.ndarray:
    raw_data = load_raw_data(filepath, flatfield_not_data, raw_data_limits)

    # In theory, we could support loading a flat field with a different set of modules compared
    # to the real data. That would add some complexity, and it's not obvious to me that it's
    # scientifically valid to do that.

    if raw_data.shape != angles.shape:
        raise ValueError(
            f"""
The loaded raw data (from '{filepath}') has shape {raw_data.shape}, but expected shape {angles.shape}.

This may be due to bad modules in the detector, which have been removed from the EPICS config.
If a bad module has been removed in EPICS, it also needs to be removed from the modules config file 
(see --modules command line flag).

If bad modules have now been removed, and you get this error referring to the flat-field run,
you should take a new flatfield run with the detector in it's new configuration to match the real data.
""".lstrip()
        )

    return mask_and_histogram(raw_data, angles, bad_channels, bins)


def write_xye(
    bin_centres: np.ndarray,
    histogrammed_counts: np.ndarray,
    histogrammed_count_errors: np.ndarray,
    out_file: str,
) -> None:
    """
    Write out an .xye-formatted file.

    .xye is a simple ASCII 3-column format: x, y, (error in y)

    In our case X is angle, y is counts, and e is error in counts.

    The error is a standard deviation, not a variance.
    """
    combined = np.stack(
        (bin_centres, histogrammed_counts, histogrammed_count_errors), axis=-1
    )
    # np.savetxt can conveniently handle a format that looks just like .xye
    with timing("write .xye"):
        np.savetxt(out_file, combined, fmt="%.6f", delimiter=" ", newline="\n")


@timing("main")
def main(
    data_filepath: str,
    raw_data_limits: tuple[Optional[int], Optional[int]],
    angular_calibration_filepath: Optional[str],
    modules_filepath: Optional[str],
    encoder: float,
    flat_field_filepath: Optional[str],
    bad_channels_filepath: Optional[str],
    out_file: str,
    bin_step: float,
):
    """
    - Reads in a HDF5-formatted raw data file from the mythen3 detector
    - Histograms the data & applies 3 types of corrections:
      * Flat-field
      * Bad-channels
      * Angular calibration
    - Writes a .xye formatted output file

    """
    if modules_filepath:
        modules = load_int_array_from_file(modules_filepath)
    else:
        modules = DEFAULT_MODULES

    if bad_channels_filepath:
        bad_channels = load_bad_channels(bad_channels_filepath, modules, raw_data_limits)
        print(bad_channels)
    else:
        # Bad channels not provided, assume no bad channels.
        bad_channels = np.array([], dtype=np.int64)

    if angular_calibration_filepath:
        calib_dict = load_angular_calibration(angular_calibration_filepath)
        angles = get_angular_calibrations(calib_dict, modules, encoder)
    else:
        # Not doing any angular calibration, create a 1-1 mapping of index in
        # the raw data file -> "angle"
        angles = np.arange(len(modules) * STRIPS_PER_MODULE, dtype=np.int64).astype(
            np.float64
        )

    bins = get_bins(angles, bin_step)

    histogrammed = load_and_histogram(
        data_filepath, False, angles, bad_channels, bins, raw_data_limits
    )
    # Errors ~ poisson counting statistics
    histogrammed_errors = np.sqrt(histogrammed)

    if flat_field_filepath:
        # Load flat-field and bin it using the same bins as the actual data.
        #
        # It is tempting to do the flat-field correction on the raw data
        # rather than histogrammed data, but that would break the property
        # that err = sqrt(counts) for the histogrammed data.
        flatfield_histogrammed = load_and_histogram(
            flat_field_filepath, True, angles, bad_channels, bins, raw_data_limits
        )

        counts = apply_flatfield_correction(histogrammed, flatfield_histogrammed)
        # Assumption: uncertainty due to flatfield counts is insignificant compared to uncertainty in counts.
        # So by applying the same flat field correction to the errors, we keep the relative uncertainty the same.
        count_errors = apply_flatfield_correction(
            histogrammed_errors, flatfield_histogrammed
        )
    else:
        # Flat-field not provided, don't apply flat-field correction.
        counts = histogrammed
        count_errors = histogrammed_errors

    bin_centres = calculate_bin_centres(bins)

    # Make sure we have consistent dimensionality for our XYE data...
    assert (
        bin_centres.shape == counts.shape == count_errors.shape
    ), f"Inconsistent dimensionality: {bin_centres.shape} {counts.shape} {count_errors.shape}"

    write_xye(bin_centres, counts, count_errors, out_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Post-processor for mythen data; converts an uncalibrated .h5 file "
        "written by the detector into a calibrated and corrected .xye ASCII file.",
    )

    parser.add_argument(
        "-d", "--data", help="Path to the HDF5 data file to reduce", required=True
    )
    parser.add_argument(
        "-o", "--out-file", help="Path to write output .xye file", required=True
    )
    parser.add_argument(
        "-a",
        "--angular-calibration",
        help="Path to the angular calibration file. If not provided, don't perform angular calibration.",
        default=None,
        type=str,
    )
    parser.add_argument(
        "-m",
        "--modules",
        help="""Path to a file describing the modules that make up the detector. 

Modules should be listed in the same order that they will appear in the raw data file, which is specified in EPICS config.
This will usually be the natural order of the modules, skipping any bad modules.

If not provided, defaults to a {DEFAULT_NUM_MODULES}-module detector with no bad modules.

Has no effect if -a/--angular-calibration is not provided.
""",
        default=None,
        type=str,
    )
    parser.add_argument(
        "-e",
        "--encoder-position",
        help="Encoder position of the diffractometer circle (added as an offset to all angles). Defaults to zero.",
        default=0.0,
        type=float,
    )
    parser.add_argument(
        "-f",
        "--flat-field",
        help="Path to the HDF5 flat-field data. If not provided, don't perform flat-field correction.",
        default=None,
        type=str,
    )
    parser.add_argument(
        "-b",
        "--bad-channels",
        help="Path to the bad channels file. If not provided, no bad channels are assumed.",
        default=None,
        type=str,
    )
    parser.add_argument(
        "-s",
        "--bin-step",
        help=f"Step size to use when histogramming data. Defaults to {DEFAULT_BIN_STEP} if not provided.",
        default=DEFAULT_BIN_STEP,
        type=float,
    )
    parser.add_argument(
        "--raw-data-low-index",
        help="""Advanced option: truncate raw data to indices between (raw_data_low_index, raw_data_high_index) just after loading.

Used in conjunction with --modules, this can be used to restrict the reduction to a limited subset of mythen3 data.

The number of modules specified in --modules must match the total size of the data between raw_data_low_index and raw_data_high_index.

Default is no truncation.
""",
        default=None,
        type=int,
    )
    parser.add_argument(
        "--raw-data-high-index",
        help="""Advanced option: truncate raw data to indices between (raw_data_low_index, raw_data_high_index) just after loading.

Used in conjunction with --modules, this can be used to restrict the reduction to a limited subset of mythen3 data.

The number of modules specified in --modules must match the total size of the data between raw_data_low_index and raw_data_high_index.

Default is no truncation.
""",
        default=None,
        type=int,
    )

    args = parser.parse_args()

    main(
        data_filepath=args.data,
        raw_data_limits=(args.raw_data_low_index, args.raw_data_high_index),
        angular_calibration_filepath=args.angular_calibration,
        modules_filepath=args.modules,
        encoder=args.encoder_position,
        flat_field_filepath=args.flat_field,
        bad_channels_filepath=args.bad_channels,
        out_file=args.out_file,
        bin_step=args.bin_step,
    )
