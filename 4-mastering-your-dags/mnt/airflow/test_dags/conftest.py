import pytest
from airflow.models import DagBag

# fixture function is function that will run before each test function to which it is applied
# They are used to feed some data to the tests such as database connections, URLs, etc.
@pytest.fixture(scope="session")
def dagbag():
    return DagBag()