# Python .format syntax #
	:[[fill]align][sign][#][0][width][,][.precision][type]
## Numerical ##

| Modifier | Alignment                       |
| -------- | ------------------------------- |
|    <     | Left-align (default)            |
|    >     | Right-align                     |
|    =     | Padding between sign and digits |
|    ^     | Center-align                    |
Right align to the width of the second argument: {0:>{1}}
Fill with *: {:*^30}
>>> for align, text in [('<', 'left'), ('^', 'center'), ('>', 'right')]:
...     '{0:{fill}{align}16}'.format(text, fill=align, align=align)
...
'left<<<<<<<<<<<<'
'^^^^^center^^^^^'
'>>>>>>>>>>>right'

| Modifier | Meaning                                              |
| -------- | ---------------------------------------------------- |
|    +     | Positive and negative                                |
|    -     | Negative only                                        |
|  space   | Leading space for positive, minus sign on negative   |
|    #     | For binary, octal and hex, prefix with 0b, 0o, or 0x |
|          | (This is counted in the field width)                 |
|    ,     | Comma-aware                                          |
Usual hex format: {:#010X}

### Integer types ###

b 	Binary format. Outputs the number in base 2.
c 	Character. Converts the integer to the corresponding unicode character before printing.
d 	Decimal Integer. Outputs the number in base 10.
o 	Octal format. Outputs the number in base 8.
x 	Hex format. Outputs the number in base 16, using lower- case letters for the digits above 9.
X 	Hex format. Outputs the number in base 16, using upper- case letters for the digits above 9.
n 	Number. This is the same as 'd', except that it uses the current locale setting to insert the appropriate number separator characters.
None 	The same as 'd'.

>>> octets = [192, 168, 0, 1]
>>> '{:02X}{:02X}{:02X}{:02X}'.format(*octets)
'C0A80001'
>>> int(_, 16)
3232235521L

### Floating-point and integer types ###
e 	Exponent notation. Prints the number in scientific notation using the letter ‘e’ to indicate the exponent.
E 	Exponent notation. Same as 'e' except it uses an upper case ‘E’ as the separator character.
f 	Fixed point. Displays the number as a fixed-point number.
F 	Fixed point. Same as 'f'.
g 	General format. 
G 	General format. Same as 'g' except switches to 'E' if the number gets too large. The representations of infinity and NaN are uppercased, too.
n 	Number. This is the same as 'g', except that it uses the current locale setting to insert the appropriate number separator characters.
% 	Percentage. Multiplies the number by 100 and displays in fixed ('f') format, followed by a percent sign.
None 	The same as 'g'.

#### General format ####
For a given precision p >= 1, this rounds the number to p significant digits and then formats the result in either fixed-point format or in scientific notation, depending on its magnitude.
The precise rules are as follows: suppose that the result formatted with presentation type 'e' and precision p-1 would have exponent exp. Then if -4 <= exp < p, the number is formatted with presentation type 'f' and precision p-1-exp. Otherwise, the number is formatted with presentation type 'e' and precision p-1. In both cases insignificant trailing zeros are removed from the significand, and the decimal point is also removed if there are no remaining digits following it.
Positive and negative infinity, positive and negative zero, and nans, are formatted as inf, -inf, 0, -0 and nan respectively, regardless of the precision.
A precision of 0 is treated as equivalent to a precision of 1.

## Class representation ##
!r	repr
!s	str

## Dereferencing ##
'{0[a]};{0[b]};{0[c]};{0[d]}'.format(D)
'{0.a};{0.b};{0.c};{0.d}'.format(C)

# Type-specific formatting #
>>> import datetime
>>> d = datetime.datetime(2010, 7, 4, 12, 15, 58)
>>> '{:%Y-%m-%d %H:%M:%S}'.format(d)
'2010-07-04 12:15:58'

