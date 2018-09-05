#!/usr/bin/env python3

import os
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import idseq_dag.util.command as command
import sample_lists

def main():
    warehouse_dir = "/mnt/idseq/warehouse"
    figure_dir = f"{warehouse_dir}/figures"
    command.execute(f"mkdir -p {figure_dir}")
    idseq_predictions = f"{warehouse_dir}/idseq_predictions.csv"
    cami_labels = f"{warehouse_dir}/cami_labels.csv"
    idseq_df = pd.read_csv(idseq_predictions, index_col=[0])
    cami_df = pd.read_csv(cami_labels, index_col=[0])
    for sample_name in sample_lists.CAMI_Airways_sample_names:
        clean_sample_name = sample_lists.clean_name(sample_name)
        idseq_genus = idseq_df.loc[(idseq_df['sample_name'] == clean_sample_name) & 
                                   (idseq_df['tax_level'] == 2) &
                                   (idseq_df['taxid'] > 0)]
        cami_genus = cami_df.loc[(cami_df['sample_name'] == clean_sample_name) &
                                 (cami_df['tax_level'] == 2) &
                                 (cami_df['taxid'] > 0)]
        df = pd.merge(idseq_genus, cami_genus, how='outer', on='taxid', suffixes=('_idseq', '_cami'))
        df = df.fillna(0)
        rms = np.sqrt(mean_squared_error(df['count_cami'], df['count_idseq']))
        plt.plot('count_idseq', 'count_cami', data=df)
        plt.title(sample_name)
        plt.annotate(f"RMS error = {rms}", xy=(0.05, 0.95), xycoords='axes fraction')
        plt.savefig(f"{figure_dir}/{clean_sample_name}.png", format="png")

if __name__ == "__main__":
    main()
