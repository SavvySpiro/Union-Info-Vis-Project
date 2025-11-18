from pdf2image import convert_from_path

# splits pdf into images (~33) and saves to the assets folder. may require poppler, see requirements.txt
pages = convert_from_path('data/Final-package-offer.pdf', dpi=200)
for i, page in enumerate(pages):
    print(f"saving page {i+1}")
    page.save(f"assets/page_{i+1}.png", "PNG")
