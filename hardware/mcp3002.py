import gpiozero


class MCP3002(gpiozero.MCP3002):
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
        channel_bytes = [192, 224]
        reply_bytes = self._spi.transfer([channel_bytes[self.channel], 0])
        reply_bitstring = ''.join("{:08b}".format(n) for n in reply_bytes)
        reply = int(reply_bitstring, 2)
        return reply
