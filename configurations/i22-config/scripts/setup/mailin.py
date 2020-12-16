from setup import excel
from itertools import groupby, product

from __main__ import rscan
from gdaserver import saxs_cal, waxs_cal, sample_background, sample_name, title,\
    ncddetectors, GDAMetadata as meta
from mapping_scan_commands import sample

class Mailin(object):
    def __init__(self, capillary_positions, grid_rows, grid_columns, x_motor, y_motor):
        self._caps = capillary_positions
        self._grid = _parse_grid(grid_rows, grid_columns)
#         self._saxs_cal = saxs_cal_file
#         self._waxs_cal = waxs_cal_file
        self._x_motor = x_motor
        self._y_motor = y_motor

    def _load_sample_groups(self, loader, sample_file):
        all_samples = loader.load(sample_file)
        backgrounds = {sample['position']: sample for sample in all_samples if sample['type'].lower() == u'background'}
        samples = {bg: list(samples) 
                   for bg, samples in 
                   groupby(sorted((s for s in all_samples if s['type'].lower() == u'sample'), key=lambda s: s['background']), key=lambda s: s['background'])}
        # missing_backgrounds = set(samples) - set(backgrounds) - set('')
        # if missing_backgrounds:
        #     raise ValueError('Some samples rely on missing backgrounds: ' + ', '.join(str(s['position']) for mb in missing_backgrounds for s in samples[mb]))
    
        return backgrounds, samples, all_samples['visit']

    def run_capillaries(self, filename):
        print 'Running capillary scan'
        backgrounds, samples, visit = self._load_sample_groups(excel.capillary_loader, filename)
        self._run_samples(backgrounds, samples, visit)
    
    def run_grid(self, filename):
        print 'Running grid scan'
        backgrounds, samples, visit = self._load_sample_groups(excel.grid_loader, filename)
        self._run_samples(backgrounds, samples, visit)
    
    def _run_samples(self, backgrounds, sample_specs, visit):
        previous_visit = meta['visit']
        try:
            previous_bg = sample_background.getMetadataValue()
            sample_background.setValue('')
            meta['visit'] = visit
            for bg, samples in sample_specs.items():
                if bg:
                    print('Collect background: {} - {}'.format(self._string_location(bg), backgrounds[bg]['name']))
                    background_file = self._run_sample(backgrounds[bg])
                    if not background_file:
                        print 'Couldn\'t collect background data - skipping associated samples'
                        continue
                    sample_background.setValue(background_file)
                else:
                    sample_background.setValue(previous_bg)
                for sample in samples:
                    print('    Collect sample: {}'.format(self._string_location(sample['position'])))
                    sample_file = self._run_sample(sample)
                    print 'Collected {} for sample {}'.format(sample_file, sample['position'])
        finally:
            meta['visit'] = previous_visit
                
    def _run_sample(self, sample_spec):
        print 'Running sample {} at {}'.format(sample_spec['name'], sample_spec['position'])
        location = sample_spec['position']
        if location in self._caps:
            self._move_to(self._caps[location])
        elif location in self._grid:
            self._move_to(self._grid[location])
        else:
            print 'Unknown position {} for sample {}'.format(location, sample_spec['name'])
            return None
        
        sample_name.setValue(sample_spec['name'])
        title.setValue('{} - {}{}'.format(self._string_location(location), sample_spec['name'], '- background' if sample_spec['type'] == u'Background' else ''))
        if sample_spec.get('map', False):
            if 'step' not in sample_spec:
                print 'Step missing for sample at: ' + self._string_location(location)
            return self._collect_map_data(sample_spec['step'])
        return self._collect_static_data()
    
    def _string_location(self, loc):
        if isinstance(loc, tuple):
            return ''.join(map(str, loc))
        return str(loc)
        
    def _move_to(self, loc):
        x, y = loc
        self._x_motor.moveTo(x)
        self._y_motor.moveTo(y)
    
    def _collect_static_data(self):
        print 'Collecting static data'
        staticscan(ncddetectors, self._x_motor, self._y_motor)
        return lastScanDataPoint().getCurrentFilename()
        
    def _collect_map_data(self, step):
        print 'Collecting map data'
        rscan(self._y_motor, -0.5, 0.5, step, self._x_motor, -0.5, 0.5, step, ncddetectors)
        return lastScanDataPoint().getCurrentFilename()
        
        
        
def _parse_grid(rows, columns):
    return {(r,c): (rows[r],columns[c]) for r, c in product(rows, columns)}
