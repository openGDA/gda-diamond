from org.apache.poi.xssf.usermodel import XSSFWorkbook
from org.apache.poi.openxml4j.opc import OPCPackage
from org.apache.poi.ss.usermodel.Cell import CELL_TYPE_STRING
from collections import OrderedDict
import java

import re
import logging
grid_position_re = re.compile(r'([A-Z]+)([0-9]+)')
step_size_re = re.compile(r'([0-9]*\.?[0-9]*)mm')

class ExcelLoader(object):
    def __init__(self, sheet=0, row_offset=0, column_offset=0, columns=(), key=None, others=None):
        self._logger = logging.getLogger('gda.i22.excelLoader')
        self._sheet = sheet
        self._row = row_offset
        self._column = column_offset
        if not columns:
            raise ValueError("Column names are required")
        self._columns = [_key_func(col) for col in columns]
        self._key = key or self._columns[0][0]
        self._others = others or {}

    def load(self, filename):
        self._logger.info('Loading samples from %s', filename)
        opc = OPCPackage.open(filename)
        workbook = XSSFWorkbook(opc)
        sheet = workbook.getSheetAt(self._sheet)
        return Container(dict(self.container_info(sheet)), list(self.parse_container(sheet)))
    
    def container_info(self, sheet):
        for key, (loc, func) in self._others.items():
            loc = parse_grid(loc)
            cell = (sheet.getRow(loc[1]-1) # 0 indexed
                    .getCell(ord(loc[0])-65))
            if cell is None:
                yield key, None
            else:
                yield key, func(cell)

    def parse_container(self, sheet):
        print('Reading from sheet: {}'.format(sheet.getSheetName()))
        for i in range(self._row, sheet.getLastRowNum()):
            self._logger.debug('Loading sample from row %d of %d', i, sheet.getLastRowNum())
            try:
                sample = self.parse_sample(sheet.getRow(i))
                if sample[self._key]:
                    yield sample
            except ValueError as ve:
                self._logger.error("Error reading row %d", i, exc_info=True)
                break

    def parse_sample(self, row):
        if row is None:
            raise ValueError('Null row found')
        last_column = self._column + len(self._columns)
        cells = (row.getCell(i) for i in range(self._column, last_column))
        key_func_cell = zip(self._columns, cells)
        return {key: func(cell) for ((key, func), cell) in key_func_cell}
    
class Container(object):
    def __init__(self, details, samples):
        self._samples = samples
        self._info = details

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._samples[key]
        else:
            return self._info[key]

    def __iter__(self):
        return iter(self._samples)

def _key_func(column):
    return column if isinstance(column, tuple) else (column, string_value)

def string_value(cell):
    if cell is None: return None
    cell.setCellType(CELL_TYPE_STRING)
    return cell.getStringCellValue()

def float_value(cell):
    if cell is None: return None
    try:
        return cell.getNumericCellValue()
    except java.lang.IllegalStateException as ise:
        r = cell.getRowIndex()
        c = cell.getColumnIndex()
        raise ValueError("Can't get float value from cell {}{}".format(chr(65+c), r))

def int_value(cell):
    if cell is None: return None
    value = string_value(cell)
    return int(value) if value else None

def grid_position(cell):
    value = string_value(cell)
    if not value:
        return None
    return parse_grid(value)

def parse_grid(value):
    match = grid_position_re.match(value.upper())
    if not match:
        raise ValueError(value + " is not a valid grid position")
    letter, number = match.groups()
    return letter, int(number)

def is_isotropic(cell):
    return string_value(cell) == 'I'

def is_map(cell):
    return string_value(cell) == 'Y'

def step_size(cell):
    value = string_value(cell)
    if not value:
        return None
    match = step_size_re.match(value)
    if not match:
        raise ValueError(value + " is not a valid step size")
    size, = match.groups()
    return float(size)

grid_loader = ExcelLoader(
        sheet=1, # Which sheet to read from
        row_offset=17, # The number of rows to skip when reading samples
        column_offset=1, # The number of columns to skip when reading samples
        columns=( # sequence or field names or (name, converter) pairs
            ("position", grid_position), 
            'name', 
            'type', 
            ('background', grid_position), 
            ('isotropic', is_isotropic),
            ('map', is_map),
            ('step', step_size)
        ),
        key='position', # field used to determine if sample is present
        others={
            'energy':('J12', float_value),
            'camera_length': ('K12', string_value),
            'q_covered': ('L12', string_value),
            'holder': ('C15', string_value),
            'i_vs_q': ('C16', string_value),
            'i_vs_chi': ('E16', string_value),
            'visit': ('D3', string_value),
        },
)

capillary_loader = ExcelLoader(
        sheet=0, # Which sheet to read from
        row_offset=14, # The number of rows to skip when reading samples
        column_offset=1, # The number of columns to skip when reading samples
        columns=( # sequence or field names or (name, converter) pairs
            ("position", int_value), 
            'name', 
            'type', 
            ('background', int_value), 
        ),
        key='position', # field used to determine if sample is present
        others={
            'energy':('J12', float_value),
            'camera_length': ('K12', string_value),
            'q_covered': ('L12', string_value),
            'holder': ('C12', string_value),
            'i_vs_q': ('C13', string_value),
            'visit': ('D3', string_value),
        },
)
