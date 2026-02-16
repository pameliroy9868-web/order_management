import pandas as pd

def read_csv_safely(file):

    try:
        df = pd.read_csv(file, engine="python")

    except:
        try:
            df = pd.read_csv(file, sep=";", engine="python")

        except:
            df = pd.read_csv(file, sep="\t", engine="python")

    return df

def read_meesho_returns_csv(uploaded_file):

    # Read file content from Streamlit UploadedFile
    lines = uploaded_file.getvalue().decode("utf-8").splitlines()

    header_index = None

    for i, line in enumerate(lines):
        if '"S No"' in line:
            header_index = i
            break

    if header_index is None:
        raise Exception("Could not find CSV header")

    # Now read CSV using pandas from memory
    df = pd.read_csv(
        uploaded_file,
        skiprows=header_index,
        engine="python"
    )

    return df