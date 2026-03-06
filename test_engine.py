from symbolic_engine import process

test_cases = [
    "x^3 - x",
    "x^2 + 2*x + 1",
    "(x^2 - 4)/(x - 2)",
    "sin(x)^2 + cos(x)^2",
    "log(x*y)",
    "exp(x)*exp(x)",
    "sin(x) + x^2",
    "3x+5x-2x",  # implicit multiplication test
    "(2x+4)/2",  # rational simplification
    "2*(x+3)",   # distributive
    "2 * (x+3)",  # spaced multiplication
    "2*( x+3)",   # spaced after *
    "((x+2)^2 - 4)/(x+2 - 2)",  # rational example used in debugging
    "(x+1)^2"    # binomial expansion
]

# invalid inputs for week‑2 validation testing
invalid_cases = [
    "",              # empty string should be rejected
    "2**",          # syntax error (trailing operator)
    "x + @",        # illegal character '@'
    "(x+1"          # unbalanced parenthesis
]

print("\n=== RUNNING SYMBOLIC ENGINE TEST SUITE ===\n")

for i, expr in enumerate(test_cases, 1):
    print(f"\n--- Test {i}: {expr} ---\n")
    
    result = process(expr)

    if result["status"] == "success":
        print(result["formatted_trail"])
    else:
        print("ERROR:", result.get("error_message"))

# now run invalid-input validation checks
print("\n=== RUNNING INVALID INPUT TESTS ===\n")
for j, expr in enumerate(invalid_cases, 1):
    print(f"\n--- Invalid Test {j}: '{expr}' ---\n")
    result = process(expr)
    # we expect a failure status; log response for documentation
    if result["status"] == "success":
        print("Unexpected success — validation did not catch bad input")
        print(result["formatted_trail"])
    else:
        print("Validation output:")
        print(result.get("formatted_trail"))
        print(f"Error message: {result.get('error_message')}")

print("\n=== TESTING COMPLETE ===")
