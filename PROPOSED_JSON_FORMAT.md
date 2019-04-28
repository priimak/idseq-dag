## Proposed new json format for pipeline definition

Here I describe changes that I would like to propose to current json format used to describe
set pipeline. The goal here is to both simplify it and make it more generic. This presentation
is informal and uses examples to illustrate proposed changes:

* Instead of `output_dir_s3` use `output_dst` and derive what that destination for output 
files is from scheme of its string value. For example:
    ```python
   {
       "output_dst": "gs://idseq-data/x/y/z",
       ...
   }
    ```
  Indicates that destination for result of pipeline execution is some backets in google storage.
* Get rid of `given_targets` and `additional_files`. All dependencies should be listed 
    under `targets` key. For example
    ```python
   {
       "targets": {
           "fastqs": ["s3://idseq-samples-prod/test_samples/1/fastqs"],
           "step1_out": ["foobar.fasta"],
           "step2_in_aux": ["s3://idseq-samples-prod/foo/bar/pig.fasta"],
           "result": ["report.pdf"]
       },
       "steps": [
          {
             "in": ["fastqs"],
             "out": "step1_out",
             ...
          },
          {
              "in": ["step1_out", "step2_in_aux"],
              "out": "result",
              ...
          }
       ]
   }
    ```
    If file in target is not local (listed with specific url scheme) we download it prior to 
    execution of the step that depends on it.
* Allow referencing any top level key-string object by it is name. For example we can use that
to simplify above example like so
    ```python
   {
       "src_base": "s3://idseq-samples-prod",
       "targets": {
           "fastqs": ["${src_base}/test_samples/1/fastqs"],
           "step1_out": ["foobar.fasta"],
           "step2_in_aux": ["${src_base}/foo/bar/pig.fasta"],
           "result": ["report.pdf"]
       },
       "steps": [
            ...
       ]      
   }
    ```
    Here `${src_base}` is in-lined before parsing of this config.
* Introduce top level key `global_attributes` which is just like `additional_attributes`.
Later ones are merged with `global_attributes` and passed to execution step. For example:
    ```python
   {
      "global_attibutes": {
          "environment": "prod",
          "index_dir_suffix": "2018-04-01"
      },
      "output_dst": "..."
      "targets": { ... },
      "steps": [
          {
              ...
              "additional_attributes": {
                 "service": "gsnap", "chunks_in_flight": 32,
                 "chunk_size": 15000, "max_concurrent": 3,
              }
          },
          {
              ...
              "additional_attributes": {
                 "service": "rapsearch2", "chunks_in_flight": 32,
                 "chunk_size": 10000, "max_concurrent": 6
              }
          }
      ]
   }
    ```
