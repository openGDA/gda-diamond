#! /usr/bin/env python
import h5py
import scisoftpy as dnp
import argparse

PHI = "phi"
KAPPA = "kappa"
THETA = "theta"
MU = "mu"
DELTA_OFFSET = "delta_offset"
DELTA = "delta"
GAMMA = "gamma"

FAST = "fast"
SLOW = "slow"
ORIGIN = "origin"
UNITS = "units"
PIXEL_SIZE = "size"
CALIBRATION_SCAN = "scan"
CALIBRATION_TIME = "time"
DETECTOR_SIZE = "det_size"

DEPENDS_ON = { PHI : "/entry1/sample/transformations/kappa",
        KAPPA : "/entry1/sample/transformations/theta",
        THETA : "/entry1/sample/transformations/mu",
        MU : ".",
        DELTA_OFFSET : "/entry1/instrument/transformations/delta",
        DELTA : "/entry1/instrument/transformations/gamma",
        GAMMA : "." }

VECTORS = { PHI : [0.0, 1.0, 0.0],
        KAPPA : [0.0, 0.64278761, -0.76604443],
        THETA : [0.0, 1.0, 0.0],
        MU : [1.0, 0.0, 0.0],
        DELTA_OFFSET : [0.0, -1.0, 0.0],
        DELTA : [0.0, 1.0, 0.0],
        GAMMA : [1.0, 0.0, 0.0] }

#TODO: extract from optional geometry.xml file?
PILATUS1_GEOMETRY = { FAST : [0.716072811, -0.013563674, -0.697893800],
        SLOW : [0.009045434, 0.999907551, -0.010152305],
        ORIGIN : [50.137024325, -19.798292807, 522.266223546],
        PIXEL_SIZE : 0.172,
        UNITS : "mm",
        CALIBRATION_TIME : "2015-10-07 13:16:01",
        CALIBRATION_SCAN : 535376,
        DETECTOR_SIZE : [487, 195] }

EVOLT_TO_JOULE = 1.60217657e-19
PLANCK = 6.62606957e-34
LIGHTSPEED = 299792458.

class struct:
    def __init__( self, **kwds ):
        self.__dict__.update( kwds )
    def __str__( self ):
        return self.__dict__.__str__()


def create_group( parent, name, nxclass ):
    g = parent.create_group( name )
    g.attrs.create( "NX_class", nxclass )
    return g

def create_dataset( parent, name, data, attributes = {} ):
    try:
        len(data)
    except TypeError:
        data = dnp.array([data])
    ds = parent.create_dataset( name, data=data )
    for (k, v) in attributes.items():
        ds.attrs.create(k, v)

def extract_useful_stuff( file_name ):
    f = dnp.io.load( file_name )
    ub = [ f.metadata.UB11, f.metadata.UB12, f.metadata.UB13,
            f.metadata.UB21, f.metadata.UB22, f.metadata.UB23,
            f.metadata.UB31, f.metadata.UB32, f.metadata.UB33 ]
    lattice = [ f.metadata.a, f.metadata.b, f.metadata.c,
            f.metadata.alpha1, f.metadata.alpha2, f.metadata.alpha3 ]
    data = { PHI : f.kphi,
            KAPPA : f.kap,
            THETA : f.kth,
            MU : f.kmu,
            DELTA_OFFSET : f.metadata.delta_axis_offset,
            DELTA : f.kdelta,
            GAMMA : f.kgam }
    retrieved = [ "kphi", "kap", "kth", "kmu", "kdelta", "kgam", "metadata" ]
    other = [ x for x in f.keys() if x not in retrieved ]
    other_data = { x : f[x] for x in other }
    retrieved = [ "UB11", "UB12", "UB13", "UB21", "UB22", "UB23", "UB31", "UB32", "UB33",
            "a", "b", "c", "alpha1", "alpha2", "alpha3",
            "delta_axis_offset", "cmd" ]
    retrieved += other
    other = [ x for x in f.metadata.keys() if x not in retrieved ]
    other_metadata = { x : f.metadata[x] for x in other }
    filepaths = []
    template = f.metadata.pilatus100k_path_template
    for p in f.path:
        filepaths.append( template % p )
    return struct( transmission = f.metadata.Transmission,
            ub = ub,
            lattice = lattice,
            axis_data = data,
            pilatus_images = filepaths,
            pilatus_counttime = f.count_time,
            other_data = other_data,
            other_metadata = other_metadata,
            scan = f.metadata.cmd,
            energy = f.metadata.en )

def write_nexus( file_name, data, overwrite ):
    flags = "w" if overwrite else "w-"
    nf = h5py.File( file_name, flags )
    try:
        entry = create_group( nf, "entry1", "NXentry" )
        create_dataset( entry, "scan_command", data.scan )
        instrument = create_group( entry, "instrument", "NXinstrument" )
        atten = create_group( instrument, "attenuator", "NXattenuator" )
        create_dataset( atten, "attenuator_transmission", data.transmission )
        pilatus = create_group( instrument, "pil100k", "NXdetector" )
        create_dataset( pilatus, "image_data", data.pilatus_images, {"data_filename" : 1} )
        create_dataset( pilatus, "count_time", data.pilatus_counttime )
        create_dataset( pilatus, "depends_on", "/entry1/instrument/pil100k/transformations/origin_offset" )
        det_origin = create_group( pilatus, "transformations", "NXtransformations" )
        create_dataset( det_origin, "origin_offset", 1,
                { "depends_on" : "/entry1/instrument/transformations/delta_offset",
                    "units" : PILATUS1_GEOMETRY[UNITS],
                    "offset" : [0.0, 0.0, 0.0],
                    "offset_units" : "mm",
                    "transformation_type" : "translation",
                    "vector" : PILATUS1_GEOMETRY[ORIGIN] } )
        module = create_group( pilatus, "module", "NXdetector_module" )
        create_dataset( module, "data_origin", [0, 0] )
        create_dataset( module, "data_size", PILATUS1_GEOMETRY[DETECTOR_SIZE] )
        create_dataset( module, "fast_pixel_direction", PILATUS1_GEOMETRY[PIXEL_SIZE],
                { "depends_on" : "/entry1/instrument/pil100k/module/module_offset",
                    "offset" : [0.0, 0.0, 0.0],
                    "transformation_type" : "translation",
                    "units" : PILATUS1_GEOMETRY[UNITS],
                    "vector" : PILATUS1_GEOMETRY[FAST] } )
        create_dataset( module, "slow_pixel_direction", PILATUS1_GEOMETRY[PIXEL_SIZE],
                { "depends_on" : "/entry1/instrument/pil100k/module/module_offset",
                    "offset" : [0.0, 0.0, 0.0],
                    "transformation_type" : "translation",
                    "units" : PILATUS1_GEOMETRY[UNITS],
                    "vector" : PILATUS1_GEOMETRY[SLOW] } )
        create_dataset( module, "module_offset", 0.0,
                { "depends_on" : "/entry1/instrument/pil100k/transformations/origin_offset",
                    "offset" : [0.0, 0.0, 0.0],
                    "transformation_type" : "translation",
                    "units" : PILATUS1_GEOMETRY[UNITS],
                    "vector" : [0.0, 0.0, 0.0] } )

        transformations = create_group( instrument, "transformations", "NXtransformations" )
        for axis in [ DELTA_OFFSET, DELTA, GAMMA ]:
            attributes = { "transformation_type" : "rotation",
                    "units" : "deg",
                    "depends_on" : DEPENDS_ON[axis],
                    "vector" : VECTORS[axis] }
            create_dataset( transformations, axis, data.axis_data[axis], attributes )
        for (ds_name, ds_data) in data.other_data.items():
            g = create_group( instrument, ds_name, "NXpositioner" )
            create_dataset( g, ds_name, ds_data )

        sample = create_group( entry, "sample", "NXsample" )
        ubmat = dnp.array( data.ub )
        ubmat.shape = [3, 3]
        ubmat = dnp.array( [[1, 0, 0], [0, 0, -1], [0, 1, 0]] ).dot( ubmat )
        ubmat.shape = [1, 3, 3]
        create_dataset( sample, "orientation_matrix", ubmat )
        create_dataset( sample, "unit_cell", data.lattice, {"angle_units" : "deg", "length_units" : "angstrom"} )
        create_dataset( sample, "depends_on", "/entry1/sample/transformations/phi" )
        beam = create_group( sample, "beam", "NXbeam" )
        create_dataset( beam, "incident_energy", data.energy, {"units":"keV"} )
        wavelength = 1e9 * PLANCK * LIGHTSPEED / (data.energy * 1000 * EVOLT_TO_JOULE)
        create_dataset( beam, "incident_wavelength", wavelength, {"units" : "nm"} )
        sample_transformations = create_group( sample, "transformations", "NXtransformations" )
        for axis in [ PHI, KAPPA, THETA, MU ]:
            attributes = { "transformation_type" : "rotation",
                    "units" : "deg",
                    "depends_on" : DEPENDS_ON[axis],
                    "vector" : VECTORS[axis] }
            create_dataset( sample_transformations, axis, data.axis_data[axis], attributes )

        metadata = create_group( entry, "before_scan", "NXcollection" )
        for (ds_name, ds_data) in data.other_metadata.items():
            #cannot be exactly like a real Nexus file because we have lost group information
            g = create_group( metadata, ds_name, "NXpositioner" )
            create_dataset( g, ds_name, ds_data )
    finally:
        nf.flush()
        nf.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument( "files", nargs="+", help="list of file names to process" )
    parser.add_argument( "-t", "--trunc", const=True, default=False, action="store_const",
            help="truncate (overwrite) existing nexus files" )
    parser.add_argument
    args = parser.parse_args()
    for f in args.files:
        #replace last .dat with .nxs
        nxs = f[::-1].replace( "tad.", "sxn.", 1 )[::-1]
        data = extract_useful_stuff( f )
        write_nexus( nxs, data, args.trunc )
    print "Done"

if __name__ == "__main__":
    main()
