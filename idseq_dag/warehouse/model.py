#!/usr/bin/env python3

import pandas as pd
import tensorflow as tf

def main():
    warehouse_dir = "/mnt/idseq/warehouse"
    model_dir = f"{warehouse_dir}/models"
    command.execute(f"mkdir -p {model_dir}")
    idseq_coverages = f"{warehouse_dir}/coverage_histograms.csv"
    cami_labels = f"{warehouse_dir}/cami_labels.csv"
    
    feature_df = dw.subset(pd.read_csv(idseq_coverages, index_col=[0]),
                           tax_level=2)
    label_df = dw.subset(pd.read_csv(cami_labels, index_col=[0]),
                         tax_level=2)
    df = pd.merge(feature_df, label_df, how='outer', on=['taxid', 'sample_name'], suffixes=('_feature', '_label'))
    df = df.fillna(0)
    print(df)

if __name__ == "__main__":
    main()
