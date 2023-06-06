from random import choice

from model_bakery import baker
from rest_framework.test import APIClient

import pytest

from students.models import Course, Student

URL = r'/api/v1/courses/'


def get_data(url, client, params=False):
    response = client.get(url, data=params)
    data = response.json()
    return response.status_code, data


def get_random_course_data(list_of_courses, name=False):
    random_course = choice(list_of_courses)
    if name:
        return random_course.name
    return random_course.id


@pytest.fixture
def url_factory():
    def factory(url, object=False):
        if object:
            url += f'{object.id}/'
        return url
    return factory


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def course_baker():
    return baker.make(Course)


@pytest.fixture
def courses_baker():
    return baker.make(Course, _quantity=30)


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory


@pytest.mark.django_db
def test_get_new_course(client, url_factory, course_baker):
    status, data = get_data(url_factory(URL, course_baker), client)
    assert status == 200
    assert data['id'] == course_baker.id


@pytest.mark.django_db
def test_get_list_of_course(client, url_factory, courses_baker):
    status, data = get_data(url_factory(URL), client)
    for index, course in enumerate(data):
        assert course['id'] == courses_baker[index].id
    assert status == 200


@pytest.mark.django_db
def test_course_filter_id(client, url_factory, courses_baker):
    random_course_id = get_random_course_data(courses_baker)
    params = {'id': random_course_id}
    status, data = get_data(url_factory(URL), client, params=params)
    assert data[0]['id'] == random_course_id
    assert status == 200


@pytest.mark.django_db
def test_course_filter_name(client, url_factory, courses_baker):
    random_course_name = get_random_course_data(courses_baker, name=True)
    params = {'name': random_course_name}
    status, data = get_data(url_factory(URL), client, params=params)
    assert data[0]['name'] == random_course_name
    assert status == 200


@pytest.mark.django_db
def test_course_create(client, url_factory):
    count = Course.objects.count()
    course_name = 'Python_course'
    data = {'name': course_name}
    response = client.post(url_factory(URL), data=data)
    new_course = Course.objects.filter(name=course_name)[0]
    assert response.status_code == 201
    assert Course.objects.count() == count + 1
    assert new_course.name == course_name


@pytest.mark.django_db
def test_course_update(client, url_factory, course_baker, student_factory):
    student = student_factory()
    len_before_update = len(course_baker.students.all())
    data = {'students': [student.id]}
    response = client.patch(url_factory(URL, course_baker), data=data)
    len_after_update = len(course_baker.students.all())
    assert len_before_update == len_after_update - 1
    assert response.status_code == 200


@pytest.mark.django_db
def test_course_delete(client, url_factory, course_baker):
    response = client.delete(url_factory(URL, course_baker))
    deleted_course = Course.objects.filter(id=course_baker.id)
    assert not deleted_course
    assert response.status_code == 204
