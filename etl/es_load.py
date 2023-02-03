import json
import logging
from dataclasses import asdict

from decorator import backoff
from elasticsearch.exceptions import RequestError
from index import INDEXES
from settings import Settings


class ES_LOAD:
    def __init__(self, conn):
        self.cnf = Settings()
        self.conn = conn

    @backoff(logger=logging.getLogger('es_load::create_index'))
    def create_index(self, index: int):
        """
        Создание индекса в es
        """
        try:
            self.conn.indices.create(self.cnf.elastic_index[index], body=INDEXES[index])
        except RequestError as e:
            if e.error == 'resource_already_exists_exception':
                pass
            else:
                logging.error(e)
                raise e

    @backoff(logger=logging.getLogger('es_load::bulk_update'))
    def bulk_update(self, index:int, docs) -> bool:
        """
        Запись данных в es
        """
        if not docs:
            logging.warning('No more data to update in elastic')
            return None
        body = []
        for doc in docs:
            es_index = {"index": {"_index" : self.cnf.elastic_index[index], "_id" : doc.id}}
            body.append(json.dumps(es_index))
            body.append(json.dumps(asdict(doc)))
        results = self.conn.bulk(body)
        if results['errors']:
            error = [result['index'] for result in results['items'] if result['index']['status'] != 200]
            logging.error(results['took'])
            logging.error(results['errors'])
            logging.error(error)
            return None
        return True