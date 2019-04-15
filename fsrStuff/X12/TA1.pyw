X12 TA1 Acknowledgment

The X12 TA1 technical acknowledgment reports the status of the processing of an interchange header and trailer by the address receiver. When the ISA and IEA of the X12-encoded message are valid, a positive TA1 ACK is sent, whatever the status of the other content is. If not, TA1 ACK with an error code is sent.

The X12 TA1 acknowledgment conforms to the X12_<version number>_TA1.xsd schema. The TA1 ACK is sent inside an ISA/IEA envelope. The ISA and IEA are no different than any other interchange.

The segments within the interchange of a TA1 ACK are shown in the following table.
Field # 	Name of Field 	            Mapped to Incoming Interchange 	        Value

TA101       Interchange control number  ISA13 - Interchange control number      -
TA102       Interchange Date            ISA09 - Interchange Date                -
TA103       Interchange Time            ISA10 – Interchange Time                -
TA104       Interchange ACK Code*       N/A                                     {"A":"Accept",
                                                                                 "E":"Interchange accepted with errors",
                                                                                 "R":"Interchange rejected/suspended"}
TA105       Interchange Note Code       N/A                                     Processing result error code.

{"000":"Success",
 "001":"The Interchange Control Numbers in the header ISA 13 and trailer IEA02 do not match",
 "002":"Standard in ISA11 (Control Standards) is not supported",
 "003":"Version of the controls is not supported",
 "004":"Segment Terminator is Invalid2",
 "005":"Invalid Interchange ID Qualifier for Sender",
 "006":"Invalid Interchange Sender ID",
 "007":"Invalid Interchange ID Qualifier for Receiver",
 "008":"Invalid Interchange Receiver ID",
 "009":"Unknown Interchange Receiver ID",
 "010":"Invalid Authorization Information Qualifier value",
 "011":"Invalid Authorization Information value",
 "012":"Invalid Security Information Qualifier value",
 "013":"Invalid Security Information value",
 "014":"Invalid Interchange Date value",
 "015":"Invalid Interchange Time value",
 "016":"Invalid Interchange Standards Identifier value",
 "017":"Invalid Interchange Version ID value",
 "018":"Invalid Interchange Control Number value",
 "019":"Invalid Acknowledgment Requested value",
 "020":"Invalid Test Indicator value",
 "021":"Invalid Number of Included Groups value",
 "022":"Invalid Control Structure",
 "023":"Improper (Premature) End-of-File (Transmission)",
 "024":"Invalid Interchange Content (e.g., Invalid GS segment)",
 "025":"Duplicate Interchange Control Number",
 "026":"Invalid Data Element Separator",
 "027":"Invalid Component Element Separator"}
