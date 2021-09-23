# Get data

```sh
cd experiments/scenario_bowl2019

# download datasets
bin/get-data.sh

# convert datasets from transaction list to features for metric learning
bin/make-datasets.sh
```

# Main scenario, best params

```sh
cd experiments/scenario_bowl2019
export SC_DEVICE="cuda"

sh bin/run_all_scenarios.sh

# check the results
cat results/*.txt
cat results/*.csv
```
