# Centromere Status Checker
[![CI](https://github.com/logsdon-lab/centromere-status-checker/actions/workflows/main.yml/badge.svg)](https://github.com/logsdon-lab/centromere-status-checker/actions/workflows/main.yml)

Determine the status of centromeric contigs based on [`RepeatMasker`](https://www.repeatmasker.org/) annotations.

### Setup
```bash
pip install centromere_status_checker
```

### Usage
Takes `RepeatMasker` output from centromeric contigs to check and centromeric contigs from a reference.
```bash
cens-status -i input_cens.out -r ref_cens.out > cens_status.tsv
```

Return tab-delimited output with the following fields:
1. Original contig name.
2. Remapped contig name.
3. Correct orientation of contig with `fwd` indicating an already correctly oriented contig.
4. Contig is a partial centromeric contig.

```
HG00171_chr21_haplotype2-0000154:33297526-38584922      HG00171_chr21_haplotype2-0000154:33297526-38584922      rev     false
HG00171_chr21_haplotype1-0000029:4196961-10792258       HG00171_chr13_haplotype1-0000029:4196961-10792258       fwd     false
HG00171_chr21_haplotype1-0000019:33327260-37313906      HG00171_chr21_haplotype1-0000019:33327260-37313906      rev     true
chm13_chr21:7700001-11850000    chm13_chr21:7700001-11850000    fwd     false
```

### Similarity Metrics
Two metrics are used to determine orientation and mapping.
* [Jaccard index](https://www.statisticshowto.com/jaccard-index/)
* [Edit distance](https://en.wikipedia.org/wiki/Edit_distance) using the [`editdistance`](https://pypi.org/project/editdistance/) library.

### Algorithm
1. Every centromeric contig and its reverse orientation is paired with a reference centromeric contig.
    * Repeat types are used to gauge similarity.
    * Complexity is reduced by merging certain repeat types.

2. Next, the both metrics are calculated for each pair.
    * If both chromosomes in a pair are acrocentric and have similar number of HOR arrays, then only repeats along the q-arm are used.
        * This is due to high recombination along the p-arms [1].

3. Partial contigs are checked by calculating the percentage of `ALR/Alpha` repeat types along the edges of the contig.
    * If the percentage is greater than a set threshold, the contig is considered partial.

4. The results for each pair are grouped by contig and merged/filtered depending on the metric.
    * Jaccard index
        * Select the pair with the **largest similarity index**.
    * Edit distance
        * Filter pairs with an **edit distance below the 30th percentile of all distances** and select the pair with the **lowest distance** from the filtered group.
        * We also calculate create a separate table with only pairs with matching chromosomes to use as a default pair if no pairs remain after filtering.

5. The results are joined by contig and determined by the following checks:
    * If *both jaccard index and edit distance agree*, the chromosome contig name is remapped to the reference chromosome. Its orientation is used.
    * If *neither metric agrees*, the chromosome contig name remains the same. The orientation is determined by the best match in the separate table with only pairs with matching chromosomes.

### Build
```bash
make venv && make build && make install
source venv/bin/activate && cens-status -h
```

To run tests:
```bash
source venv/bin/activate && pip install pytest
pytest -s -vv
```

### Sources
1. Guarracino, A., Buonaiuto, S., de Lima, L.G. et al. Recombination between heterologous human acrocentric chromosomes. Nature 617, 335–343 (2023). https://doi.org/10.1038/s41586-023-05976-y
