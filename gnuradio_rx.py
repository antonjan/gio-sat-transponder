class codec2_modem_rx(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "Codec2 Modem RX")

        samp_rate = 48000
        baud_rate = 2400
        freq = 433e6
        gain = 30

        self.src = uhd.usrp_source(
            ",",
            uhd.stream_args(cpu_format="fc32", channels=[0]),
        )
        self.src.set_center_freq(freq)
        self.src.set_samp_rate(samp_rate)
        self.src.set_gain(gain)

        self.rrc = filter.fir_filter_ccf(1, filter.firdes.root_raised_cosine(
            1.0, samp_rate, baud_rate, 0.35, 100))

        self.demod = digital.psk.psk_demod(
            constellation_points=2,
            differential=True,
            samples_per_symbol=int(samp_rate / baud_rate),
            excess_bw=0.35,
            phase_bw=0.0628,
            timing_bw=0.0628,
            mod_code="gray",
            verbose=False,
            log=False,
        )

        self.sink = blocks.file_sink(gr.sizeof_char, '/tmp/codec2_rx.bit')

        self.connect(self.src, self.rrc, self.demod, self.sink)
