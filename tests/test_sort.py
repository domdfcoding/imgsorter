# 3rd party
from coincidence import AdvancedDataRegressionFixture
from domdf_python_tools.paths import PathPlus

# this package
from imgsorter import sort_images

example_photos = PathPlus(__file__).parent / "example_photos"


def test_sort_images(
		tmp_pathplus: PathPlus,
		advanced_data_regression: AdvancedDataRegressionFixture,
		):
	destination = tmp_pathplus / "photos"

	all_example_photos = example_photos.rglob("*.jpg")
	sort_images(destination, *all_example_photos)
	advanced_data_regression.check([p.relative_to(tmp_pathplus).as_posix() for p in destination.iterchildren()])


def test_sort_images_known_cameras(
		tmp_pathplus: PathPlus,
		advanced_data_regression: AdvancedDataRegressionFixture,
		):
	destination = tmp_pathplus / "photos"

	all_example_photos = example_photos.rglob("*.jpg")
	sort_images(destination, *all_example_photos, known_cameras={"VKY-L09": "Smartphone"})
	advanced_data_regression.check([p.relative_to(tmp_pathplus).as_posix() for p in destination.iterchildren()])


def test_sort_images_duplicate(
		tmp_pathplus: PathPlus,
		advanced_data_regression: AdvancedDataRegressionFixture,
		):
	destination = tmp_pathplus / "photos"

	all_example_photos = list(example_photos.rglob("*.jpg"))
	sort_images(destination, *all_example_photos)
	sort_images(destination, *all_example_photos)

	advanced_data_regression.check([p.relative_to(tmp_pathplus).as_posix() for p in destination.iterchildren()])
