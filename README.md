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

# 2. Install LaTeX packages for plot generation

```sh
sudo apt-get install dvipng texlive-latex-extra texlive-fonts-recommended cm-super
```

# 3. Age prediction dataset experiments

```sh
cd experiments/scenario_age_pred

# download datasets
bin/get-data.sh

# convert datasets from transaction list to features for metric learning
bin/make-datasets-spark.sh

export SC_DEVICE="cuda"
# run experiments
sh bin/run_all_scenarios.sh

# optionally return to the project root
cd ../..
```

# 4. Churn dataset experiments

```sh
cd experiments/scenario_rosbank

# download datasets
bin/get-data.sh

# convert datasets from transaction list to features for metric learning
bin/make-datasets-spark.sh

export SC_DEVICE="cuda"
# run experiments
sh bin/run_all_scenarios.sh

# optionally return to the project root
cd ../..
```

# 5. Assessment dataset experiments

 ```sh
cd experiments/scenario_bowl2019

# download datasets
bin/get-data.sh

# convert datasets from transaction list to features for metric learning
bin/make-datasets-spark.sh

export SC_DEVICE="cuda"
# run experiments
sh bin/run_all_scenarios.sh

# optionally return to the project root
cd ../..
```

# 6. Retail dataset experiments

```sh
cd experiments/scenario_x5

# download datasets
bin/get-data.sh

# convert datasets from transaction list to features for metric learning
bin/make-datasets-spark.sh

export SC_DEVICE="cuda"
# run experiments
sh bin/run_all_scenarios.sh

# optionally return to the project root
cd ../..
```

# 8. Results

Raw result files are stored in `experiments/*/results` folder. Current results are cached in Git, final tables and plots can be generated without full experiment run.

[Tables from paper](experiments/notebooks/collect_tables.ipynb): tables 2, 3, 4, 5, 6, 7 from the paper that compare model quality metrics are produced by this notebook

[RNN hidden size figures](experiments/notebooks/hidden_size_figures.ipynb): figure 3 from the paper is produced by this notebook

[Periodicity and repeatability of the data figures](experiments/notebooks/kl_cyclostationary.ipynb): figure 2 from the paper is produced by this notebook

[Model quality for different dataset sizes figures](experiments/notebooks/semi_supervised_figures.ipynb): figure 4 from the paper is produced by this notebook
