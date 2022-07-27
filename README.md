# Prerequisites

The code is tested on Ubuntu Linux 18.04.5 LTS server with NVIDIA Tesla P100 GPU. It should also work on any modern Linux with modern NVIDIA Tesla GPU.

Churn dataset experiments require around 1 day to complete.

Assessment dataset experiments require around 1 day to complete.

Age prediction dataset experiments require around 3 days to complete.

Retail dataset experiments - require around 7 days to complete.

# 1. Setup using pipenv

```sh
# Ubuntu 18.04

sudo apt install python3.8 python3-venv
pip3 install pipenv

pipenv sync --dev  # install packages exactly as specified in Pipfile.lock
pipenv shell # activate virtual environment

# run luigi server
luigid

# optionally check embedding validation progress at `http://localhost:8082/`
```

# 2. Age prediction dataset

```sh
cd experiments/scenario_age_pred

# download datasets
bin/get-data.sh

# convert datasets from transaction list to features for metric learning
bin/make-datasets-spark.sh

export SC_DEVICE="cuda"

sh bin/run_all_scenarios.sh

# check the results
cat results/*.txt
cat results/*.csv

cd ../..
```

# 3. Churn dataset

```sh
cd experiments/scenario_rosbank

# download datasets
bin/get-data.sh

# convert datasets from transaction list to features for metric learning
bin/make-datasets-spark.sh

export SC_DEVICE="cuda"

sh bin/run_all_scenarios.sh

# check the results
cat results/*.txt
cat results/*.csv

cd ../..
```

# 4. Assessment dataset

 ```sh
cd experiments/scenario_bowl2019

# download datasets
bin/get-data.sh

# convert datasets from transaction list to features for metric learning
bin/make-datasets-spark.sh

export SC_DEVICE="cuda"

sh bin/run_all_scenarios.sh

# check the results
cat results/*.txt
cat results/*.csv

cd ../..
```

# 5. Retail dataset

```sh
cd experiments/scenario_x5

# download datasets
bin/get-data.sh

# convert datasets from transaction list to features for metric learning
bin/make-datasets-spark.sh

export SC_DEVICE="cuda"

sh bin/run_all_scenarios.sh

# check the results
cat results/*.txt
cat results/*.csv

cd ../..
```

# 6. Results

All results are stored in `experiments/*/results` folder.
