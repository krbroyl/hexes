# Hex Grid Tool

This is a hex grid tool created for brainstorming game ideas. It allows you to create, modify and visualize hex grids with different terrain types.

## Features

- Customizable grid size and hex dimensions
- Multiple terrain types with editable colors
- Two hex orientation options (flat-top and pointy-top)
- Resizable window with responsive UI panels
- Intuitive controls for terrain editing

## Running the Tool

### Prerequisites
- Python installed on your system
- PyGame and PyGame_GUI libraries

### Quick Start
1. Make sure Python is installed.
2. Download the repo, then navigate to the directory with the .py file.
3. Right click on the file browser and select "Open in Terminal"
4. Type `pip install pygame pygame_gui` and press the enter key.
5. Type `python hex_clicker.py` and press the enter key
6. Enjoy!

## Staying Updated with Git

### Prerequisites

* **Git installed**
  * Windows: install Git for Windows (https://git-scm.com/download/win)
  * macOS: `brew install git` (if Homebrew) or download installer
  * Linux: `sudo apt install git` (Debian/Ubuntu) or equivalent
* **VS Code installed**
  * Download from https://code.visualstudio.com/

### Clone the Repository

1. Open a terminal (or PowerShell on Windows) and run:

   ```bash
   git clone https://github.com/yourusername/hex-grid.git
   ```

2. Change into the newly created directory:

   ```bash
   cd hex-grid
   ```

### Open in VS Code

In the terminal (inside the project directory), run:

```bash
code .
```

VS Code will launch, showing the project.

### Configure VS Code's Git Integration

1. VS Code already has Git built-in. In the Activity Bar (left), click the **Source Control** icon.
2. You'll see "0 changes" (clean working tree).

### Enable Auto-fetch (Optional)

1. Open Settings (File → Preferences → Settings).
2. Search for **Git: Auto Fetch** and check the box.
3. Optionally set **Git: Auto Refresh** to true so the UI updates.

   Now VS Code will periodically fetch remote commits in the background.

### Pulling in the Latest Changes

Whenever there are new changes in the repository:

* A 🔄 badge will appear on the Source Control icon.
* Click **⋯ → Pull** in the Source Control menu, or run in the built-in terminal:

  ```bash
  git pull
  ```

* This will merge the latest updates into your local copy.

### Tips for Git Beginners

* **Commit often.** Save snapshots of your own tweaks.
* **Use branches** if you want to experiment without touching `main`.

  ```bash
  git checkout -b my-ideas
  ```
* **GitHub Desktop** is an alternative GUI if the CLI feels too scary.

## Project Structure

- `hex_clicker.py` - Main application file
- `hex.py` - Hex cell class and geometry functions
- `grid.py` - Grid management functions
- `ui.py` - User interface components
- `constants.py` - Configuration values and defaults

## License

This software is provided as-is with no guarantees.
