import math;
from gda.device.scannable.scannablegroup import ScannableGroup

class ScanCreator:
    """Class containing methods to create scannable groups and to calculate
    list of tuples according to user-defined functions
    """
    def __init__(self, start_val, end_val, step, scannable_func_list):

        self.scannable_func_list = scannable_func_list
        self.start_val = start_val
        self.end_val = end_val
        self.step = step
        self.range = self.calculate_range()
        self.tuple_list = self.convert_range_to_tuple_list()

    def calculate_range(self):
        """Calculate a range of values determined by start_val, end_val and step"""
        range_list = []

        if float(self.step) == 0.0:
            raise ValueError("Step size should not be 0!")
        if self.start_val == self.end_val:
            raise ValueError("Values for start and end should be different!")

        step = abs(self.step)
        number_of_steps = abs(int(math.floor(abs(self.end_val - self.start_val) / self.step))) + 1
        print "Steps: {0}".format(number_of_steps)

        range_val = float(self.start_val)
        # Change the sign of the step if the user has put in something counter-intuitive
        if ((self.end_val < self.start_val and step > 0)
           or (self.end_val > self.start_val and step < 0)):
            step *= -1

        for i in range(number_of_steps):
            range_list.append(range_val)
            range_val += step

        return range_list

    def convert_range_to_tuple_list(self):
        """ Convert the object's range list to a list of tuples"""
        return [(val,) for val in self.range]

    def create_group_and_tuples(self):
        """Function to create a scannable group from scannables passed in"""
        # If scan_group has already been defined in the namespace, remove scannables
        global scan_group
        if "scan_group" not in globals():
            scan_group = ScannableGroup()
            self.insert_into_namespace("scan_group", scan_group)
        else:
            for member in scan_group.getGroupMembers():
                scan_group.removeGroupMemberByScannable(member)

        # Add the primary scannable to the group
        self.add_scannable_to_group(self.scannable_func_list[0])

        # Add the other list members to the group and append their function values to tuple list
        for scannable, func, scannable_start_val in self.scannable_func_list[1:]:
            self.add_scannable_to_group(scannable)
            self.append_function_values(func, scannable_start_val)

        # Configure the scan_group
        scan_group.setName("scan_group")
        scan_group.configure()
        tuples = tuple(self.tuple_list)
        self.insert_into_namespace("scan_points", tuples)
        return tuples

    def add_scannable_to_group(self, item):
        """Helper function to add a scannable to a scannable group"""
        if self.is_single_scannable(item):
            scan_group.addGroupMember(item)
        else:
            raise TypeError("List member {0} is not a single scannable that can be added to a group"
                            .format(item))

    def is_single_scannable(self, input):
        """Helper function which returns true if input object is a scannable but not a scannable group"""
        if (isinstance(input, gda.device.Scannable)
            and not isinstance(input, gda.device.scannable.scannablegroup.ScannableGroup)):
            return True
        return False

    def append_function_values(self, function_name, scannable_start_val):
        """Inputs: [function_name].
         For each value in range list, append value calculated according to function_name to tuple
         with first value corresponding to scannable_start_value
         """
        constant = 0
        if scannable_start_val is not None:
            constant = scannable_start_val - function_name(float(self.start_val))
        self.tuple_list = [tup + (function_name(tup[0]) + constant,) for tup in self.tuple_list]

    def insert_into_namespace(self, name, value, name_space=globals()):
       """Takes variable name (name) and assigns a value (value) to it in a namespace
       (name_space)
       """
       name_space[name] = value
       print "{0} created in namespace".format(name)

