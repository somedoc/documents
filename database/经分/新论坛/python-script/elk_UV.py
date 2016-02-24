# -*- coding: utf-8 -*-
from __future__ import division
__author__ = 'Abbott'

import datetime
import time
import mysqlconf
from elk_common import *

day = 4

starttime = (datetime.date.today() - datetime.timedelta(days=day)).strftime("%Y-%m-%d 00:00:00")
endtime = (datetime.date.today() - datetime.timedelta(days=day)).strftime("%Y-%m-%d 23:59:59")

starttimestamp = "%s000" % int(time.mktime(time.strptime(starttime, '%Y-%m-%d %H:%M:%S')))
endtimestamp = "%s999" % int(time.mktime(time.strptime(endtime, '%Y-%m-%d %H:%M:%S')))

todaystarttime = datetime.date.today().strftime("%Y-%m-%d 00:00:00")
todayendtime = datetime.date.today().strftime("%Y-%m-%d 23:59:59")

todaystarttimestamp = "%s000" % int(time.mktime(time.strptime(todaystarttime, '%Y-%m-%d %H:%M:%S')))
todayendtimestamp = "%s000" % int(time.mktime(time.strptime(todayendtime, '%Y-%m-%d %H:%M:%S')))

ElkAddress = 'http://172.16.31.100:9200/'
LogstatshIndex = 'logstash-*'
TargeIndex = 'interim'
DocType = 'presession'

GlobalPreSeesionBody = {
    "size": 0,
    "query": {
        "filtered": {
            "query": {
                "query_string": {
                    "query": "_exists_:fid",
                    "analyze_wildcard": "true"
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
        "mysession": {
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

GlobalUuidBody = {
    "size": 0,
    "query": {
        "filtered": {
            "query": {
                "query_string": {
                    "query": "_exists_:fid",
                    "analyze_wildcard": "true"
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
        "mysession": {
            "cardinality": {
                "field": "uuid.raw"
            }
        }
    }
}

GlobalSessionKeepTimeBody = {
    "size": 0,
    "query": {
        "filtered": {
            "query": {
                "query_string": {
                    "query": "_type:presession",
                    "analyze_wildcard": "true"
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
        "1": {
            "sum": {
                "script": "doc['maxtimes'].value-doc['mintimes'].value",
                "lang": "expression"
            }
        }
    }
}

GlobalPreSeesionMapping = {
    "presession": {
        "properties": {
            "timestamp": {"type": "date"},
            "sessionid": {"type": "string"},
            "maxtimes": {"type": "date"},
            "maxtimestamp": {"type": "long"},
            "mintimes": {"type": "date"},
            "mintimestamp": {"type": "long"}
        }
    }
}

DB_HOST = '127.0.0.1'
DB_USER = 'abbott'
DB_PASSWD = '123456'
DB_PORT = 3366
DB_DATABASE = 'discuz_stat'
DB_CHAR_SET = 'utf8'

mysql_conf = mysqlconf.mysql_connect()

insert_sql = "insert into discuz_uv_stat(sessioncounts, newsessionrate, newusercounts, pvpersession, timepresession, stat_date) value ('%d', '%.2f', '%d', '%.2f', '%.2f', '%s')"
if __name__ == '__main__':
    GlobalUuidRes = RunElasticsearch(ElkAddress, LogstatshIndex, GlobalUuidBody)
    GlobalPreSeesionRes = RunElasticsearch(ElkAddress, LogstatshIndex, GlobalPreSeesionBody)
    GlobalPV = GlobalUuidRes['hits']['total']
    GlobalSession = GlobalUuidRes['aggregations']['mysession']['value']

    for PS in GlobalPreSeesionRes['aggregations']['mysession']['buckets']:
        InputBody = {
            'timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'sessionid': PS['key'],
            'maxtimes': PS['maxtime']['value_as_string'],
            'maxtimestamp': int(PS['maxtime']['value']),
            'mintimes': PS['mintime']['value_as_string'],
            'mintimestamp': int(PS['mintime']['value'])
        }
        InputElasticsearch(ElkAddress, TargeIndex, GlobalPreSeesionMapping, DocType, InputBody)

    GlobalSessionKeepTime = RunElasticsearch(ElkAddress, TargeIndex, GlobalSessionKeepTimeBody)
    GlobalSessionKeepTimeCount = GlobalSessionKeepTime['hits']['total']

    # save mysql
    datetimes = (datetime.date.today() - datetime.timedelta(days=day)).strftime("%Y-%m-%d 00:00:00")
    mysql_conf.sql_exec(DB_HOST, DB_USER, DB_PASSWD, DB_PORT, DB_DATABASE, DB_CHAR_SET, insert_sql % (
        int(GlobalSession), float('%.2f' % 2.5), 1000, float('%.2f' % (GlobalPV / GlobalSession)),
        float('%.2f' % (GlobalSessionKeepTimeCount / GlobalSession)),
        datetimes))
    DeleteElasticsearch(ElkAddress, TargeIndex)
    # result list
    # result_list = res['aggregations']['mydomain']['buckets']
    #
    # # #processing results
    # for result in result_list:
    #     datetimes = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
    #     domain = result['key']
    #     for r in result['myforum']['buckets']:
    #         #save mysql
    #         mysql_conf.sql_exec(DB_HOST, DB_USER, DB_PASSWD, DB_PORT, DB_DATABASE, DB_CHAR_SET, insert_sql % (
    #         domain, int(r['key']), r['doc_count'], r['myclinetip_counts']['value'], r['myuser_counts']['value'],
    #         datetimes))


