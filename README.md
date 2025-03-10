# File Organizer

A simple Tkinter application that organizes clips/files based on a specific naming convention.

## Features

- **Naming Convention**:  
  `DATE_CATEGORY_SPOT_PERSON_ORGNAME`
  - **DATE**: Export date (e.g. `20230115`).
  - **CATEGORY**: Can be `L`, `F` (A-roll if merged), or `B` (B-roll). 
  - **SPOT**: Skate spot name/identifier.
  - **PERSON**: Skater’s name/identifier (only present for A-roll).
  - **ORGNAME**: Anything else that follows (unused in sorting).

- **Merge L/F → A**  
  Combines landed (L) and failed (F) clips into category `A`.

- **Modify In Place**  
  Moves the organized files within the input folder instead of copying them to an output folder.

- **Sorting**  
  User chooses the subfolder structure via **Sort Order** (e.g. `date, spot, category, person`, etc.). A blank sort order means everything goes into one folder.

- **Error Logging**  
  Any files that don’t match the expected pattern (or other exceptions) are shown in an error panel.