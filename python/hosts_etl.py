import os
import json
import xml.etree.ElementTree as ET


def read_csv(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    header = lines[0].strip().split(',')
    hostnames = [col.split('#')[1] for col in header[1:]]
    data = [line.strip().split(',') for line in lines[1:] if line.strip()]
    return hostnames, data


def hosts_stats(hostnames, data):
    # Initialize data structures for collecting data per host
    col_data = {hostname: [] for hostname in hostnames}
    hosts = {hostname: {} for hostname in hostnames}

    for row in data:
        for i, value in enumerate(row[1:]):
            if value:
                col_data[hostnames[i]].append(float(value))

    min_all = float('inf')
    max_all = 0
    tal_all = 0
    cnt_all = 0

    for hostname in hosts:
        col_total = sum(col_data[hostname])
        col_count = len(col_data[hostname])
        if col_count:
            hosts[hostname]['min'] = min(col_data[hostname])
            hosts[hostname]['max'] = max(col_data[hostname])
            hosts[hostname]['avg'] = round(col_total / col_count, 2)
        else:
            hosts[hostname]['min'] = 0
            hosts[hostname]['max'] = 0
            hosts[hostname]['avg'] = None
        min_all = min(min_all, hosts[hostname]['min'])
        max_all = max(max_all, hosts[hostname]['max'])
        tal_all += col_total
        cnt_all += col_count

    # stats for all hosts
    hosts['ALL_HOSTS'] = {
        'min': min_all,
        'max': max_all,
        'avg': round(tal_all / cnt_all, 2) if cnt_all else None
    }

    return hosts


def dict_to_xml(tag, d):
    elem = ET.Element(tag)
    for key, val in d.items():
        if isinstance(val, dict):
            child = dict_to_xml(key, val)
        else:
            child = ET.Element(key)
            child.text = str(val)
        elem.append(child)
    return elem


def dict_to_yaml(data, indent=0):
    yaml_str = ""

    for key, value in data.items():
        yaml_str += " " * indent + str(key) + ": "
        if isinstance(value, dict):
            yaml_str += "\n" + dict_to_yaml(value, indent + 2)
        else:
            yaml_str += str(value) + "\n"

    return yaml_str


def dict_to_txt(data):
    lines = ["Host|Minimum|Maximum|Average"]
    for key, attrs in data.items():
        lines.append(f"{key}|{attrs['min']}|{attrs['max']}|{attrs['avg']}")
    return '\n'.join(lines)


def main():
    dir_path = os.path.dirname(__file__)
    filename = os.path.join(dir_path, 'data.csv')
    hostnames, data = read_csv(filename)
    hosts = hosts_stats(hostnames, data)

    # default output
    # ---------------------------------------------
    print(hosts)
    print('-'*100)

    # JSON output
    # ---------------------------------------------
    json_string = json.dumps(hosts, indent=4)
    print(json_string)
    print('-'*100)

    # JSON file
    with open(os.path.join(dir_path, 'hosts.json'), 'w') as file:
        json.dump(hosts, file, indent=4)

    # XML output
    # ---------------------------------------------
    xml_root = dict_to_xml('HOSTS', hosts)
    print(ET.tostring(xml_root).decode())
    print('-'*100)

    # XML file
    with open(os.path.join(dir_path, 'hosts.xml'), 'w') as file:
        file.write(ET.tostring(xml_root).decode())

    # YAML output
    # ---------------------------------------------
    print(dict_to_yaml(hosts))
    print('-'*100)

    # YAML file
    with open(os.path.join(dir_path, 'hosts.yaml'), 'w') as file:
        file.write(dict_to_yaml(hosts))

    # Export pipe delimited flat hosts.txt
    # ---------------------------------------------
    with open(os.path.join(dir_path, 'hosts.txt'), 'w') as file:
        file.write(dict_to_txt(hosts))


if __name__ == "__main__":
    main()
