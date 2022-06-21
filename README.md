# Concept-Drift-NHANES-Diabetes-Classification

### Overview
The contents of this repository conducts drift detection on models predicting diabetes using data from the National Health and Nutrition Examination Survey (NHANES) scraped from the CDC website below:

https://www.cdc.gov/nchs/nhanes/index.htm

### Concept Drift
Most machine learning models are deployed in a dynamic environment where the statistical properties of the outcome variable change the relationship between the outcome and predictor variables across time, a process called concept drift. This is important to monitor and detect such shifts in deployed models to keep models relevant, since concept drift can lead to poor and misleading results. These changes can take place suddenly, incrementally with multiple intermediate steps, gradually with a slow shift from one distribution to a second distribution without intermediate steps, or reoccurring with a previous relationship reoccurring at a later point in time. 