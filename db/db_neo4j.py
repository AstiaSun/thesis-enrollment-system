import uuid
from datetime import datetime
from typing import Optional

from py2neo import Graph, Node, Relationship, NodeMatcher

from db.exceptions import ObjectExistsException, IncorrectArgumentException, \
    ObjectDoesNotExist
from settings import NEO4J_HOSTNAME, NEO4J_USER, NEO4J_PORT, NEO4J_PASSWORD


class GraphDatabaseClient:
    def __init__(self, hostname: str = NEO4J_HOSTNAME, port: int = NEO4J_PORT,
                 user: str = NEO4J_USER, password: str = NEO4J_PASSWORD):
        url = f'bolt://{hostname}:{port}/db/data/'
        self.graph = Graph(url, username=user, password=password)

    def find(self, node_type: str, properties: Optional[dict] = None):
        matcher = NodeMatcher(self.graph)
        if properties is None:
            return matcher.match(node_type)
        return matcher.match(node_type, **properties)

    def find_one(self, node_type, properties: dict):
        matcher = NodeMatcher(self.graph)
        return matcher.match(node_type, **properties).first()


class ThesisStatus:
    CREATED = 0
    CANCELED = 1
    ENROLLED = 2
    APPROVED = 3
    VERIFIED = 4
    DEFENCED = 5
    NOT_DEFENCED = 6


class UniversityYear:
    BACHELOR_FIRST = 1
    BACHELOR_SECOND = 2
    BACHELOR_THIRD = 3
    BACHELOR_FOURTH = 4
    MASTER_FIRST = 5
    MASTER_SECOND = 6


class Degree:
    BACHELOR = 'bachelor'
    MASTER = 'master'
    DOCTOR = 'doctor'
    CANDIDATE = 'candidate'
    PROFESSOR = 'professor'


class Relations:
    DEPARTMENT_GROUP = 'CONSISTS_OF'
    GROUP_DEPARTMENT = 'BELONGS_TO'
    THESIS_INSTRUCTOR = 'IS_SUPERVISED'
    INSTRUCTOR_THESIS = 'SUPERVISES'
    DEPARTMENT_INSTRUCTOR = 'CONSISTS_OF'
    INSTRUCTOR_DEPARTMENT = 'BELONGS_TO'
    THESIS_TAG = 'TAGGED'
    TAG_THESIS = 'TAGS'
    THESIS_GROUP = 'BELONGS'
    GROUP_THESIS = 'CONSISTS_OF'


class Thesis:
    node_type = 'Thesis'

    def __init__(self, thesis_name: str, description: str,
                 year: int, difficulty: int, tags: Optional[list] = None,
                 score: Optional[float] = None,
                 student_info: Optional[dict] = None,
                 creation_ts: Optional[float] = None,
                 student_enrol_ts: Optional[float] = None,
                 update_ts: Optional[float] = None,
                 student_id: Optional[str] = None):
        """
        :param thesis_name: key value for object - a topic of thesis
        :param description: detailed description of a thesis
        :param year: in range from 1 to 6 where 1- is a first year of
        a bachelor degree, 6 - last year of a master degree
        :param difficulty: value from 1 to 5 where 1 is very easy, 5 -
        very difficult
        :param tags: dict of tags or requirements of a specific object
        :param student_info: information about the student, allocated after
        the topic has been written
        :param score: score of a thesis and student work overall
        :param creation_ts: creation timestamp
        :param student_enrol_ts: timestamp when last student has been enrolled
        :param update_ts: last time when the thesis has been updated, timestamp
        :param student_id: id of a student im mongodb, allocated after the
        student has enrolled for the thesis
        """
        self.id = str(uuid.uuid4())
        self.student_id = student_id
        self.thesis_name = thesis_name
        self.description = description
        if 1 > year or year > 6:
            raise IncorrectArgumentException(
                'Topic: "year" field must be in range [1, 6]')
        self.year = year
        if 1 > difficulty or difficulty > 5:
            raise IncorrectArgumentException(
                'Thesis: "difficulty" field must be in range [1, 5]')
        self.difficulty = difficulty
        self.tags = tags
        self.student_info = student_info
        self.score = score
        self.creation_ts = datetime.now().timestamp() \
            if not creation_ts else creation_ts
        self.update_ts = self.creation_ts if update_ts is None else update_ts
        self.student_enrol_ts = student_enrol_ts
        self.status = ThesisStatus.CREATED

    def to_dict(self) -> dict:
        fields_values = {key: value for key, value in vars(self).items()
                         if key[:2] != '__' and key not in
                         ['node_type', 'instructor_id'] and value}
        return fields_values

    def find(self, client: GraphDatabaseClient):
        thesis = client.find_one(self.node_type, dict(thesis_name=self.thesis_name))
        return thesis

    def create(self, client: GraphDatabaseClient, instructor_id: str):
        instructor = client.find_one(Instructor.node_type,
                                     {'id': instructor_id})
        if instructor is None:
            raise ObjectDoesNotExist(Instructor.node_type,
                                     {'id': instructor_id})
        if self.find(client) is None:
            thesis_node = Node(self.node_type)
            thesis_node.update(self.to_dict())
            client.graph.create(thesis_node)
            rel = Relationship(instructor, Relations.INSTRUCTOR_THESIS,
                               thesis_node)
            client.graph.create(rel)
            rel = Relationship(thesis_node, Relations.THESIS_INSTRUCTOR,
                               instructor)
            client.graph.create(rel)

            return thesis_node
        else:
            raise ObjectExistsException(self.node_type, self.to_dict())

    @staticmethod
    def thesis_enrol(client: GraphDatabaseClient, thesis_name: str, student_id: str, group: dict):
        thesis = client.find_one(Thesis.node_type, {'thesis_name': thesis_name})
        if thesis is None:
            raise ObjectDoesNotExist(Thesis.node_type, {'thesis_name': thesis_name})
        group = client.find_one(Group.node_type, group)
        if not group:
            raise ObjectDoesNotExist(Group.node_type, group)
        thesis['student_id'] = student_id
        thesis['student_enrol_ts'] = datetime.now().timestamp()
        thesis['update_ts'] = thesis['student_enrol_ts']
        client.graph.push(thesis)
        rel = Relationship(thesis, Relations.THESIS_GROUP, group)
        client.graph.create(rel)
        rel = Relationship(group, Relations.GROUP_THESIS, thesis)
        client.graph.create(rel)


class Instructor:
    node_type = 'Instructor'

    def __init__(self, id: str, degree: Optional[str] = None,
                 load: Optional[int] = None, classroom: Optional[str] = None):
        self.id = id
        self.degree = degree
        self.load = load
        self.classroom = classroom

    def to_dict(self) -> dict:
        fields_values = {key: value for key, value in vars(self).items()
                         if key[:2] != '__' and key != 'node_type' and value}
        return fields_values

    def find(self, client: GraphDatabaseClient):
        instructor = client.find_one(self.node_type, dict(id=self.id))
        return instructor

    def create(self, client: GraphDatabaseClient, department_id: str):
        params = {'department_id': department_id}
        department = client.find_one(Department.node_type, params)
        if department is None:
            raise ObjectDoesNotExist(Department.node_type, params)
        if self.find(client) is None:
            node = Node(Instructor.node_type)
            node.update(self.to_dict())
            client.graph.create(node)
            rel = Relationship(department, Relations.DEPARTMENT_INSTRUCTOR, node)
            client.graph.create(rel)
            rel = Relationship(node, Relations.INSTRUCTOR_DEPARTMENT, department)
            client.graph.create(rel)
        else:
            raise ObjectExistsException(self.node_type, self.to_dict())

    def add_thesis(self, client: GraphDatabaseClient, thesis: Thesis, tags: str):
        thesis_node = thesis.create(client, self.id)

        if not tags:
            return

        tags = [x.strip() for x in tags.lower().split(',')]
        for name in set(tags):
            tag = Node('Tag', name=name)
            client.graph.merge(tag, "Thesis", "name")
            rel = Relationship(thesis_node, Relations.THESIS_TAG, tag)
            client.graph.create(rel)
            rel = Relationship(tag, Relations.TAG_THESIS, thesis_node)
            client.graph.create(rel)

    def get_thesis(self, client: GraphDatabaseClient):
        """
        get all thesis for currect instructor
        :return: list of thesis
        """
        query = f'MATCH (:{Instructor.node_type} ' + '{id: "' + self.id + '"}'+ ')-' \
            f'[:{Relations.INSTRUCTOR_THESIS}]->(t:{Thesis.node_type})' \
            f'RETURN t'
        result = client.graph.run(query).data()
        return list(map(lambda x: dict(x['t']), result))

    def delete_thesis(self, client: GraphDatabaseClient, thesis_name: str):
        """
        delete thesis by its name
        """
        query = f'MATCH (a: {Thesis.node_type}' + '{thesis_name: "' + \
                thesis_name + '"})' + f'-[:{Relations.THESIS_INSTRUCTOR}]->(i:Instructor ' + \
                '{id: "' + self.id + '"}) RETURN a'
        thesis_node = client.graph.run(query).to_subgraph()
        if thesis_node is None:
            raise ObjectDoesNotExist(
                Thesis.node_type, {'thesis_name': thesis_node, 'instructor_id': self.id})
        client.graph.delete(thesis_node)


class Group:
    node_type = 'Group'

    def __init__(self, name: str, year: int, degree: str):
        self.id = str(uuid.uuid4())
        self.name = name
        print(1 > year > 6)
        if 1 > year > 6:
            raise IncorrectArgumentException(
                'Group: "year" field must be in range [1, 6]')
        self.year = year
        if not(degree == Degree.BACHELOR or degree == Degree.MASTER):
            raise IncorrectArgumentException(
                f'Group: "degree" field must be in range [{Degree.BACHELOR},'
                f' {Degree.MASTER}]')
        self.degree = degree

    def to_dict(self) -> dict:
        fields_values = {key: value for key, value in vars(self).items()
                         if key[:2] != '__' and key not in
                         ['node_type', 'department_id'] and value}
        return fields_values

    def create(self, client: GraphDatabaseClient, department_id: str):
        params = {'department_id': department_id}
        department = client.find_one(Department.node_type, params)
        if department is None:
            raise ObjectDoesNotExist(Department.node_type, params)
        if client.find_one(self.node_type, self.to_dict()) is None:
            group = Node(self.node_type)
            group.update(self.to_dict())
            client.graph.create(group)
            rel = Relationship(department, Relations.DEPARTMENT_GROUP, group)
            client.graph.create(rel)
            rel = Relationship(group, Relations.GROUP_DEPARTMENT, department)
            client.graph.create(rel)
        else:
            raise ObjectExistsException(self.node_type, self.to_dict())

    @staticmethod
    def get_thesis(client: GraphDatabaseClient, group_id: str):
        query = f'MATCH (g:Group' + \
                ' {id: "' + group_id + '"})-' + \
                f'[:{Relations.GROUP_DEPARTMENT}]->(:{Department.node_type})-' \
                f'[:{Relations.DEPARTMENT_INSTRUCTOR}]->(:{Instructor.node_type})-' \
                f'[:{Relations.INSTRUCTOR_THESIS}]->(t: Thesis) RETURN t'
        data = client.graph.run(query).data()
        return list(map(lambda x: dict(x['t']), data))


class Department:
    node_type = 'Department'

    def __init__(self, name: str, faculty: str, enrol_ts: Optional[int] = None,
                 predefence_ts: Optional[int] = None,
                 defence_ts: Optional[int] = None):
        self.department_id = str(uuid.uuid4())
        self.name = name
        self.faculty = faculty
        if enrol_ts is not None:
            self.enrol_ts = enrol_ts
        if predefence_ts is not None:
            self.predefence_ts = predefence_ts
        if defence_ts is not None:
            self.defence_ts = defence_ts

    def to_dict(self) -> dict:
        fields_values = {key: value for key, value in vars(self).items()
                         if key[:2] != '__' and key != 'node_type' and value}
        return fields_values

    def create(self, client: GraphDatabaseClient):
        if client.find_one(self.node_type, self.to_dict()) is None:
            node = Node(self.node_type)
            node.update(self.to_dict())
            client.graph.create(node)
        else:
            raise ObjectExistsException(self.node_type, self.to_dict())
