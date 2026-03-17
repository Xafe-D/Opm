from symbolic_engine import process

tests = [
("2(x+1)^2", "Binomial Expansion, Distributive Property"),
]

for i, (expr, expected) in enumerate(tests, 1):
    print("TEST", i)
    print("Input Expression:", expr)
    print("Expected Rules:", expected)

    result = process(expr)

    if result["status"] == "success":
        print("ENGINE OUTPUT:")
        print(result["formatted_trail"])
    else:
        print("ERROR:", result.get("error_message"))