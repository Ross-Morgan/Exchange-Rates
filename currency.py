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
