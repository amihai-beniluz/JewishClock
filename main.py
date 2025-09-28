# -*- coding: utf-8 -*-

import tkinter as tk
import pytz
from tkinter import font
from tkinter import messagebox
from datetime import datetime

from constants import TURQUOISE, ECRU, GRAY, YELLOW, BLACK

# ייבוא פונקציות החישוב
from calculations import calculate_temporary_time, get_tatraf_combination, get_week_of_month, SEFIROT_MONTH, \
    get_adnut_combinations

# --- GUI Setup ---
root = tk.Tk()
root.title("שעון זמני")
root.configure(bg="#2c3e50")

# הגדרת הגופנים המותאמים אישית
custom_font = font.Font(family="Arial", size=64, weight="bold")
prominent_font = font.Font(family="Arial", size=40, weight="bold")
small_font = font.Font(family="Arial", size=18)
title_font = font.Font(family="Arial", size=24, weight="bold")
info_font = font.Font(family="Arial", size=14)
combination_font = font.Font(family="Arial", size=18, weight="bold")

# הגדרת משתנים גלובליים לכל רכיבי ממשק המשתמש של החלון הראשי
main_temporary_time_label = None
main_tatraf_label = None
main_local_time_label = None
main_hebrew_date_label = None
main_sun_times_label = None
main_duration_label = None
main_sefirah_elef_label = None
main_sefirah_meah_label = None
main_sefirah_asor_label = None
main_sefirah_shanah_label = None
main_zodiac_label = None
main_sefirah_month_label = None
main_month_combination_labels = []
main_planet_label = None
main_planet_servant_label = None
main_holy_combination_labels = []
main_parzuf_label = None
main_sefirah_hayom_label = None
main_et_of_the_day_label = None
main_camp_of_the_day_label = None
main_moon_course_label = None
main_adnut_hour_combination_label_1 = None
main_adnut_hour_combination_label_2 = None
main_adnut_month_combination_label_1 = None
main_adnut_month_combination_label_2 = None
main_tribe_label = None
main_stone_label = None
main_house_label = None
main_ability_label = None
main_diagonal_boundary_label = None

# מזהה ה-after של הקריאות החוזרות
update_after_id = None
local_time_after_id = None


def cancel_all_updates():
    """מבטל את כל העדכונים שנקבעו מראש."""
    global update_after_id, local_time_after_id
    if update_after_id:
        try:
            root.after_cancel(update_after_id)
        except tk.TclError:
            pass
        update_after_id = None
    if local_time_after_id:
        try:
            root.after_cancel(local_time_after_id)
        except tk.TclError:
            pass
        local_time_after_id = None


def toggle_fullscreen():
    """הופך את החלון למסך מלא ומציג את ממשק המשתמש המלא."""
    cancel_all_updates()
    for widget in main_frame.winfo_children():
        widget.destroy()

    root.attributes('-fullscreen', True)
    root.geometry(f'{root.winfo_screenwidth()}x{root.winfo_screenheight()}')
    create_full_ui(main_frame, is_specific=False)
    update_main_ui()
    update_local_time_main()


def exit_fullscreen_by_esc(event):
    """מאפשר יציאה ממסך מלא בלחיצת ESC."""
    if root.attributes('-fullscreen'):
        cancel_all_updates()
        root.attributes('-fullscreen', False)
        for widget in main_frame.winfo_children():
            widget.destroy()
        create_small_ui(main_frame)
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = 500
        window_height = 500
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate - 40}")
        update_main_ui()
        update_local_time_main()


def create_small_ui(parent_frame):
    """יוצר את ממשק המשתמש המינימלי."""
    global main_temporary_time_label, main_tatraf_label, main_local_time_label

    parent_frame.grid_columnconfigure(1, weight=0, minsize=0)
    parent_frame.grid_columnconfigure(2, weight=0, minsize=0)

    parent_frame.grid_columnconfigure(0, weight=1)
    for i in range(5):
        parent_frame.grid_rowconfigure(i, weight=1)

    tk.Label(parent_frame, text="שעון שעות זמניות", font=title_font, fg="#2ecc71", bg="#2c3e50").grid(row=0, column=0,
                                                                                                      pady=(40, 6))
    main_temporary_time_label = tk.Label(parent_frame, text="--:----", font=custom_font, fg="#ecf0f1", bg="#2c3e50")
    main_temporary_time_label.grid(row=1, column=0, pady=(2, 4))
    main_tatraf_label = tk.Label(parent_frame, text="יחוד תתר\"ף: ?", font=prominent_font, fg="#f1c40f", bg="#2c3e50")
    main_tatraf_label.grid(row=2, column=0, pady=(4, 6))
    main_local_time_label = tk.Label(parent_frame, text="", font=small_font, fg="#bdc3c7", bg="#2c3e50")
    main_local_time_label.grid(row=3, column=0, pady=(2, 2))
    expand_button = tk.Button(parent_frame, text="הרחב תצוגה", command=toggle_fullscreen, font=small_font, bg="#34495e",
                              fg="#ecf0f1")
    expand_button.grid(row=4, column=0, pady=(20, 10))


def create_full_ui(parent_frame, is_specific=False):
    """יוצר את ממשק המשתמש המלא (פריסת לוח מחוונים)."""
    global main_temporary_time_label, main_tatraf_label, main_local_time_label, main_hebrew_date_label, main_sun_times_label, main_duration_label
    global main_sefirah_elef_label, main_sefirah_meah_label, main_sefirah_asor_label, main_sefirah_shanah_label
    global main_zodiac_label, main_sefirah_month_label, main_month_combination_labels
    global main_planet_label, main_holy_combination_labels, main_adnut_month_combination_label_1, main_adnut_month_combination_label_2
    global main_parzuf_label, main_sefirah_hayom_label, main_adnut_hour_combination_label_1, main_adnut_hour_combination_label_2
    global main_tribe_label, main_stone_label, main_house_label, main_ability_label, main_diagonal_boundary_label
    global main_planet_servant_label, main_et_of_the_day_label, main_camp_of_the_day_label, main_moon_course_label

    # הגדרות grid ראשיות עבור החלון הראשי
    parent_frame.grid_columnconfigure(0, weight=1)  # עמודה צד ימין (למידע)
    parent_frame.grid_columnconfigure(1, weight=0, minsize=520)  # עמודה מרכזית (לשעון)
    parent_frame.grid_columnconfigure(2, weight=1)  # עמודה צד שמאל (למידע)
    parent_frame.grid_rowconfigure(0, weight=0)  # כותרת עליונה
    parent_frame.grid_rowconfigure(1, weight=1)  # שורה מרכזית
    parent_frame.grid_rowconfigure(2, weight=0)  # שורה תחתונה (לכפתור)

    # כותרת עליונה
    tk.Label(parent_frame, text="שעון שעות זמניות", font=title_font, fg="#2ecc71", bg="#2c3e50").grid(row=0, column=0,
                                                                                                      columnspan=3,
                                                                                                      pady=(40, 6),
                                                                                                      sticky="n")
    # מסגרת ללוח הימני (המוצג בצד שמאל בגלל RTL)
    right_col = tk.Frame(parent_frame, bg="#2c3e50")
    right_col.grid(row=1, column=0, sticky="nsew", padx=(20, 10))
    right_col.grid_columnconfigure(0, weight=1)
    right_col.grid_rowconfigure(0, weight=0)  # פרטי השנה
    right_col.grid_rowconfigure(1, weight=0)  # פרטי החודש
    right_col.grid_rowconfigure(2, weight=1)  # שורה ריקה שתספוג את החלל
    right_col.grid_rowconfigure(3, weight=0)  # זמני היום

    # מיקום הפריטים בתוך הלוח הימני
    year_sefi_frame = tk.Frame(right_col, bg="#2c3e50")
    year_sefi_frame.grid(row=0, column=0, sticky="n", pady=5)
    month_frame = tk.Frame(right_col, bg="#2c3e50")
    month_frame.grid(row=1, column=0, sticky="n", pady=5)
    day_times_frame = tk.Frame(right_col, bg="#2c3e50")
    day_times_frame.grid(row=3, column=0, sticky="s", pady=(10, 0))

    # מסגרת ללוח השמאלי (המוצג בצד ימין בגלל RTL)
    left_col = tk.Frame(parent_frame, bg="#2c3e50")
    left_col.grid(row=1, column=2, sticky="nsew", padx=(10, 20), pady=(10, 30))
    left_col.grid_columnconfigure(0, weight=1)
    left_col.grid_rowconfigure(0, weight=0)  # פרטי השבוע והיום
    left_col.grid_rowconfigure(1, weight=1)  # שורה ריקה שתספוג את החלל
    left_col.grid_rowconfigure(2, weight=0)  # פרטי השעה

    # מיקום הפריטים בתוך הלוח השמאלי
    day_week_frame = tk.Frame(left_col, bg="#2c3e50")
    day_week_frame.grid(row=0, column=0, sticky="n", pady=5)
    hour_frame = tk.Frame(left_col, bg="#2c3e50")
    hour_frame.grid(row=2, column=0, sticky="s", pady=5)

    # מסגרת מרכזית לשעון
    center_top_frame = tk.Frame(parent_frame, bg="#2c3e50")
    center_top_frame.grid(row=1, column=1, sticky="n", padx=10, pady=(70, 10))
    main_temporary_time_label = tk.Label(center_top_frame, text="--:----", font=custom_font, fg="#ecf0f1", bg="#2c3e50")
    main_temporary_time_label.pack(side="top", pady=(2, 4))
    main_tatraf_label = tk.Label(center_top_frame, text="יחוד תתר\"ף: ?", font=prominent_font, fg="#f1c40f",
                                 bg="#2c3e50")
    main_tatraf_label.pack(side="top", pady=(4, 6))
    main_local_time_label = tk.Label(center_top_frame, text="", font=small_font, fg="#bdc3c7", bg="#2c3e50")
    main_local_time_label.pack(side="top", pady=(2, 2))

    # כפתור תחתון
    if not is_specific:
        bottom_buttons_frame = tk.Frame(parent_frame, bg="#2c3e50")
        bottom_buttons_frame.grid(row=2, column=1, pady=(0, 40))
        specific_date_button = tk.Button(bottom_buttons_frame, text="הזן תאריך מסוים", command=show_specific_date_input,
                                         font=small_font, bg="#34495e", fg="#ecf0f1")
        specific_date_button.pack()

    # --- הוספת התוכן המלא לכל המסגרות ---

    # תוכן year_sefi_frame
    tk.Label(year_sefi_frame, text="פרטי השנה", font=("Arial", 22, "bold"), fg="#ecf0f1", bg="#2c3e50").pack(
        pady=(0, 2))
    main_sefirah_elef_label = tk.Label(year_sefi_frame, text="ספירת האלף: ?", font=info_font, fg="#ecf0f1",
                                       bg="#2c3e50")
    main_sefirah_elef_label.pack(pady=1)
    main_sefirah_meah_label = tk.Label(year_sefi_frame, text="ספירת המאה: ?", font=info_font, fg="#ecf0f1",
                                       bg="#2c3e50")
    main_sefirah_meah_label.pack(pady=1)
    main_sefirah_asor_label = tk.Label(year_sefi_frame, text="ספירת העשור: ?", font=info_font, fg="#ecf0f1",
                                       bg="#2c3e50")
    main_sefirah_asor_label.pack(pady=1)
    main_sefirah_shanah_label = tk.Label(year_sefi_frame, text="ספירת השנה: ?", font=info_font, fg="#ecf0f1",
                                         bg="#2c3e50")
    main_sefirah_shanah_label.pack(pady=1)

    # תוכן month_frame
    tk.Label(month_frame, text="פרטי החודש", font=("Arial", 22, "bold"), fg="#ecf0f1", bg="#2c3e50").pack(pady=(0, 2))
    month_combination_frame = tk.Frame(month_frame, bg="#2c3e50")
    month_combination_frame.pack(pady=5)
    tk.Label(month_combination_frame, text=":צירוף הוי\"ה", font=combination_font, fg="#ecf0f1", bg="#2c3e50").pack(
        side="right", padx=(0, 5))
    main_month_combination_labels.clear()
    for _ in range(4):
        label = tk.Label(month_combination_frame, text="?", font=combination_font, fg="#ecf0f1", bg="#2c3e50")
        label.pack(side="left", padx=1)
        main_month_combination_labels.append(label)
    adnut_month_combination_frame = tk.Frame(month_frame, bg="#2c3e50")
    adnut_month_combination_frame.pack(pady=5)
    tk.Label(adnut_month_combination_frame, text=":צירופי אדנות", font=combination_font, fg="#ecf0f1",
             bg="#2c3e50").pack(side="right", padx=(0, 5))
    main_adnut_month_combination_label_1 = tk.Label(adnut_month_combination_frame, text="?", font=combination_font,
                                                    fg="#ecf0f1",
                                                    bg="#2c3e50")
    main_adnut_month_combination_label_1.pack(side="left", padx=1)
    main_adnut_month_combination_label_2 = tk.Label(adnut_month_combination_frame, text="?", font=combination_font,
                                                    fg="#ecf0f1",
                                                    bg="#2c3e50")
    main_adnut_month_combination_label_2.pack(side="left", padx=1)
    main_zodiac_label = tk.Label(month_frame, text="מזל  ?", font=info_font, fg="#ecf0f1", bg="#2c3e50")
    main_zodiac_label.pack(pady=1)
    main_sefirah_month_label = tk.Label(month_frame, text="ספירת  ?", font=info_font, fg="#ecf0f1", bg="#2c3e50")
    main_sefirah_month_label.pack(pady=1)

    # תוכן day_times_frame
    tk.Label(day_times_frame, text="זמני היום", font=("Arial", 22, "bold"), fg="#ecf0f1", bg="#2c3e50").pack(
        pady=(0, 2))
    main_hebrew_date_label = tk.Label(day_times_frame, text="תאריך עברי: ?", font=info_font, fg="#bdc3c7", bg="#2c3e50")
    main_hebrew_date_label.pack(pady=1)
    main_sun_times_label = tk.Label(day_times_frame, text="", font=info_font, fg="#bdc3c7", bg="#2c3e50")
    main_sun_times_label.pack()
    main_duration_label = tk.Label(day_times_frame, text="", font=info_font, fg="#bdc3c7", bg="#2c3e50")
    main_duration_label.pack(pady=(10, 0))

    # תוכן day_week_frame
    tk.Label(day_week_frame, text="פרטי השבוע והיום", font=("Arial", 22, "bold"), fg="#ecf0f1", bg="#2c3e50").pack(
        pady=(0, 2))
    main_parzuf_label = tk.Label(day_week_frame, text="פרצוף השבוע: ?", font=("Arial", 14), fg="#ecf0f1", bg="#2c3e50")
    main_parzuf_label.pack(pady=2)
    main_moon_course_label = tk.Label(day_week_frame, text="מהלך הלבנה: ?", font=("Arial", 14), fg="#ecf0f1",
                                      bg="#2c3e50")
    main_moon_course_label.pack(pady=2)
    main_et_of_the_day_label = tk.Label(day_week_frame, text="עת: ?", font=("Arial", 14), fg="#ecf0f1", bg="#2c3e50")
    main_et_of_the_day_label.pack(pady=2)
    main_camp_of_the_day_label = tk.Label(day_week_frame, text="מחנה השכינה: ?", font=("Arial", 14), fg="#ecf0f1",
                                          bg="#2c3e50")
    main_camp_of_the_day_label.pack(pady=2)
    main_sefirah_hayom_label = tk.Label(day_week_frame, text="ספירת היום: ?", font=("Arial", 14), fg="#ecf0f1",
                                        bg="#2c3e50")
    main_sefirah_hayom_label.pack(pady=2)

    # תוכן hour_frame
    tk.Label(hour_frame, text="פרטי השעה", font=("Arial", 22, "bold"), fg="#ecf0f1", bg="#2c3e50").pack(pady=(0, 2))
    combination_frame = tk.Frame(hour_frame, bg="#2c3e50")
    combination_frame.pack(pady=5)
    tk.Label(combination_frame, text=":צירוף הוי\"ה", font=combination_font, fg="#ecf0f1", bg="#2c3e50").pack(
        side="right", padx=(0, 5))
    main_holy_combination_labels.clear()
    for _ in range(4):
        label = tk.Label(combination_frame, text="?", font=combination_font, fg="#ecf0f1", bg="#2c3e50")
        label.pack(side="left", padx=1)
        main_holy_combination_labels.append(label)
    adnut_hour_combination_frame = tk.Frame(hour_frame, bg="#2c3e50")
    adnut_hour_combination_frame.pack(pady=5)
    tk.Label(adnut_hour_combination_frame, text=":צירופי אדנות", font=combination_font, fg="#ecf0f1",
             bg="#2c3e50").pack(
        side="right", padx=(0, 5))
    main_adnut_hour_combination_label_1 = tk.Label(adnut_hour_combination_frame, text="?", font=combination_font,
                                                   fg="#ecf0f1",
                                                   bg="#2c3e50")
    main_adnut_hour_combination_label_1.pack(side="left", padx=1)
    main_adnut_hour_combination_label_2 = tk.Label(adnut_hour_combination_frame, text="?", font=combination_font,
                                                   fg="#ecf0f1", bg="#2c3e50")
    main_adnut_hour_combination_label_2.pack(side="left", padx=1)
    main_planet_label = tk.Label(hour_frame, text="כוכב: ?", font=("Arial", 14), fg="#ecf0f1", bg="#2c3e50")
    main_planet_label.pack(pady=1)
    main_planet_servant_label = tk.Label(hour_frame, text="משרת: ?", font=("Arial", 14), fg="#ecf0f1", bg="#2c3e50")
    main_planet_servant_label.pack(pady=1)
    main_tribe_label = tk.Label(hour_frame, text="שבט: ?", font=("Arial", 14), fg="#ecf0f1", bg="#2c3e50")
    main_tribe_label.pack(pady=1)
    main_stone_label = tk.Label(hour_frame, text="אבן: ?", font=("Arial", 14), fg="#ecf0f1", bg="#2c3e50")
    main_stone_label.pack(pady=1)
    main_house_label = tk.Label(hour_frame, text="בית: ?", font=("Arial", 14), fg="#ecf0f1", bg="#2c3e50")
    main_house_label.pack(pady=1)
    main_ability_label = tk.Label(hour_frame, text="פעולה: ?", font=("Arial", 14), fg="#ecf0f1", bg="#2c3e50")
    main_ability_label.pack(pady=1)
    main_diagonal_boundary_label = tk.Label(hour_frame, text="גבול אלכסון: ?", font=("Arial", 14), fg="#ecf0f1",
                                            bg="#2c3e50")
    main_diagonal_boundary_label.pack(pady=1)


def update_main_ui():
    """מעדכן את כל הנתונים על המסך הראשי."""
    global update_after_id

    # בדיקה האם התיבה הראשית עדיין קיימת לפני כל עדכון
    if not main_temporary_time_label or not main_temporary_time_label.winfo_exists():
        update_after_id = root.after(1000, update_main_ui)
        return

    (temp_time_str, temp_hour_duration, temp_part_duration, _, _, _,
     planet_of_the_hour, planet_servant, holy_combination, quarter_of_hour, is_day, total_parts, hebrew_date_str,
     sefirah_elef, sefirah_meah, sefirah_asor, sefirah_shanah, sefirah_month, month_combination, hebrew_date,
     zodiac_sign, parzuf_hashavua, moon_course_str, et_of_the_day,
     camp_of_the_day, sefirah_hayom, adnut_combination_1, adnut_combination_2, tribe_of_the_hour,
     stone_of_the_hour, house_of_the_hour, ability_of_the_hour, diagonal_boundary) = calculate_temporary_time()

    main_temporary_time_label.config(text=temp_time_str)
    tatraf_combination = get_tatraf_combination(is_day, total_parts, holy_combination)
    main_tatraf_label.config(text=f"יחוד תתר\"ף: {tatraf_combination}")

    # עדכון שדות התצוגה המלאה רק אם המשתנים לא ריקים
    if main_hebrew_date_label and main_hebrew_date_label.winfo_exists():
        main_hebrew_date_label.config(text=hebrew_date_str)
        main_sefirah_elef_label.config(text=f"ספירת האלף: {sefirah_elef}")
        main_sefirah_meah_label.config(text=f"ספירת המאה: {sefirah_meah}")
        main_sefirah_asor_label.config(text=f"ספירת העשור: {sefirah_asor}")
        main_sefirah_shanah_label.config(text=f"ספירת השנה: {sefirah_shanah}")
        main_zodiac_label.config(text=f"מזל {zodiac_sign}")

        if hebrew_date and hebrew_date.month is not None:
            if 1 <= hebrew_date.month <= 6:
                sefirah_index = hebrew_date.month - 1
                sefirah_month_val = SEFIROT_MONTH[sefirah_index]
            elif 7 <= hebrew_date.month <= 13:
                sefirah_index = (hebrew_date.month - 7) % 6
                sefirah_month_val = SEFIROT_MONTH[sefirah_index]
            else:
                sefirah_month_val = "שגיאה"
            main_sefirah_month_label.config(text=f"ספירת {sefirah_month_val}")

        if hebrew_date and month_combination != "שגיאה":
            current_week = get_week_of_month(hebrew_date.day)
            for i in range(4):
                if main_month_combination_labels[i].winfo_exists():
                    char = month_combination[3 - i]
                    color = "#2ecc71" if (3 - i) == current_week else "#ecf0f1"
                    main_month_combination_labels[i].config(text=char, fg=color)
        else:
            for label in main_month_combination_labels:
                if label.winfo_exists():
                    label.config(text="?", fg="#ecf0f1")

        main_parzuf_label.config(text=f"פרצוף השבוע: {parzuf_hashavua}")
        main_moon_course_label.config(text=f"מהלך הלבנה: {moon_course_str}")
        main_et_of_the_day_label.config(text=f"עת: {et_of_the_day}")
        main_camp_of_the_day_label.config(text=f"שם מחנה השכינה: {camp_of_the_day}")
        main_sefirah_hayom_label.config(text=f"ספירת היום: {sefirah_hayom}")

        if holy_combination != "שגיאה":
            for i in range(4):
                if main_holy_combination_labels[i].winfo_exists():
                    char = holy_combination[3 - i]
                    color = "#2ecc71" if (3 - i) == quarter_of_hour else "#ecf0f1"
                    main_holy_combination_labels[i].config(text=char, fg=color)
        else:
            for label in main_holy_combination_labels:
                if label.winfo_exists():
                    label.config(text="?", fg="#ecf0f1")

        main_adnut_hour_combination_label_1.config(text=adnut_combination_1)
        main_adnut_hour_combination_label_2.config(text=adnut_combination_2)

        if hebrew_date and hebrew_date.month is not None:
            adnut_combination_1_val, adnut_combination_2_val = get_adnut_combinations(hebrew_date.month - 1)
            main_adnut_month_combination_label_1.config(text=adnut_combination_1_val)
            main_adnut_month_combination_label_2.config(text=adnut_combination_2_val)

        main_planet_label.config(text=f"כוכב: {planet_of_the_hour}")
        main_planet_servant_label.config(text=f"משרת: {planet_servant}")
        main_tribe_label.config(text=f"שבט: {tribe_of_the_hour}")
        main_stone_label.config(text=f"אבן: {stone_of_the_hour}")
        main_house_label.config(text=f"בית: {house_of_the_hour}")
        main_ability_label.config(text=f"פעולה: {ability_of_the_hour}")
        main_diagonal_boundary_label.config(text=f"גבול אלכסון: {diagonal_boundary}")

        main_duration_label.config(
            text=f"אורך שעה זמנית: {temp_hour_duration / 60:.2f}"
                 f" דקות\nאורך חלק זמני: {temp_part_duration:.4f} שניות")

    if temp_part_duration > 0:
        update_after_id = root.after(int(temp_part_duration * 1000), update_main_ui)
    else:
        update_after_id = root.after(1000, update_main_ui)


def update_local_time_main():
    """מעדכן את השעה המקומית וזמני השמש על המסך הראשי."""
    global local_time_after_id

    # בדיקה האם התיבה הראשית עדיין קיימת לפני כל עדכון
    if not main_local_time_label or not main_local_time_label.winfo_exists():
        local_time_after_id = root.after(1000, update_local_time_main)
        return

    (_, _, _, local_time_str, sunrise_str, sunset_str, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
     _, _, _, _, _, _) = calculate_temporary_time()

    main_local_time_label.config(text=f"זמן מקומי: {local_time_str}")
    if main_sun_times_label and main_sun_times_label.winfo_exists():
        main_sun_times_label.config(text=f"זריחה: {sunrise_str} | שקיעה: {sunset_str}")

    local_time_after_id = root.after(1000, update_local_time_main)


def show_specific_date_input():
    """מציג חלון קופץ לקבלת תאריך ושעה מהמשתמש במרכז המסך."""
    input_window = tk.Toplevel(root)
    input_window.title("הזן תאריך ושעה")
    input_window.configure(bg="#2c3e50")

    # חישוב המיקום למרכז המסך
    window_width = 350
    window_height = 250
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_cordinate = int((screen_width / 2) - (window_width / 2))
    y_cordinate = int((screen_height / 2) - (window_height / 2))
    input_window.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

    input_window.transient(root)
    input_window.grab_set()

    tk.Label(input_window, text="הזן תאריך (DD-MM-YYYY):", bg="#2c3e50", fg="#ecf0f1", font=small_font).pack(pady=10)
    date_entry = tk.Entry(input_window, font=small_font)
    date_entry.pack(pady=5)
    date_entry.focus_set()  # כדי לאפשר לחיצה על אנטר מיד

    tk.Label(input_window, text="הזן שעה (HH:MM):", bg="#2c3e50", fg="#ecf0f1", font=small_font).pack(pady=10)
    time_entry = tk.Entry(input_window, font=small_font)
    time_entry.pack(pady=5)

    def on_submit():
        date_str = date_entry.get()
        time_str = time_entry.get()
        try:
            full_datetime_str = f"{date_str} {time_str}"
            naive_datetime = datetime.strptime(full_datetime_str, "%d-%m-%Y %H:%M")
            jerusalem_tz = pytz.timezone("Asia/Jerusalem")
            specific_datetime = jerusalem_tz.localize(naive_datetime)
            input_window.destroy()
            show_specific_date_window(specific_datetime)
        except ValueError:
            messagebox.showerror("שגיאת קלט",
                                 "פורמט תאריך או שעה שגוי. אנא הזן תאריך בפורמט DD-MM-YYYY ושעה בפורמט HH:MM.")

    tk.Button(input_window, text="הצג נתונים", command=on_submit, font=small_font, bg="#34495e", fg="#ecf0f1").pack(
        pady=20)

    # קושרים את מקש ה-Enter לפונקציית on_submit
    input_window.bind('<Return>', lambda event: on_submit())


def show_specific_date_window(now):
    """מציג חלון חדש עם הנתונים עבור התאריך והשעה שהוזנו."""
    cancel_all_updates()

    specific_window = tk.Toplevel(root)
    specific_window.title("נתונים לתאריך ספציפי")
    # שינוי צבע הרקע לטורקיז
    specific_window.configure(bg="#1abc9c")
    specific_window.attributes('-fullscreen', True)

    # יצירת פונקציית עזר לסגירה שגם הורסת את החלון
    def close_specific_window():
        specific_window.destroy()
        # מפעיל מחדש את הלולאות של החלון הראשי
        update_main_ui()
        update_local_time_main()

    # קושרים את מקש ה-ESC לפונקציית הסגירה החדשה
    specific_window.bind('<Escape>', lambda e: close_specific_window())

    specific_frame = tk.Frame(specific_window, bg="#1abc9c")
    specific_frame.pack(fill="both", expand=True)

    # יצירת מופעים חדשים של כל הרכיבים בתוך החלון החדש
    specific_labels = {}
    create_full_ui_for_specific(specific_frame, specific_labels)

    # עדכון הנתונים בתוך החלון החדש
    update_specific_ui(specific_labels, now)
    update_local_time_specific(specific_labels, now)


def create_full_ui_for_specific(parent_frame, labels_dict):
    """יוצר את ממשק המשתמש המלא עבור החלון הספציפי ומאחסן את הרכיבים במילון."""
    parent_frame.grid_columnconfigure(0, weight=1)
    parent_frame.grid_columnconfigure(1, weight=0, minsize=520)
    parent_frame.grid_columnconfigure(2, weight=1)
    parent_frame.grid_rowconfigure(0, weight=0)
    parent_frame.grid_rowconfigure(1, weight=1)
    parent_frame.grid_rowconfigure(2, weight=0)

    tk.Label(parent_frame, text="שעון שעות זמניות", font=title_font, fg=BLACK, bg=TURQUOISE).grid(row=0, column=0,
                                                                                                  columnspan=3,
                                                                                                  pady=(40, 6),
                                                                                                  sticky="n")

    # כל המסגרות שהיו בעמודה הימנית (right_col) הועברו כעת לעמודה השמאלית (column=0)
    right_col = tk.Frame(parent_frame, bg=TURQUOISE)
    right_col.grid(row=1, column=0, sticky="nsew", padx=(20, 10))
    right_col.grid_columnconfigure(0, weight=1)
    right_col.grid_rowconfigure(0, weight=1)
    right_col.grid_rowconfigure(1, weight=1)
    right_col.grid_rowconfigure(2, weight=1)

    year_sefi_frame = tk.Frame(right_col, bg=TURQUOISE)
    year_sefi_frame.grid(row=0, column=0, sticky="nwe", pady=5)
    tk.Label(year_sefi_frame, text="פרטי השנה", font=("Arial", 22, "bold"), fg=ECRU, bg=TURQUOISE).pack(
        pady=(0, 2))
    labels_dict["sefirah_elef"] = tk.Label(year_sefi_frame, text="ספירת האלף: ?", font=info_font, fg=ECRU, bg=TURQUOISE)
    labels_dict["sefirah_elef"].pack(pady=1)
    labels_dict["sefirah_meah"] = tk.Label(year_sefi_frame, text="ספירת המאה: ?", font=info_font, fg=ECRU, bg=TURQUOISE)
    labels_dict["sefirah_meah"].pack(pady=1)
    labels_dict["sefirah_asor"] = tk.Label(year_sefi_frame, text="ספירת העשור: ?", font=info_font, fg=ECRU,
                                           bg=TURQUOISE)
    labels_dict["sefirah_asor"].pack(pady=1)
    labels_dict["sefirah_shanah"] = tk.Label(year_sefi_frame, text="ספירת השנה: ?", font=info_font, fg=ECRU,
                                             bg=TURQUOISE)
    labels_dict["sefirah_shanah"].pack(pady=1)

    month_frame = tk.Frame(right_col, bg=TURQUOISE)
    month_frame.grid(row=1, column=0, sticky="nwe", pady=5)
    tk.Label(month_frame, text="פרטי החודש", font=("Arial", 22, "bold"), fg=ECRU, bg=TURQUOISE).pack(pady=(0, 2))
    month_combination_frame = tk.Frame(month_frame, bg=TURQUOISE)
    month_combination_frame.pack(pady=5)
    tk.Label(month_combination_frame, text=":צירוף הוי\"ה", font=combination_font, fg=ECRU, bg=TURQUOISE).pack(
        side="right", padx=(0, 0))
    labels_dict["month_combination_labels"] = []
    for _ in range(4):
        label = tk.Label(month_combination_frame, text="?", font=combination_font, fg=ECRU, bg=TURQUOISE)
        label.pack(side="left", padx=1)
        labels_dict["month_combination_labels"].append(label)
    adnut_month_combination_frame = tk.Frame(month_frame, bg=TURQUOISE)
    adnut_month_combination_frame.pack(pady=5)
    tk.Label(adnut_month_combination_frame, text=":צירופי אדנות", font=combination_font, fg=ECRU,
             bg=TURQUOISE).pack(
        side="right", padx=(0, 5))
    labels_dict["adnut_month_combination_label_1"] = tk.Label(adnut_month_combination_frame, text="?",
                                                              font=combination_font,
                                                              fg=ECRU,
                                                              bg=TURQUOISE)
    labels_dict["adnut_month_combination_label_1"].pack(side="left", padx=1)
    labels_dict["adnut_month_combination_label_2"] = tk.Label(adnut_month_combination_frame, text="?",
                                                              font=combination_font,
                                                              fg=ECRU,
                                                              bg=TURQUOISE)
    labels_dict["adnut_month_combination_label_2"].pack(side="left", padx=1)
    labels_dict["zodiac"] = tk.Label(month_frame, text="מזל  ?", font=info_font, fg=ECRU, bg=TURQUOISE)
    labels_dict["zodiac"].pack(pady=1)
    labels_dict["sefirah_month"] = tk.Label(month_frame, text="ספירת  ?", font=info_font, fg=ECRU, bg=TURQUOISE)
    labels_dict["sefirah_month"].pack(pady=1)

    day_times_frame = tk.Frame(right_col, bg=TURQUOISE)
    day_times_frame.grid(row=2, column=0, sticky="nswe", pady=(10, 0))
    tk.Label(day_times_frame, text="זמני היום", font=("Arial", 22, "bold"), fg=ECRU, bg=TURQUOISE).pack(
        pady=(0, 2))
    labels_dict["hebrew_date"] = tk.Label(day_times_frame, text="תאריך עברי: ?", font=info_font, fg=GRAY, bg=TURQUOISE)
    labels_dict["hebrew_date"].pack(pady=1)
    labels_dict["sun_times"] = tk.Label(day_times_frame, text="", font=info_font, fg=GRAY, bg=TURQUOISE)
    labels_dict["sun_times"].pack()
    labels_dict["duration"] = tk.Label(day_times_frame, text="", font=info_font, fg=GRAY, bg=TURQUOISE)
    labels_dict["duration"].pack(pady=(10, 0))

    center_top_frame = tk.Frame(parent_frame, bg=TURQUOISE)
    center_top_frame.grid(row=1, column=1, sticky="n", padx=10, pady=(100, 10))
    labels_dict["temporary_time"] = tk.Label(center_top_frame, text="--:----", font=custom_font, fg=ECRU, bg=TURQUOISE)
    labels_dict["temporary_time"].pack(side="top", pady=(2, 4))
    labels_dict["tatraf"] = tk.Label(center_top_frame, text="יחוד תתר\"ף: ?", font=prominent_font, fg=YELLOW,
                                     bg=TURQUOISE)
    labels_dict["tatraf"].pack(side="top", pady=(4, 6))
    labels_dict["local_time"] = tk.Label(center_top_frame, text="", font=small_font, fg=GRAY, bg=TURQUOISE)
    labels_dict["local_time"].pack(side="top", pady=(2, 2))

    # כל המסגרות שהיו בעמודה השמאלית (left_col) הועברו כעת לעמודה הימנית (column=2)
    left_col = tk.Frame(parent_frame, bg=TURQUOISE)
    left_col.grid(row=1, column=2, sticky="nsew", padx=(10, 20), pady=(10, 0))
    left_col.grid_columnconfigure(0, weight=1)
    left_col.grid_rowconfigure(0, weight=1)
    left_col.grid_rowconfigure(1, weight=1)
    left_col.grid_rowconfigure(2, weight=1)

    day_week_frame = tk.Frame(left_col, bg=TURQUOISE)
    day_week_frame.grid(row=0, column=0, sticky="nwe", pady=5)
    tk.Label(day_week_frame, text="פרטי השבוע והיום", font=("Arial", 22, "bold"), fg=ECRU, bg=TURQUOISE).pack(
        pady=(0, 2))
    labels_dict["parzuf"] = tk.Label(day_week_frame, text="פרצוף השבוע: ?", font=("Arial", 14), fg=ECRU, bg=TURQUOISE)
    labels_dict["parzuf"].pack(pady=2)
    labels_dict["moon_course"] = tk.Label(day_week_frame, text="מהלך הלבנה: ?", font=("Arial", 14), fg=ECRU,
                                          bg=TURQUOISE)
    labels_dict["moon_course"].pack(pady=2)
    labels_dict["et_of_the_day"] = tk.Label(day_week_frame, text="עת: ?", font=("Arial", 14), fg=ECRU, bg=TURQUOISE)
    labels_dict["et_of_the_day"].pack(pady=2)
    labels_dict["camp_of_the_day"] = tk.Label(day_week_frame, text="שם מחנה השכינה: ?", font=("Arial", 14), fg=ECRU,
                                              bg=TURQUOISE)
    labels_dict["camp_of_the_day"].pack(pady=2)
    labels_dict["sefirah_hayom"] = tk.Label(day_week_frame, text="ספירת היום: ?", font=("Arial", 14), fg=ECRU,
                                            bg=TURQUOISE)
    labels_dict["sefirah_hayom"].pack(pady=2)

    hour_frame = tk.Frame(left_col, bg=TURQUOISE)
    hour_frame.grid(row=1, column=0, sticky="nwe", pady=5)
    tk.Label(hour_frame, text="פרטי השעה", font=("Arial", 22, "bold"), fg=ECRU, bg=TURQUOISE).pack(pady=(0, 2))
    combination_frame = tk.Frame(hour_frame, bg=TURQUOISE)
    combination_frame.pack(pady=5)
    tk.Label(combination_frame, text=":צירוף הוי\"ה", font=combination_font, fg=ECRU, bg=TURQUOISE).pack(
        side="right", padx=(0, 0))
    labels_dict["holy_combination_labels"] = []
    for _ in range(4):
        label = tk.Label(combination_frame, text="?", font=combination_font, fg=ECRU, bg=TURQUOISE)
        label.pack(side="left", padx=1)
        labels_dict["holy_combination_labels"].append(label)
    adnut_hour_combination_frame = tk.Frame(hour_frame, bg=TURQUOISE)
    adnut_hour_combination_frame.pack(pady=5)
    tk.Label(adnut_hour_combination_frame, text=":צירופי אדנות", font=combination_font, fg=ECRU, bg=TURQUOISE).pack(
        side="right", padx=(0, 5))
    labels_dict["adnut_hour_combination_label_1"] = tk.Label(adnut_hour_combination_frame, text="?",
                                                             font=combination_font, fg=ECRU,
                                                             bg=TURQUOISE)
    labels_dict["adnut_hour_combination_label_1"].pack(side="left", padx=1)
    labels_dict["adnut_hour_combination_label_2"] = tk.Label(adnut_hour_combination_frame, text="?",
                                                             font=combination_font, fg=ECRU,
                                                             bg=TURQUOISE)
    labels_dict["adnut_hour_combination_label_2"].pack(side="left", padx=1)

    labels_dict["planet"] = tk.Label(hour_frame, text="כוכב: ?", font=("Arial", 14), fg=ECRU, bg=TURQUOISE)
    labels_dict["planet"].pack(pady=1)
    labels_dict["planet_servant"] = tk.Label(hour_frame, text="משרת: ?", font=("Arial", 14), fg=ECRU, bg=TURQUOISE)
    labels_dict["planet_servant"].pack(pady=1)
    labels_dict["tribe"] = tk.Label(hour_frame, text="שבט: ?", font=("Arial", 14), fg=ECRU, bg=TURQUOISE)
    labels_dict["tribe"].pack(pady=1)
    labels_dict["stone"] = tk.Label(hour_frame, text="אבן: ?", font=("Arial", 14), fg=ECRU, bg=TURQUOISE)
    labels_dict["stone"].pack(pady=1)
    labels_dict["house"] = tk.Label(hour_frame, text="בית: ?", font=("Arial", 14), fg=ECRU, bg=TURQUOISE)
    labels_dict["house"].pack(pady=1)
    labels_dict["ability"] = tk.Label(hour_frame, text="פעולה: ?", font=("Arial", 14), fg=ECRU, bg=TURQUOISE)
    labels_dict["ability"].pack(pady=1)
    labels_dict["diagonal_boundary"] = tk.Label(hour_frame, text="גבול אלכסון: ?", font=("Arial", 14), fg=ECRU,
                                                bg=TURQUOISE)
    labels_dict["diagonal_boundary"].pack(pady=1)


def update_specific_ui(labels, now):
    """מעדכן את כל הנתונים על המסך של החלון הספציפי."""
    (temp_time_str, temp_hour_duration, temp_part_duration, _, _, _,
     planet_of_the_hour, planet_servant, holy_combination, quarter_of_hour, is_day, total_parts, hebrew_date_str,
     sefirah_elef, sefirah_meah, sefirah_asor, sefirah_shanah, sefirah_month, month_combination, hebrew_date,
     zodiac_sign, parzuf_hashavua, moon_course_str, et_of_the_day,
     camp_of_the_day, sefirah_hayom, adnut_combination_1, adnut_combination_2, tribe_of_the_hour,
     stone_of_the_hour, house_of_the_hour, ability_of_the_hour, diagonal_boundary) = calculate_temporary_time(now=now)

    labels["temporary_time"].config(text=temp_time_str)
    tatraf_combination = get_tatraf_combination(is_day, total_parts, holy_combination)
    labels["tatraf"].config(text=f"יחוד תתר\"ף: {tatraf_combination}")

    labels["hebrew_date"].config(text=hebrew_date_str)
    labels["sefirah_elef"].config(text=f"ספירת האלף: {sefirah_elef}")
    labels["sefirah_meah"].config(text=f"ספירת המאה: {sefirah_meah}")
    labels["sefirah_asor"].config(text=f"ספירת העשור: {sefirah_asor}")
    labels["sefirah_shanah"].config(text=f"ספירת השנה: {sefirah_shanah}")
    labels["zodiac"].config(text=f"מזל {zodiac_sign}")

    if hebrew_date and hebrew_date.month is not None:
        if 1 <= hebrew_date.month <= 6:
            sefirah_index = hebrew_date.month - 1
            sefirah_month_val = SEFIROT_MONTH[sefirah_index]
        elif 7 <= hebrew_date.month <= 13:
            sefirah_index = (hebrew_date.month - 7) % 6
            sefirah_month_val = SEFIROT_MONTH[sefirah_index]
        else:
            sefirah_month_val = "שגיאה"
        labels["sefirah_month"].config(text=f"ספירת {sefirah_month_val}")

    if hebrew_date and month_combination != "שגיאה":
        current_week = get_week_of_month(hebrew_date.day)
        for i in range(4):
            if labels["month_combination_labels"][i].winfo_exists():
                char = month_combination[3 - i]
                color = "#ff0000" if (3 - i) == current_week else "#ecf0f1"
                labels["month_combination_labels"][i].config(text=char, fg=color)

    labels["parzuf"].config(text=f"פרצוף השבוע: {parzuf_hashavua}")
    labels["moon_course"].config(text=f"מהלך הלבנה: {moon_course_str}")
    labels["et_of_the_day"].config(text=f"עת: {et_of_the_day}")
    labels["camp_of_the_day"].config(text=f"שם מחנה השכינה: {camp_of_the_day}")
    labels["sefirah_hayom"].config(text=f"ספירת היום: {sefirah_hayom}")

    if holy_combination != "שגיאה":
        for i in range(4):
            if labels["holy_combination_labels"][i].winfo_exists():
                char = holy_combination[3 - i]
                color = "#ff0000" if (3 - i) == quarter_of_hour else "#ecf0f1"
                labels["holy_combination_labels"][i].config(text=char, fg=color)

    labels["adnut_hour_combination_label_1"].config(text=adnut_combination_1)
    labels["adnut_hour_combination_label_2"].config(text=adnut_combination_2)

    if hebrew_date and hebrew_date.month is not None:
        adnut_combination_1_val, adnut_combination_2_val = get_adnut_combinations(hebrew_date.month - 1)
        labels["adnut_month_combination_label_1"].config(text=adnut_combination_1_val)
        labels["adnut_month_combination_label_2"].config(text=adnut_combination_2_val)

    labels["planet"].config(text=f"כוכב: {planet_of_the_hour}")
    labels["planet_servant"].config(text=f"משרת: {planet_servant}")
    labels["tribe"].config(text=f"שבט: {tribe_of_the_hour}")
    labels["stone"].config(text=f"אבן: {stone_of_the_hour}")
    labels["house"].config(text=f"בית: {house_of_the_hour}")
    labels["ability"].config(text=f"פעולה: {ability_of_the_hour}")
    labels["diagonal_boundary"].config(text=f"גבול אלכסון: {diagonal_boundary}")

    labels["duration"].config(
        text=f"אורך שעה זמנית: {temp_hour_duration / 60:.2f}"
             f" דקות\nאורך חלק זמני: {temp_part_duration:.4f} שניות")


def update_local_time_specific(labels, now):
    """מעדכן את השעה המקומית וזמני השמש על המסך של החלון הספציפי."""
    (_, _, _, local_time_str, sunrise_str, sunset_str, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
     _, _, _, _, _) = calculate_temporary_time(now=now)

    labels["local_time"].config(text=f"זמן מקומי: {local_time_str}")
    if labels["sun_times"]:
        labels["sun_times"].config(text=f"זריחה: {sunrise_str} | שקיעה: {sunset_str}")


# יצירת ממשק המשתמש הראשוני
main_frame = tk.Frame(root, bg="#2c3e50")
main_frame.pack(fill="both", expand=True)

# יצירת ממשק המשתמש המינימלי
create_small_ui(main_frame)

# יצירת מסגרת תחתונה חדשה לכפתור
bottom_frame = tk.Frame(root, bg="#2c3e50")
bottom_frame.pack(side="bottom", pady=20)  # מיקום בתחתית המסך

# יצירת הכפתור והצגתו במסגרת החדשה
specific_date_button = tk.Button(bottom_frame, text="הזן תאריך מסוים", command=show_specific_date_input,
                                 font=small_font, bg="#34495e", fg="#ecf0f1")
specific_date_button.pack()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 500
window_height = 500
x_cordinate = int((screen_width / 2) - (window_width / 2))
y_cordinate = int((screen_height / 2) - (window_height / 2))
root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate - 40}")

# קשירה של כפתור ESC ליציאה ממסך מלא
root.bind('<Escape>', exit_fullscreen_by_esc)

# התחלת עדכון השעון
update_main_ui()
update_local_time_main()

root.mainloop()
