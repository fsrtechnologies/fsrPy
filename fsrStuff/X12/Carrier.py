class Carrier(object):
    carDict = {
        "Jur. E NorCal"  : {"LongName":"Noridian JE Part B",              "PayorID":"01112", "IQ":"27", "Dial":"(701)277-2355", "DME":False},
        "Jur. E SoCal"   : {"LongName":"Noridian JE Part B",              "PayorID":"01182", "IQ":"27", "Dial":"(701)277-2355", "DME":False},
        "CA(N)-PartB"    : {"LongName":"PALMETTO GBA",                    "PayorID":"01102", "IQ":"27", "Dial":"(803)788-9860", "DME":False},
        "CA(S)-PartB"    : {"LongName":"PALMETTO GBA",                    "PayorID":"01192", "IQ":"27", "Dial":"(803)788-9860", "DME":False},
        "Medi-Cal"       : {"LongName":"Medi-Cal",                        "PayorID":"610442","IQ":"ZZ", "Dial":"(213)555-1212", "DME":False},
        "DME-Jur. A"     : {"LongName":"NHIC",                            "PayorID":"16003", "IQ":"ZZ", "Dial":"(860)602-0000", "DME":True},
        "DME-Jur. B"     : {"LongName":"National Government Services",    "PayorID":"17003", "IQ":"ZZ", "Dial":"(860)602-0000", "DME":True},
        "DME-Jur. C"     : {"LongName":"Cigna Government Services",       "PayorID":"18003", "IQ":"ZZ", "Dial":"(860)602-0000", "DME":True},
        "DME-Jur. D (CA)": {"LongName":"Noridian Administrative Services","PayorID":"19003", "IQ":"ZZ", "Dial":"(860)602-0000", "DME":True},
        "CO-PartB"       : {"LongName":"TRAILBLAZER HEALTH ENTERPRISES",  "PayorID":"04102", "IQ":"27", "Dial":"(213)555-1212", "DME":False},
        "CO-Medicaid"    : {"LongName":"CO Medicaid",                     "PayorID":"77016", "IQ":"ZZ", "Dial":"(213)555-1212", "DME":False},}

    def __init__(self):
        pass


