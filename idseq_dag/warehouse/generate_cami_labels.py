#!/usr/bin/env python3
import gzip
import pandas as pd
import shelve
from collections import defaultdict

import sample_lists
import idseq_dag.util.s3 as s3
import idseq_dag.util.command as command
import idseq_dag.util.lineage as lineage

def main():
    warehouse_dir = "/mnt/idseq/warehouse"
    scratch_dir = f"{warehouse_dir}/tmp"
    result_file = f"{warehouse_dir}/cami_labels.csv"
    command.execute(f"rm -rf {scratch_dir}; mkdir -p {scratch_dir}")

    lineage_db = s3.fetch_from_s3("s3://idseq-database/taxonomy/2018-04-01-utc-1522569777-unixtime__2018-04-04-utc-1522862260-unixtime/taxid-lineages.db",
                                  scratch_dir, allow_s3mi = True)
    lineage_map = shelve.open(lineage_db.replace('.db', ''), 'r')

    mapping_files = sample_lists.CAMI_Airways_reads_mapping
    df = pd.DataFrame(columns=['sample_name', 'taxid', 'count'])
    for sample_name, mapping in mapping_files.items():
        print(f"Starting to process {sample_name}")
        taxon_counts = defaultdict(lambda: 0)
        with gzip.open(mapping, 'r') as input_file:
            for idx, line in enumerate(input_file):
                taxid = line.decode("utf-8").split("\t")[2] # columns: anonymous_read_id, genome_id, tax_id, read_id
                taxid_lineage = lineage_map.get(taxid, lineage.NULL_LINEAGE) # note: taxid assigned to a read can be any level (family, genus, ...)
                for id in taxid_lineage:
                    taxon_counts[id] += 1
                if idx % 10**6 == 0:
                    print(f"{idx // 10**6}M reads processed")
        df = pd.concat([df] + [pd.DataFrame([[sample_name, taxid, count]],
                                            columns = ['sample_name', 'taxid', 'count'],
                                            index = [f"{sample_name}-{taxid}"]) for taxid, count in taxon_counts.items()])
        df.to_csv(result_file)
        print(f"Finished processing {sample_name}")

if __name__ == "__main__":
    main()

