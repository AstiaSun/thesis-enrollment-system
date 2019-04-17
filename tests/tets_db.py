import logging

import pytest

from db.db_neo4j import GraphDatabaseClient, Thesis, UniversityYear, \
    Department, Group, Degree, Instructor

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
    thesis = Thesis('Create new features!@#$', 'Some fancy description', 123,
                    UniversityYear.BACHELOR_FOURTH, 4)
    thesis.create(database)
    result = database.find(thesis.node_type, {'name': thesis.name})
    assert len(result) == 1
    logging.info(f'Got thesis object: {result.first()}')
    assert result.first()


def test_create_instructor(database):
    i = Instructor(123, 123, Degree.PROFESSOR, 12, 213)
    i.create(database)
    result = database.find_one(i.node_type, i.to_dict())
    assert result


def test_create_department(database):
    d = Department(123, 'Informatics', 'Cybernetics')
    d.create(database)
    result = database.find_one(d.node_type, d.to_dict())
    assert result


def test_find_all(database):
    result = database.find(Thesis.node_type)
    for i in result:
        print(i)


def test_create_group(database):
    g = Group('Super Team', 123, UniversityYear.BACHELOR_FOURTH, Degree.BACHELOR)
    g.create(database)
    result = database.find_one(g.node_type, g.to_dict())
    assert result
