#!/bin/bash
# launch the option-(b) runs: reference stretches with synthetic extension, rev1x stretches real-only
cd /root/ingnet-revision
PY=/root/miniconda3/envs/sgwbpe/bin/python
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
R=real/results
run() { # gpu run stretches extra tag
  CUDA_VISIBLE_DEVICES=$1 nohup $PY -u real/option_b_real.py --runs $2 --stretches $3 $4 --out $R/option_b_$5.json > $R/option_b_$5.log 2>&1 &
  echo "launched $5 pid $!"
}
run 0 O3a 0 --synthetic O3a_ref
run 1 O3b 0 --synthetic O3b_ref
run 0 O4a 0 --synthetic O4a_ref
run 1 O3a 1,2,3,4 "" O3a_x
run 0 O3b 1,2,3,4 "" O3b_x
run 1 O4a 1,2,3,4 "" O4a_x
sleep 60; nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv; tail -n 3 $R/*.log
