import uuid
from datetime import datetime
from typing import Optional

from py2neo import Graph, Node, NodeMatcher, Relationship

from db.exceptions import ObjectExistsException, IncorrectArgumentException
from settings import NEO4J_HOSTNAME, NEO4J_USER, NEO4J_PORT, NEO4J_PASSWORD

url = f'bolt://{NEO4J_HOSTNAME}:{NEO4J_PORT}'

graph = Graph(url + f'/db/data/', username=NEO4J_USER,
              password=NEO4J_PASSWORD)


class Instructor:
    def __init__(self, id, department_id, degree, load, classroom):
        self.id = id
        self.department_id = department_id
        self.degree = degree
        self.load = load
        self.classroom = classroom

    def find(self, id):
        matcher = NodeMatcher(graph)
        instructor = matcher.match('Instructor', id=id)
        return instructor

    def add_thesis(self, thesis_name, description, creation_ts, year, difficulty, requirements, status, tags):
        instructor = self.find()
        thesis = Node(
            'Thesis',
            id=str(uuid.uuid4()),
            instructor_id=instructor.id,
            thesis_name=thesis_name,
            description=description,
            creation_ts=creation_ts,
            year=year,
            difficulty=difficulty,
            requirements=requirements,
            status=status
        )
        rel = Relationship(instructor, 'SUPERVISES', thesis)
        graph.create(rel)

        tags = [x.strip() for x in tags.lower().split(',')]
        for name in set(tags):
            tag = Node('Tag', name=name)
            graph.merge(tag)

            rel = Relationship(tag, 'TAGGED', thesis)
            graph.create(rel)


class Thesis:
    def __init__(self, thesis_name: str, description: str,
                 year: int, difficulty: int, status: int,
                 tags: Optional[dict] = None, score: Optional[float] = None,
                 student_info: Optional[dict] = None,
                 creation_ts: Optional[float] = None,
                 student_enrol_ts: Optional[float] = None,
                 update_ts: Optional[float] = None,
                 student_id: Optional[str] = None):
        """
        :param thesis_name: key value for object - a topic of thesis
        :param description: detai;ed description of a thesis
        :param year: in range from 1 to 6 where 1- is a first year of
        a bachelor degree, 6 - last year of a master degree
        :param difficulty: value from 1 to 5 where 1 is very easy, 5 -
        very difficult
        :param status: status of the topic, 0 is created
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
        self.student_id = student_id
        self.name = thesis_name
        self.description = description
        if 1 > year > 6:
            raise IncorrectArgumentException(
                'Topic: "year" field must be in range [1, 6]')
        self.year = year
        if 1 > difficulty > 5:
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
        self.status = status
        self.node_type = 'Thesis'

    def _to_dict(self) -> dict:
        fields_values = {key: value for key, value in vars(self).items()
                         if key[:2] != '__' and key != 'node_type' and value}
        return fields_values

    def find(self):
        matcher = NodeMatcher(graph)
        thesis = matcher.match(self.node_type, thesis_name=self.name).first()
        return thesis

    def create(self):
        if not self.find():
            thesis_node = Node()
            thesis_node.update(self._to_dict())
            graph.create(thesis_node)
        raise ObjectExistsException(self.node_type, self._to_dict())
