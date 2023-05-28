"""Constants and functions used in formatting dates for the app."""
from calendar import month_name

# The array of month names in chronological order provided by the calendar
# module has the empty string as the first element, which is discarded.
ORDERED_MONTHS = list(month_name)[1:]

# Dictionary used in converting month names to month numbers (1-based indexing).
MONTH_NUMBERS = {month: index + 1
                 for index, month in enumerate(ORDERED_MONTHS)}

# Dictionary used in converting month names to formatted number strings that can
# be used in ISO-formatted dates.
ISO_MONTH_LABELS = {month_name: format(month_number, '02')
                    for month_name, month_number in MONTH_NUMBERS.items()}
