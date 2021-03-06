''' Generate Coverage Statistics '''
import json
import os
import pysam

from idseq_dag.engine.pipeline_step import PipelineStep
import idseq_dag.util.command as command
import idseq_dag.util.log as log
import idseq_dag.util.count as count
MIN_CONTIG_FILE_SIZE = 50

class PipelineStepGenerateCoverageStats(PipelineStep):
    ''' Generate Coverage Statistics from Assembly Output '''
    def run(self):
        """
          1. extract contigs.fasta and read-contig.sam
          2. run pile up
        """
        contigs, _scaffolds, read_contig_sam, _stats = self.input_files_local[0]
        coverage_json, coverage_summary_csv = self.output_files_local()

        if os.path.getsize(contigs) < MIN_CONTIG_FILE_SIZE:
            command.execute("echo '{}' > " +  coverage_json)
            command.execute("echo 'No Contigs' > " +  coverage_summary_csv)
            return

        contig2coverage = {}
        # generate bam files
        bam_file = read_contig_sam.replace(".sam", ".bam")
        command.execute(f"samtools view -S -b  {read_contig_sam} | samtools sort - -o {bam_file}")
        command.execute(f"samtools index {bam_file}")

        # run coverage info
        with pysam.AlignmentFile(bam_file, "rb") as f:
            contig_names = f.references
            for c in contig_names:
                coverage = []
                for pileup_column in f.pileup(contig=c):
                    coverage.append(pileup_column.get_num_aligned())
                sorted_coverage = sorted(coverage)
                contig_len = len(coverage)
                if contig_len <= 0:
                    continue

                avg = sum(coverage)/contig_len
                contig2coverage[c] = {
                    "coverage": coverage,
                    "avg": avg,
                    "p0": sorted_coverage[0],
                    "p100": sorted_coverage[-1],
                    "p25": sorted_coverage[int(0.25*contig_len)],
                    "p50": sorted_coverage[int(0.5*contig_len)],
                    "p75": sorted_coverage[int(0.75*contig_len)],
                    "avg2xcnt": len(list(filter(lambda t: t > 2*avg, coverage)))/contig_len,
                    "cnt0": len(list(filter(lambda t: t == 0, coverage)))/contig_len,
                    "cnt1": len(list(filter(lambda t: t == 1, coverage)))/contig_len,
                    "cnt2": len(list(filter(lambda t: t == 2, coverage)))/contig_len
                }

        with open(coverage_json, 'w') as csf:
            json.dump(contig2coverage, csf)

        with open(coverage_summary_csv, 'w') as csc:
            csc.write("contig_name,avg,min,max,p25,p50,p75,avg2xcnt,cnt0,cnt1,cnt2\n")
            for contig, stats in contig2coverage.items():
                output_row = [
                    contig, stats['avg'], stats['p0'], stats['p100'],
                    stats['p25'], stats['p50'], stats['p75'],
                    stats['avg2xcnt'], stats['cnt0'], stats['cnt1'], stats['cnt2']
                ]
                output_str = ','.join(str(e) for e in output_row)
                csc.write(output_str + "\n")

    def count_reads(self):
        ''' Count reads '''
        pass


