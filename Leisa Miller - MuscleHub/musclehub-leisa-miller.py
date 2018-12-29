#!/usr/bin/env python
# coding: utf-8

# # Capstone Project 1: MuscleHub AB Test

# ## Step 1: Get started with SQL

# Like most businesses, Janet keeps her data in a SQL database.  Normally, you'd download the data from her database to a csv file, and then load it into a Jupyter Notebook using Pandas.
# 
# For this project, you'll have to access SQL in a slightly different way.  You'll be using a special Codecademy library that lets you type SQL queries directly into this Jupyter notebook.  You'll have pass each SQL query as an argument to a function called `sql_query`.  Each query will return a Pandas DataFrame.  Here's an example:

# In[1]:


# This import only needs to happen once, at the beginning of the notebook
from codecademySQL import sql_query
import pandas as pd


# In[2]:


# Here's an example of a query that just displays some data
sql_query('''
SELECT *
FROM visits
LIMIT 5
''')


# In[3]:


# Here's an example where we save the data to a DataFrame
df = sql_query('''
SELECT *
FROM applications
LIMIT 5
''')


# ## Step 2: Get your dataset

# Let's get started!
# 
# Janet of MuscleHub has a SQLite database, which contains several tables that will be helpful to you in this investigation:
# - `visits` contains information about potential gym customers who have visited MuscleHub
# - `fitness_tests` contains information about potential customers in "Group A", who were given a fitness test
# - `applications` contains information about any potential customers (both "Group A" and "Group B") who filled out an application.  Not everyone in `visits` will have filled out an application.
# - `purchases` contains information about customers who purchased a membership to MuscleHub.
# 
# Use the space below to examine each table.

# In[4]:


# Examine visits here
sql_query('''
SELECT *
FROM visits
LIMIT 5
''')


# In[5]:


# Examine fitness_tests here
sql_query('''
SELECT *
FROM fitness_tests
LIMIT 5
''')


# In[6]:


# Examine applications here
sql_query('''
SELECT *
FROM applications
LIMIT 5
''')


# In[7]:


# Examine purchases here
sql_query('''
SELECT *
FROM purchases
LIMIT 5
''')


# We'd like to download a giant DataFrame containing all of this data.  You'll need to write a query that does the following things:
# 
# 1. Not all visits in  `visits` occurred during the A/B test.  You'll only want to pull data where `visit_date` is on or after `7-1-17`.
# 
# 2. You'll want to perform a series of `LEFT JOIN` commands to combine the four tables that we care about.  You'll need to perform the joins on `first_name`, `last_name`, and `email`.  Pull the following columns:
# 
# 
# - `visits.first_name`
# - `visits.last_name`
# - `visits.gender`
# - `visits.email`
# - `visits.visit_date`
# - `fitness_tests.fitness_test_date`
# - `applications.application_date`
# - `purchases.purchase_date`
# 
# Save the result of this query to a variable called `df`.
# 
# Hint: your result should have 5004 rows.  Does it?

# In[8]:


df = sql_query('''
SELECT visits.first_name,
       visits.last_name,
       visits.visit_date,
       fitness_tests.fitness_test_date,
       applications.application_date,
       purchases.purchase_date
FROM visits
LEFT JOIN fitness_tests
    ON fitness_tests.first_name = visits.first_name
    AND fitness_tests.last_name = visits.last_name
    AND fitness_tests.email = visits.email
LEFT JOIN applications
    ON applications.first_name = visits.first_name
    AND applications.last_name = visits.last_name
    AND applications.email = visits.email
LEFT JOIN purchases
    ON purchases.first_name = visits.first_name
    AND purchases.last_name = visits.last_name
    AND purchases.email = visits.email
WHERE visits.visit_date >= '7-1-17'
''')



# ## Step 3: Investigate the A and B groups

# We have some data to work with! Import the following modules so that we can start doing analysis:
# - `import pandas as pd`
# - `from matplotlib import pyplot as plt`

# In[9]:


from matplotlib import pyplot as plt


# We're going to add some columns to `df` to help us with our analysis.
# 
# Start by adding a column called `ab_test_group`.  It should be `A` if `fitness_test_date` is not `None`, and `B` if `fitness_test_date` is `None`.

# In[10]:


lambda_1 = lambda x: 'B' if pd.isnull(x) else 'A'
df['ab_test_group'] = df.fitness_test_date.apply(lambda_1)

print(df.head())


# Let's do a quick sanity check that Janet split her visitors such that about half are in A and half are in B.
# 
# Start by using `groupby` to count how many users are in each `ab_test_group`.  Save the results to `ab_counts`.

# In[11]:


ab_counts = df.groupby('ab_test_group').first_name.count().reset_index()
print(ab_counts)


# We'll want to include this information in our presentation.  Let's create a pie cart using `plt.pie`.  Make sure to include:
# - Use `plt.axis('equal')` so that your pie chart looks nice
# - Add a legend labeling `A` and `B`
# - Use `autopct` to label the percentage of each group
# - Save your figure as `ab_test_pie_chart.png`

# In[12]:


plt.pie(ab_counts.first_name.values, labels=['A', 'B'], autopct='%0.2f%%')
plt.axis('equal')
plt.legend()
plt.show()
plt.savefig('ab_test_pie_chart.png')


# ## Step 4: Who picks up an application?

# Recall that the sign-up process for MuscleHub has several steps:
# 1. Take a fitness test with a personal trainer (only Group A)
# 2. Fill out an application for the gym
# 3. Send in their payment for their first month's membership
# 
# Let's examine how many people make it to Step 2, filling out an application.
# 
# Start by creating a new column in `df` called `is_application` which is `Application` if `application_date` is not `None` and `No Application`, otherwise.

# In[13]:


lambda_2 = lambda x: 'No Application' if pd.isnull(x) else 'Application'
df['is_application'] = df.application_date.apply(lambda_2)

df.head()


# Now, using `groupby`, count how many people from Group A and Group B either do or don't pick up an application.  You'll want to group by `ab_test_group` and `is_application`.  Save this new DataFrame as `app_counts`

# In[14]:


app_counts = df.groupby(['ab_test_group', 'is_application']).first_name.count().reset_index()
app_counts


# We're going to want to calculate the percent of people in each group who complete an application.  It's going to be much easier to do this if we pivot `app_counts` such that:
# - The `index` is `ab_test_group`
# - The `columns` are `is_application`
# Perform this pivot and save it to the variable `app_pivot`.  Remember to call `reset_index()` at the end of the pivot!

# In[15]:


app_pivot = app_counts.pivot(index='ab_test_group', columns='is_application', values='first_name').reset_index()
app_pivot


# Define a new column called `Total`, which is the sum of `Application` and `No Application`.

# In[16]:


app_pivot['Total'] = app_pivot['Application'] + app_pivot['No Application']
app_pivot


# Calculate another column called `Percent with Application`, which is equal to `Application` divided by `Total`.

# In[17]:


app_pivot['Percent with Application'] = app_pivot['Application'] / app_pivot['Total']
app_pivot


# It looks like more people from Group B turned in an application.  Why might that be?
# 
# We need to know if this difference is statistically significant.
# 
# Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[41]:


from scipy.stats import chi2_contingency

chi_test = [[250, 2254], [325, 2175]]
chi2, pval, dof, expected = chi2_contingency(chi_test)
pval


# ## Step 4: Who purchases a membership?

# Of those who picked up an application, how many purchased a membership?
# 
# Let's begin by adding a column to `df` called `is_member` which is `Member` if `purchase_date` is not `None`, and `Not Member` otherwise.

# In[19]:


lambda_3 = lambda x: 'Not Member' if pd.isnull(x) else 'Member'
df['is_member'] = df.purchase_date.apply(lambda_3)

df.head()


# Now, let's create a DataFrame called `just_apps` the contains only people who picked up an application.

# In[20]:


just_apps = df[df.is_application == 'Application']

just_apps.head()


# Great! Now, let's do a `groupby` to find out how many people in `just_apps` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `member_pivot`.

# In[21]:


just_members = just_apps.groupby(['ab_test_group', 'is_member']).first_name.count().reset_index()

member_pivot = just_members.pivot(columns = 'is_member', index = 'ab_test_group', values = 'first_name')
member_pivot['Total'] = member_pivot['Member'] + member_pivot['Not Member']
member_pivot['Percent Purchase'] = member_pivot['Member'] / member_pivot['Total']

member_pivot


# It looks like people who took the fitness test were more likely to purchase a membership **if** they picked up an application.  Why might that be?
# 
# Just like before, we need to know if this difference is statistically significant.  Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[22]:


X = [[200, 50],
     [250, 75]]
chi2_1, pval_1, dof_1, expected_1 = chi2_contingency(X)
pval_1


# Previously, we looked at what percent of people **who picked up applications** purchased memberships.  What we really care about is what percentage of **all visitors** purchased memberships.  Return to `df` and do a `groupby` to find out how many people in `df` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `final_member_pivot`.

# In[23]:


all_visitors = df.groupby(['ab_test_group', 'is_member']).first_name.count().reset_index()

final_member_pivot = all_visitors.pivot(columns = 'is_member', index = 'ab_test_group', values = 'first_name')
final_member_pivot['Total'] = final_member_pivot['Member'] + final_member_pivot['Not Member']
final_member_pivot['Percent Purchase'] = final_member_pivot['Member'] / final_member_pivot['Total']

final_member_pivot


# Previously, when we only considered people who had **already picked up an application**, we saw that there was no significant difference in membership between Group A and Group B.
# 
# Now, when we consider all people who **visit MuscleHub**, we see that there might be a significant different in memberships between Group A and Group B.  Perform a significance test and check.

# In[24]:


X_2 = [[200, 2304],
     [250, 2250]]
chi2_2, pval_2, dof_2, expected_2 = chi2_contingency(X_2)
pval_2


# ## Step 5: Summarize the acquisition funel with a chart

# We'd like to make a bar chart for Janet that shows the difference between Group A (people who were given the fitness test) and Group B (people who were not given the fitness test) at each state of the process:
# - Percent of visitors who apply
# - Percent of applicants who purchase a membership
# - Percent of visitors who purchase a membership
# 
# Create one plot for **each** of the three sets of percentages that you calculated in `app_pivot`, `member_pivot` and `final_member_pivot`.  Each plot should:
# - Label the two bars as `Fitness Test` and `No Fitness Test`
# - Make sure that the y-axis ticks are expressed as percents (i.e., `5%`)
# - Have a title

# In[25]:


ax = plt.subplot()
plt.bar(range(len(app_pivot)), app_pivot['Percent with Application'].values)
ax.set_xticks(range(len(app_pivot)))
ax.set_xticklabels(['Fitness Test', 'No Fitness Test'])
ax.set_yticks([0, 0.05, 0.10, 0.15, 0.20])
ax.set_yticklabels(['0%', '5%', '10%', '15%', '20%'])
ax.set_title('Percent of visitors who apply')
plt.show()
plt.savefig('visitors_who_apply.png')


# In[26]:


ax = plt.subplot()
plt.bar(range(len(member_pivot)), member_pivot['Percent Purchase'].values)
ax.set_xticks(range(len(app_pivot)))
ax.set_xticklabels(['Fitness Test', 'No Fitness Test'])
ax.set_yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
ax.set_yticklabels(['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'])
ax.set_title('Percent of applicants who purchase a membership')
plt.show()
plt.savefig('applicants_who_purchase.png')


# In[27]:


ax = plt.subplot()
plt.bar(range(len(final_member_pivot)), final_member_pivot['Percent Purchase'].values)
ax.set_xticks(range(len(app_pivot)))
ax.set_xticklabels(['Fitness Test', 'No Fitness Test'])
ax.set_yticks([0, 0.05, 0.10, 0.15, 0.20])
ax.set_yticklabels(['0%', '5%', '10%', '15%', '20%'])
ax.set_title('Percent of visitors who purchase a membership')
plt.show()
plt.savefig('visitors_who_purchase.png')


# In[28]:


# Creating bar chart to vizualize funnel better

stages = ["visitors", "applicants", "purchasers"]
a_test =  [2504, 250, 200]
b_test = [2500, 325, 250]
range1 = [1.2, 3.2, 5.2]

# a_test
n = 1
t = 2
d = len(stages)
w = 0.8
store1_x = [t*element + w*n for element in range(d)]

plt.bar(store1_x, a_test, label='Variant A')

# b_test
n = 2
t = 2
d = len(stages)
w = 0.8
store2_x = [t*element + w*n for element in range(d)]

plt.bar(store2_x, b_test, label='Variant B')

ax3 = plt.subplot()
ax3.set_xticks(range1)
ax3.set_xticklabels(stages)
ax3.set_title('A/B Test by Stages')

plt.legend()
plt.show()
plt.savefig('bar_funnel_1.png')


# In[29]:


# Creating another bar chart to visualize the funnel

total_vs = 2504 + 2500
total_as = 250 + 325
total_ps = 200 + 250

bar_value_totals = [total_vs, total_as, total_ps]
ax4 = plt.subplot()
ax4.bar(range(3), bar_value_totals)
ax4.set_xticks(range(3))
ax4.set_xticklabels(stages)
ax4.set_title('Stages of the Funnel')
plt.show()
plt.savefig('bar_funnel_2.png')


# In[30]:


# Running some more SQL queries to see how long the test was run
# I'm an idiot - I was told they started in July at the beginning of the notebook...

# First visit
print("First visit: \n")
sql_query('''
SELECT *
FROM visits
ORDER BY visit_date ASC
LIMIT 1
''')


# In[31]:


# Last visit
print("Last visit: \n")
sql_query('''
SELECT *
FROM visits
ORDER BY visit_date DESC
LIMIT 1
''')


# In[32]:


# First fitness test
print("First fitness test: \n")
sql_query('''
SELECT *
FROM fitness_tests
ORDER BY fitness_test_date ASC
LIMIT 1
''')


# In[33]:


# Last fitness test
print("Last fitness test: \n")
sql_query('''
SELECT *
FROM fitness_tests
ORDER BY fitness_test_date DESC
LIMIT 1
''')


# In[34]:


# First application
print("First application: \n")
sql_query('''
SELECT *
FROM applications
ORDER BY application_date ASC
LIMIT 1
''')


# In[35]:


# Last application
print("Last application: \n")
sql_query('''
SELECT *
FROM applications
ORDER BY application_date DESC
LIMIT 1
''')


# In[36]:


# First purchase
print("First purchase: \n")
sql_query('''
SELECT *
FROM purchases
ORDER BY purchase_date ASC
LIMIT 1
''')


# In[37]:


# Last purchase
print("Last purchase: \n")
sql_query('''
SELECT *
FROM purchases
ORDER BY purchase_date DESC
LIMIT 1
''')

