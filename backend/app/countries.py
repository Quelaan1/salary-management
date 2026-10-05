"""Countries ACME employs people in, each with its currency and a fixed exchange rate.

This is the only place that links a country to a currency and a rate. The seed
script and the exchange_rates table both read it.

Rates are ECB reference rates for 2026-10-05, from https://api.frankfurter.dev.
"""

from decimal import Decimal

# country -> (currency, units of that currency per 1 USD)
COUNTRIES: dict[str, tuple[str, Decimal]] = {
    "Australia": ("AUD", Decimal("1.4367")),
    "Brazil": ("BRL", Decimal("4.9847")),
    "Canada": ("CAD", Decimal("1.4253")),
    "Germany": ("EUR", Decimal("0.89254")),
    "India": ("INR", Decimal("96.3")),
    "Singapore": ("SGD", Decimal("1.2803")),
    "United Kingdom": ("GBP", Decimal("0.75616")),
    "United States": ("USD", Decimal("1")),
}

RATES: dict[str, Decimal] = dict(COUNTRIES.values())
