from scrap_sentinel import get_data

polygon_coords = [
    [16.249166, 52.656369],
    [16.242085, 52.650071],
    [16.260538, 52.643198],
    [16.272211, 52.651242],
    [16.2641, 52.658243],
    [16.249166, 52.656369],
]

time_interval = ("2021-01-01", "2021-12-31")

resolution = 10
indicators = [
    {
        # Tells us if area is dry or wet
        "name": "Moisture Index",
        "qname": "Normalized Difference Moisture Index (NDMI)",
        "evalscript": """

            //VERSION=3
            const moistureRamps = [
            [-0.8, 0x800000],
            [-0.24, 0xff0000],
            [-0.032, 0xffff00],
            [0.032, 0x00ffff],
            [0.24, 0x0000ff],
            [0.8, 0x000080],
            ];

            const viz = new ColorRampVisualizer(moistureRamps);

            function setup() {
            return {
                input: ["B03", "B04", "B8A", "B11", "dataMask"],
                output: [
                { id: "default", bands: 4 },
                { id: "index", bands: 1, sampleType: "FLOAT32" },
                { id: "eobrowserStats", bands: 2, sampleType: "FLOAT32" },
                { id: "dataMask", bands: 1 },
                ],
            };
            }

            function evaluatePixel(samples) {
            let val = index(samples.B8A, samples.B11);
            // The library for tiffs works well only if there is only one channel returned.
            // So we encode the "no data" as NaN here and ignore NaNs on frontend.
            const indexVal = samples.dataMask === 1 ? val : NaN;
            return {
                default: [...viz.process(val), samples.dataMask],
                index: [indexVal],
                eobrowserStats: [val, isCloud(samples) ? 1 : 0],
                dataMask: [samples.dataMask],
            };
            }

            function isCloud(samples) {
            const NGDR = index(samples.B03, samples.B04);
            const bRatio = (samples.B03 - 0.175) / (0.39 - 0.175);
            return bRatio > 1 || (bRatio > 0 && NGDR > 0);
            }
        """,
    },
    {
        # Tells us if vegetation is healthy or not
        "name": "EVI Index",
        "qname": "Enhanced Vegetation Index (EVI)",
        "evalscript": """

            //VERSION=3
            // Enhanced Vegetation Index  (abbrv. EVI)
            // General formula: 2.5 * (NIR - RED) / ((NIR + 6*RED - 7.5*BLUE) + 1)
            // URL https://www.indexdatabase.de/db/si-single.php?sensor_id=96&rsindex_id=16

            function setup() {
            return {
                input: ["B02", "B03", "B04", "B08", "dataMask"],
                output: [
                { id: "default", bands: 4 },
                { id: "index", bands: 1, sampleType: "FLOAT32" },
                { id: "eobrowserStats", bands: 2, sampleType: "FLOAT32" },
                { id: "dataMask", bands: 1 },
                ],
            };
            }

            function evaluatePixel(samples) {
            let EVI =
                (2.5 * (samples.B08 - samples.B04)) /
                (samples.B08 + 6.0 * samples.B04 - 7.5 * samples.B02 + 1.0);
            let imgVals = null;
            // The library for tiffs works well only if there is only one channel returned.
            // So we encode the "no data" as NaN here and ignore NaNs on frontend.
            // We limit the index value to [-1 , 1] as the EVI mostly falls in that range
            const indexVal = samples.dataMask === 1 && EVI >= -1 && EVI <= 1 ? EVI : NaN;

            if (EVI < -1.1) imgVals = [0, 0, 0, samples.dataMask];
            else if (EVI < -0.2) imgVals = [0.75, 0.75, 1, samples.dataMask];
            else if (EVI < -0.1) imgVals = [0.86, 0.86, 0.86, samples.dataMask];
            else if (EVI < 0) imgVals = [1, 1, 0.88, samples.dataMask];
            else if (EVI < 0.025) imgVals = [1, 0.98, 0.8, samples.dataMask];
            else if (EVI < 0.05) imgVals = [0.93, 0.91, 0.71, samples.dataMask];
            else if (EVI < 0.075) imgVals = [0.87, 0.85, 0.61, samples.dataMask];
            else if (EVI < 0.1) imgVals = [0.8, 0.78, 0.51, samples.dataMask];
            else if (EVI < 0.125) imgVals = [0.74, 0.72, 0.42, samples.dataMask];
            else if (EVI < 0.15) imgVals = [0.69, 0.76, 0.38, samples.dataMask];
            else if (EVI < 0.175) imgVals = [0.64, 0.8, 0.35, samples.dataMask];
            else if (EVI < 0.2) imgVals = [0.57, 0.75, 0.32, samples.dataMask];
            else if (EVI < 0.25) imgVals = [0.5, 0.7, 0.28, samples.dataMask];
            else if (EVI < 0.3) imgVals = [0.44, 0.64, 0.25, samples.dataMask];
            else if (EVI < 0.35) imgVals = [0.38, 0.59, 0.21, samples.dataMask];
            else if (EVI < 0.4) imgVals = [0.31, 0.54, 0.18, samples.dataMask];
            else if (EVI < 0.45) imgVals = [0.25, 0.49, 0.14, samples.dataMask];
            else if (EVI < 0.5) imgVals = [0.19, 0.43, 0.11, samples.dataMask];
            else if (EVI < 0.55) imgVals = [0.13, 0.38, 0.07, samples.dataMask];
            else if (EVI < 0.6) imgVals = [0.06, 0.33, 0.04, samples.dataMask];
            else imgVals = [0, 0.27, 0, samples.dataMask];

            return {
                default: imgVals,
                index: [indexVal],
                eobrowserStats: [EVI, isCloud(samples) ? 1 : 0],
                dataMask: [samples.dataMask],
            };
            }

            function isCloud(samples) {
            const NGDR = index(samples.B03, samples.B04);
            const bRatio = (samples.B03 - 0.175) / (0.39 - 0.175);
            return bRatio > 1 || (bRatio > 0 && NGDR > 0);
            }
        """,
    },
    {
        # Tells us if vegetation is present or not
        "name": "NDVI Index",
        "qname": "Normalized Difference Vegetation Index (NDVI)",
        "evalscript": """
            //VERSION=3
            function setup() {
            return {
                input: ["B04", "B08", "SCL", "dataMask"],
                output: [
                { id: "default", bands: 4 },
                { id: "index", bands: 1, sampleType: "FLOAT32" },
                { id: "eobrowserStats", bands: 2, sampleType: "FLOAT32" },
                { id: "dataMask", bands: 1 },
                ],
            };
            }

            function evaluatePixel(samples) {
            let val = index(samples.B08, samples.B04);
            let imgVals = null;
            // The library for tiffs works well only if there is only one channel returned.
            // So we encode the "no data" as NaN here and ignore NaNs on frontend.
            const indexVal = samples.dataMask === 1 ? val : NaN;

            if (val < -0.5) imgVals = [0.05, 0.05, 0.05, samples.dataMask];
            else if (val < -0.2) imgVals = [0.75, 0.75, 0.75, samples.dataMask];
            else if (val < -0.1) imgVals = [0.86, 0.86, 0.86, samples.dataMask];
            else if (val < 0) imgVals = [0.92, 0.92, 0.92, samples.dataMask];
            else if (val < 0.025) imgVals = [1, 0.98, 0.8, samples.dataMask];
            else if (val < 0.05) imgVals = [0.93, 0.91, 0.71, samples.dataMask];
            else if (val < 0.075) imgVals = [0.87, 0.85, 0.61, samples.dataMask];
            else if (val < 0.1) imgVals = [0.8, 0.78, 0.51, samples.dataMask];
            else if (val < 0.125) imgVals = [0.74, 0.72, 0.42, samples.dataMask];
            else if (val < 0.15) imgVals = [0.69, 0.76, 0.38, samples.dataMask];
            else if (val < 0.175) imgVals = [0.64, 0.8, 0.35, samples.dataMask];
            else if (val < 0.2) imgVals = [0.57, 0.75, 0.32, samples.dataMask];
            else if (val < 0.25) imgVals = [0.5, 0.7, 0.28, samples.dataMask];
            else if (val < 0.3) imgVals = [0.44, 0.64, 0.25, samples.dataMask];
            else if (val < 0.35) imgVals = [0.38, 0.59, 0.21, samples.dataMask];
            else if (val < 0.4) imgVals = [0.31, 0.54, 0.18, samples.dataMask];
            else if (val < 0.45) imgVals = [0.25, 0.49, 0.14, samples.dataMask];
            else if (val < 0.5) imgVals = [0.19, 0.43, 0.11, samples.dataMask];
            else if (val < 0.55) imgVals = [0.13, 0.38, 0.07, samples.dataMask];
            else if (val < 0.6) imgVals = [0.06, 0.33, 0.04, samples.dataMask];
            else imgVals = [0, 0.27, 0, samples.dataMask];

            return {
                default: imgVals,
                index: [indexVal],
                eobrowserStats: [val, isCloud(samples.SCL) ? 1 : 0],
                dataMask: [samples.dataMask],
            };
            }

            function isCloud(scl) {
            if (scl == 3) {
                // SC_CLOUD_SHADOW
                return false;
            } else if (scl == 9) {
                // SC_CLOUD_HIGH_PROBA
                return true;
            } else if (scl == 8) {
                // SC_CLOUD_MEDIUM_PROBA
                return true;
            } else if (scl == 7) {
                // SC_CLOUD_LOW_PROBA
                return false;
            } else if (scl == 10) {
                // SC_THIN_CIRRUS
                return true;
            } else if (scl == 11) {
                // SC_SNOW_ICE
                return false;
            } else if (scl == 1) {
                // SC_SATURATED_DEFECTIVE
                return false;
            } else if (scl == 2) {
                // SC_DARK_FEATURE_SHADOW
                return false;
            }
            return false;
            }

        """,
    },
    {
        # Tells us if area is dry and needs water
        "name": "Moisture Stress",
        "qname": "NDMI for Moisture Stress",
        "evalscript": """
            //VERSION=3
            // Normalized Difference Moisture Stress Index (abbrv. Stress NDMI)
            // General formula: (820nm - 1600nm) / (820nm + 1600nm)
            // URL https://www.indexdatabase.de/db/si-single.php?sensor_id=96&rsindex_id=56

            function setup() {
            return {
                input: ["B03", "B04", "B08", "B11", "dataMask"],
                output: [
                { id: "default", bands: 4 },
                { id: "index", bands: 1, sampleType: "FLOAT32" },
                { id: "eobrowserStats", bands: 2, sampleType: "FLOAT32" },
                { id: "dataMask", bands: 1 },
                ],
            };
            }

            function evaluatePixel(samples) {
            let val = (samples.B08 - samples.B11) / (samples.B08 + samples.B11);
            let imgVals = null;
            // The library for tiffs works well only if there is only one channel returned.
            // So we encode the "no data" as NaN here and ignore NaNs on frontend.
            const indexVal = samples.dataMask === 1 ? val : NaN;

            if (val <= 0) imgVals = [1, 1, 1, samples.dataMask];
            else if (val <= 0.2) imgVals = [0, 0.8, 0.9, samples.dataMask];
            else if (val <= 0.4) imgVals = [0, 0.5, 0.9, samples.dataMask];
            else imgVals = [0, 0, 0.7, samples.dataMask];

            return {
                default: imgVals,
                index: [indexVal],
                eobrowserStats: [val, isCloud(samples) ? 1 : 0],
                dataMask: [samples.dataMask],
            };
            }

            function isCloud(samples) {
            const NGDR = index(samples.B03, samples.B04);
            const bRatio = (samples.B03 - 0.175) / (0.39 - 0.175);
            return bRatio > 1 || (bRatio > 0 && NGDR > 0);
            }

        """,
    },
]

for indicator in indicators:
    indicator_name = indicator["name"]
    indicator_qname = indicator["qname"]
    evalscript = indicator["evalscript"]
    get_data(polygon_coords, time_interval, resolution, evalscript)
