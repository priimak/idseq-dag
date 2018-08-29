#!/usr/bin/env python3

import os
import json
import pandas as pd
from collections import defaultdict

import idseq_dag.util.s3 as s3
import idseq_dag.util.command as command
import sample_lists

def parse_tree(current_dict, results, key = None):
    """
    Produce a dictionary like:
      { "accession 1": { "coverage_summary": ... },
        "accession 2": { "coverage_summary": ... },
        ...
      }
    from a dictionary like:
      { "family taxid 1": {
          "genus taxid 1": {
            "species taxid 1": {
              "accession 1": { "coverage_summary": ... },
            }
          },
          "genus taxid 2": {
            "species taxid 2": {
              "accession 2": { "coverage_summary": ... },
            }
          }
        }
      }
    """
    if "coverage_summary" in current_dict:
        results[key] = current_dict
    else:
        for key2, sub_dict in current_dict.items():
            parse_tree(sub_dict, results, key2)

def main():
    '''
    Make a csv containing a coverage histogram for each sample and taxid.
    Different accessions are considered to contain different loci, which is not true for overlapping records.
    TODO: assess whether we still obtain useful features with this approximation.
    '''
    warehouse_dir = "/mnt/idseq/warehouse"
    scratch_dir = f"{warehouse_dir}/tmp"
    result_file = f"{warehouse_dir}/coverage_histograms.csv"
    command.execute(f"rm -rf {scratch_dir}; mkdir -p {scratch_dir}")
    df = pd.DataFrame()
    for align_viz_s3_path in sample_lists.CAMI_Airways_align_viz:
        s3_basenames = s3.list_files(align_viz_s3_path, folder = True)
        s3_files = [f"{align_viz_s3_path.rstrip('/')}/{basename}" for basename in s3_basenames]
        for s3f in s3_files:
            # example s3f: s3://idseq-samples-staging/samples/87/901/postprocess/2.7/align_viz/nt.species.96230.align_viz.json
            _hit_type, _tax_level, taxid, _suffix = os.path.basename(s3f).split(".", 3)
            if int(taxid) < 0:
                continue
            coverage_histogram = defaultdict(lambda: 0)
            project_id, sample_id, _dummy, pipeline_version = s3f.split("/")[4:8]
            coverage_histogram.update({
                "taxid": taxid, "project_id": project_id, "sample_id": sample_id, "pipeline_version": pipeline_version
            })
            coverage_file = s3.fetch_from_s3(s3f, scratch_dir)
            with open(coverage_file, 'r') as f:
                align_viz_map = json.load(f)
            coverage_map = {}
            parse_tree(align_viz_map, coverage_map)
            print(f"Starting to process accessions for sample {sample_id}: {coverage_map.keys()}")
            for accession, data in coverage_map.items():
                coverage_by_locus = data["coverage_summary"]["coverage"]
                for loci, coverage in coverage_by_locus.items():
                    start_locus, end_locus = loci.split("-")
                    n_bases = int(end_locus) - int(start_locus) + 1
                    coverage_histogram[coverage] += n_bases
                print(f"processed {accession}")
            coverage_df = pd.DataFrame(coverage_histogram, index=[f"{project_id}-{sample_id}-{pipeline_version}-{taxid}"])
            df = df.append(coverage_df)
        df = df.fillna(0)
        df.to_csv(result_file) # keep overwriting
        command.execute(f"rm {scratch_dir}/*")
        print(f"Finished processing {align_viz_path}")

if __name__ == "__main__":
    main()
