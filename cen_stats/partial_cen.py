import polars as pl

from .constants import EDGE_LEN, EDGE_PERC_ALR_THR


def is_partial_centromere(
    df: pl.DataFrame,
    *,
    edge_len: int = EDGE_LEN,
    edge_perc_alr_thr: float = EDGE_PERC_ALR_THR,
) -> bool:
    """
    Check if centromere is partially constructed based on ALR percentage at either ends of the contig.

    ALR/Alpha repeat content is used as a heuristic as we expect primarily monomeric repeats to be at the edges of the HOR array.

    ### Args
    `df`
        RepeatMasker output with a `dst` column for each repeat row.
    `edge_len`
        Edge len to check. Defaults to 100 kbp.
    `edge_perc_alr_thr`
        ALR percentage threshold needed to be considered incomplete. Defaults to 70%.

    ### Returns
    Whether the centromere is partially constructed.
    """
    # Check if partial centromere based on ALR perc on ends.
    # Check N kbp from start and end of contig.
    ledge = df.filter(pl.col("end") < df[0]["end"] + edge_len)
    redge = df.filter(pl.col("end") > df[-1]["end"] - edge_len)
    try:
        ledge_perc_alr = (
            ledge.group_by("type")
            .agg(pl.col("dst").sum() / ledge["dst"].sum())
            .filter(pl.col("type") == "ALR/Alpha")
            .row(0)[1]
        )
    except Exception:
        ledge_perc_alr = 0.0
    try:
        redge_perc_alr = (
            redge.group_by("type")
            .agg(pl.col("dst").sum() / redge["dst"].sum())
            .filter(pl.col("type") == "ALR/Alpha")
            .row(0)[1]
        )
    except Exception:
        redge_perc_alr = 0.0

    return ledge_perc_alr > edge_perc_alr_thr or redge_perc_alr > edge_perc_alr_thr