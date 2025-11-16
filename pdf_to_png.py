from pdf2image import convert_from_path

pages = convert_from_path("assets/Final-package-offer.pdf", dpi=200)
for i, page in enumerate(pages):
    page.save(f"assets/page_{i+1}.png", "PNG")
