# Runtime for the vortex validation on kunanyi: the Anaconda module supplies the pinned
# NumPy 1.26.4 and SciPy 1.11.4; R 4.3.3 with nlme 3.1.171 from the project library.
# Sourced by the PBS scripts with VBASE set (the run directory holding src/, Rlib/, banks).
source /etc/profile >/dev/null 2>&1 || true
module purge
module load Anaconda3/2024.02-1 R/4.3.3-gfbf-2023b
export R_LIBS_USER="$VBASE/Rlib"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 FLEXIBLAS_NUM_THREADS=1
cd "$VBASE/src"
