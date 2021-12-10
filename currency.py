from datapackage import Package as Pkg


def get_codes():
    package = Pkg('https://datahub.io/core/currency-codes/datapackage.json')
    codes: list[str] = []

    for resource in package.resources:
        if resource.descriptor['datahub']['type'] == 'derived/csv':
            codes = list(map(lambda x: x[2], resource.read()))

            while None in codes:
                codes.remove(None)

    return codes


# currency_codes = (
#     "JPY", "CNY", "SDG", "RON", "MKD", "MXN", "CAD", "XAF", "GYD", "AFN",
#     "ZAR", "AUD", "NOK", "ILS", "ISK", "SYP", "LYD", "UYU", "YER", "CSD",
#     "EEK", "THB", "IDR", "LBP", "AED", "BOB", "QAR", "BHD", "HNL", "HRK",
#     "COP", "ALL", "DKK", "MYR", "SEK", "RSD", "BGN", "DOP", "KRW", "LVL",
#     "VEF", "CZK", "TND", "KWD", "VND", "JOD", "NZD", "PAB", "CLP", "PEN",
#     "GBP", "DZD", "CHF", "RUB", "UAH", "ARS", "SAR", "EGP", "INR", "PYG",
#     "TWD", "TRY", "BAM", "OMR", "SGD", "MAD", "BYR", "NIO", "HKD", "LTL",
#     "SKK", "GTQ", "BRL", "EUR", "HUF", "IQD", "CRC", "PHP", "SVC", "PLN",
#     "USD", "XBB", "XBC", "XBD", "UGX", "MOP", "SHP", "TTD", "UYI", "KGS",
#     "DJF", "BTN", "XBA", "HTG", "BBD", "XAU", "FKP", "MWK", "PGK", "XCD",
#     "COU", "RWF", "NGN", "BSD", "XTS", "TMT", "SOS", "TOP", "AOA", "KPW",
#     "GEL", "VUV", "FJD", "MVR", "AZN", "MNT", "MGA", "WST", "KMF", "GNF",
#     "SBD", "BDT", "MMK", "TJS", "CVE", "MDL", "KES", "SRD", "LRD", "MUR",
#     "CDF", "BMD", "USN", "CUP", "USS", "GMD", "UZS", "CUC", "ZMK", "NPR",
#     "NAD", "LAK", "SZL", "XDR", "BND", "TZS", "MXV", "LSL", "KYD", "LKR",
#     "ANG", "PKR", "SLL", "SCR", "GHS", "ERN", "BOV", "GIP", "IRR", "XPT",
#     "BWP", "XFU", "CLF", "ETB", "STD", "XXX", "XPD", "AMD", "XPF", "JMD",
#     "MRO", "BIF", "CHW", "ZWL", "AWG", "MZN", "CHE", "XOF", "KZT", "BZD",
#     "XAG", "KHR",
# )
