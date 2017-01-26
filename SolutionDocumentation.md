# Solution Documentation

This code takes an input event file in the main function and performs two methods: ingest(e, D) and topXSimpleLTVCustomers(x, stats).

## Language and Packages

This code is written in Python 2.7. Three packages are used: _pandas_, _datetime_, and _math_.

## Process

### Main function

1. A DataFrame `stats` is defined to store the statistics of every customer by `customer_id`, including total expenditures `total_exp`, total number of site visits `total_visit`, first day of site visit `first_day`, expenditures per visit `exp_per_visit`, visits per week `visit_per_week`, and lifetime value `ltv`.

2. A list `data` is defined to store the incoming events. A dictionary `D` combines `stats` and `data` to pass into method `ingest(e, D)`.

3. The input file `input.txt` is read to `incoming` as a DataFrame.

4. For every row in `incoming`, the method `ingest(e, D)` is called to process the row, store the row to `data` and update `stats`.

5. The method `topXSimpleLTVCustomers(x, stats)` is called to generate top x customers with highest LTVs and save the results to an output file `output.txt` in JSON format.

### ingest(e, D)

`e` is a Series containing one event. `D` contains address to a list `data` and a DataFrame `stats`. This method will process event `e`, update `data` and `stats` in-place, and will not return anything.

1. `e` is appended to the `data` list.

2. The type of the event is then checked. For the purpose of this problem, if event type is 'IMAGE', no further process will be made, since it does not contain statistics related here.

3. For all other types, `event_date` is determined from the event's event_time, as smallest time precision of stats calculated in this problem is days. A variable `cid` is defined as customer id for the event.

  1. If event type is 'CUSTOMER', `cid` is obtained from `key` in the event. If `cid` is not in the index of `stats`, a new row with index `cid` is initiated, with `first_day` being the `event_date` and all other values being 0.

  2. If event type is 'SITE_VISIT', `cid` is obtained from `customer_id` in the event. If `cid` is not in the index of `stats`, a new row with index `cid` is initiated, with `first_day` being the `event_date`, and number of visit `total_visit` being 1; otherwise increase `total_visit` by 1, and choose the earlier date value between existing `first_day` and the event's `event_date` as the new `first_day`.

  3. If event type is 'ORDER', `cid` is obtained from `customer_id` in the event. If `cid` is not in the index of `stats`, a new row with index `cid` is initiated, with `first_day` being the `event_date`, and expenditure amount `total_exp` being the value of `total_amount` in the event; otherwise add the value of `total_amount` in the event to `total_exp` in `stats`.

4. For the customer `cid` in the event, the expenditure per visit `exp_per_visit` is calculated and saved in `stats`, by dividing `total_exp` with `total_visit` and rounding to 2 decimals.

5. The number of weeks `num_weeks` from the customer's first site-visit date to current date is calculated by dividing the days by 7, then rounding up. This ensures an accurate ratio of visits per week, rather than separating weeks by a fixed day of week. Then the visits per week `visit_per_week` is calculated by dividing `total_visit` by `num_weeks` and rounding to 2 decimals.

6. The lifetime value of a customer, `ltv`, is calculated using the equation `exp_per_visit` * `visit_per_week` * 52 * 10, where 10 is the Shutterfly average lifespan.

### topXSimpleLTVCustomers(x, stats)

`x` is the number of top customers needed, and stats is the statistics of every customer, containing updated lifetime value `ltv`. This method first sorts `stats` by `ltv` in descending order, then writes the top `x` records of `ltv` and corresponding `customer_id` to a JSON-formatted output file `output.txt`.


## Justifications for Data Structures

1. `data` as a list. For the purpose of this problem, new data is frequently ingested and stored in `data`. If a DataFrame is used for `data`, every time a new record is appended, the whole data frame will be copied, which costs both space and time. Using a list and appending new events to the list takes an average time complexity of O(1), without copying the whole list.

2. `stats` as a DataFrame. `stats` is used to store aggregated statistics of every customer, and is updated with every incoming event. The advantage is that whenever a statistics is required, such as a customer's LTV or top customers with highest LTVs, a quick search can be performed to give outputs promptly, without having to scan through the whole `data` every time a statistics is needed. A trade-off is that time for `ingest(e, D)` will be longer due to frequent update of `stats`. However, as `ingest(e, D)` only updates `stats` by indexed customer ID, the computation time and memory requirement is lower than scanning through all the data. Therefore, in the case of frequent request for statistics, a `stats` DataFrame is preferred, as coded in this solution.

## Test Cases

The test input contains events for four customers, represented by strings: `test0`, `test1`, `test2`, and `test3`. For the scope of this problem, all the incoming events are assumed correct in format and without missing required fields.

1. `test0` tests capture of multiple SITE_VISIT events with random time sequences and multiple ORDERS. Events are coming in the sequence of ['CUSTOMER', 'SITE_VISIT' (3rd), 'SITE_VISIT' (2nd), 'SITE_VISIT' (1st), 'ORDER', 'ORDER']. Its stats will contain 3 `total_visit`, earliest `first_day` among 3 site visits, sum of two order amounts in `total_exp`, and corresponding other statistics.

2. `test1` tests situation when a event of the customer comes before the first 'CUSTOMER'-type event is ingested. Events are coming in the sequence of ['SITE_VISIT', 'ORDER', 'CUSTOMER', 'ORDER', 'ORDER']. Its stats will contain 1 `total_visit`, `first_day` for the site visit, sum of three order amounts in `total_exp`, and corresponding other statistics.

3. `test2` tests the impact of 'IMAGE'-type event. For this problem, 'IMAGE' events are not used in stats. Events are coming in the sequence of ['CUSTOMER', 'SITE_VISIT', 'IMAGE', 'ORDER']. Its stats will contain 1 `total_visit`, `first_day` for the site visit, the order amount in `total_exp`, and corresponding other statistics.

4. `test3` tests stats results when there is no 'SITE_VISIT' or 'ORDER' for a customer. Only one event is present: 'CUSTOMER'. Its stats will contain `first_day` when the event is generated, and NaN value for `ltv`.

The output of method `topXSimpleLTVCustomers(x, stats)` is stored in `output.txt` under `output` directory. In the test case, `x` is set to 2, and the top two customers, `test1` and `test0`, with their LTVs, are saved in the file.
