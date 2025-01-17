from typing import Tuple, Dict, Literal, Callable
import pandas as pd
import os
import json
from decodex.constant import DECODEX_DIR


class SignatureLookUp:
    def __init__(self) -> None:
        pass

    def __call__(self, byte_sign: str) -> Tuple[Dict, str]:
        """
        Search for the signature in the database and return the corresponding abi and text_signature.

        Parameters
        ----------
        byte_sign : str
            The signature in hex string, 0x prefixed.

        Returns
        -------
        Tuple[Dict, str]
            The abi (Dict) and text_signature (str) corresponding to the signature.

        """
        raise NotImplementedError


class CSVSignatureLookUp(SignatureLookUp):
    def __init__(self, uri: str = None, chain: str = "ethereum") -> None:
        super().__init__()
        if uri is None:
            uri = DECODEX_DIR.joinpath(chain, "signatures.csv")
            if not os.path.isfile(uri):
                raise ValueError(f"Signature lookup file {uri} does not exist")
        self.df = pd.read_csv(uri)
        self.__validate__()

    def __validate__(self):
        if self.df.empty:
            raise ValueError("Signature lookup file is empty")

        cols = set(self.df.columns)
        expected_cols = {"byte_sign", "abi", "text_sign"}
        if cols != expected_cols:
            raise ValueError(
                f"Signature lookup file is not valid, expected columns: {', '.join(expected_cols)}"
            )

    def __call__(self, byte_sign: str) -> Tuple[Dict, str]:
        """
        Search for the signature in the database and return the corresponding abi and text_signature.

        Parameters
        ----------
        byte_sign : str
            The signature in hex string, 0x prefixed.

        Returns
        -------
        Tuple[Dict, str]
            The abi (Dict) and text_signature (str) corresponding to the signature.

        """
        rows = self.df[self.df["byte_sign"] == byte_sign]
        if rows.empty:
            return {}, ""
        abi, text_sign = rows.iloc[0]["abi"], rows.iloc[0]["text_sign"]
        return json.loads(abi), text_sign


class SignatureFactory:
    """
    A factory class to instantiate various types of SignatureLookUp classes based on the given format.

    Methods
    -------
    create(fmt: Literal["csv"], uri: str = None) -> SignatureLookUp:
        Creates and returns an instance of a SignatureLookUp subclass based on the specified format.

    Example
    -------
    >>> factory = SignatureFactory()
    >>> csv_lookup = factory.create("csv", uri="path/to/signatures.csv")

    Parameters for static methods
    ------------------------------
    fmt : Literal["csv"]
        The format of the SignatureLookUp to instantiate. Currently, only "csv" is supported.
    uri : str, optional
        The URI where the signature lookup file can be found. Defaults to None, which may use a defaul value in their constructor.
        For example, CSVSignatureLookUp uses "~/.decodex/signatures.csv" as the default value.

    Returns
    -------
    SignatureLookUp
        An instance of the corresponding SignatureLookUp subclass.

    Raises
    ------
    ValueError
        If the given `fmt` is not supported.
    """

    @staticmethod
    def create(
        fmt: Literal["csv"],
        uri: str = None,
        chain: str = "ethereum",
    ) -> SignatureLookUp:
        if fmt == "csv":
            return CSVSignatureLookUp(uri=uri, chain=chain)
        else:
            raise ValueError(f"Signature lookup format {fmt} is not supported")
