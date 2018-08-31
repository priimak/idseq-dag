def clean_name(sample_name):
    return sample_name.replace(".", "-")

CAMI_Airways_reads_mapping = {sample_name: f"/home/ubuntu/cdebourcy/cami/short_read/{sample_name}/reads/reads_mapping.tsv.gz" for sample_name in [
                                 "2017.12.04_18.56.22_sample_10", "2017.12.04_18.56.22_sample_12", "2017.12.04_18.56.22_sample_26", "2017.12.04_18.56.22_sample_4",
                                 "2017.12.04_18.56.22_sample_8", "2017.12.04_18.56.22_sample_11", "2017.12.04_18.56.22_sample_23", "2017.12.04_18.56.22_sample_27",
                                 "2017.12.04_18.56.22_sample_7", "2017.12.04_18.56.22_sample_9"]}

CAMI_Airways_align_viz = {"2017.12.04_18.56.22_sample_10": "s3://idseq-samples-prod/samples/105/6417/postprocess/2.7/align_viz",
                          "2017.12.04_18.56.22_sample_11": "s3://idseq-samples-prod/samples/105/6418/postprocess/2.7/align_viz",
                          "2017.12.04_18.56.22_sample_12": "s3://idseq-samples-prod/samples/105/6419/postprocess/2.7/align_viz", 
                          "2017.12.04_18.56.22_sample_23": "s3://idseq-samples-prod/samples/105/6420/postprocess/2.7/align_viz",
                          "2017.12.04_18.56.22_sample_26": "s3://idseq-samples-prod/samples/105/6421/postprocess/2.7/align_viz",
                          "2017.12.04_18.56.22_sample_27": "s3://idseq-samples-prod/samples/105/6422/postprocess/2.7/align_viz",
                          "2017.12.04_18.56.22_sample_4": "s3://idseq-samples-prod/samples/105/6416/postprocess/2.7/align_viz",
                          "2017.12.04_18.56.22_sample_7": "s3://idseq-samples-prod/samples/105/6415/postprocess/2.7/align_viz",
                          "2017.12.04_18.56.22_sample_8": "s3://idseq-samples-prod/samples/105/6414/postprocess/2.7/align_viz",
                          "2017.12.04_18.56.22_sample_9": "s3://idseq-samples-prod/samples/105/6413/postprocess/2.7/align_viz"}
