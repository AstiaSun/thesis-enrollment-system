from db.db_mongo import DatabaseClient
from db.db_neo4j import GraphDatabaseClient, Department, Group, UniversityYear, \
    Degree, Instructor, Thesis

neo_client = GraphDatabaseClient()
mongo_client = DatabaseClient()


def create_user(email: str, password: str, role: str, first_name: str,
                middle_name: str, last_name: str, group_id: str = '') -> str:
    new_user = {
        'email': email, 'password': password, 'role': role,
        'first_name': first_name, 'middle_name': middle_name,
        'last_name': last_name, 'thesis_is': ''}
    if group_id:
        new_user['group_id'] = group_id
    return mongo_client.db.users.insert(new_user)


# departments
department = Department('Компютерні науки', 'Інформатика')
department.create(neo_client)

group = Group('КІ-2', UniversityYear.BACHELOR_SECOND, Degree.BACHELOR)
group.create(neo_client, department.department_id)

create_user('test_user1@test.com', 'qwerty', 'student', 'Test', 'Test', 'Test', group.id)
create_user('test_user2@test.com', 'qwerty123', 'student', 'Test123', 'Test123', 'Test123', group.id)
user_id = create_user('admin_1@test.com', 'qwerty123', 'instructor', 'Instructor1', 'Test123', 'Test123')
instructor = Instructor(str(user_id), Degree.DOCTOR, 12, '123-c')
instructor.create(neo_client, department.department_id)
thesis = Thesis('Lorem Ipsum', 'Some random test here is the most beutiful day in deep learning', UniversityYear.BACHELOR_SECOND, 3)
instructor.add_thesis(neo_client, thesis, 'deep-learning, statistics')
thesis = Thesis('Hello world in Java', 'Please create the most spiky hello world in Java', UniversityYear.BACHELOR_THIRD, 5)
instructor.add_thesis(neo_client, thesis, tags='java')

department = Department('Програмна інженерія', 'Інформатика')
department.create(neo_client)
group = Group('ПІ-4', UniversityYear.BACHELOR_FOURTH, Degree.BACHELOR)
group.create(neo_client, department.department_id)
create_user('test_user3@test.com', 'qwerty', 'student', 'Test', 'Test', 'Test', group.id)
create_user('test_user4@test.com', '123456', 'student', 'Snezhanna', 'Mykolayvna', 'Mohyla', group.id)
user_id = str(create_user('instructor@test.com', 'qwerty123', 'instructor', 'Instructor2', 'Test123', 'Test123'))
instructor = Instructor(user_id, Degree.PROFESSOR, 10, '201')
instructor.create(neo_client, department.department_id)
thesis = Thesis('Lorem Ipsum in London', 'Some random tests here is the most beutiful day in deep learning', UniversityYear.BACHELOR_SECOND, 4)
instructor.add_thesis(neo_client, thesis, 'deep-learning, statistics')
