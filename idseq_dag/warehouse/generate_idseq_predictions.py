#!/usr/bin/env python3

import glob
import pandas as pd

import sample_lists
import idseq_dag.util.s3 as s3
import idseq_dag.util.command as command

def main():
    warehouse_dir = "/mnt/idseq/warehouse"
    scratch_dir = f"{warehouse_dir}/tmp"
    result_file = f"{warehouse_dir}/idseq_predictions.csv"
    command.execute(f"rm -rf {scratch_dir}; mkdir -p {scratch_dir}")
    reports_dir = s3.fetch_from_s3("s3://idseq-samples-test/cami_airways_reports.tar.gz",
                                   scratch_dir, auto_unzip = True, auto_untar = True)
    df = pd.DataFrame(columns=['sample_name', 'taxid', 'NT_r', 'NR_r', 'count'])
    for report_file in glob.glob(f"{reports_dir}/*"):
        print(f"Starting to process {report_file}")
        report_df = pd.read_csv(report_file, usecols=["tax_id", "NT_r", "NR_r"])
        report_df['count'] = report_df.apply(lambda row: (row["NT_r"] + row["NR_r"]) / 2.0, axis = 1)
        report_df['sample_name'] = sample_lists.clean_name(os.path.splitext(os.path.basename(report_file))[0])
        report_df.rename(columns={'tax_id': 'taxid'}, inplace=True)
        df = pd.concat([df, report_df])
        df.to_csv(result_file)
        print(f"Finished processing {report_file}")

if __name__ == "__main__":
    main()
