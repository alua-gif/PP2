from datetime import datetime, timedelta
def parse_datetime(line):
    date_part, tz_part = line.split()
    dt = datetime.strptime(date_part, "%Y-%m-%d")

    sign = 1 if '+' in tz_part else -1
    hours, minutes = map(int, tz_part[4:].split(":"))
    offset = timedelta(hours=hours, minutes=minutes)

    return dt - sign * offset

dt1 = parse_datetime(input())
dt2 = parse_datetime(input())

difference = abs((dt1 - dt2).total_seconds()) // 86400
print(int(difference))