import streamlit as st
from PyPDF2 import PdfWriter, PdfReader
from PIL import Image
import io, base64


def create_watermark(input_pdf, output, watermark_type, watermark):
    pdf_reader = PdfReader(input_pdf)
    pdf_writer = PdfWriter()

    if watermark_type == 'Image':
        # Open the image
        image = Image.open(watermark).convert("RGBA")
        watermark_page = PdfWriter().add_blank_page(
            image.width, image.height)
        watermark_page.merge_translated_page(
            PdfReader(io.BytesIO()).get_page(0), 0, 0, expand=True)
        watermark_page.merge_page(
            PdfReader(io.BytesIO()).get_page(0))

        # Watermark all the pages
        for page_number in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_number]
            page.merge_page(watermark_page.pages[0])
            pdf_writer.add_page(page)

    elif watermark_type == 'Text':
        # Watermark all the pages with the text
        for page_number in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_number]
            watermark_page = PdfWriter().add_blank_page(
                page.mediabox.getWidth(), page.mediaBox.getHeight())
            watermark_page.merge_page(PdfReader(io.BytesIO()).get_page(0))
            watermark_page.merge_page(page)
            pdf_writer.add_page(watermark_page.pages[0])

            # Add the text watermark
            pdf_writer.add_page(page)

            # Add the watermark text
            watermark_text = watermark
            watermark_text_width = watermark_text.get_size()[0]
            watermark_text_height = watermark_text.get_size()[1]

            watermark_text_page = PdfWriter().add_blank_page(
                watermark_text_width, watermark_text_height)
            watermark_text_page.merge_translated_page(
                PdfReader(io.BytesIO()).get_page(0), 0, 0, expand=True)
            watermark_text_page.merge_page(
                PdfReader(io.BytesIO()).get_page(0))

            watermark_text_page.merge_translated_page(
                PdfReader(io.BytesIO()).get_page(0),
                (page.mediaBox.Width() - watermark_text_width) / 2,
                (page.mediaBox.Height() - watermark_text_height) / 2,
                expand=True)
            watermark_page.merge_page(watermark_text_page.pages[0])
            pdf_writer.add_page(watermark_page.pages[0])

    with open(output, 'wb') as out:
        pdf_writer.write(out)


def main():
    st.title("PDF Watermarking App")

    # File Upload
    st.subheader("Upload PDF")
    input_pdf = st.file_uploader("Upload the PDF file", type=["pdf"])

    st.subheader("Watermark Type")
    watermark_type = st.radio("Select Watermark Type", ("Image", "Text"))

    if watermark_type == "Image":
        st.subheader("Upload Watermark Image")
        watermark = st.file_uploader("Upload the watermark image", type=["png", "jpg", "jpeg"])
    elif watermark_type == "Text":
        st.subheader("Watermark Text")
        watermark = st.text_input("Enter the watermark text")

    if input_pdf and watermark:
        output_pdf = 'watermarked_notebook.pdf'
        create_watermark(input_pdf, output_pdf, watermark_type, watermark)

        # Download Link
        st.subheader("Download Watermarked PDF")
        st.markdown(get_download_link(output_pdf), unsafe_allow_html=True)


def get_download_link(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode('utf-8')
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_path}">Click here to download</a>'
    return href


if __name__ == '__main__':
    main()

