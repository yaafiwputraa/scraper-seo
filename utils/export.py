from io import BytesIO

import pandas as pd


def df_to_excel(df: pd.DataFrame, sheet_name: str = "Sheet1") -> bytes:
    """
    Konversi DataFrame ke bytes Excel (.xlsx).

    Args:
        df: DataFrame yang akan diekspor.
        sheet_name: Nama sheet pada file Excel.

    Returns:
        Bytes dari file Excel.
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()


def build_filename(prefix: str, keywords: list[str], ext: str = "xlsx") -> str:
    """
    Buat nama file dari prefix dan list keyword.

    Args:
        prefix: Awalan nama file (misal 'paa', 'youtube').
        keywords: List keyword yang digunakan.
        ext: Ekstensi file (default 'xlsx').

    Returns:
        String nama file.
    """
    base = "_".join(keywords) if keywords else "hasil"
    if prefix:
        return f"{prefix}_{base}.{ext}"
    return f"{base}.{ext}"
