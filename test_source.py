from source_reader import fetch_source_text

url = input("Enter a public webpage URL: ").strip()

text, error = fetch_source_text(url)

if error:
    print("Could not read source:", error)
else:
    print("\nSource text retrieved successfully:\n")
    print(text[:1000])