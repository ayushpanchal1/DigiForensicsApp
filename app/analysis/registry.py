from regipy.registry import RegistryHive

def extract_registry_entries(registry_hive_path):
    registry = RegistryHive(registry_hive_path)
    registry.print_hive_structure()

    entries = []
    for subkey in registry.get_all_subkeys():
        subkey_info = {'path': subkey.path, 'values': []}
        for value in subkey.values:
            subkey_info['values'].append({value.name: value.value})
        entries.append(subkey_info)
    return entries
