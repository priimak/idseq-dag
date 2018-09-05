def subset(df, tax_level, sample_name=None):
    condition = (idseq_df['tax_level'] == 2) &
                (idseq_df['taxid'] > 0)
    if sample_name != None:
        condition = (df['sample_name'] == sample_name) & condition
    return df.loc[condition]
