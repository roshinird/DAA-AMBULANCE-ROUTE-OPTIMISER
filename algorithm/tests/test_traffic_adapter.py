import unittest

from algorithm.traffic_adapter import (
    get_traffic_multiplier,
    normalize_traffic_multipliers,
    validate_edge_id,
    validate_traffic_multiplier,
)


class TestValidateTrafficMultiplier(unittest.TestCase):

    def test_valid_integer(self):
        self.assertEqual(
            validate_traffic_multiplier(2),
            2.0,
        )

    def test_valid_float(self):
        self.assertEqual(
            validate_traffic_multiplier(1.5),
            1.5,
        )

    def test_string_number_is_accepted(self):
        self.assertEqual(
            validate_traffic_multiplier("2.5"),
            2.5,
        )

    def test_zero_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_traffic_multiplier(0)

    def test_negative_value_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_traffic_multiplier(-1)

    def test_nan_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_traffic_multiplier(float("nan"))

    def test_positive_infinity_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_traffic_multiplier(float("inf"))

    def test_negative_infinity_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_traffic_multiplier(float("-inf"))

    def test_boolean_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_traffic_multiplier(True)


class TestValidateEdgeId(unittest.TestCase):

    def test_valid_edge_id(self):
        self.assertEqual(
            validate_edge_id(10),
            10,
        )

    def test_zero_edge_id_is_valid(self):
        self.assertEqual(
            validate_edge_id(0),
            0,
        )

    def test_negative_edge_id_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_edge_id(-1)

    def test_non_integer_edge_id_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_edge_id(1.5)

    def test_string_edge_id_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_edge_id("10")

    def test_boolean_edge_id_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_edge_id(True)


class TestNormalizeTrafficMultipliers(unittest.TestCase):

    def test_none_returns_empty_dictionary(self):
        self.assertEqual(
            normalize_traffic_multipliers(None),
            {},
        )

    def test_valid_mapping_is_normalized(self):
        traffic = {
            0: 1,
            1: 1.5,
            2: 2,
        }

        result = normalize_traffic_multipliers(traffic)

        self.assertEqual(
            result,
            {
                0: 1.0,
                1: 1.5,
                2: 2.0,
            },
        )

    def test_input_mapping_is_not_modified(self):
        traffic = {
            10: 2,
            20: 3,
        }

        original = traffic.copy()

        normalize_traffic_multipliers(traffic)

        self.assertEqual(
            traffic,
            original,
        )

    def test_invalid_edge_id_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_traffic_multipliers(
                {
                    -1: 2.0,
                }
            )

    def test_invalid_multiplier_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_traffic_multipliers(
                {
                    10: 0,
                }
            )

    def test_non_mapping_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_traffic_multipliers(
                [1, 2, 3]
            )

    def test_string_multiplier_is_normalized(self):
        result = normalize_traffic_multipliers(
            {
                5: "2.5",
            }
        )

        self.assertEqual(
            result,
            {
                5: 2.5,
            },
        )


class TestGetTrafficMultiplier(unittest.TestCase):

    def test_existing_edge_returns_multiplier(self):
        traffic = {
            10: 2.0,
        }

        self.assertEqual(
            get_traffic_multiplier(10, traffic),
            2.0,
        )

    def test_missing_edge_returns_default(self):
        traffic = {
            10: 2.0,
        }

        self.assertEqual(
            get_traffic_multiplier(20, traffic),
            1.0,
        )

    def test_none_returns_default(self):
        self.assertEqual(
            get_traffic_multiplier(10, None),
            1.0,
        )

    def test_custom_default_is_used(self):
        traffic = {
            10: 2.0,
        }

        self.assertEqual(
            get_traffic_multiplier(
                20,
                traffic,
                default=1.25,
            ),
            1.25,
        )

    def test_invalid_edge_id_is_rejected(self):
        with self.assertRaises(ValueError):
            get_traffic_multiplier(
                -1,
                None,
            )

    def test_invalid_default_is_rejected(self):
        with self.assertRaises(ValueError):
            get_traffic_multiplier(
                10,
                None,
                default=0,
            )

    def test_invalid_mapping_value_is_rejected(self):
        with self.assertRaises(ValueError):
            get_traffic_multiplier(
                10,
                {
                    10: -2,
                },
            )

    def test_existing_string_multiplier_is_normalized(self):
        traffic = {
            10: "2.5",
        }

        self.assertEqual(
            get_traffic_multiplier(10, traffic),
            2.5,
        )


if __name__ == "__main__":
    unittest.main()