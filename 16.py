from datetime import datetime, timedelta
def parse_datetime(line):
    date_part, time_part, tz_part = line.split()
    dt = datetime.strptime(date_part + " " + time_part, "%Y-%m-%d %H:%M:%S")
    sign = 1 if '+' in tz_part else -1
    h, m = map(int, tz_part[4:].split(":"))
    offset = timedelta(hours=h, minutes=m)
    return dt - sign * offset
start = parse_datetime(input())
end = parse_datetime(input())

print(int((end - start).total_seconds()))