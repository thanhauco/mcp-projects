
from common.mcp_core.server import app as base_app
from common.mcp_core.tools import tool
import pandas as pd
from sdv.metadata import SingleTableMetadata
from sdv.single_table import CTGANSynthesizer

app = base_app

@tool("generate_synthetic")
def generate_synthetic(schema: dict, rows: int = 100):
    # schema: {"columns": {"name":"string","age":"int","amount":"float"}}
    cols = list(schema["columns"].keys())
    # Create a tiny seed dataframe with inferred dtypes
    sample = {}
    for c, t in schema["columns"].items():
        if t == "int":
            sample[c] = [1, 2, 3]
        elif t == "float":
            sample[c] = [1.0, 2.5, 3.1]
        else:
            sample[c] = ["a","b","c"]
    df = pd.DataFrame(sample)

    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(df)
    synth = CTGANSynthesizer(metadata)
    synth.fit(df)
    out = synth.sample(num_rows=rows)
    return {"rows": len(out), "preview": out.head(10).to_dict(orient="records")}

@app.get("/health")
def health():
    return {"status":"ok","tools":["generate_synthetic"]}
