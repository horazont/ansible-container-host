#!/usr/bin/env python3

# WARNING: this file us currently unused, unless the command copying it to the
# remote has been re-enabled :)

import ipaddress
import subprocess
import sys

PORT_MAP_INFO = [
{% for entry in container_host.port_forwards %}
    ("{{ entry.guest }}",
     {{ entry.outside }},
     {{ entry.to_port }},
     ipaddress.IPv4Address("{{ entry.to_ip }}")),
{% endfor %}
]

IPTABLES = "iptables"

GUEST_MAP = {}
for guest, *info in PORT_MAP_INFO:
    GUEST_MAP.setdefault(guest, []).append(info)


def mk_preroute_rule(outside, to_port, to_ip):
    return [
        "-p", "tcp",
        "--dport", str(outside),
        "-j", "DNAT",
        "--to", "{}:{}".format(to_ip, to_port),
    ]

def mk_forward_rule(outside, to_port, to_ip):
    return [
        "-d", "{}/32".format(to_ip),
        "-p", "tcp",
        "-m", "state",
        "--state", "NEW",
        "-m", "tcp",
        "--dport", str(to_port),
        "-j", "ACCEPT",
    ]

try:
    info = GUEST_MAP[sys.argv[1]]
except KeyError:
    # nothing to do
    sys.exit(0)

if sys.argv[2] in {"stopped", "reconnect"}:
    # tear down
    for outside, to_port, to_ip in info:
        subprocess.check_call(
            [
                IPTABLES,
                "-t", "nat",
                "-D", "PREROUTING",
            ]+mk_preroute_rule(outside, to_port, to_ip)
        )
        subprocess.check_call(
            [
                IPTABLES,
                "-D", "FORWARD",
            ]+mk_forward_rule(outside, to_port, to_ip)
        )
else:
    # set up
    for outside, to_port, to_ip in info:
        subprocess.check_call(
            [
                IPTABLES,
                "-t", "nat",
                "-A", "PREROUTING",
            ]+mk_preroute_rule(outside, to_port, to_ip)
        )
        subprocess.check_call(
            [
                IPTABLES,
                "-A", "FORWARD",
            ]+mk_forward_rule(outside, to_port, to_ip)
        )
