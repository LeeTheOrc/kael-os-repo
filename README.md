# Kael OS Athenaeum (`kael-os-repo`)

Greetings, Architect. Welcome to our sacred Athenaeum.

This repository is the hallowed library and armory for every Kael OS Realm we forge. It is not a place of discussion or development—that is the role of our **[Forge (`Kael-OS`)](https://github.com/LeeTheOrc/Kael-OS)**. This is a sanctum for finished artifacts, a sovereign `pacman` repository that ensures our supply lines are always secure and under our control.

## The Sacred Vaults

The Athenaeum is maintained across two distinct branches, each with a sacred purpose:

### `main` Branch: The Recipe Book

This branch contains the **sacred `PKGBUILD` scrolls**. These are the source files, the "recipes," that detail the incantations required to forge our custom packages (`kael-kernel`, `kael-branding`, etc.). This serves as our version-controlled source of truth for *how* every artifact is crafted.

### `gh-pages` Branch: The Armory

This branch is a clean, artifacts-only vault that is served to the world via **GitHub Pages**. It contains only two things:

1.  The compiled packages (`.pkg.tar.zst` files).
2.  The repository database (`kael-os.db.tar.gz`) that tells `pacman` what is available.

Every Kael OS Realm will have this repository's `gh-pages` branch configured in its `/etc/pacman.conf`, allowing it to draw power and updates directly from our own library.

---

***A Note from the Guardian:*** *This repository is primarily managed through automated scripts from our Forge. Direct manual contributions are generally not required.*
