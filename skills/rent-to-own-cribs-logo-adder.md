# Rent to Own Cribs Logo Adder

Add the Rent2OwnCribs logo watermark to a folder of house photos.

## What this skill does
- Resizes each image to **940 × 626 px**
- Places the **RTOC Logo** at **409 × 247 px** in the **bottom-right corner** (12px padding)
- Exports every image as **PNG**
- Saves results to `C:/Users/joshu/Downloads/WATERMARKED_COMPLETED_<FOLDER_NAME>` (all caps)

## Fixed paths
- **Logo:** `C:/Users/joshu/Downloads/RTOC Logo (Rent to Own Cribs Logo).png`
- **Script:** `C:/Users/joshu/.claude/scripts/watermark/watermark.js`

## How to run

When the user invokes `/rent-to-own-cribs-logo-adder`, ask:
> "Which folder of house photos should I watermark? Please provide the full path or folder name inside Downloads."

Then run:
```
node "C:/Users/joshu/.claude/scripts/watermark/watermark.js" "<INPUT_FOLDER>" "C:/Users/joshu/Downloads/RTOC Logo (Rent to Own Cribs Logo).png" "C:/Users/joshu/Downloads/WATERMARKED_COMPLETED_<FOLDER_NAME_UPPERCASE>"
```

Replace `<INPUT_FOLDER>` with the full path to the house photos folder, and `<FOLDER_NAME_UPPERCASE>` with the source folder name in ALL CAPS with spaces replaced by underscores.

After running, confirm how many images were processed and show the output folder path.
