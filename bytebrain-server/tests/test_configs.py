import unittest
import yaml


def load_config_from_str(config_str):
    return yaml.safe_load(config_str)


def merge_configs(base_config, override_config):
    merged_config = base_config.copy()
    merged_config.update(override_config)
    return merged_config


class TestConfigMerge(unittest.TestCase):

    def setUp(self):
        base_config_str = """
        param1: default_value1
        param2: default_value2
        nested:
          param: 3
        """
        self.base_config = load_config_from_str(base_config_str)

    def test_merge_with_override1(self):
        override_config1_str = "param1: overridden_value1\nnested.param: 6"
        override_config1 = load_config_from_str(override_config1_str)
        merged_config1 = merge_configs(self.base_config, override_config1)
        expected_result1 = {'param1': 'overridden_value1', 'param2': 'default_value2', 'nested.param': 3}
        self.assertEqual(merged_config1, expected_result1)

    def test_merge_with_override2(self):
        override_config2_str = "param2: overridden_value2"
        override_config2 = load_config_from_str(override_config2_str)
        merged_config2 = merge_configs(self.base_config, override_config2)
        expected_result2 = {'param1': 'default_value1', 'param2': 'overridden_value2', 'nested.param': 3}
        self.assertEqual(merged_config2, expected_result2)

    def test_merge_with_both_overrides(self):
        override_config1_str = "param1: overridden_value1"
        override_config2_str = "param2: overridden_value2"
        override_config1 = load_config_from_str(override_config1_str)
        override_config2 = load_config_from_str(override_config2_str)
        merged_config = merge_configs(self.base_config, override_config1)
        merged_config = merge_configs(merged_config, override_config2)
        expected_result = {'param1': 'overridden_value1', 'param2': 'overridden_value2', 'nested.param': 3, 'nested.param2': 5}
        self.assertEqual(merged_config, expected_result)


if __name__ == '__main__':
    unittest.main()
