import xml.etree.ElementTree as ET
from xml.dom import minidom

import borfile

# Register necessary namespaces
namespaces = {
    "": "http://diggsml.org/schemas/2.6",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "xlink": "http://www.w3.org/1999/xlink",
    "gml": "http://www.opengis.net/gml/3.2",
    "g3.3": "http://www.opengis.net/gml/3.3/ce",
    "glr": "http://www.opengis.net/gml/3.3/lr",
    "glrov": "http://www.opengis.net/gml/3.3/lrov",
    "diggs_geo": "http://diggsml.org/schemas/2.6/geotechnical",
    "witsml": "http://www.witsml.org/schemas/131",
    "diggs": "http://diggsml.org/schemas/2.6",
}


def convert_to_diggs(file_path):
    bf = borfile.read(file_path)

    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)

    root = ET.Element(
        "Diggs",
        {
            "xmlns": "http://diggsml.org/schemas/2.6",
            "xmlns:diggs": "http://diggsml.org/schemas/2.6",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xmlns:xlink": "http://www.w3.org/1999/xlink",
            "xmlns:gml": "http://www.opengis.net/gml/3.2",
            "xmlns:g3.3": "http://www.opengis.net/gml/3.3/ce",
            "xmlns:glr": "http://www.opengis.net/gml/3.3/lr",
            "xmlns:glrov": "http://www.opengis.net/gml/3.3/lrov",
            "xmlns:diggs_geo": "http://diggsml.org/schemas/2.6/geotechnical",
            "xmlns:witsml": "http://www.witsml.org/schemas/131",
            "xsi:schemaLocation": "http://diggsml.org/schemas/2.6 https://diggsml.org/schema-dev/Diggs.xsd",
            "gml:id": "bor2diggs",
        },
    )

    # Add document information
    doc_info_element = ET.SubElement(
        ET.SubElement(root, "documentInformation"),
        "DocumentInformation",
        {"gml:id": f"di_{bf.description['filename']}"},
    )
    ET.SubElement(doc_info_element, "creationDate").text = bf.description["creation"]

    # Add source software information
    software_application_element = ET.SubElement(
        ET.SubElement(root, "sourceSoftware"),
        "SoftwareApplication",
        {"gml:id": "bor2diggs"},
    )
    ET.SubElement(software_application_element, "gml:name").text = "bor2diggs"
    ET.SubElement(software_application_element, "version").text = "beta"

    # Add project information
    project_element = ET.SubElement(
        ET.SubElement(root, "project"),
        "Project",
        {"gml:id": f"pr_{bf.description['project_ref']}"},
    )
    ET.SubElement(project_element, "gml:name").text = bf.description["project_ref"]

    # # Add sampling feature (borehole)
    borehole = ET.SubElement(
        ET.SubElement(root, "samplingFeature"),
        "Borehole",
        {"gml:id": f"id_{bf.description['borehole_ref']}"},
    )
    ET.SubElement(borehole, "gml:name").text = bf.description["borehole_ref"]
    ET.SubElement(borehole, "investigationTarget").text = "Natural Ground"
    ET.SubElement(
        borehole, "projectRef", {"xlink:href": f"pr_{bf.description['project_ref']}"}
    )

    # Convert coordinate strings to floats and format them
    try:
        latitude = float(bf.description["position"]["latitude"]["value"])
        longitude = float(bf.description["position"]["longitude"]["value"])
        altitude = float(bf.description["position"]["altitude"]["value"])

        # Format coordinates to 6 decimal places
        coord_string = f"{latitude:.6f} {longitude:.6f} {altitude:.2f}"
        pos_altitude = altitude - bf.data.DEPTH.iat[-1]
        pos_string = f"{coord_string} {latitude:.6f} {longitude:.6f} {pos_altitude:.2f}"
    except ValueError:
        # If conversion fails, use a default or log an error
        print("Warning: Invalid coordinate data in header. Using default values.")
        coord_string = "0.000000 0.000000 0.00"
        pos_string = "{coord_string} {coord_string}"

    # add reference point
    ET.SubElement(
        ET.SubElement(
            ET.SubElement(borehole, "referencePoint"),
            "PointLocation",
            {"gml:id": f"pl_bh_{bf.description['borehole_ref']}"},
        ),
        "gml:pos",
        {
            "srsDimension": "3",
            "uomLabels": "dega dega m",
            "axisLabels": "latitude longitude height",
        },
    ).text = coord_string

    # add center line
    ET.SubElement(
        ET.SubElement(
            ET.SubElement(borehole, "centerLine"),
            "LinearExtent",
            {"gml:id": f"cl_bh_{bf.description['borehole_ref']}"},
        ),
        "gml:posList",
        {
            "srsDimension": "3",
            "uomLabels": "dega dega m",
            "axisLabels": "latitude longitude height",
        },
    ).text = pos_string

    # add linear referencing
    lsrs = ET.SubElement(
        ET.SubElement(borehole, "linearReferencing"),
        "LinearSpatialReferenceSystem",
        {"gml:id": f"lr_bh_{bf.description['borehole_ref']}"},
    )

    ET.SubElement(
        lsrs, "gml:identifier", {"codeSpace": "DIGGS"}
    ).text = f"urn:x-diggs:def:fi:DIGGSINC:lr_bh_{bf.description['borehole_ref']}"

    ET.SubElement(
        lsrs,
        "glr:linearElement",
        {"xlink:href": f"#cl_bh_{bf.description['borehole_ref']}"},
    )

    lrm_method = ET.SubElement(
        ET.SubElement(lsrs, "glr:lrm"),
        "glr:LinearReferencingMethod",
        {"gml:id": f"lrm_bh_{bf.description['borehole_ref']}"},
    )
    ET.SubElement(lrm_method, "glr:name").text = "chainage"
    ET.SubElement(lrm_method, "glr:type").text = "absolute"
    ET.SubElement(lrm_method, "glr:units").text = "m"

    # add totalMeasuredDepth
    ET.SubElement(
        borehole,
        "totalMeasuredDepth",
        {"uom": "ft"},
    ).text = f"{bf.data.DEPTH.iat[-1]:g}"

    # add construction method
    construction_method = ET.SubElement(borehole, "constructionMethod")
    method_element = ET.SubElement(
        construction_method,
        "BoreholeConstructionMethod",
        {"gml:id": f"cm_bh_{bf.description['borehole_ref']}"},
    )
    ET.SubElement(method_element, "gml:name").text = borfile.codes.DRILLING_METHOD[
        bf.description["drilling"]["method"]
    ]

    # Add location element
    location = ET.SubElement(method_element, "location")
    linear_extent = ET.SubElement(
        location,
        "LinearExtent",
        {"gml:id": f"le_cm_bh_{bf.description['borehole_ref']}"},
    )

    ET.SubElement(
        linear_extent,
        "gml:posList",
        {"srsName": f"#lr_bh_{bf.description['borehole_ref']}", "srsDimension": "1"},
    ).text = f"{bf.data.DEPTH.iat[0]:g} {bf.data.DEPTH.iat[-1]:g}"

    # Add DrillRig
    if bf.description["drilling"].get("machine_ref"):
        ET.SubElement(
            ET.SubElement(method_element, "constructionEquipment"),
            "DrillRig",
            {"gml:id": bf.description["drilling"]["machine_ref"]},
        )

    # Add CuttingTool
    if bf.description["drilling"].get("tool"):
        cuttingtool_el = ET.SubElement(
            ET.SubElement(method_element, "cuttingToolInfo"), "CuttingTool"
        )
        ET.SubElement(
            cuttingtool_el,
            "gml:name",
        ).text = borfile.codes.DRILLING_TOOL[bf.description["drilling"]["tool"]]
        if bf.description["drilling"].get("tool_diameter"):
            ET.SubElement(
                cuttingtool_el,
                "toolOuterDiameter",
                {"uom": bf.description["drilling"]["tool_diameter"]["@unit"]},
            ).text = bf.description["drilling"]["tool_diameter"]["value"]

    # add measurement
    measurement = ET.SubElement(root, "measurement")
    mwd = ET.SubElement(
        measurement,
        "MeasurementWhileDrilling",
        {"gml:id": f"mwd_{bf.description['filename']}"},
    )
    ET.SubElement(mwd, "gml:name").text = f"MWD_{bf.description['filename']}"
    ET.SubElement(mwd, "investigationTarget").text = "Natural Ground"
    ET.SubElement(
        mwd, "projectRef", {"xlink:href": f"#pr_{bf.description['project_ref']}"}
    )
    ET.SubElement(
        mwd,
        "samplingFeatureRef",
        {"xlink:href": f"#bh_{bf.description['borehole_ref']}"},
    )

    # add mwd result
    outcome = ET.SubElement(mwd, "outcome")
    result = ET.SubElement(
        outcome, "MWDResult", {"gml:id": f"mwdr_{bf.description['filename']}"}
    )

    # add time domain
    time_domain = ET.SubElement(result, "timeDomain")
    time_position_list = ET.SubElement(
        time_domain,
        "TimePositionList",
        {"gml:id": f"tpl_{bf.description['filename']}", "unit": "second"},
    )
    positions = ET.SubElement(time_position_list, "timePositionList")
    # Join all timestamps with a space and wrap every 5 timestamps
    timestamps = list(f"{t:g}" for t in bf.data.index.array)
    wrapped_timestamps = (
        [" "]
        + [" ".join(timestamps[i : i + 5]) for i in range(0, len(timestamps), 5)]
        + [""]
    )
    positions.text = "\n                ".join(wrapped_timestamps)

    # add result set
    results = ET.SubElement(result, "results")
    result_set = ET.SubElement(results, "ResultSet")

    parameters = ET.SubElement(result_set, "parameters")
    property_params = ET.SubElement(
        parameters, "PropertyParameters", {"gml:id": "params1"}
    )
    properties = ET.SubElement(property_params, "properties")

    property_classes = {
        "time": "measured_time",
        "DEPTH": "measured_depth",
        "AS": "penetration_rate",
        "RV": "vibration_acceleration",
        "EVR": "event_new_rod",
        "TP": "hydraulic_crowd_pressure",
        "TPAF": "crowd_downward_thrust",
        "TQ": "hydraulic_torque_pressure",
        "TQAT": "torque",
        "HP": "holdback_pressure",
        "SP": "hammering_pressure",
        "IP": "fluid_injection_pressure",
        "IF": "fluid_injection_volume_rate",
        "OF": "fluid_return_volume_rate",
        "RSP": "rotation_shaft",
        "GEAR": "gear_number",
    }

    index = 1
    for name, info in bf.metadata.items():
        unit = info.get("unit", "-")

        property_element = ET.SubElement(
            properties, "Property", {"gml:id": f"prop{index}", "index": str(index)}
        )
        ET.SubElement(property_element, "propertyName").text = name
        ET.SubElement(property_element, "typeData").text = "double"

        property_class = property_classes.get(name, "missing")
        ET.SubElement(
            property_element,
            "propertyClass",
            {"codeSpace": "http://diggsml.org/def/codes/DIGGS/0.1/mwd_properties.xml"},
        ).text = property_class

        if unit != "-":
            ET.SubElement(property_element, "uom").text = unit

        index += 1

    # add data values
    data_values = ET.SubElement(
        result_set, "dataValues", {"cs": ",", "ts": " ", "decimal": "."}
    )
    data_values.text = bf.to_csv(header=False, index=False).strip()

    # Convert the XML to a pretty-printed string
    xml_diggs = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    return xml_diggs
