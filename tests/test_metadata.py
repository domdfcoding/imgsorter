# stdlib
import datetime

# 3rd party
import pytest
from coincidence import AdvancedDataRegressionFixture
from domdf_python_tools.paths import PathPlus

# this package
from imgsorter.metadata import date_to_directory, get_metadata_for_file, parse_camera_id, parse_date_from_metadata

example_photos = PathPlus(__file__).parent / "example_photos"


@pytest.mark.parametrize(
		"filename", [pytest.param(example_photos / "IMG_20181228_155131.jpg", id="IMG_20181228_155131")]
		)
def test_get_metadata_for_file(advanced_data_regression: AdvancedDataRegressionFixture, filename: PathPlus):
	metadata = get_metadata_for_file(filename)
	advanced_data_regression.check(metadata)


@pytest.mark.parametrize(
		"filename, date", [(example_photos / "IMG_20181228_155131.jpg", datetime.date(2018, 12, 28))]
		)
def test_parse_date_from_metadata(filename: PathPlus, date: datetime.date):
	metadata = get_metadata_for_file(filename)
	assert parse_date_from_metadata(metadata) == date


@pytest.mark.parametrize("filename, camera_id", [(example_photos / "IMG_20181228_155131.jpg", "VKY-L09")])
def test_parse_camera_id(filename: PathPlus, camera_id: str):
	metadata = get_metadata_for_file(filename)
	assert parse_camera_id(metadata) == camera_id


@pytest.mark.parametrize("date, expected", [(datetime.date(2018, 12, 28), "2018_12_28")])
def test_date_to_directory(date: datetime.date, expected):
	assert date_to_directory(date) == expected
