# -*- coding: utf-8 -*-
__author__ = 'Abbott'

import datetime
import time
import mysqlconf
from elk_common import *


starttime = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
endtime = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d 23:59:59")

starttimestamp = "%s000" % int(time.mktime(time.strptime(starttime, '%Y-%m-%d %H:%M:%S')))
endtimestamp = "%s999" % int(time.mktime(time.strptime(endtime, '%Y-%m-%d %H:%M:%S')))

ElkAddress = 'http://172.16.31.100:9200/'
LogstatshIndex = 'logstash-*'


# send elasticsearch API mapping
SearchBody = {
    "query": {
        "filtered": {
            "query": {
                "query_string": {
                    "query": "_exists_:fid",
                    "analyze_wildcard": 'true'
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
    "size": 0,
    "aggs": {
        "mydomain": {
            "terms": {
                "field": "http_host.raw",
                "size": 100,
                "order": {
                    "myuuid": "desc"
                }
            },
            "aggs": {
                "myuuid": {
                    "cardinality": {
                        "field": "uuid.raw"
                    }
                }
            }
        }
    }
}

DB_HOST = '172.16.31.50'
DB_USER = 'bos_usr'
DB_PASSWD = 'yse84fe6ddf8e376ddf8e3'
DB_PORT = 6980
DB_DATABASE = 'discuz_stat'
DB_CHAR_SET = 'utf8'

mysql_conf = mysqlconf.mysql_connect()

insert_sql = "insert into discuz_session_stat(domain_name, session_counts, stat_date) value ('%s', '%d', '%s')"
if __name__ == '__main__':
    res = RunElasticsearch(ElkAddress, LogstatshIndex, SearchBody)

    # result list
    result_list = res['aggregations']['mydomain']['buckets']

    # #processing results
    for result in result_list:
        datetimes = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
        domain = result['key']

        # save mysql
        mysql_conf.sql_exec(DB_HOST, DB_USER, DB_PASSWD, DB_PORT, DB_DATABASE, DB_CHAR_SET, insert_sql % (
            domain, result['myuuid']['value'], datetimes))