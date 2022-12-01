from easygui import *
import math
import pgeocode

country = pgeocode.Nominatim("gb")


def get_variables():
    PropertyDict = {
        "General Business": "g0",
        "Weekday Business": "g1",
        "Evening Business": "g2",
        "Continuous Business": "g3",
        "Shop / Barber": "g4",
        "Bakery": "g5",
        "Weekend Business": "g6",
        "Mobile Phone Transmitter Station": "g7",
        "General Farm": "l0",
        "Dairy / Livestock Farm": "l1",
        "Other Farm": "l2",
        "Household": "h0",
    }

    while 1:
        message = "How do you want to input property location?"
        title = "EST PV-BDEW tool: Location"
        if boolbox(message, title, ["Postcode", "Coordinates"]):
            postcodemsg = "What is the postcode?"
            title = "EST PV-BDEW tool: Location"
            fieldNames = ["UK postcode"]
            postcode = []  # we start with blanks for the values
            postcode = multenterbox(postcodemsg, title, fieldNames)
            while 1:
                if postcode == None:
                    break
                errmsg = ""
                for i in range(len(fieldNames)):
                    if postcode[i].strip() == "":
                        errmsg = errmsg + (
                            '"%s" is a required field.\n\n' % fieldNames[i]
                        )
                    elif (
                        math.isnan(country.query_postal_code(postcode)["latitude"])
                        == True
                    ):
                        errmsg = errmsg + "Invalid postcode!"

                if errmsg == "":
                    break  # no problems found
                postcode = multenterbox(errmsg, title, fieldNames, postcode)

            postcode_data = country.query_postal_code(postcode)
            coordinates = [
                str(postcode_data["latitude"].values[0]),
                str(postcode_data["longitude"].values[0]),
            ]

        else:
            lonlatmsg = "What are the coordinates?"
            title = "EST PV-BDEW tool: Location"
            fieldNames = ["Latitude", "Longitude"]
            coordinates = []  # we start with blanks for the values
            coordinates = multenterbox(lonlatmsg, title, fieldNames)

            # make sure that none of the fields was left blank
            while 1:
                if coordinates == None:
                    break
                errmsg = ""
                for i in range(len(fieldNames)):
                    if coordinates[i].strip() == "":
                        errmsg = errmsg + (
                            '"%s" is a required field.\n\n' % fieldNames[i]
                        )
                if errmsg == "":
                    break  # no problems found
                coordinates = multenterbox(errmsg, title, fieldNames, coordinates)

        msg = "What is the property type?"
        title = "EST PV-BDEW tool: Property type"
        choices = PropertyDict.keys()
        choice = choicebox(msg, title, choices)
        property_type = PropertyDict[choice]

        powermsg = "What is the demand and the proposed PV install?"
        title = "EST PV-BDEW tool: PV"
        fieldNames = [
            "Annual property demand [kWh]",
            "PV install peak power [kWp]",
            "Surface tilt (default = 35)",
            "Surface azimuth (default = 0)",
        ]
        values = []  # we start with blanks for the values
        values = multenterbox(powermsg, title, fieldNames)
        # make sure that none of the fields was left blank
        while 1:
            if values == None:
                break
            errmsg = ""
            for i in range(len(fieldNames)):
                if values[i].strip() == "":
                    errmsg = errmsg + ('"%s" is a required field.\n\n' % fieldNames[i])
            if errmsg == "":
                break  # no problems found
            values = multenterbox(errmsg, title, fieldNames, values)

        msg = (
            "Property type "
            + PropertyDict[choice]
            + ": "
            + str(choice)
            + "\n\n"
            + "Located at "
            + coordinates[0]
            + " latitude and "
            + coordinates[1]
            + " longitude.\n\n"
            + "With annual demand of "
            + values[0]
            + " kWh and PV generation of "
            + values[1]
            + " kWp.\n\n"
        )

        title = "EST PV-BDEW tool: Summary"
        if ccbox(msg, title):  # show a Continue/Cancel dialog
            return (
                property_type,
                float(coordinates[0]),
                float(coordinates[1]),
                float(values[0]),
                float(values[1]),
                float(values[2]),
                float(values[3]),
            )  # user chose Continue
        else:
            pass  # user chose Cancel
