import logging

import pytest

from db.db_neo4j import GraphDatabaseClient, Thesis, UniversityYear

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('pytest.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter(
        '%(asctime)s %(filename)25s:%(lineno)-4d %(levelname)-8s %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


@pytest.fixture
def database():
    yield GraphDatabaseClient()


def test_create_thesis(database):
    thesis = Thesis('Create new features!@#$', 'Some fancy description',
                    UniversityYear.BACHELOR_FOURTH, 4)
    thesis.create(database)
    result = database.find(thesis.node_type, {'name': thesis.name})
    assert len(result) == 1
    logging.info(f'Got thesis object: {result}')
    assert result
