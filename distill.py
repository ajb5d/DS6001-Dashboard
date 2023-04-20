import pandas as pd

gss = pd.read_csv(
    "data/gss2018.csv.gz",
    encoding='cp1252',
    low_memory=False,
    na_values=['IAP', 'IAP,DK,NA,uncodeable', 
               'NOT SURE','DK', 'IAP, DK, NA, uncodeable',
               '.a', "CAN'T CHOOSE"])

keep_cols = {
    'sex': 'sex',
    'educ': 'education',
    'region': 'region',
    'coninc': 'income',
    'prestg10': 'job_prestige',
    'sei10': 'socioeconomic_index',
    'satjob': 'satjob',
    'fechld': 'relationship',
    'fefam': 'male_breadwinner',
    'fepol': 'men_bettersuited',
    'fepresch': 'child_suffer',
    'meovrwrk': 'men_overwork'
}

gss_clean = gss[keep_cols.keys()]
gss_clean = gss_clean.rename(keep_cols,axis=1)

gss_clean.education = (
    pd.qcut(
        gss_clean.education,
        q = 4,
        labels = ['Lowest Quartile', 'Q2', 'Q3', 'Highest Quartile'])
        .cat.add_categories('not answered')
        .fillna("not answered")
)

gss_clean.satjob = (
    gss_clean.satjob
        .astype('category')
        .cat.reorder_categories([
            'very dissatisfied', 
            'a little dissat', 
            'mod. satisfied', 
            'very satisfied'])
        .cat.as_ordered()
        .cat.add_categories('not answered')
        .fillna("not answered")
)

def cat_and_reorder(feature, levels):
    return (
        feature
            .astype('category')
            .cat.reorder_categories(levels)
            .cat.add_categories('not answered')
            .fillna("not answered")
    )

for col in ['relationship', 'male_breadwinner', 'child_suffer']:
    gss_clean[col] = cat_and_reorder(gss_clean[col], ['strongly disagree', 'disagree', 'agree', 'strongly agree'])

gss_clean['men_bettersuited'] = cat_and_reorder(gss_clean['men_bettersuited'], ['disagree', 'agree'])
gss_clean['men_overwork'] = cat_and_reorder(gss_clean['men_overwork'], 
    ['strongly disagree', 'disagree', 'neither agree nor disagree',  'agree', 'strongly agree'])

gss_clean.to_parquet("data/gss2018clean.parquet")