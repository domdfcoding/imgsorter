#!/usr/bin/env python3
#
#  metadata.py
"""
Read image metadata.
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
import datetime
import json
import re
from typing import Any, Dict

# 3rd party
import exifread  # type: ignore
import exiftool  # type: ignore
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike

__all__ = [
		"date_to_directory",
		"get_metadata_for_file",
		"parse_camera_id",
		"parse_date_from_metadata",
		]


def get_metadata_for_file(filename: PathLike) -> Dict[str, Any]:
	"""
	Returns the EXIF metadata for ``filename``, as a ``key: value`` mapping.

	:param filename:
	"""

	filename = PathPlus(filename)

	if not filename.is_file():
		raise FileNotFoundError(filename)

	# get the tags
	with filename.open("rb") as fp:
		data = exifread.process_file(fp, details=False, debug=False)

	if data:
		return {k: str(v) for k, v in data.items()}

	else:
		# using exiftool as a backup for some files including videos
		with exiftool.ExifTool() as et:
			try:
				data = et.get_metadata(str(filename))
			except json.decoder.JSONDecodeError:
				raise ValueError(f"Could not parse EXIF data for {filename} or no EXIF data found.")

	return dict(data)


def parse_date_from_metadata(metadata: Dict[str, Any]) -> datetime.date:
	"""
	Determine the date the photograph was taken from its EXIF data.

	:param metadata: EXIF data to find the date from.
	"""

	for key in [
			"EXIF DateTimeOriginal",
			"Image DateTime",
			"EXIF:DateTimeOriginal",
			"QuickTime:MediaCreateDate",
			]:
		if key in metadata:
			date = str(metadata[key])[:10]
			# date = date.replace(':', '_').replace(' ', '_')
			year, month, day, *_ = map(int, re.split("[:_-]", date))
			return datetime.date(year=year, month=month, day=day)

	raise ValueError("Could not parse date.")


def date_to_directory(date: datetime.date) -> str:
	"""
	Convert a date into a directory name.

	:param date:
	:return:
	"""

	return date.strftime("%Y_%m_%d")


def parse_camera_id(metadata: Dict[str, Any]) -> str:
	"""
	Determine the camera the photograph was taken with from its EXIF data.

	:param metadata: EXIF data to find the camera from.

	:returns: The camera id, if it could be determined. If not, returns ``'Unknown'``.
	"""

	for key in [
			"Image Model",
			"EXIF:Model",  # Video files, Canon
			"MakerNotes:Model",  # Video files, Panasonic
			"QuickTime:Model",  # Video files, GoPro 7
			"QuickTime:LensSerialNumber",  # GoPro
			]:
		if key in metadata:
			return str(metadata[key])

	return "Unknown"
