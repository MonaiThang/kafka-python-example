import random
import string


def random_n_digits(n):
    """
    Generate a specified number of digits randomly
    Reference: https://stackoverflow.com/questions/2673385/how-to-generate-random-number-with-the-specific-length-in-python
    :param n: Number of digits that it should be generated
    :return: Specified number of random digits
    """
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return random.randint(range_start, range_end)


def random_alphanumeric_string(length=8, lowercase_only=True):
    """
    Generate a random alphanumeric string of letters and digit with specified length, configurable to get only lowercase
    Reference: https://pynative.com/python-generate-random-string/
    :param length: Length of random alphanumeric string
    :param lowercase_only: Specify whether to only get lowercase letters
    :return:
    """
    if lowercase_only:
        alphanumeric = string.ascii_lowercase + string.digits
    else:
        alphanumeric = string.ascii_letters + string.digits
    return ''.join((random.choice(alphanumeric) for i in range(length)))
