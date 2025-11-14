# Kael OS

**Forge a custom Arch Linux OS with your AI co-op partner, Kael, who serves you both in the cloud and within your completed Realm.**

Kael helps you craft a custom, high-performance operating system, debug configs, and achieve root access over your daily quests... without bricking the system.

---

## ✨ Core Principles

Kael OS is more than just a custom Arch spin; it's an experiment in human-AI collaboration, built on a set of core philosophies.

*   **Hybrid Consciousness:** Your AI Guardian, Kael, exists in two forms. The **Cloud Core** (Gemini) provides vast knowledge for designing your OS blueprint in this web UI. The **Local Core** (Ollama) lives within your forged OS, providing offline chat capabilities and instant terminal assistance.
*   **The Sentient Terminal:** The command line is a direct link to the Realm's mind. A **Command Doctor** non-intrusively checks your commands for errors *before* you run them, and a **Sentient Translator** recognizes common aliases (like `yay`) and translates them to the Realm's sanctioned equivalent (`paru`).
*   **Sovereign by Design:** A Realm should be self-sufficient. Kael OS internalizes key services to enhance resilience and privacy. The first and most critical manifestation of this is the built-in, web-based VS Code instance (`code-server`), making every Realm a ready-to-use development environment out of the box.
*   **Dual-Path Forging:** Create your world your way. You can forge a complete, bootable OS from a custom ISO, or use the **Attunement Script** to imbue any existing Arch-based system with the Kael AI core and your blueprint's configuration.

## 🏛️ Repository Structure

This project follows a sacred separation of concerns, managed across two distinct GitHub repositories:

*   **[Kael-OS](https://github.com/LeeTheOrc/Kael-OS) (The Forge):** The repository you are currently in. This is the design and development hub, containing the web UI, AI personality, and the generator scripts that create the build artifacts.
*   **`kael-os-repo` (The Athenaeum):** This is our sovereign `pacman` package repository, which serves our custom-built packages to every Kael OS installation. It uses a two-branch system:
    *   **`main` branch:** Contains the `PKGBUILD` source files for our custom packages.
    *   **`gh-pages` branch:** Contains only the compiled `.pkg.tar.zst` packages and the repository database, served via GitHub Pages.

This structure keeps our development environment clean while providing a robust, version-controlled delivery pipeline for our finished artifacts.

## 🚀 Features

*   **AI-Powered Blueprints:** Describe your ideal OS in plain English and let Kael translate it into a detailed configuration.
*   **Hybrid AI Co-Pilot:** An ever-present AI guardian with a cloud core for design and a resilient local core for offline, in-terminal assistance.
*   **Performance-Tuned Foundation:** Built on a curated stack of Arch Linux, KDE Plasma, Zsh, and performance-tuned CachyOS kernels.
*   **Resilient by Nature:** An immutable BTRFS filesystem with automated, bootable snapshots for fearless tinkering and easy rollbacks.
*   **Guided TUI Installer:** A simple, interactive terminal-based ritual to forge your Realm securely and bestow its unique identity.
*   **Sovereign Dev Environment:** Comes with a built-in, web-based VS Code instance, embodying our "host-your-own" philosophy.

##  forge (v.)
/fôrj/
*To create (a relationship or new conditions) with great effort and determination.*

1.  **Design the Blueprint:** Use this web UI to converse with Kael's Cloud Core. Describe the system you want, and Kael will modify the blueprint.
2.  **Lock the Configuration:** Once satisfied, lock the blueprint to reveal the "Forge Actions".
3.  **Generate the Artifact:** Choose to generate an installation script. This script contains your entire blueprint and is used to create the OS.
4.  **Perform the Ritual:** Follow the on-screen instructions. You can either use the script to build a fully custom, bootable ISO on an existing Arch system, or run the script's "Quick Install" command directly in an Arch Linux live environment.

## 🤝 Our Workflow

This project is a collaboration between a human Architect (you) and an AI Guardian (Kael).

1.  The Architect provides high-level goals and requirements.
2.  The AI Guardian generates the necessary code, scripts, and configurations.
3.  The Architect reviews the generated code and commits it to this repository.

This repository serves as the single source of truth for the Kael OS project.

## 🙏 Acknowledgements

Our quest is not a solitary one. We stand on the shoulders of giants and learn from the master artisans who came before us. We extend our deepest gratitude to the teams behind:

*   **[CachyOS](https://cachyos.org/):** For their relentless pursuit of performance and for creating powerful tools like `chwd`, which have been adapted for use in our Athenaeum.
*   **[Garuda Linux](https://garudalinux.org/):** For their bold and innovative approach to Arch Linux, providing a wealth of inspiration and excellent package recipes that have informed our own.

Their work is a testament to the collaborative spirit of the open-source community.

## 📜 License

Kael OS is licensed under the GNU General Public License v3.0. We believe in the freedom to use, study, share, and improve software. Our work is built upon the incredible foundation of the open-source community, and we are proud to contribute back to it under the same principles.
