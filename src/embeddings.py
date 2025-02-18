# FLOW of this script
    # 1. Extract the Data using Docling
    # 2. Apply hybrid chunking (or any chunking strat based on the use-case)
    # 3. Create a LanceDB database and table (can use any other DB (local/online)
    # 4. Prepare the chunks for the table
    # 5. Load the table (for verification)

from typing import List
import lancedb
from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from dotenv import load_dotenv
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from openai import OpenAI
from src.utils.tokenizer import OpenAITokenizerWrapper
from pdf2image import convert_from_path
import os

# OPENAI API KEY
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")  
client = OpenAI(api_key=openai_api_key)

#TOKENIZATION
tokenizer = OpenAITokenizerWrapper()  
MAX_TOKENS = 8191  


def extract_and_process_pdf(pdf_path: str):

    # --------------------------------------------------------------
    # 1. Extract the Data using Docling
    # --------------------------------------------------------------

    converter = DocumentConverter()
    result = converter.convert(pdf_path)

    print("Extracting data")
    # --------------------------------------------------------------
    # 2. Apply hybrid chunking (or any chunking strat based on the use-case)
    # --------------------------------------------------------------

    chunker = HybridChunker(
        tokenizer=tokenizer,
        max_tokens=MAX_TOKENS,
        merge_peers=True,
    )

    chunk_iter = chunker.chunk(dl_doc=result.document)
    chunks = list(chunk_iter)
    print("Chunking")

    # --------------------------------------------------------------
    # 3. Create a LanceDB database and table (can use any other DB (local/online)
    # --------------------------------------------------------------

    db = lancedb.connect("data/lancedb")
    func = get_registry().get("openai").create(name="text-embedding-3-large")

    class ChunkMetadata(LanceModel):
        filename: str | None
        page_numbers: List[int] | None
        title: str | None

    class Chunks(LanceModel):
        text: str = func.SourceField()
        vector: Vector(func.ndims()) = func.VectorField()  # type: ignore
        metadata: ChunkMetadata

    table = db.create_table("docling", schema=Chunks, mode="overwrite")

    print("LanceDB created")

    # --------------------------------------------------------------
    # 4. Prepare the chunks for the table
    # --------------------------------------------------------------

    processed_chunks = [
        {
            "text": chunk.text,
            "metadata": {
                "filename": chunk.meta.origin.filename,
                "page_numbers": [
                    page_no
                    for page_no in sorted(
                        set(
                            prov.page_no
                            for item in chunk.meta.doc_items
                            for prov in item.prov
                        )
                    )
                ]
                or None,
                "title": chunk.meta.headings[0] if chunk.meta.headings else None,
            },
        }
        for chunk in chunks
    ]


    table.add(processed_chunks)
    print("Table added")

    # --------------------------------------------------------------
    # 5. Load the table (for verification)
    # --------------------------------------------------------------

    table.to_pandas()
    table.count_rows()

    print(table)

