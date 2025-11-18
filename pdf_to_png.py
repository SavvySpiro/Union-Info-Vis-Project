from pdf2image import convert_from_path

pages = convert_from_path('data/Final-package-offer.pdf', dpi=200)
for i, page in enumerate(pages):
    print(f"saving page {i+1}")
    page.save(f"assets/page_{i+1}.png", "PNG")
