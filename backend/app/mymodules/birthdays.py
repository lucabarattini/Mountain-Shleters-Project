birthdays = {
    'Albert Einstein': '03/14/1879',
    'Benjamin Franklin': '01/17/1706',
    'Ada Lovelace': '12/10/1815',
    'Donald Trump': '06/14/1946',
    'Rowan Atkinson': '01/6/1955'}

# Extract from birthdays dictionary the names of the people and add them in a string
def print_birthdays_str():
    print('Welcome to the birthday dictionary. We know the birthdays of these people:')
    names = ''
    for name in birthdays:
        names += name + ', '
    return names[:-2]


def return_birthday(name):
    if name in birthdays:
        return('{}\'s birthday is {}.'.format(name, birthdays[name]))
    else:
        return('Sadly, we don\'t have {}\'s birthday.'.format(name))