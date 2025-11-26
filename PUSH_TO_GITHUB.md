# Push to GitHub - Commands

After creating a GitHub repository, run these commands:

```bash
# Add your GitHub repository as remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Or if using SSH:
# git remote add origin git@github.com:YOUR_USERNAME/REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Quick Example

If your GitHub username is `sreemakam` and repo name is `resume-parser`:

```bash
git remote add origin https://github.com/sreemakam/resume-parser.git
git branch -M main
git push -u origin main
```

## If you need to authenticate

- **HTTPS**: GitHub will prompt for username and personal access token
- **SSH**: Make sure your SSH key is added to GitHub

## After pushing

Your code will be on GitHub and ready to deploy to Render/Vercel!

