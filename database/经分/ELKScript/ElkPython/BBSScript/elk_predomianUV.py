# -*- coding: utf-8 -*-
from __future__ import division

__author__ = 'Abbott'

import datetime
import time
import mysqlconf
from elk_common import *
import uuid

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
DocType = 'predomain'

PreDomainUvdoc = {
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
    "size": 0,
    "aggs": {
        "domain": {
            "terms": {
                "field": "http_host.raw",
                "size": 0,
                "order": {
                    "_count": "desc"
                }
            },
            "aggs": {
                "session": {
                    "terms": {
                        "field": "uuid.raw",
                        "size": 0,
                        "order": {
                            "_count": "desc"
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

PreDomainSessionDoc = {
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
        "domain": {
            "terms": {
                "field": "domain.raw",
                "size": 0,
                "order": {
                    "pvcount": "desc"
                }
            },
            "aggs": {
                "pvcount": {
                    "sum": {
                        "field": "sessionpvcount"
                    }
                },
                "sessioncount": {
                    "cardinality": {
                        "field": "sessionid.raw"
                    }
                },
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

GlobalPreSeesionMapping = {
    "predomain": {
        "properties": {
            "timestamp": {"type": "date"},
            "myid": {"type": "multi_field",
                       "fields": {
                           "myid": {"type": "string", "index": "analyzed"},
                           "raw": {"type": "string", "index": "not_analyzed"}
                       }},
            "domain": {"type": "multi_field",
                       "fields": {
                           "domain": {"type": "string", "index": "analyzed"},
                           "raw": {"type": "string", "index": "not_analyzed"}
                       }},
            "sessionid": {"type": "multi_field",
                          "fields": {
                              "sessionid": {"type": "string", "index": "analyzed"},
                              "raw": {"type": "string", "index": "not_analyzed"}
                          }},
            "sessionpvcount": {"type": "long"},
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

insert_sql = "insert into discuz_domain_uv_stat(domains, sessioncounts, newsessionrate, newusercounts, pvpersession, timepresession, stat_date) value ('%s', '%d', '%.2f', '%d', '%.2f', '%.2f', '%s')"
if __name__ == '__main__':
    preDomainRes = RunElasticsearch(ElkAddress, LogstatshIndex, PreDomainUvdoc)
    #print preDomainRes['aggregations']['domain']['buckets']

    for PD in preDomainRes['aggregations']['domain']['buckets']:
        for PS in PD['session']['buckets']:
            # print PD['key'], PD['doc_count'], PS['key'], PS['maxtime']['value_as_string'], PS['mintime'][
                # 'value_as_string'], PS['doc_count']
            # Ids = '%s-%s' % (PD['key'], PS['key'])
            Ids = str(uuid.uuid1())
            InputBody = {
                    'myid': Ids,
                    'timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                    'domain': PD['key'],
                    'sessionid': PS['key'],
                    "sessionpvcount": PS['doc_count'],
                    'maxtimes': PS['maxtime']['value_as_string'],
                    'maxtimestamp': int(PS['maxtime']['value']),
                    'mintimes': PS['mintime']['value_as_string'],
                    'mintimestamp': int(PS['mintime']['value'])
                }
            InputElasticsearch(ElkAddress, TargeIndex, GlobalPreSeesionMapping, DocType, Ids, InputBody)


    preDomainSessionRes = RunElasticsearch(ElkAddress, TargeIndex, PreDomainSessionDoc)
    for PDS in preDomainSessionRes['aggregations']['domain']['buckets']:
        # print PDS['key'], PDS['sessioncount']['value'], PDS['pvcount']['value'], PDS['keeptime']['value'], float('%.2f' % (PDS['pvcount']['value'] / PDS['sessioncount']['value'])), float('%.2f' % (PDS['keeptime']['value'] / PDS['sessioncount']['value']))


        # save mysql
        datetimes = (datetime.date.today() - datetime.timedelta(days=day)).strftime("%Y-%m-%d 00:00:00")
        mysql_conf.sql_exec(DB_HOST, DB_USER, DB_PASSWD, DB_PORT, DB_DATABASE, DB_CHAR_SET, insert_sql % (PDS['key'],
            int(PDS['sessioncount']['value']), float('%.2f' % 2.5), 1000, float('%.2f' % (PDS['pvcount']['value'] / PDS['sessioncount']['value'])),
            float('%.2f' % (PDS['keeptime']['value'] / PDS['sessioncount']['value'] / 1000)),
            datetimes))
    DeleteElasticsearch(ElkAddress, TargeIndex)



