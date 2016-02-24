# -*- coding: utf-8 -*-
__author__ = 'Abbott'

import datetime
from elasticsearch import Elasticsearch




def RunElasticsearch(ElkAddress, LogstatshIndex, SearchBody):
    # Get time row
    times = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y.%m.%d")
    # times = '2015.10.25'

    # Connect elasticsearch API
    es = Elasticsearch("%s" % ElkAddress)

    # Number of query result data
    max_result_number = 0

    # Data index name
    logstash_index = '%s' % LogstatshIndex

    # Execute elasticsearch search, res is result, u can use it that get ur rows
    res = es.search(index=logstash_index, size=max_result_number, body=SearchBody)

    return res


def InputElasticsearch(ElkAddress, TargeIndex, Mapping, DocType, Ids, InputBody):
    es = Elasticsearch("%s" % ElkAddress)
    if Mapping != 'None':
        es.indices.create(index=TargeIndex, body=Mapping, ignore=400)
        es.indices.put_mapping(index=TargeIndex, doc_type=DocType, body=Mapping)
    res = es.index(index=TargeIndex, doc_type=DocType, id=Ids, body=InputBody)
    # print res


def DeleteElasticsearch(ElkAddress, TargeIndex):
    es = Elasticsearch("%s" % ElkAddress)
    es.indices.delete(index=TargeIndex, ignore=[400, 404])


def UpdateElasticsearch(ElkAddress, TargeIndex, DocType, Ids, UpdateBody):
    es = Elasticsearch("%s" % ElkAddress)
    es.update(index=TargeIndex, doc_type=DocType, id=Ids, body=UpdateBody)
    es.indices.refresh(index=TargeIndex)

def GetElasticsearch(ElkAddress, TargeIndex, DocType, Ids):
    es = Elasticsearch("%s" % ElkAddress)
    try:
        res = es.get(index=TargeIndex, doc_type=DocType, id=Ids)
        # print res
        return True
    except:
        return False
    # return res
