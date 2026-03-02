from datetime import datetime, timedelta
import calendar
def parse_date(line):
    date_part, tz_part = line.split()
    dt = datetime.strptime(date_part, "%Y-%m-%d")
    sign = 1 if '+' in tz_part else -1
    h, m = map(int, tz_part[4:].split(":"))
    offset = timedelta(hours=h, minutes=m)
    return dt - sign * offset, dt.year
birth_line = input()
current_line = input()
birth_utc, birth_year = parse_date(birth_line)
current_utc, current_year = parse_date(current_line)

birth_date = datetime.strptime(birth_line.split()[0], "%Y-%m-%d")
month = birth_date.month
day = birth_date.day

def get_birthday(year):
    if month == 2 and day == 29 and not calendar.isleap(year):
        return datetime(year, 2, 28)
    return datetime(year, month, day)

candidate = get_birthday(current_year)
candidate_utc, _ = parse_date(candidate.strftime("%Y-%m-%d") + " " + current_line.split()[1])

if candidate_utc < current_utc:
    candidate = get_birthday(current_year + 1)
    candidate_utc, _ = parse_date(candidate.strftime("%Y-%m-%d") + " " + current_line.split()[1])

delta = (candidate_utc - current_utc).total_seconds()
print(int(delta // 86400))