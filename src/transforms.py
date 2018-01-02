def simple_pass(field):
    return field

# types conversions
def integer2string(value):
    return str(value)


def string2integer(value):
    return int(value)


def string2number(value):
    return float(value)


def integer2number(value):
    return value

# value conversions
def FtoC(value):
    return (float(value) - 32)*(5/9)


def CtoF(value):
    return float(value)*1.8 + 32


def CtoK(value):
    return float(value) + 273.15


def USDtoPLN(value):
    return float(value)*3.58


def KMHtoMPH(value):
    return float(value)*0.621371192

if __name__ == "__main__":
    print(CtoF(20))