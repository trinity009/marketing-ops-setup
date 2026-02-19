# Push Guide (Beginner Friendly)

This guide helps you push this project to your GitHub repo safely.

## 0) Open terminal in the project folder

```bash
cd /Users/nehamisra9/Desktop/Python_Practice/marketing-ops-setup
pwd
```

You should see:

`/Users/nehamisra9/Desktop/Python_Practice/marketing-ops-setup`

## 1) Check Git is available

```bash
git --version
```

## 2) Initialize repo (only once)

```bash
git init
```

## 3) Set your Git identity (only once on your machine)

```bash
git config --global user.name "YOUR NAME"
git config --global user.email "YOUR_EMAIL@example.com"
```

## 4) Review what will be committed

```bash
git status
```

## 5) Add files and create first commit

```bash
git add .
git commit -m "Initial commit: marketing ops setup system"
```

## 6) Set branch name to `main`

```bash
git branch -M main
```

## 7) Connect your GitHub repo

Use SSH (recommended):

```bash
git remote add origin git@github.com:<your-username>/<your-repo>.git
```

If origin already exists, update it:

```bash
git remote set-url origin git@github.com:<your-username>/<your-repo>.git
```

## 8) Push to GitHub

```bash
git push -u origin main
```

## 9) Verify push worked

```bash
git remote -v
git status
```

`git status` should show: `nothing to commit, working tree clean`

## Common issues

### A) "remote origin already exists"

Use:

```bash
git remote set-url origin git@github.com:<your-username>/<your-repo>.git
```

### B) "Permission denied (publickey)"

Your SSH key is not connected to GitHub yet.

Quick fix path:
1. Generate key: `ssh-keygen -t ed25519 -C "YOUR_EMAIL@example.com"`
2. Start agent: `eval "$(ssh-agent -s)"`
3. Add key: `ssh-add ~/.ssh/id_ed25519`
4. Copy public key: `cat ~/.ssh/id_ed25519.pub`
5. Add it to GitHub: Settings -> SSH and GPG keys -> New SSH key
6. Retry push.

### C) Pushed wrong files

Because `.gitignore` is already set, common local files are excluded. If needed, run:

```bash
git status
```

before every commit.

## Safe workflow going forward

For each change:

```bash
git status
git add .
git commit -m "Describe your change"
git push
```
