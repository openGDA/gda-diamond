from types import TupleType, ListType, FloatType, IntType, StringType
from gda.device import Scannable
from gda.device.scannable.scannablegroup import ScannableGroup

def all_elements_are_scannable(arg):
    for each in arg:
        if not isinstance(each, Scannable):
            return False
    return True

def all_elements_are_list_of_number(arg):
    for each in arg:
        if type(each) != ListType:
            return False
        for item in each:
            if not (type(item) == FloatType or type(item) == IntType):
                return False
    return True

def all_elements_are_list_of_number_or_string(arg):
    for each in arg:
        if type(each) != ListType:
            return False
        for item in each:
            if not (type(item) == FloatType or type(item) == IntType or type(item) == StringType):
                return False
    return True

def all_elements_are_number(arg):
    for each in arg:
        if not (type(each) == FloatType or type(each) == IntType):
            return False
    return True

def all_elements_are_string(arg):
    for each in arg:
        if (type(each) != StringType):
            return False
    return True

def all_elements_are_tuples_of_numbers(arg):
    for each in arg:
        # Check its a tuple or Check all elements of the tuple are numbers
        if (type(each) != TupleType) or not all_elements_are_number(each):
            return False
    return True

def get_adbase(collection_strategy):
    from gda.device.detector.addetector.collectionstrategy import ContinuousAcquisition, EpicsStartStop, SoftwareStartStop
    if isinstance(collection_strategy, (SoftwareStartStop, ContinuousAcquisition, EpicsStartStop)):
        return collection_strategy.getAdBase()
    else:
        return get_adbase(collection_strategy.getDecoratee())

def get_image_mode_decorator(collection_strategy):
    from gda.device.detector.addetector.collectionstrategy import ImageModeDecorator
    if isinstance(collection_strategy, ImageModeDecorator):
        return collection_strategy
    else:
        return get_image_mode_decorator(collection_strategy.getDecoratee())

def parse_tuple_arguments(command, newargs, arg):
    command += "("

    if all_elements_are_scannable(arg):  # parsing (scannable1, scannable2,...) as scannable group
        scannable_group = ScannableGroup()
        scannable_names = []
        for each in arg:
            scannable_group.addGroupMember(each)
            scannable_names.append(each.getName())
            command += ",".join(scannable_names)
            scannable_group.setName("pathgroup")
            newargs.append(scannable_group)

    elif all_elements_are_list_of_number_or_string(arg):  # parsing scannable group's position lists
        newargs.append(arg)
        list_of_lists = []
        for each in arg:
            list_of_lists.append("[" + ",".join([str(x) for x in each]) + "]")
        command += ",".join(list_of_lists)

    elif all_elements_are_number(arg):  # parsing scannable group's position lists
        newargs.append(arg)
        command += ",".join([str(x) for x in arg])

    elif all_elements_are_tuples_of_numbers(arg):  # This case is to fix BLIX-206 when using a scannable group with a tuple of tuples of positions
        newargs.append(arg)
        list_of_tuples = []
        for each in arg:
            list_of_tuples.append("(" + ",".join([str(x) for x in each]) + ")")
        command += ",".join(list_of_tuples)

    elif all_elements_are_string(arg):
        newargs.append(arg)
        command += ",".join(arg)

    else:
        raise TypeError, "Only tuple of scannables, tuple of numbers, tuple of lists of numbers or Strings, list of numbers, or tuple of Strings are supported."

    command += ") "
    return command, newargs

def save_detector_settings_before_scan(arg):
    adbase = get_adbase(arg.getCollectionStrategy())
    image_mode = adbase.getImageMode()
    num_images = adbase.getNumImages()
    return adbase, image_mode, num_images

def restore_detector_setting_after_scan(adbase, image_mode, num_images):
    adbase.setImageMode(image_mode)
    adbase.setNumImages(num_images)

def set_number_of_images_to_collect_per_scan_data_point(command, newargs, args, i, image_mode_decorator):
    if i < len(args) - 1:  # more than 2 arguments following detector
        if isinstance(args[i], int) and isinstance(args[i + 1], (int, float)):
            image_mode_decorator.setImageMode(1)  # this will make sure metadata in detector setting are correct as image_mode_decorator setting comes after metadata are collected
            image_mode_decorator.setNumberOfImagesPerCollection(args[i])  # support the miscan command - first input after detector is number of images per data point
        elif isinstance(args[i], float) and isinstance(args[i + 1], (int, float)):
            raise TypeError, "Number of images to collect per scan data point must be int type."
        elif isinstance(args[i], float) and not isinstance(args[i + 1], (int, float)):
            image_mode_decorator.setImageMode(0)  # single image mode
            image_mode_decorator.setNumberOfImagesPerCollection(1)
    elif i == len(args) - 1:  # followed by only one argument - must be exposure time
        image_mode_decorator.setImageMode(0)  # single image mode
        image_mode_decorator.setNumberOfImagesPerCollection(1)
        newargs.append(args[i])
    command += str(args[i]) + " "
    return command, newargs

def parse_detector_arguments(command, newargs, args, i, arg):
    image_mode_decorator = get_image_mode_decorator(arg.getCollectionStrategy())
    if image_mode_decorator is not None:
        command, newargs = set_number_of_images_to_collect_per_scan_data_point(command, newargs, args, i, image_mode_decorator)
    else:
        newargs.append(args[i])  # single image per data point
        command += str(args[i])  # exposure time is the last one in the scan command
    return command, newargs

def parse_other_arguments(command, arg):
    if isinstance(arg, Scannable):
        command += arg.getName() + " "
    if type(arg) == IntType or type(arg) == FloatType:
        command += str(arg) + " "
    return command
