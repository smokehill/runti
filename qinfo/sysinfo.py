import os
import sys
import re
import time
import subprocess


# def __bytes_to_human(bytes, format=None):
#     keys = ('B','K','M','G','T','P','E')
#     size = float(bytes)

#     i = 1
#     while size >= 1024:
#         size = size / 1024
#         i = i + 1

#     if format != None:
#         size = format % size

#     return size, keys[i]

def __bt_to_gb(bytes, format=None):
    size = float(bytes) / 1024 / 1024

    if format != None:
        size = format % size

    return size, 'G'

def cpu():
    # https://supportcenter.checkpoint.com/supportcenter/portal?eventSubmit_doGoviewsolutiondetails=&solutionid=sk65143
    # https://rosettacode.org/wiki/Linux_CPU_utilization
    resp = []

    info = subprocess.check_output('cat /proc/stat | grep -i cpu', shell=True)
    old_info = []
    for line in info.splitlines():
        line = ' '.join(re.sub('cpu[0-9+]?', '', line).split()).split(' ')
        line = [float(l) for l in line]

        old_info.append([line[3], sum(line)])

    time.sleep(0.5)

    info = subprocess.check_output('cat /proc/stat | grep -i cpu', shell=True)
    i = 0
    for line in info.splitlines():
        line = ' '.join(re.sub('cpu[0-9+]?', '', line).split()).split(' ')
        line = [float(l) for l in line]

        idle, total = line[3], sum(line)
        idle_delta, total_delta = idle - old_info[i][0], total - old_info[i][1]
        try:
            utilisation = 100.0 * (1.0 - idle_delta / total_delta)
        except:
            # Traceback [ZeroDivisionError: float division by zero].
            # It happens if try to change screen size rapidly.
            utilisation = 0.0

        r = {}
        r['name'] = 'core' + str(i) if i > 0 else 'total'
        r['used'] = "%.0f" % utilisation

        resp.append(r)
        i = i + 1

    return resp

def mem():
    resp = {}

    info = subprocess.check_output('free | grep -i mem', shell=True)
    info = ' '.join(re.sub('Mem:', '', info).split()).split(' ')

    resp['size'], resp['size_f'] = __bt_to_gb(int(info[0]), "%.1f")
    resp['used'], resp['used_f'] = __bt_to_gb(int(info[1]), "%.1f")

    return resp

def swp():
    resp = {}

    info = subprocess.check_output('free | grep -i swap', shell=True)
    info = ' '.join(re.sub('Swap:', '', info).split()).split(' ')

    resp['size'], resp['size_f'] = __bt_to_gb(int(info[0]), "%.1f")
    resp['used'], resp['used_f'] = __bt_to_gb(int(info[1]), "%.1f")

    return resp

def hdd():
    resp = []

    info = subprocess.check_output('df | grep \'sda\'', shell=True)
    for line in info.splitlines():
        line = ' '.join(line.split()).split(' ')

        r = {}
        r['size'], r['size_f'] = __bt_to_gb(int(line[1]), "%.0f")
        r['used'], r['used_f'] = __bt_to_gb(int(line[2]), "%.0f")
        r['name'] = line[5]

        resp.append(r)

    return resp

def upt():
    info = subprocess.check_output('uptime', shell=True)
    info = ' '.join(re.sub(r'[0-9+] users?,', '', info).split())

    return info

def rel():
    file_path = os.path.expanduser('~') + '/.cache/qinfo/.rel'

    if os.path.isfile(file_path) == False:
        # release
        info1 = subprocess.check_output('cat /etc/os-release | grep -i "^name\|^version_id"', shell=True)
        info1 = [''.join(line.split('=')[1].replace('"', '').split()) for line in info1.splitlines()]
        info1 = ' '.join(info1)

        # architecture
        info2 = subprocess.check_output('uname -m', shell=True)
        info2 = info2.rstrip()

        # kernel
        info3 = subprocess.check_output('uname -s -r', shell=True)
        info3 = info3.rstrip()

        info_all = "{0} {1}, {2}".format(info1, info2, info3)

        f = open(file_path, 'w')
        f.write(info_all)
        f.close()

        return info_all

    else:
        f = open(file_path, 'r')
        return f.readline()