def format_thesis_collection_code(collection_code):
    if collection_code in ("uqam", "uqac", "uqtr", "uqat", "uqar", "enap"):
        return collection_code.upper()
    elif collection_code == "laval":
        return "Laval"
    elif collection_code == "udem":
        return "UdeM"
    elif collection_code == "mcgill":
        return "McGill"
