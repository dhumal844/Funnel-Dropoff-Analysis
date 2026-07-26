"""
User Funnel Drop-off Analysis
"""

import pandas as pd

# ---------------------------------------------------------------
# 1. Load data + basic data-quality handling
# ---------------------------------------------------------------
df = pd.read_csv('funnel_events_sample.csv')

# A user can log the same event twice (duplicate event). We only care
# WHETHER a user reached a step, not how many times -> de-dupe on
# (user_id, step) before counting.
df = df.drop_duplicates(subset=['user_id', 'step'])

# Fixed, real-world funnel order. Steps must NOT be treated as
# unordered categories (e.g. sorted alphabetically or by frequency).
step_order = ['visited_site', 'signup_started', 'details_filled',
              'email_verified', 'purchase_completed']
step_labels = {
    'visited_site': 'Visited Site',
    'signup_started': 'Signup Started',
    'details_filled': 'Details Filled',
    'email_verified': 'Email Verified',
    'purchase_completed': 'Purchase Completed'
}

# ---------------------------------------------------------------
# 2. Unique users reaching each stage
# ---------------------------------------------------------------
stage_counts = df.groupby('step')['user_id'].nunique().reindex(step_order)

funnel = pd.DataFrame({'stage': step_order, 'users': stage_counts.values})
funnel['label'] = funnel['stage'].map(step_labels)
funnel['pct_of_total'] = (funnel['users'] / funnel['users'].iloc[0] * 100).round(1)
funnel['pct_of_previous'] = 100.0
funnel['users_lost'] = 0
funnel['dropoff_pct'] = 0.0

for i in range(1, len(funnel)):
    prev, curr = funnel.loc[i - 1, 'users'], funnel.loc[i, 'users']
    funnel.loc[i, 'pct_of_previous'] = round(curr / prev * 100, 1)
    funnel.loc[i, 'users_lost'] = prev - curr
    funnel.loc[i, 'dropoff_pct'] = round((prev - curr) / prev * 100, 1)

print("FUNNEL CONVERSION TABLE")
print(funnel[['label', 'users', 'pct_of_total', 'pct_of_previous',
              'users_lost', 'dropoff_pct']].to_string(index=False))

funnel.to_csv('funnel_results.csv', index=False)

# ---------------------------------------------------------------
# 3. Automatically flag the biggest drop-off stage
# ---------------------------------------------------------------
drop_rows = funnel.iloc[1:]
biggest = funnel.loc[drop_rows['dropoff_pct'].idxmax()]
prev_label = funnel.loc[drop_rows['dropoff_pct'].idxmax() - 1, 'label']

print(f"\n>>> BIGGEST DROP-OFF: {prev_label} -> {biggest['label']} "
      f"({biggest['dropoff_pct']}% of users lost, {int(biggest['users_lost'])} users)")
