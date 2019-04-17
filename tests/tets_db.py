import logging
import uuid

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
    department = Department('test_create_thesis', 'Cybernetics')
    department.create(database)

    instructor = Instructor(str(uuid.uuid4()), Degree.PROFESSOR, 12, '213')
    instructor.create(database, department.department_id)

    thesis = Thesis('Create new features!@#$', 'Some fancy description',
                    UniversityYear.BACHELOR_FOURTH, 4)
    instructor.add_thesis(database, thesis, '')
    result = database.find(thesis.node_type, {'thesis_name': thesis.thesis_name})
    assert len(result) == 1
    logging.info(f'Got thesis object: {result.first()}')
    assert result.first()


def test_create_instructor(database):
    obj = database.find_one(Department.node_type, {'name': 'Informatics'})
    assert obj
    i = Instructor('5cb673e70d34e12dab8cd206', Degree.PROFESSOR, 12, '213')
    i.create(database, obj['department_id'])
    result = database.find_one(i.node_type, i.to_dict())
    assert result


def test_create_department(database):
    d = Department('Informatics', 'Cybernetics')
    d.create(database)
    result = database.find_one(d.node_type, d.to_dict())
    assert result


def test_find_all(database):
    result = database.find(Thesis.node_type)
    for i in result:
        print(i)


def test_create_group(database):
    g = Group('Super Team', UniversityYear.BACHELOR_FOURTH, Degree.BACHELOR)
    g.create(database, '123')
    result = database.find_one(g.node_type, g.to_dict())
    assert result


def test_enrol(database):
    name = 'Lorem Ipsum'
    Thesis.thesis_enrol(database, name, '5cb673e70d34e12dab8cd206')


def test_delete(database):
    result = database.find(Thesis.node_type, {'name': '*'})
    database.graph.delete(result)


def test_get_thesis_per_instructor(database):
    i = Instructor('5cb673e70d34e12dab8cd206')
    print(i.get_thesis(database))


def test_delete_thesis(database):
    i = Instructor('5cb673e70d34e12dab8cd206')
    thesis = Thesis('to delete thesis test', 'Some fancy description',
                    UniversityYear.BACHELOR_FOURTH, 4)
    i.add_thesis(database, thesis, '')
    assert database.find_one(Thesis.node_type, {'thesis_name': 'to delete thesis test'})
    i.delete_thesis(database, 'to delete thesis test')
    assert not database.find_one(Thesis.node_type,
                             {'thesis_name': 'to delete thesis test'})
