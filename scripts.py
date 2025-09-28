from astral import LocationInfo
from datetime import datetime, date
from astral.sun import sun
import pandas as pd
from pytz import timezone
from pyluach import dates
from calculations import molad_calculation_function

# הגדרת המיקום בירושלים
city = LocationInfo("Jerusalem", "Israel", "Asia/Jerusalem", 31.7683, 35.2137)

now = datetime.now(timezone(city.timezone))
hebrew_date = dates.GregorianDate.from_pydate(now.date()).to_heb()
# העברת אובייקט המיקום לפונקציה
molad = molad_calculation_function(hebrew_date, city)

print(f"{hebrew_date}\n")
print(molad)