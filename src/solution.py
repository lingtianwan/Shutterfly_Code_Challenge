# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 14:58:54 2017

@author: lingtian
"""
import pandas as pd
import datetime
import math


def ingest(e, data, stats):
    """
    Update data with event e, and update stats.

    Args:
        e: Series, stores a line of event
        data: list, stores all event data
        stats: DataFrame, stores all customers' related statistics

    Returns:
        None
    """
    data.append(e)
    if e['type'] == 'IMAGE':
        return
    event_date = datetime.datetime.strptime(e['event_time'][:10], '%Y-%m-%d')
    cid = ''
    if e['type'] == 'CUSTOMER':
        cid = e['key']
        if cid not in stats.index:
            stats.loc[cid] = [0.0, 0, event_date, 0, 0.0, 0.0]
    elif e['type'] == 'SITE_VISIT':
        cid = e['customer_id']
        if cid not in stats.index:
            stats.loc[cid] = [0.0, 1, event_date, 0, 0.0, 0.0]
        else:
            stats.loc[cid, 'total_visit'] += 1
            stats.loc[cid, 'first_day'] = min(stats.loc[cid, 'first_day'],
                                              event_date)
    elif e['type'] == 'ORDER':
        cid = e['customer_id']
        expenditure = float(e['total_amount'][:-3])
        if cid not in stats.index:
            stats.loc[cid] = [expenditure, 0, event_date, 0, 0.0, 0.0]
        else:
            stats.loc[cid, 'total_exp'] += expenditure
    stats.loc[cid, 'exp_per_visit'] = round(stats.loc[cid]['total_exp'] /
                                            stats.loc[cid]['total_visit'], 2)
    num_weeks = math.ceil((datetime.datetime.utcnow() -
                          stats.loc[cid]['first_day']).days / 7.0)
    stats.loc[cid, 'visit_per_week'] = round(stats.loc[cid]['total_visit'] /
                                             num_weeks, 2)
    stats.loc[cid, 'ltv'] = stats.loc[cid]['exp_per_visit'] *\
        stats.loc[cid]['visit_per_week'] * 52 * 10


def topXSimpleLTVCustomers(x, stats):
    """
    Return top x customer ids with highest LTV.

    Args:
        x: int, number of top customers wanted
        stats: DataFrame, stores all customers' related statistics

    Returns:
        None
    """
    stats.sort_values(by='ltv', ascending=False)['ltv'][:x].\
        to_json('../output/output.txt')


if __name__ == '__main__':
    stats = pd.DataFrame(columns=['total_exp', 'total_visit', 'first_day',
                                  'exp_per_visit', 'visit_per_week', 'ltv'])
    data = []
    D = dict(stats=stats, data=data)
    incoming = pd.read_json('../input/input.txt')
    for index, row in incoming.iterrows():
        ingest(row, **D)
    topXSimpleLTVCustomers(2, stats)
