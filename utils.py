def prettify_print(objects: dict) -> None:
    print(objects.items())

    # for key, value in objects.items():
    #     print("RESULT")
    #     print(f"{key}: {value}")
    #     print("RESULT END")

    # for item in objects:
    # print(item)


def print_hash(num: int, char="#"):
    try:
        print(num * char)
    except ValueError:
        print(f"Invalid")
