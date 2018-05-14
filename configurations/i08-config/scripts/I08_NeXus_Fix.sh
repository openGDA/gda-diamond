#!/bin/bash

module load global/cluster

qsub -q medium.q@@com06 -pe smp 6 /dls_sw/i08/software/gda/config/scripts/I08_NeXus_Fix_Runner.sh $@
