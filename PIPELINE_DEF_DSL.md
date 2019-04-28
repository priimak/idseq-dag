### Sacla based DSL for pipeline definition
Here you can see example of some kind of DSL embedded into another language (in this example
Scala-like language). Using it instead of json users can take advantage of the full power 
of proper language. For example we not longer need to do anything to support variable substitution.
```scala
input_base = "s3://idseq-samples-prod/test_samples/1/fastqs"
pipeline_def = PipelineDefinition()

pipeline_def.setOutputDefinition("s3://idseq-samples-prod/test_samples/1/results")

pipeline_def += Seq(
    Target("fastqs",       input_base + "/RR004_water_2_S23_R1_001.fastq.gz"),
    Target("star_out",     "unmapped.star.1.fq"),
    Target("priceseq_out", "priceseqfilter.unmapped.star.1.fasta")
    Target("gsnap_out",
        "subsample_1000000/multihit.gsnapl.unmapped.bowtie2.lzw.cdhitdup.priceseqfilter.unmapped.star.m8",
        "subsample_1000000/dedup.multihit.gsnapl.unmapped.bowtie2.lzw.cdhitdup.priceseqfilter.unmapped.star.m8",
        "subsample_1000000/summary.multihit.gsnapl.unmapped.bowtie2.lzw.cdhitdup.priceseqfilter.unmapped.star.tab",
        "subsample_1000000/nt_multihit_idseq_web_sample.json"),
    Target("star_genome",
          "s3://idseq-database/host_filter/human/2018-02-15-utc-1518652800-unixtime__2018-02-15-utc-1518652800-unixtime/STAR_genome.tar")
)
pipeline_def += TargetCallback("fastqs", fragmentCounter(count_reads=1, max_fragments=1024))
pipeline_def += Seq(
    Step(
        in = ["fastqs", "sart_genome"],
        out = "star_out",
        function = PipelineStepRunStar(truncate_fragments_to = 75000000)
    ),
    Step(
        in = ["star_out"],
        out = "priceseq_out",
        function = PipelineStepRunPriceSeq()
    )
}
pipeline_flow = PipelineFlow(pipeline_def)
pipeline_flow.start()
```
