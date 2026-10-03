import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import sync_data as sd


class ReadCoordinatesTests(unittest.TestCase):
    def test_lon_lat_fields(self):
        self.assertEqual(sd.read_coordinates({"lon": -122.6, "lat": 49.2}), (-122.6, 49.2, None))

    def test_geometry_wins_and_strings_are_converted(self):
        photo = {"geometry": {"coordinates": ["-122.6", "49.2"]}, "lon": 1, "lat": 1}
        self.assertEqual(sd.read_coordinates(photo), (-122.6, 49.2, None))

    def test_missing_is_no_coordinates(self):
        for photo in ({}, {"lon": None, "lat": 49.2}, {"geometry": None}, {"geometry": {"coordinates": [1]}}):
            self.assertEqual(sd.read_coordinates(photo)[2], sd.NO_COORDINATES, photo)

    def test_unusable_values_are_invalid(self):
        for lon, lat in (("abc", 49.2), (float("nan"), 49.2), (float("inf"), 49.2), (-122.6, 91),
                         (181, 49.2), (0, 0), ([1], 49.2)):
            self.assertEqual(sd.read_coordinates({"lon": lon, "lat": lat})[2], sd.INVALID_COORDINATES, (lon, lat))

    def test_zero_on_one_axis_is_fine(self):
        self.assertIsNone(sd.read_coordinates({"lon": 0, "lat": 49.2})[2])


class GeojsonProblemsTests(unittest.TestCase):
    def feature(self, **changes):
        f = {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-122.6, 49.2]},
             "properties": {"id": 7, "objects": []}}
        f.update(changes)
        return f

    def collection(self, *features):
        return {"type": "FeatureCollection", "features": list(features)}

    def test_good_data_has_no_problems(self):
        self.assertEqual(sd.geojson_problems(self.collection(self.feature(), self.feature())), [])

    def test_wrong_top_level(self):
        self.assertTrue(sd.geojson_problems({"type": "Feature"}))
        self.assertTrue(sd.geojson_problems({"type": "FeatureCollection", "features": None}))

    def test_bad_features_are_named(self):
        bad = [self.feature(type="Thing"),
               self.feature(geometry={"type": "Polygon", "coordinates": []}),
               self.feature(geometry={"type": "Point", "coordinates": [-122.6]}),
               self.feature(geometry={"type": "Point", "coordinates": [-122.6, 99]}),
               self.feature(geometry={"type": "Point", "coordinates": [float("nan"), 49.2]}),
               self.feature(properties={"id": 7}),
               self.feature(properties=None)]
        problems = sd.geojson_problems(self.collection(*bad))
        self.assertEqual(len(problems), len(bad))
        self.assertIn("feature 3 (photo 7)", problems[3])


if __name__ == "__main__":
    unittest.main()
