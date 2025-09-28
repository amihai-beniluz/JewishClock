# -*- coding: utf-8 -*-

import math

from astral import LocationInfo
from astral.sun import sun
from datetime import datetime, timedelta
from pytz import timezone
from pyluach import dates


# ייבוא קבועים
from constants import (
    PLANETS, H_NAMES, H_NAMES_CLEANED, NIKUDIM, GIMATRIA, HEBREW_MONTHS, HEBREW_GIMATRIA_MAP,
    HEBREW_ZODIAC, SEFIROT, SEFIROT_MONTH,
    PARZUF_HASHAVUA, SEFIROT_DAY, HEBREW_WEEKDAYS, FIRST_DAY_STARS, FIRST_NIGHT_STARS, A_NAMES, TRIBES, STONES, HOUSES,
    DIAGONAL_BOUNDARIES, ABILITIES, DAY_SERVANTS, NIGHT_SERVANTS, ET, CAMP, T, C
)


def number_to_hebrew_letters(n):
    """Converts a number (up to 999) to its Hebrew letter (Gimatria) representation."""
    if not isinstance(n, int) or n < 1 or n > 999:
        return ""

    result = ""
    hundreds_val = (n // 100) * 100
    if hundreds_val > 0:
        if hundreds_val <= 400:
            result += HEBREW_GIMATRIA_MAP.get(hundreds_val, "")
        else:
            result += HEBREW_GIMATRIA_MAP.get(400, "")
            hundreds_val -= 400
            result += HEBREW_GIMATRIA_MAP.get(hundreds_val, "")

    n %= 100
    if n == 15:
        result += "ט\"ו"
    elif n == 16:
        result += "ט\"ז"
    else:
        tens_val = (n // 10) * 10
        units_val = n % 10
        result += HEBREW_GIMATRIA_MAP.get(tens_val, "")
        result += HEBREW_GIMATRIA_MAP.get(units_val, "")

    if len(result) > 1 and "\"" not in result:
        result = result[:-1] + "\"" + result[-1]
    elif len(result) == 1:
        result += "'"
    return result


def calculate_gimatriya(combination_str):
    """Calculates the Gimatria of a given string."""
    total = 0
    for char in combination_str:
        total += GIMATRIA.get(char, 0)
    return total


def molad_calculation_function(hebrew_date, location_info):
    """
    Calculates the last molad based on the user's specific, detailed algorithm.
    """

    def r(y):
        if hebrew_date.month >= 7:
            month_index_from_tishrei = hebrew_date.month - 7
        else:
            month_index_from_tishrei = hebrew_date.month + 6

        return T + ((235 * (y - 1) + 1) // 19 + month_index_from_tishrei) * C

    def h(y):
        return (r(y) - math.floor(r(y))) * 24

    # The user's specific logic for the molad calculation

    # Step 1: Get the day and time from the Julian calculation
    total_days_from_epoch = r(hebrew_date.year)
    # The molad weekday (1=Sunday, 7=Saturday)
    molad_day_of_week = math.ceil(total_days_from_epoch % 7)

    # Step 2: Determine the Gregorian Molad date
    rosh_chodesh_heb = dates.HebrewDate(hebrew_date.year, hebrew_date.month, 1)
    rosh_chodesh_greg = rosh_chodesh_heb.to_greg()
    rosh_chodesh_greg_datetime = datetime(rosh_chodesh_greg.year, rosh_chodesh_greg.month, rosh_chodesh_greg.day)

    # Convert Gregorian weekday (0=Mon, 6=Sun) to match Molad weekday (1=Sun, 7=Sat)
    rosh_chodesh_weekday = rosh_chodesh_greg_datetime.weekday()
    if rosh_chodesh_weekday == 6:  # Sunday
        rosh_chodesh_weekday = 1
    else:
        rosh_chodesh_weekday += 2

    final_molad_date = None

    # Step 3: Adjust the date if the weekday is the same
    if rosh_chodesh_weekday == molad_day_of_week:
        # The molad was after midnight on the Gregorian date
        final_molad_date = rosh_chodesh_greg_datetime

        # Calculate the time from the previous sunset to midnight
        prev_sunset_date = final_molad_date - timedelta(days=1)
        s = sun(location_info.observer, date=prev_sunset_date.date(), tzinfo=location_info.timezone)
        prev_sunset_time = s["sunset"]

        time_from_sunset_to_midnight = timedelta(hours=24) - timedelta(
            hours=prev_sunset_time.hour,
            minutes=prev_sunset_time.minute,
            seconds=prev_sunset_time.second
        )

        # The remaining time is the molad time
        molad_time = h(hebrew_date.year) - (time_from_sunset_to_midnight.total_seconds() / 3600)

        hours = int(molad_time)
        minutes = int((molad_time - hours) * 60)
        seconds = round(((molad_time - hours) * 60 - minutes) * 60)

        return final_molad_date + timedelta(hours=hours, minutes=minutes, seconds=seconds)

    # Step 4: Adjust the date if the weekday is one day greater
    elif rosh_chodesh_weekday == molad_day_of_week + 1:
        # The molad was between the previous sunset and midnight
        final_molad_date = rosh_chodesh_greg_datetime - timedelta(days=1)

        # Calculate the time from the sunset two days prior to the original date
        prev_sunset_date = rosh_chodesh_greg_datetime - timedelta(days=2)
        s = sun(location_info.observer, date=prev_sunset_date.date(), tzinfo=location_info.timezone)
        prev_sunset_time = s["sunset"]

        time_from_sunset_to_midnight = timedelta(hours=24) - timedelta(hours=prev_sunset_time.hour,
                                                                       minutes=prev_sunset_time.minute,
                                                                       seconds=prev_sunset_time.second)

        molad_time = h(hebrew_date.year) - (time_from_sunset_to_midnight.total_seconds() / 3600)

        hours = int(molad_time)
        minutes = int((molad_time - hours) * 60)
        seconds = round(((molad_time - hours) * 60 - minutes) * 60)

        return final_molad_date + timedelta(hours=hours, minutes=minutes, seconds=seconds)

    # Step 5: Handle cases not covered
    else:
        # Based on your instructions, this case should not happen.
        # This is a fallback to prevent errors.
        raise ValueError("The provided algorithm does not cover this day-of-week combination.")


def get_moon_course_data(now, last_molad_time):
    """
    Calculates the Moon's course based on the time elapsed since the last molad (new moon).
    The average lunar month is divided into 13 parts.
    """
    try:
        # Check if the datetime objects are timezone-aware and handle accordingly
        if now.tzinfo is not None and last_molad_time.tzinfo is None:
            # Localize the naive datetime object with the same timezone as 'now'
            localized_last_molad_time = now.tzinfo.localize(last_molad_time)
        else:
            # If both are timezone-aware or both are naive, use as is.
            localized_last_molad_time = last_molad_time

        # Average synodic month duration in seconds
        avg_synodic_month_seconds = C * 24 * 60 * 60

        # Duration of each of the 13 parts in seconds
        part_duration_seconds = avg_synodic_month_seconds / 13

        # Calculate the time elapsed since the last molad
        elapsed_time = now - localized_last_molad_time
        elapsed_seconds = elapsed_time.total_seconds()

        # Determine which part of the cycle we are in (0-12)
        part_index = int(elapsed_seconds / part_duration_seconds)

        # Assign the appropriate H_NAMES combination
        if 0 <= part_index < len(H_NAMES):
            moon_course_combination = H_NAMES[part_index]
        else:
            moon_course_combination = "-"

        return moon_course_combination

    except Exception as e:
        print(f"Error in Moon course calculation: {e}")
        return "שגיאה"


def get_current_quarter_data(part_in_hour, holy_combination):
    first_quarter = (calculate_gimatriya(holy_combination[0]) + 1) * 36
    second_quarter = first_quarter + (calculate_gimatriya(holy_combination[1]) + 1) * 36
    third_quarter = second_quarter + (calculate_gimatriya(holy_combination[2]) + 1) * 36
    if 0 <= part_in_hour < first_quarter:
        return 0, part_in_hour
    elif first_quarter <= part_in_hour < second_quarter:
        return 1, part_in_hour - first_quarter
    elif second_quarter <= part_in_hour < third_quarter:
        return 2, part_in_hour - second_quarter
    else:
        return 3, part_in_hour - third_quarter


def get_tatraf_combination(is_day, total_parts, holy_combination):
    part_in_hour = int(total_parts % 1080)
    quarter_of_hour, parts_into_quarter = get_current_quarter_data(part_in_hour, holy_combination)
    letter_for_tatraf = holy_combination[quarter_of_hour]
    gimatriya_value = calculate_gimatriya(letter_for_tatraf)
    index_in_36 = parts_into_quarter // (gimatriya_value + 1)
    nikud_main = NIKUDIM[(index_in_36 // 6) % 6]
    nikud_aleph = NIKUDIM[index_in_36 % 6]
    if is_day:
        return f"{letter_for_tatraf}{nikud_main}א{nikud_aleph}"
    else:
        return f"א{nikud_aleph}{letter_for_tatraf}{nikud_main}"


def get_adnut_combinations(temporary_hour):
    """Retrieves the two 'Adnut' combinations for the current temporary hour."""
    adnut_index_1 = (temporary_hour * 2) % 12
    adnut_index_2 = (adnut_index_1 + 1) % 12

    if 0 <= adnut_index_2 < len(A_NAMES):
        return A_NAMES[adnut_index_1], A_NAMES[adnut_index_2]
    else:
        #TODO: בשביל החודשים - לברר באדר ב מה הצירופים - האם כמו בהויות שזה כולם
        return "שגיאה", "שגיאה"


def get_tribe_of_the_hour(temporary_hour):
    """Retrieves the tribe name for the current temporary hour."""
    tribe_index = temporary_hour
    if 0 <= tribe_index < len(TRIBES):
        return TRIBES[tribe_index]
    else:
        return "שגיאה"


def get_stone_of_the_hour(temporary_hour):
    """Retrieves the stone name for the current temporary hour."""
    stone_index = temporary_hour
    if 0 <= stone_index < len(STONES):
        return STONES[stone_index]
    else:
        return "שגיאה"


def get_house_of_the_hour(temporary_hour):
    """Retrieves the house name for the current temporary hour."""
    house_index = temporary_hour
    if 0 <= house_index < len(HOUSES):
        return HOUSES[house_index]
    else:
        return "שגיאה"


def get_ability_of_the_hour(temporary_hour):
    """Retrieves the ability type for the current temporary hour."""
    ability_index = temporary_hour
    if 0 <= ability_index < len(ABILITIES):
        return ABILITIES[ability_index]
    else:
        return "שגיאה"


def get_diagonal_boundary(temporary_hour):
    """Retrieves the diagonal boundary name for the current temporary hour."""
    boundary_index = temporary_hour
    if 0 <= boundary_index < len(DIAGONAL_BOUNDARIES):
        return DIAGONAL_BOUNDARIES[boundary_index]
    else:
        return "שגיאה"


def get_month_combination(hebrew_month_num):
    month_index = (hebrew_month_num - 1) % 12
    return H_NAMES_CLEANED[month_index]


def get_week_of_month(hebrew_day):
    if 1 <= hebrew_day <= 7:
        return 0
    elif 8 <= hebrew_day <= 14:
        return 1
    elif 15 <= hebrew_day <= 21:
        return 2
    else:
        return 3


def get_planet_index(hebrew_day_of_week_index, is_day, current_hour):
    if is_day:
        star_of_current_day_or_night = FIRST_DAY_STARS[hebrew_day_of_week_index]
    else:
        star_of_current_day_or_night = FIRST_NIGHT_STARS[hebrew_day_of_week_index]
    star_of_current_day_or_night = (star_of_current_day_or_night + current_hour) % 7
    return star_of_current_day_or_night


def get_seravnt_of_planet(planet_index, is_day):
    if is_day:
        return DAY_SERVANTS[planet_index]
    return NIGHT_SERVANTS[planet_index]


def get_et_and_camp_of_the_day(hebrew_day):
    """
    Returns the 'Et' and 'Camp' values based on the Hebrew day of the month.
    For days 29 and 30, returns a hyphen.
    """
    et_value = ET[hebrew_day - 1]
    camp_value = CAMP[hebrew_day - 1]

    return et_value, camp_value


def calculate_temporary_time(now=None):
    if now is None:
        loc = LocationInfo("my home", "Israel", "Asia/Jerusalem", 31.696520, 35.121194)
        now = datetime.now(timezone(loc.timezone))
    else:
        loc = LocationInfo("my home", "Israel", "Asia/Jerusalem", 31.696520, 35.121194)

    is_day = False
    total_parts = 0
    temporary_hour_seconds = 0
    temporary_part_seconds = 0
    planet_of_the_hour = "שגיאה"
    servant_of_planet = "שגיאה"
    holy_combination = "שגיאה"
    quarter_of_hour = 0
    hebrew_date = None
    hebrew_date_str = "שגיאה"
    zodiac_sign = "שגיאה"
    month_combination = "שגיאה"
    parzuf_hashavua = "שגיאה"
    moon_course_str = "שגיאה"
    et_of_the_day = "שגיאה"
    sefirah_hayom = "שגיאה"
    sefirah_elef = "שגיאה"
    sefirah_meah = "שגיאה"
    sefirah_asor = "שגיאה"
    sefirah_shanah = "שגיאה"
    temp_time_str = "שגיאה"
    local_time_str = "שגיאה"
    sunrise_str = "שגיאה"
    sunset_str = "שגיאה"

    try:
        loc = LocationInfo("my home", "Israel", "Asia/Jerusalem", 31.696520, 35.121194)
        today = now.date()
        weekday_index = now.weekday()

        s = sun(loc.observer, date=today, tzinfo=timezone(loc.timezone))
        sunrise = s['sunrise']
        sunset = s['sunset']
        p_s = sun(loc.observer, date=today - timedelta(days=1), tzinfo=timezone(loc.timezone))
        p_sunset = p_s['sunset']
        n_s = sun(loc.observer, date=today + timedelta(days=1), tzinfo=timezone(loc.timezone))
        n_sunrise = n_s['sunrise']

        if now >= sunrise and now <= sunset:
            is_day = True
            shift_for_pyluach = 0
            hebrew_day_of_week_index = (weekday_index + 1) % 7
            time_since_start_seconds = (now - sunrise).total_seconds()
            duration_seconds = (sunset - sunrise).total_seconds()
        elif now > sunset:
            is_day = False
            shift_for_pyluach = 1
            hebrew_day_of_week_index = (weekday_index + 2) % 7
            time_since_start_seconds = (now - sunset).total_seconds()
            duration_seconds = (n_sunrise - sunset).total_seconds()
        else:
            is_day = False
            shift_for_pyluach = 0
            hebrew_day_of_week_index = (weekday_index + 1) % 7
            time_since_start_seconds = (now - p_sunset).total_seconds()
            duration_seconds = (sunrise - p_sunset).total_seconds()

        hebrew_date = dates.GregorianDate.from_pydate((now + timedelta(days=shift_for_pyluach)).date()).to_heb()
        hebrew_day_of_month_str = number_to_hebrew_letters(hebrew_date.day)
        hebrew_year = hebrew_date.year
        hebrew_year_last_digits = hebrew_year % 1000
        hebrew_year_str = "ה'" + number_to_hebrew_letters(hebrew_year_last_digits)
        zodiac_sign = HEBREW_ZODIAC.get(hebrew_date.month, "לא ידוע")
        hebrew_month_num = hebrew_date.month
        if 1 <= hebrew_month_num <= 6:
            sefirah_index = hebrew_month_num - 1
            sefirah_month = SEFIROT_MONTH[sefirah_index]
        elif 7 <= hebrew_month_num <= 13:
            sefirah_index = (hebrew_month_num - 7) % 6
            sefirah_month = SEFIROT_MONTH[sefirah_index]

        month_combination = get_month_combination(hebrew_date.month)
        sefirah_elef = SEFIROT[8]
        hundreds_digit = (hebrew_year // 100) % 10
        sefirah_meah = SEFIROT[hundreds_digit]
        decades_digit = (hebrew_year // 10) % 10
        sefirah_asor = SEFIROT[decades_digit]
        year_digit = hebrew_year % 10
        sefirah_shanah = SEFIROT[year_digit]
        week_of_month = get_week_of_month(hebrew_date.day)
        parzuf_hashavua = PARZUF_HASHAVUA[week_of_month]
        et_of_the_day, camp_of_the_day = get_et_and_camp_of_the_day(hebrew_date.day)
        last_molad_time = molad_calculation_function(hebrew_date, loc)
        moon_course_str = get_moon_course_data(now, last_molad_time)

        if duration_seconds > 0:
            temporary_hour_seconds = duration_seconds / 12
            temporary_part_seconds = temporary_hour_seconds / 1080
            total_parts = time_since_start_seconds / temporary_part_seconds
            temporary_hour = int(total_parts // 1080)
            temporary_parts = int(total_parts % 1080)
            holy_combination = H_NAMES_CLEANED[temporary_hour % 12]
            quarter_of_hour, _ = get_current_quarter_data(temporary_parts, holy_combination)

            tuesday_evening = now.date()
            while tuesday_evening.weekday() != 1:
                tuesday_evening -= timedelta(days=1)
            start_of_cycle = datetime.combine(tuesday_evening, sunset.time(), tzinfo=timezone(loc.timezone))
            if start_of_cycle > now:
                start_of_cycle -= timedelta(days=7)

            sefirah_hayom = SEFIROT_DAY[(hebrew_day_of_week_index) % 7]

            # Use the correct index for the Hebrew day
            current_hebrew_weekday_name = HEBREW_WEEKDAYS.get(hebrew_day_of_week_index, "שגיאה")

            # Reconstruct the Hebrew date string with the weekday name
            hebrew_date_str = f"יום {current_hebrew_weekday_name} {hebrew_day_of_month_str} ב{HEBREW_MONTHS.get(hebrew_date.month, '')} {hebrew_year_str}"

            planet_index = get_planet_index(hebrew_day_of_week_index, is_day, temporary_hour)
            planet_of_the_hour = PLANETS[planet_index]
            servant_of_planet = get_seravnt_of_planet(planet_index, is_day)

            adnut_combination_1, adnut_combination_2 = get_adnut_combinations(temporary_hour)
            tribe_of_the_hour = get_tribe_of_the_hour(temporary_hour)
            stone_of_the_hour = get_stone_of_the_hour(temporary_hour)
            house_of_the_hour = get_house_of_the_hour(temporary_hour)
            ability_of_the_hour = get_ability_of_the_hour(temporary_hour)
            diagonal_boundary = get_diagonal_boundary(temporary_hour)

            temp_time_str = f"{temporary_hour}:{temporary_parts:04}"
            local_time_str = f"{now.strftime('%H:%M:%S')}"
            sunrise_str = f"{sunrise.strftime('%H:%M:%S')}"
            sunset_str = f"{sunset.strftime('%H:%M:%S')}"

        else:
            raise ValueError("Duration of day/night is zero or negative.")

    except Exception as e:
        print(f"An error occurred: {e}")
        # The variables already have their default "שגיאה" values.

    return (
        temp_time_str, temporary_hour_seconds, temporary_part_seconds,
        local_time_str, sunrise_str, sunset_str,
        planet_of_the_hour, servant_of_planet, holy_combination, quarter_of_hour, is_day, total_parts, hebrew_date_str,
        sefirah_elef, sefirah_meah, sefirah_asor, sefirah_shanah, sefirah_month, month_combination,
        hebrew_date, zodiac_sign, parzuf_hashavua, moon_course_str, et_of_the_day,
        camp_of_the_day, sefirah_hayom, adnut_combination_1, adnut_combination_2,
        tribe_of_the_hour, stone_of_the_hour, house_of_the_hour, ability_of_the_hour, diagonal_boundary
    )
