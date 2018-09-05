def subset(df, tax_level, sample_name=None):
    condition = (df['tax_level'] == tax_level) & (df['taxid'] > 0)
    if sample_name != None:
        condition = (df['sample_name'] == sample_name) & condition
    return df.loc[condition]
