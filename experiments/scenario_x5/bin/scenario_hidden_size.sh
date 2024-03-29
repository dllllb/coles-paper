for SC_HIDDEN_SIZE in 0064 0160 0480 0800
do
  export SC_SUFFIX="hidden_size__hs_${SC_HIDDEN_SIZE}"
  python ../../metric_learning.py \
      params.device="$SC_DEVICE" \
      params.rnn.hidden_size=${SC_HIDDEN_SIZE} \
      model_path.model="models/x5_mlm__$SC_SUFFIX.p" \
      --conf "conf/dataset.hocon" "conf/mles_params.json"
  python ../../ml_inference.py \
      params.device="$SC_DEVICE" \
      model_path.model="models/x5_mlm__$SC_SUFFIX.p" \
      output.path="data/emb__$SC_SUFFIX" \
      --conf "conf/dataset.hocon" "conf/mles_params.json"
done

for SC_HIDDEN_SIZE in 1600
do
  export SC_SUFFIX="hidden_size__hs_${SC_HIDDEN_SIZE}"
  python ../../metric_learning.py \
      params.device="$SC_DEVICE" \
      params.rnn.hidden_size=${SC_HIDDEN_SIZE} \
      params.train.batch_size=128 \
      model_path.model="models/x5_mlm__$SC_SUFFIX.p" \
      --conf "conf/dataset.hocon" "conf/mles_params.json"
  python ../../ml_inference.py \
      params.device="$SC_DEVICE" \
      model_path.model="models/x5_mlm__$SC_SUFFIX.p" \
      output.path="data/emb__$SC_SUFFIX" \
      --conf "conf/dataset.hocon" "conf/mles_params.json"
done

# Compare
rm results/scenario_x5__hidden_size.txt
# rm -r conf/embeddings_validation.work/
PYTHONPATH=../.. LUIGI_CONFIG_PATH=conf/luigi.cfg python -m embeddings_validation \
    --conf conf/embeddings_validation_short.hocon --workers 10 --total_cpu_count 20 \
    --conf_extra \
      'report_file: "../results/scenario_x5__hidden_size.txt",
      auto_features: ["../data/emb__hidden_size_*.pickle"]'

