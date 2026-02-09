conda activate ebspack
spack --version
module use /cvmfs/software.eessi.io/init/modules
module load EESSI/2023.06
~/src/spood/quick_start.sh demo_spood

ls -l ~/demo_spood/
export SPACK_USER_CONFIG_PATH=/home/lercole/demo_spood
export SPACK_USER_CACHE_PATH=/home/lercole/demo_spood/cache
spack load quantum-espresso
OMP_NUM_THREADS=8  pw.x < ~/src/q-e/PW/examples/example01/results/cu.scf.david.in | more
