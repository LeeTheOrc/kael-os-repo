# Kael OS Athenaeum

This is the sovereign `pacman` package repository for Kael OS. It serves our custom-built packages to every Kael OS installation.

## 🏛️ Repository Structure

This repository uses a two-branch system:

*   **`main` branch:** Contains the `PKGBUILD` source files (the "recipes") for our custom packages.
*   **`gh-pages` branch:** Contains only the compiled `.pkg.tar.zst` packages and the repository database, served via GitHub Pages. This is the branch that `pacman` on a Kael OS Realm will point to.

## 🙏 Acknowledgements

Our quest is not a solitary one. We stand on the shoulders of giants and learn from the master artisans who came before us. We extend our deepest gratitude to the teams behind:

*   **[CachyOS](https://cachyos.org/):** For their relentless pursuit of performance and for creating powerful tools like `chwd`, which have been adapted for use in our Athenaeum.
*   **[Garuda Linux](https://garudalinux.org/):** For their bold and innovative approach to Arch Linux, providing a wealth of inspiration and excellent package recipes that have informed our own.

Their work is a testament to the collaborative spirit of the open-source community.

## 📜 License

The packages and scripts in this repository are licensed under the GNU General Public License v3.0. See the LICENSE file for the full text.
