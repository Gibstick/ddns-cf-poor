import configparser
import urllib.request

import CloudFlare


def get_ip(ip_url):
    with urllib.request.urlopen(ip_url) as response:
        return response.read().decode("utf-8").rstrip()


def main(domain, name, record_type, ip_url):
    cf = CloudFlare.CloudFlare()
    zones = cf.zones.get()

    # Find the zone id of the domain we want to update
    for zone in zones:
        if zone["name"] == domain:
            zone_id = zone["id"]
            break
    else:
        exit("Zone with name {} not found".format(domain))

    dns_record = {
        "name": name,
        "type": record_type,
        "content": get_ip(ip_url),
        "proxied": False
        # leave TTL at default
    }

    records = cf.zones.dns_records.get(zone_id)
    # Update the record
    for record in records:
        if record["name"] == name:
            record_id = record["id"]
            cf.zones.dns_records.put(zone_id, record_id, data=dns_record)
            break
    # If the record doesn't exist yet, we should create it
    else:
        print("Created new record for {}".format(name))
        cf.zones.dns_records.post(zone_id, data=dns_record)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("ddns.ini")

    section = config["DEFAULT"]
    domain = section["Domain"]
    name = section["Name"]
    record_type = section["RecordType"]
    ip_url = section["IpUrl"]

    try:
        main(domain, name, record_type, ip_url)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit(str(format(e)))
