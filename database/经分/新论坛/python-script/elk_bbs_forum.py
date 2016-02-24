# -*- coding: utf-8 -*-
__author__ = 'Abbott'

import datetime
from elasticsearch import Elasticsearch
import mysqlconf

mysql_conf = mysqlconf.mysql_connect()
import time

insert_sql = "insert into discuz_api_stat(api_source_name, api_name, api_counts, invt_time) value ('%s', '%s', '%d', '%d')"


# Get time row
times = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y.%m.%d")
# times = '2015.10.25'

# Connect elasticsearch API
es = Elasticsearch("http://172.16.31.100:9200/")

# Number of query result data
max_result_number = 0

starttime = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
endtime = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d 23:59:59")

starttimestamp = "%s000" % int(time.mktime(time.strptime(starttime, '%Y-%m-%d %H:%M:%S')))
endtimestamp = "%s999" % int(time.mktime(time.strptime(endtime, '%Y-%m-%d %H:%M:%S')))

# Data index name
# logstash_index = 'logstash-%s' % times
logstash_index = 'logstash-*'

# send elasticsearch API mapping
body = {
  "query": {
    "filtered": {
      "query": {
        "query_string": {
          "analyze_wildcard": 'true',
          "query": "_exists_:fid"
        }
      },
      "filter": {
        "bool": {
          "must": [
            {
              "range": {
                "@timestamp": {
                  "gte": 1449504000000,
                  "lte": 1449590399999
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
    "2": {
      "terms": {
        "field": "http_host.raw",
        "size": 100,
        "order": {
          "_count": "desc"
        }
      },
      "aggs": {
        "4": {
          "terms": {
            "field": "fid.raw",
            "size": 600,
            "order": {
              "_count": "desc"
            }
          },
          "aggs": {
            "3": {
              "cardinality": {
                "field": "uid.raw"
              }
            },
            "5": {
              "cardinality": {
                "field": "clientip.raw"
              }
            }
          }
        }
      }
    }
  }
}


# Execute elasticsearch search, res is result, u can use it that get ur rows
res = es.search(index=logstash_index, size=max_result_number, body=body)
print res


# result list
# result_list = res['aggregations']['mydata']['buckets']
#
# #processing results
# for result in result_list:
#     datetimes = datetime.datetime.strptime(result['key_as_string'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime("%Y%m%d")
#     for r in result['api_data']['buckets']:
#         #save mysql
#         if r['key'] in api_dic.keys():
#             mysql_conf.sql_exec(insert_sql % (r['key'], api_dic[r['key']], r['doc_count'], int(datetimes)))
#         else:
#             now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             f = open(elk_log_path, 'ab+')
#             f.write("%s\n\n" % now_time)
#             f.write("%s\n\n" % r['key'])
#             f.write("\n\n\n")
#             f.close()
