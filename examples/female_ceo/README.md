
# Research of Female CEO

This is a research which is done by [Karen Rubin from Quantopian](https://www.quantopian.com/posts/investing-in-female-ceos-sector-neutral-a-different-benchmark-and-new-data)
on over market return of Female lead CEO company in market.

This represent a pipeline which illustrate the data.


## Raw data used

* Female CEO classification CSV - provided from [Karen's dropbox](https://www.dropbox.com/sh/qb0qjhzhbbmoaxq/AACiXyN25R0QKg7Js6T2IDbra?dl=0&preview=FemaleCEOs_v6.csv)
* List of pricing data from a list of related universe of 500 tickers (roughly represent top tickers)

Data that can be used for practice
* [Sample sentimental data from AlphaOne](https://www.quandl.com/data/AOS-Alpha-One-Sentiment-Data?filterSelection=sample)
  - Both tickers for `IBM` and `DD` (Dupont) is available which can be used as practice enrichment process


## A brief discussion of the pipeline

We discuss building this pipeline iteratively


### 1. Obtaining augmenting data

Pull daily pricing data for the from outside data sources (Yahoo in this case)

Lesson:

- How to cross-validate between different sources?
- How to generate initial fixtures?
- How to treat fixture files?

### 2. Calculate CEO change effect

Calculate the CEO change effect

Lesson:

- How to capture real data for testing?
- How to capture edge cases (e.g. weekend days)?

### 3. Calculate moving average of previous price based on start date

We calculate the moving average previously

Lesson:
- How to validate against edge case?
- How to detect abnormal edge case?

### 4. Apply a fake buy/sell signal based on data

We want to ensure that our buy/sell signal is not crazy.

Lesson:
- Using failsafe signal on fail-safe catch
- How to emit metrics and graph automatically?

### 5. Extended: Debugging a SQL statement

We compose all the data into a SQLlite query, and ensure that we validate each
step of the SQL query.

### 6. Extended: Black box validation

For someone who doesn't understand complex moving average data, they should
be able to:
* visualize and understand
* apply simple cross validate features
* judge how well the model does
