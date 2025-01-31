import streamlit as st
import fitz  # PyMuPDF for PDF extraction
from Working_Parser import IndianAddressExtractor

def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file using PyMuPDF (fitz)."""
    try:
        with fitz.open(stream=pdf_file.getvalue(), filetype="pdf") as doc:
            text = "\n".join([page.get_text("text") for page in doc])
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

# Initialize address extractor
extractor = IndianAddressExtractor()

def extract_addresses(text):
    """Extracts addresses from text using IndianAddressExtractor."""
    try:
        addresses = extractor.extract_addresses(text)
        return addresses  # Return full AddressMatch objects
    except Exception as e:
        st.error(f"Error extracting addresses: {e}")
        return []

# Streamlit UI
st.set_page_config(page_title="Indian Address Parser", layout="wide")
st.title("📍 Indian Address Parser")
st.write("Extract Indian addresses from PDFs or entered text easily!")

# Overview section
st.write("### Overview")
st.markdown(
    """
    The **Indian Address Parser** is an advanced **Natural Language Processing (NLP)** tool that extracts structured address information from unstructured text or complex PDF documents. 
    It leverages **spaCy**, **Regex-based pattern matching**, and **custom entity recognition** to identify addresses efficiently. 
    
    ### Features:
    - 📄 Extracts addresses from PDFs and raw text
    - 🔍 Uses **NLP & Named Entity Recognition (NER)** for accurate parsing
    - 🗺️ Identifies **cities, states, PIN codes, and localities**
    - 🚀 Fast and optimized for large-scale documents
    
    This project showcases my **expertise in NLP, Machine Learning, and Data Extraction**—ideal for applications in **logistics, e-commerce, and business intelligence**.
    """
)



uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
manual_text = st.text_area("Or paste text manually:")

# Process uploaded PDF file
if uploaded_file:
    with st.spinner("Extracting addresses from PDF..."):
        extracted_text = extract_text_from_pdf(uploaded_file)
        if extracted_text.strip():
            addresses = extract_addresses(extracted_text)
        else:
            addresses = []

    if addresses:
        st.success(f"✅ Extracted {len(addresses)} addresses successfully!")
        st.write("### Extracted Addresses")

        for idx, addr in enumerate(addresses, 1):
            st.markdown(
                f"""
                **{idx}. Formatted Address:**
                ``` 
                {extractor.format_address(addr)}
                ```
                **Confidence Score:** {addr.confidence_score:.2f}
                **Region:** {addr.region}
                **Components:**
                ``` 
                {addr.components}
                ```
                ---
                """
            )

        formatted_addresses = [extractor.format_address(addr) for addr in addresses]
        st.download_button("📥 Download Addresses", data="\n".join(formatted_addresses), file_name="addresses.txt")
    else:
        st.warning("⚠️ No valid Indian addresses found.")

# Process pasted text with a submit button
if manual_text:
    submit_button = st.button("Submit")
    if submit_button:
        with st.spinner("Extracting addresses from text..."):
            extracted_text = manual_text
            if extracted_text.strip():
                addresses = extract_addresses(extracted_text)
            else:
                addresses = []

        if addresses:
            st.success(f"✅ Extracted {len(addresses)} addresses successfully!")
            st.write("### Extracted Addresses")

            for idx, addr in enumerate(addresses, 1):
                st.markdown(
                    f"""
                    **{idx}. Formatted Address:**
                    ``` 
                    {extractor.format_address(addr)}
                    ```
                    **Confidence Score:** {addr.confidence_score:.2f}
                    **Region:** {addr.region}
                    **Components:**
                    ``` 
                    {addr.components}
                    ```
                    ---
                    """
                )

            formatted_addresses = [extractor.format_address(addr) for addr in addresses]
            st.download_button("📥 Download Addresses", data="\n".join(formatted_addresses), file_name="addresses.txt")
        else:
            st.warning("⚠️ No valid Indian addresses found.")

# Added "Work In Progress" section
st.write("### Work In Progress")
st.markdown(
    """
    🚧 **Version 2 is coming soon!** 🚧

    I'm currently working on improving the address extraction accuracy and adding support for additional document formats, more robust NLP models, and customizations. Stay tuned for the next version of the **Indian Address Parser** with enhanced features and faster processing!

    Your feedback and suggestions are always welcome!
    """
)

# Contact information
st.write("### Contact")
st.write("For any queries, feel free to connect with me on [LinkedIn](https://www.linkedin.com/in/aditya-gupta-062478250/)")
