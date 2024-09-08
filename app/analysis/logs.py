import pyevtx

def extract_system_logs(evtx_path):
    logs = []
    with open(evtx_path, 'rb') as evtx_file:
        evtx = pyevtx.open(evtx_file)
        for record in evtx.records():
            logs.append(record.xml())
    return logs
