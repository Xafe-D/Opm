# TEST_PLANv1

## Purpose
This test plan validates the core functionality of the OPM symbolic math application for the midterm version. It covers expression simplification, rule detection, trail generation, validation behavior, and export/history features.

## Test Environment
- Operating System: Windows 10/11
- Python Version: 3.12+ (Tested on 3.14.3)
- Core Dependencies: sympy, customtkinter
- Optional Dependencies: reportlab (for PDF generation)
- Execution Command: ```bash
`python main.py` or **run OPM_Symbolic_Math_Generator.exe from /OPM_Symbolic_Math_Generator.exe**

## Test Cases

### 0. Bonus Test File
- Run `test_engine.py.`
**Includes multiple test cases, displays expected method and the actual method along the solution trail**

*More Test Cases*
### 1. Linear Expression Simplification
- Input: `2x + 5x - 3`
- Expected behavior:
  - Final answer should show `7*x - 3` or equivalent simplified form
  - Trail should include `Combine Like Terms`
  - A valid solution trail should appear in the UI, no parsing or validation error, verification should confirm the simplified result matches the original expression

### 2. Binomial Expansion
- Input: `(x+2)^2`
- Expected behavior:
  - Final answer should show `x^2 + 4x + 4`
  - Trail should include `Binomial Expansion`
  - A valid solution trail should appear in the UI, no parsing or validation error, verification should confirm the simplified result matches the original expression

### 3. Rational Simplification and Special Products
- Input: `(x^2 - 1)/(x - 1)` 
- Expected behavior:
  - Final answer should show `x + 1`
  - Trail should include `Special Products` and `Rational Expression Simplification`
  - A valid solution trail should appear in the UI, no parsing or validation error, verification should confirm the simplified result matches the original expression

### 4. Factorization
- Input: `x^2 + 5x + 6` 
- Expected behavior:
   - Final answer factored should show `(x + 2)(x + 3)`
   - Trail should include `Post-processing: Factorization`
   - A valid solution trail should appear in the UI, no parsing or validation error, verification should confirm the simplified result matches the original expression

### 5. Distributive Property
- Input: `8(x - 3)` 
- Expected behavior:
   - Final answer should show `8*x - 24`
   - Trail should include `Distributive Property`
   - A valid solution trail should appear in the UI, no parsing or validation error, verification should confirm the simplified result matches the original expression

### 6. Multi-Term Distribution and Combine Like Terms
- Input: `(x + 1)(x^2 - x + 1)` 
- Expected behavior:
   - Final answer should show `x^3 + 1`
   - Trail should include `Multi-Term Distribution` and `Combine Like Terms`
   - A valid solution trail should appear in the UI, no parsing or validation error, verification should confirm the simplified result matches the original expression

### 7. Exponent Rules
- Input: `x^3*x^2` 
- Expected behavior:
   - Final answer should show `x^5`
   - Trail should include `Exponent Rules`
   - A valid solution trail should appear in the UI, no parsing or validation error, verification should confirm the simplified result matches the original expression
  
### 8. Invalid Expression Handling
- Input: `2x ++` or `(x+1`
- Expected behavior:
  - The app should reject the expression with a validation or parsing error
  - No final answer should be produced
  - The UI should show an informative message

### 9. Trail Export and History
- Action:
  - Compute a valid expression such as `3(x+4)`
  - Use the `EXPORT` button to save the trail as a TXT or PDF file
  - View history with `NEW` and `CLEAR` button
- Expected behavior:
  - A `.txt` or `.pdf` file containing the solution trail should be created
  - The history sidebar should add the any new computation entry
  - `NEW` presents a clean main solver `CLEAR` button clears existing history entries

## Additional Verification
- Confirm `About/Help` dialog opens when the `ℹ` icon is clicked
- Confirm the output window displays the full `SOLUTION TRAIL:` text
- Confirm the app still runs without `reportlab` installed for TXT export

## Notes
- `reportlab` should be installed for the `EXPORT` `.pdf`  to work
- The app automatically regenerates `history.json` if the file is missing

## 👥 The Team
Miranda, Jessa Bien T.
Oakes, Kenneth Gabren E.
Pato, Mhira Shane O.