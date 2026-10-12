# Create the GitHub link

This project has not been pushed to GitHub. Once you have a repository, its URL will be `https://github.com/YOUR_USERNAME/combat-golf-killstreak-chaos`.

## Browser method

1. Open https://github.com/new .
2. Repository name: `combat-golf-killstreak-chaos`.
3. Choose **Public** to share MIT-licensed source, or **Private** while developing. Leave **Add a README**, **.gitignore** and **license** unchecked because all three are in the archive already.
4. Select **Create repository**.
5. Extract the project ZIP; on the empty repository page choose **uploading an existing file** and upload the **contents of the extracted folder** (including dotfiles), not the ZIP itself. Commit to `main`.

## Git command-line method (from the extracted directory)

```bash
git init -b main
git add .
git commit -m "Add Combat Golf rules and Melty development draft"
git remote add origin https://github.com/YOUR_USERNAME/combat-golf-killstreak-chaos.git
git push -u origin main
```

This does not make the project available on Melty. `melty.draft.json` is intentionally not the `melty.json` that Melty imports for validated builds. Do not publish it until the actual game integrations and Melty one-click tests pass.
