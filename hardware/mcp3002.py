import gpiozero
from functools import reduce
from operator import or_
from math import log, ceil


class MCP3002(gpiozero.MCP3002):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._min_value = (
            -(2 ** self._bits)
            if self.differential
            else 0
            )

        self._range = 2 ** (self.bits + 1) - 1

    def _words_to_int(self, words, expected_bits=None):
        """
        Given a sequence of words which each fit in the internal SPI
        interface's number of bits per word, returns the value obtained by
        concatenating each word into a single bit-string.
        If *expected_bits* is specified, it limits the size of the output to
        the specified number of bits (by masking off bits above the expected
        number). If unspecified, no limit will be applied.

        Notes
        -----
        this is to be removed once the new gpiozero interface gets released (as
        it is a copy from github)
        """
        if expected_bits is None:
            expected_bits = len(words) * self._spi.bits_per_word

        shifts = range(0, expected_bits, self._spi.bits_per_word)[::-1]
        mask = 2 ** expected_bits - 1

        shifted_words = (
            word << shift
            for word, shift in zip(words, shifts)
            )

        return reduce(or_, shifted_words) & mask

    def _int_to_words(self, pattern):
        """
        Given a bit-pattern expressed in an integer number, return a sequence
        of the individual words that make up the pattern. The number of bits
        per word will be obtained from the internal SPI interface.
        """
        try:
            bits_required = int(ceil(log(pattern, 2)))
        except ValueError:
            # pattern == 0 (technically speaking, no bits are required to
            # transmit the value zero ;)
            bits_required = 1

        shifts = range(0, bits_required, self._spi.bits_per_word)[::-1]
        mask = 2 ** self._spi.bits_per_word - 1
        return [(pattern >> shift) & mask for shift in shifts]

    def _send(self):
        """
        construct the bytes to be sent via spi
        """
        differential_mask = (not self.differential) << 2
        channel_mask = self.channel << 1
        total_pattern = 0b1000 | differential_mask | channel_mask
        shifted_pattern = total_pattern << (self.bits + 2)
        message = self._int_to_words(shifted_pattern)
        return message

    def _read(self):
        """ The `MCP3002`_ is a 10-bit analog to digital converter
        with 2 channels (0-1).

        MCP3002 protocol looks like the following:

            Byte        0        1
            ==== ======== ========
            Tx   01MCLxxx xxxxxxxx
            Rx   xxxxx0RR RRRRRRRR for the 3002

        The transmit bits start with several preamble "0" bits, the number of
        which is determined by the amount required to align the last byte of
        the result with the final byte of output. A start "1" bit is then
        transmitted, followed by the single/differential bit (M); 1 for
        single-ended read, 0 for differential read. Next comes a single bit
        for channel (M) then the MSBF bit (L) which selects whether the data
        will be read out in MSB form only (1) or whether LSB read-out will
        occur after MSB read-out (0).

        Read-out begins with a null bit (0) followed by the result bits (R).
        All other bits are don't care (x).

        .. _MCP3002: http://www.farnell.com/datasheets/1599363.pdf
        """
        message = self._send()
        reply_bytes = self._spi.transfer(message)
        reply = self._words_to_int(reply_bytes)
        return reply
