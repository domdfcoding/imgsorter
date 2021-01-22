#!/usr/bin/env python3
#
#  __init__.py
"""
A library for sorting and grouping images and videos.
"""
#
#  Copyright © 2014-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
import enum
import os
import pathlib
import shutil
import sys
from typing import Any, Callable, Dict, List

# 3rd party
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike
from enum_tools import StrEnum

# this package
from imgsorter.metadata import date_to_directory, get_metadata_for_file, parse_camera_id, parse_date_from_metadata

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2014-2021 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.0.0"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = ["SortMode", "sort_images"]


class SortMode(StrEnum):
	"""
	:class:`enum.Enum` of the sorting mode -- whether to move the images or only copy them.
	"""

	MODE_MOVE = "move"
	MODE_COPY = "copy"


MODE_MOVE = SortMode.MODE_MOVE
MODE_COPY = SortMode.MODE_COPY


def sort_images(
		destination: PathLike,
		*source: PathLike,
		known_cameras: Dict[str, str] = None,
		mode: SortMode = MODE_COPY,
		) -> Dict[str, List[PathPlus]]:
	r"""
	Sort all images in ``*source`` into ``destination``.

	:param destination:
	:param \*source:
	:param known_cameras: A mapping of camera IDs -- as listed in the image metadata -- to human-readable names.
		For example, ``VKY-L09`` might map to ``Smartphone``.
	:param mode: The sorting mode -- whether to move the images or only copy them.
	"""

	if known_cameras is None:
		known_cameras = {}

	destination = PathPlus(destination)

	stats: Dict[str, List[PathPlus]] = {"success": [], "fail": []}

	for filename in source:
		filename = PathPlus(filename)

		metadata = get_metadata_for_file(filename)

		camera_id = parse_camera_id(metadata)
		camera_id = known_cameras.get(camera_id, camera_id)

		date = date_to_directory(parse_date_from_metadata(metadata))

		destination_path = destination / date / camera_id
		destination_path.maybe_make(parents=True)

		destination_filename = destination_path / filename.name

		# If file already exists, add a (number) to the end of the filename
		# TODO: Use filecmp to see if files are identical

		num = 0
		base_filename, extension = os.path.splitext(destination_filename.name)

		while destination_filename.is_file():
			num += 1
			destination_filename = destination_filename.with_name(f"{base_filename} ({num}){extension}")

		print(f"{date}  {camera_id} -> {destination_filename}")

		sort_op: Callable[..., Any]

		if mode == MODE_COPY:
			sort_op = shutil.copy2
		elif mode == MODE_MOVE:
			sort_op = shutil.move
		else:
			raise ValueError(f"{mode!r} is not a supported mode. Choose from 'move', 'copy'.")

		try:
			sort_op(filename, destination_filename)
			stats["success"].append(filename)
		except Exception:
			print(f"Failed to copy '{filename}'", file=sys.stderr)
			stats["fail"].append(filename)

	return stats
