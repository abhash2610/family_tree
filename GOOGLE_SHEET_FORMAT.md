# 📊 Google Sheet Format Guide

## Required Columns

Your Google Sheet **must** have these columns in the first row:

| Column | Required | Type | Description |
|--------|----------|------|-------------|
| **Name** | ✅ Yes | Text | Full name of the person |
| **ID** | ✅ Yes | Text/Number | Unique identifier for each person |
| **Father_ID** | ✅ Yes | Text/Number | ID of the father (leave blank if unknown) |
| **Mother_ID** | ✅ Yes | Text/Number | ID of the mother (leave blank if unknown) |
| **Gender** | ✅ Yes | Text | "M" for Male or "F" for Female |
| **Birth_Year** | ❌ Optional | Number | Year of birth (for display purposes) |
| **Spouse_ID** | ❌ Optional | Text/Number | Not currently used in tree |

---

## Example 1: Simple 3-Generation Family

```
Name,ID,Father_ID,Mother_ID,Gender,Birth_Year
Grandpa Robert,1,,M,1930
Grandma Mary,2,,F,1935
Dad John,3,1,2,M,1960
Mom Patricia,4,,F,1962
Uncle Mike,5,1,2,M,1965
Aunt Susan,6,,F,1968
You,7,3,4,M,1990
Your Sister,8,3,4,F,1992
Cousin Sarah,9,5,6,F,1991
```

**Visual Structure:**
```
        Grandpa(1)─────Grandma(2)
           │
       ┌───┼───┐
       │       │
    Dad(3)  Uncle(5)────Aunt(6)
       │                   │
       │                Cousin(9)
       │
    You(7) Sister(8)
```

---

## Example 2: Large Extended Family

```
Name,ID,Father_ID,Mother_ID,Gender,Birth_Year
Great Grandpa Jack,1,,M,1910
Great Grandma Rose,2,,F,1912
Grandpa Thomas,3,1,2,M,1935
Grandma Helen,4,,F,1938
Grandpa William,5,,M,1932
Grandma Dorothy,6,,F,1936
Dad Robert,7,3,4,M,1960
Mom Sarah,8,5,6,F,1962
Uncle Michael,9,3,4,M,1962
Aunt Jennifer,10,,F,1965
Dad's Sister Anna,11,3,4,F,1964
You,12,7,8,M,1990
Your Brother,13,7,8,M,1992
Your Sister,14,7,8,F,1995
Cousin David,15,9,10,M,1988
Cousin Emma,16,9,10,F,1990
```

**Visual Structure:**
```
Great Grandpa(1)──Great Grandma(2)        Grandpa(5)──Grandma(6)
        │                                      │
        │                                      │
   Grandpa(3)──Grandma(4)                 ┌────┴─────┐
        │                                 │           │
    ┌───┼───┬────┐              Mom(8) Dad(7)      
    │   │   │    │                    │
  Dad Uncle Michael Aunt Jennifer     │
    │   (9)      │                    │
    │   │        │                    │
    │   │    Cousin David(15)   ┌─────┼──────┐
    │   │    Cousin Emma(16)    │     │      │
    │   │                      You  Brother Sister
 Brother│
        │
      You(12)
```

---

## Example 3: Multiple Siblings with Multiple Children

```
Name,ID,Father_ID,Mother_ID,Gender,Birth_Year
Grandpa James,1,,M,1925
Grandma Alice,2,,F,1928
Dad John,3,1,2,M,1950
Uncle Richard,4,1,2,M,1952
Auntie Margaret,5,1,2,F,1955
Mom Louise,6,,F,1952
Aunt Caroline,7,,F,1954
Cousin Peter,8,4,,M,1975
Cousin Anna,9,4,,F,1978
Cousin James,10,5,,M,1980
You,11,3,6,M,1985
Sister Lisa,12,3,6,F,1987
Brother Mark,13,3,6,M,1990
```

---

## Important Rules & Tips

### 1. **Unique IDs**
- Each person must have a **unique ID**
- IDs can be numbers or text: `1`, `john_1`, `JP001`
- Use consistent format throughout

```
✅ Good:
ID: 1, 2, 3, 4...

✅ Good:
ID: john_1, mary_2, bob_3...

❌ Bad:
ID: 1, john, 3 (mixed format)
```

### 2. **Parent References**
- Father_ID and Mother_ID must reference valid IDs
- Leave blank if parent is unknown
- Don't use "Unknown" or "N/A" - leave the cell empty

```
✅ Good:
Father_ID: 1 (or leave blank)
Mother_ID: 2 (or leave blank)

❌ Bad:
Father_ID: "Unknown"
Mother_ID: "N/A"
```

### 3. **Gender Format**
- Use only: `M` or `F`
- Case insensitive in app, but use consistently
- Don't use: "Male", "Male", "m", "f"

```
✅ Good:
Gender: M
Gender: F

❌ Bad:
Gender: Male
Gender: Female
Gender: m
```

### 4. **Birth Year**
- Use 4-digit year format: `1990`, `1935`
- Optional column - can be left blank
- Used for display and sorting

```
✅ Good:
Birth_Year: 1990
Birth_Year: (empty)

❌ Bad:
Birth_Year: 90
Birth_Year: "1990-01-01"
```

### 5. **Names**
- Use full names for clarity
- Avoid special characters if possible
- Keep names under 50 characters

```
✅ Good:
Name: John Smith Jr.
Name: Mary Ann Johnson

❌ Bad:
Name: J.S.
Name: John @#$% Smith
```

---

## Full CSV Template

Copy this template and fill in your family data:

```
Name,ID,Father_ID,Mother_ID,Gender,Birth_Year
Grandparent Name 1,1,,M,1930
Grandparent Name 2,2,,F,1935
Parent Name 1,3,1,2,M,1960
Parent Name 2,4,,F,1962
Your Name,5,3,4,M,1990
Sibling Name,6,3,4,F,1992
Extended Family Member,7,1,2,M,1965
```

---

## How to Use in Google Sheets

### Method 1: Copy-Paste
1. Create a new Google Sheet
2. Paste the template above
3. Replace with your family data
4. Share with the service account email

### Method 2: Import CSV
1. Create a `.csv` file with your data
2. Open Google Sheets
3. File → Import → Upload the CSV
4. Select "Replace spreadsheet"

### Method 3: Manual Entry
1. Add headers in row 1
2. Fill in data starting from row 2
3. One person per row

---

## Common Mistakes & How to Fix

### ❌ Mistake 1: Parent ID that doesn't exist

```
Mistake:
ID: 5, Father_ID: 99 (doesn't exist!)

Fix:
Make sure Father_ID references a valid ID in column A
Or leave Father_ID blank
```

### ❌ Mistake 2: Circular references

```
Mistake:
Person A has Parent = B
Person B has Parent = A

Fix:
Double-check parent relationships
Make sure root ancestors have no parents
```

### ❌ Mistake 3: Inconsistent ID formats

```
Mistake:
ID: 1, 2, person_3, bob_4 (mixed!)

Fix:
Use consistent format: all numbers OR all text
Example: 1, 2, 3, 4 (or) person_1, person_2, person_3
```

### ❌ Mistake 4: Typos in Gender

```
Mistake:
Gender: Male, Female, m, f (inconsistent)

Fix:
Use only M or F
Replace "Male" with "M"
Replace "Female" with "F"
```

---

## Data Validation Checklist

Before sharing your sheet, verify:

- ✅ All columns are present (Name, ID, Father_ID, Mother_ID, Gender)
- ✅ All IDs are unique
- ✅ All Father_ID and Mother_ID reference valid IDs (or are blank)
- ✅ Gender column has only "M" or "F"
- ✅ Birth_Year is 4 digits or blank
- ✅ No empty Name cells
- ✅ Service account email has Editor access
- ✅ Sheet name matches the app configuration

---

## Real Family Example

Here's a complete real-looking example you can use as reference:

```
Name,ID,Father_ID,Mother_ID,Gender,Birth_Year
Harold Winston,1,,M,1918
Eleanor Russell,2,,F,1920
George Winston,3,1,2,M,1940
Patricia McKenzie,4,,F,1942
Robert Winston,5,1,2,M,1945
David Winston,6,3,4,M,1965
Susan Thompson,7,,F,1967
Michael Winston,8,3,4,M,1970
John Winston,9,6,7,M,1990
Emma Winston,10,6,7,F,1992
Sarah Winston,11,8,,F,1995
Thomas Winston,12,5,,M,1970
```

---

## Need Help?

If you're unsure about:
- **How to format dates**: Use Birth_Year (just the year, like 1990)
- **What if I don't know a parent**: Leave that cell blank
- **Can I have blank cells**: Yes, only Name and ID are truly required
- **What if someone has two moms or two dads**: Currently the app supports Father_ID and Mother_ID; if you need to show same-sex parents, you can modify the code

---

**Remember**: The app pulls data every 5 minutes, so changes appear automatically!
