"""Constants used in formatting dates for the app."""
from calendar import month_name

# The array of capitalized month names in chronological order provided by the
# calendar module has the empty string as the first element, which is discarded.
ORDERED_MONTHS = list(month_name)[1:]

# Dictionary used in converting month numbers (1-based indexing) to capitalized
# month names.
MONTH_NAMES = {(index + 1): month
               for index, month in enumerate(ORDERED_MONTHS)}

# Dictionary used in converting month names to month numbers (1-based indexing).
# The dictionary keys are lowercase month names.
MONTH_NUMBERS = {month.lower(): index + 1
                 for index, month in enumerate(ORDERED_MONTHS)}

# Dictionary used in converting month names to formatted number strings that can
# be used in ISO-formatted dates.  The dictionary keys are lowercase month names.
ISO_MONTH_LABELS = {month_name: format(month_number, '02')
                    for month_name, month_number in MONTH_NUMBERS.items()}
