from symbolic_engine import process

# =====================================================

# SYMBOLIC ENGINE RULE VALIDATION TEST SUITE

# =====================================================

# Tests rule detection, steps, and summary consistency

# =====================================================

tests = [
("3(x+4)", "Distributive Property"),
("2x + 5x - 3", "Combine Like Terms"),
("(x+2)^2", "Binomial Expansion"),
("(x+1)(x+3)", "Multi-Term Distribution, Combine Like Terms"),
("x^2 - 16", "Special Products"),
("(x^2 - 1)/(x - 1)", "Special Products, Rational Expression Simplification"),
("x^2 * x^3", "Exponent Rules"),
("(x^2)^3", "Exponent Rules"),
("2(x+1)^2", "Binomial Expansion, Distributive Property"),
("x^2 + 5x + 6", "Factorization"),
("(x+1)(x-1)/(x-1)", "Rational Expression Simplification"),
("2(x+1)(x+2) + (x+1)^2", "Binomial Expansion, Multi-Term Distribution, Combine Like Terms"),
("x+1", "Already simplified"),
("5+3", "Combine Like Terms"),
("x-x", "Combine Like Terms"),
]

print("\n======================================")
print("SYMBOLIC ENGINE RULE DETECTION TESTS")
print("======================================\n")

for i, (expr, expected) in enumerate(tests, 1):
    print("\n--------------------------------------")
    print("TEST", i)
    print("--------------------------------------")

    print("Input Expression:", expr)
    print("Expected Rules:", expected)

    result = process(expr)

    if result["status"] == "success":
        print("\nENGINE OUTPUT:\n")
        print(result["formatted_trail"].replace('→', '->'))
    else:
        print("\nERROR:", result.get("error_message"))

# ===============
# Stopping/Completion Behavior Tests
# ===============
print("\n======================================")
print("STOPPING/COMPLETION RULE TESTS")
print("======================================")

# 1) exact form reached immediately (no algebraic transformations needed)
out1 = process("x+1")
assert "exact symbolic form reached" in out1["formatted_trail"], "Expected fixed-point completion reason"

# 2) converges after rule application, then fixed point
out2 = process("2(x+1)+3(x+1)")
assert "exact symbolic form reached" in out2["formatted_trail"], "Expected convergence completion reason"
assert "5*x + 5" in out2["final_answer"], "Expected combined output"

# 3) max iterations stop
out3 = process("x+1", max_iterations=0)
assert "max_iterations set to 0" in out3["formatted_trail"], "Expected max iteration stopping reason"

print("All completion/stopping behavior tests passed.")

print("\n======================================")
print("TEST RUN COMPLETE")
print("======================================")
