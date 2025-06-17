from gnuradio import gr, analog, digital, blocks, filter, uhd

class codec2_modem_tx(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "Codec2 Modem TX")

        samp_rate = 48000
        baud_rate = 2400
        freq = 433e6
        gain = 30

        self.src = blocks.file_source(gr.sizeof_char, '/tmp/codec2_out.bit', False)

        self.mod = digital.psk.psk_mod(
            constellation_points=2,
            mod_code="gray",
            differential=True,
            samples_per_symbol=int(samp_rate / baud_rate),
            excess_bw=0.35,
        )

        self.rrc = filter.fir_filter_ccf(1, filter.firdes.root_raised_cosine(
            1.0, samp_rate, baud_rate, 0.35, 100))

        self.sink = uhd.usrp_sink(
            ",",
            uhd.stream_args(cpu_format="fc32", channels=[0]),
        )
        self.sink.set_center_freq(freq)
        self.sink.set_samp_rate(samp_rate)
        self.sink.set_gain(gain)

        self.connect(self.src, self.mod, self.rrc, self.sink)
