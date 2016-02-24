# -*- coding: utf-8 -*-
from __future__ import division

__author__ = 'Abbott'

import datetime
import time
import mysqlconf
from elk_common import *

day = 1

starttime = (datetime.date.today() - datetime.timedelta(days=day)).strftime("%Y-%m-%d 00:00:00")
endtime = (datetime.date.today() - datetime.timedelta(days=day)).strftime("%Y-%m-%d 23:59:59")

starttimestamp = "%s000" % int(time.mktime(time.strptime(starttime, '%Y-%m-%d %H:%M:%S')))
endtimestamp = "%s999" % int(time.mktime(time.strptime(endtime, '%Y-%m-%d %H:%M:%S')))

todaystarttime = datetime.date.today().strftime("%Y-%m-%d 00:00:00")
todayendtime = datetime.date.today().strftime("%Y-%m-%d 23:59:59")

todaystarttimestamp = "%s000" % int(time.mktime(time.strptime(todaystarttime, '%Y-%m-%d %H:%M:%S')))
todayendtimestamp = "%s000" % int(time.mktime(time.strptime(todayendtime, '%Y-%m-%d %H:%M:%S')))

ElkAddress = 'http://10.72.3.29:9200/'
LogstatshIndex = 'logstash-*'
TargeIndex = 'interim'
DocType = 'prepage'

GlobalPageTimeBody = {
    "size": 0,
    "query": {
        "filtered": {
            "query": {
                "query_string": {
                    "analyze_wildcard": "true",
                    "query": "*"
                }
            },
            "filter": {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": starttimestamp,
                                    "lte": endtimestamp
                                }
                            }
                        }
                    ],
                    "must_not": []
                }
            }
        }
    },
    "aggs": {
        "url": {
            "terms": {
                "field": "request.raw",
                "size": 0,
                "order": {
                    "maxtime": "desc"
                }
            },
            "aggs": {
                "maxtime": {
                    "max": {
                        "field": "@timestamp"
                    }
                },
                "sessionid": {
                    "terms": {
                        "field": "uuid.raw",
                        "size": 0,
                        "order": {
                            "maxtime": "desc"
                        }
                    },
                    "aggs": {
                        "maxtime": {
                            "max": {
                                "field": "@timestamp"
                            }
                        },
                        "mintime": {
                            "min": {
                                "field": "@timestamp"
                            }
                        }
                    }
                }
            }
        }
    }
}

GlobalPrePageTimeBody = {
    "size": 0,
    "query": {
        "filtered": {
            "query": {
                "query_string": {
                    "analyze_wildcard": "true",
                    "query": "*"
                }
            },
            "filter": {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "timestamp": {
                                    "gte": todaystarttimestamp,
                                    "lte": todayendtimestamp
                                }
                            }
                        }
                    ],
                    "must_not": []
                }
            }
        }
    },
    "aggs": {
        "page": {
            "terms": {
                "field": "page.raw",
                "size": 0,
                "order": {
                    "_count": "desc"
                }
            },
            "aggs": {
                "keeptime": {
                    "sum": {
                        "script": "doc['maxtimes'].value-doc['mintimes'].value",
                        "lang": "expression"
                    }
                }
            }
        }
    }
}

GlobalPrePageMapping = {
    "prepage": {
        "properties": {
            "timestamp": {"type": "date"},
            "page": {"type": "multi_field",
                     "fields": {
                         "page": {"type": "string", "index": "analyzed"},
                         "raw": {"type": "string", "index": "not_analyzed"}
                     }},
            "sessionid": {"type": "multi_field",
                          "fields": {
                              "sessionid": {"type": "string", "index": "analyzed"},
                              "raw": {"type": "string", "index": "not_analyzed"}
                          }},
            "maxtimes": {"type": "date"},
            "maxtimestamp": {"type": "long"},
            "mintimes": {"type": "date"},
            "mintimestamp": {"type": "long"}
        }
    }
}

DB_HOST = '10.72.3.29'
DB_USER = 'abbott'
DB_PASSWD = '123456'
DB_PORT = 3308
DB_DATABASE = 'discuz_stat'
DB_CHAR_SET = 'utf8'

mysql_conf = mysqlconf.mysql_connect()

insert_sql = "insert into discuz_page_pv_stat(pages, pvcounts, avgtimeonpage, stat_date) value ('%s', '%d', '%.2f', '%s')"
insert_pv_sql = "insert into discuz_pv_stat(pvcounts, avgtimeonpage, stat_date) value ('%d', '%.2f', '%s')"
if __name__ == '__main__':
    GlobalPageTimeRes = RunElasticsearch(ElkAddress, LogstatshIndex, GlobalPageTimeBody)

    GlobalPV = GlobalPageTimeRes['hits']['total']
    # GlobalPage = GlobalPageRes['aggregations']['page']['buckets']
    # print GlobalPageTimeRes

    for PT in GlobalPageTimeRes['aggregations']['url']['buckets']:
        for pt in PT['sessionid']['buckets']:
            # print PT['key'], pt['mintime']['value_as_string'], pt['maxtime']['value_as_string'], pt['key']
            InputBody = {
                'timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'page': PT['key'],
                'sessionid': pt['key'],
                'maxtimes': pt['maxtime']['value_as_string'],
                'maxtimestamp': int(pt['maxtime']['value']),
                'mintimes': pt['mintime']['value_as_string'],
                'mintimestamp': int(pt['mintime']['value'])
            }
            InputElasticsearch(ElkAddress, TargeIndex, GlobalPrePageMapping, DocType, InputBody)

    GlobalPrePageTimeRes = RunElasticsearch(ElkAddress, TargeIndex, GlobalPrePageTimeBody)
    # print GlobalPrePageTimeRes['aggregations']['page']['buckets']
    sum = 0
    datetimes = (datetime.date.today() - datetime.timedelta(days=day)).strftime("%Y-%m-%d 00:00:00")
    for PPT in GlobalPrePageTimeRes['aggregations']['page']['buckets']:
        # print PPT['key'], PPT['keeptime']['value'], PPT['doc_count']
        sum = sum + PPT['keeptime']['value']
        # save mysql

        mysql_conf.sql_exec(DB_HOST, DB_USER, DB_PASSWD, DB_PORT, DB_DATABASE, DB_CHAR_SET, insert_sql % (
        PPT['key'], PPT['doc_count'], float('%.2f' % (PPT['keeptime']['value'] / PPT['doc_count'] / 1000)), datetimes))

    mysql_conf.sql_exec(DB_HOST, DB_USER, DB_PASSWD, DB_PORT, DB_DATABASE, DB_CHAR_SET, insert_pv_sql % (GlobalPV, float('%.2f' % (sum / GlobalPV / 1000)), datetimes))
    DeleteElasticsearch(ElkAddress, TargeIndex)



