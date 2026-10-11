# Runtime for the vortex validation on kunanyi: the Anaconda module supplies the pinned
# NumPy 1.26.4 and SciPy 1.11.4; R 4.3.3 with nlme 3.1.171 from the project library.
# Sourced by the PBS scripts with VBASE set (the run directory holding src/, Rlib/, banks).
# Batch jobs on kunanyi do not reliably inherit Lmod: initialise it and its search path here.
export MODULEPATH="${MODULEPATH:-/opt/ohpc/pub/moduledeps/gnu8:/opt/ohpc/pub/modulefiles:/share/apps/modules:/share/apps/eb-modules/all:/share/apps/moduledeps/rosalind/Core}"
type module >/dev/null 2>&1 || source /opt/ohpc/admin/lmod/lmod/init/bash
module purge
module load Anaconda3/2024.02-1 R/4.3.3-gfbf-2023b
export R_LIBS_USER="$VBASE/Rlib"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 FLEXIBLAS_NUM_THREADS=1
cd "$VBASE/src"
