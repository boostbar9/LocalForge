# How to publish LocalForge and get a clickable installer

This is a one-time, ~10 minute setup. After this, every time you tag a new
version, GitHub builds the `LocalForge-Setup.exe` for you automatically
and posts it on a Releases page you can download from.

> **Privacy reminder**: only the source code in this folder goes to GitHub.
> Anything the app generates on your PC (images, videos, prompts, models)
> stays on your PC. None of it is in this folder. The `.gitignore` already
> excludes models, outputs, logs, and your runtime data.

---

## Step 1 — Create the repo (browser, 2 minutes)

1. Go to [github.com/new](https://github.com/new).
2. **Repository name**: `LocalForge`
3. **Visibility**: choose **Private** if you want it just for you.
   (GitHub Actions works on private repos too — you get 2,000 free build
   minutes per month, way more than you'll ever use.)
4. Leave everything else blank. Do **not** check "Add a README".
5. Click **Create repository**.

You'll land on a page with setup instructions. Ignore them — we'll use the
next step instead.

## Step 2 — Upload the code (browser, no commands)

GitHub has a drag-and-drop upload button. You don't need git installed.

1. On the new empty repo page, click **uploading an existing file**
   (small blue link in the middle of the page).
2. Open the LocalForge folder on your PC, select **everything inside it**
   (including the `.github` folder — make sure hidden files are visible:
   View → Hidden items in File Explorer).
3. Drag it all onto the GitHub upload box.
4. Scroll down, click **Commit changes**.

Wait ~30 seconds for the upload to finish.

## Step 3 — Tag a release (browser, 30 seconds)

This is what triggers the automatic build.

1. On your repo page, click **Releases** in the right sidebar
   (or go to `https://github.com/YOUR-USERNAME/LocalForge/releases`).
2. Click **Create a new release**.
3. **Choose a tag** → type `v1.1.0` → click **Create new tag: v1.1.0 on publish**.
4. **Release title**: `LocalForge 1.1.0 — Video Pro`
5. Click **Publish release**.

The moment you click Publish, GitHub starts building your installer.

## Step 4 — Wait for the build (~15 minutes, in the background)

1. Click the **Actions** tab at the top of your repo.
2. You'll see a workflow run called **Build LocalForge Installer**
   with a yellow spinner. Click it to watch progress if you want.
3. When it turns into a green checkmark, go back to **Releases**.
4. Your release now has `LocalForge-Setup-1.1.0.exe` attached at the bottom.

Click that .exe to download. **Double-click it. Done.** No commands, no terminal.

---

## Updating later

When you (or I) make changes to the source:

1. Drag the updated files onto GitHub the same way (it auto-replaces).
2. Make a new Release with tag `v1.1.1` (or whatever).
3. A new .exe appears on the Releases page ~15 min later.

## Troubleshooting

**The build failed (red X instead of green check)**
Open the failed run, expand the failed step, copy the error, and send it
to me. The most common cause is a missing dependency on the GitHub runner,
which I can fix in `.github/workflows/build.yml`.

**I don't see the `.github` folder when uploading**
It's hidden by default. In File Explorer: View menu → check
**Hidden items**. Or upload it separately by going to your repo,
clicking **Add file → Create new file**, typing
`.github/workflows/build.yml`, and pasting the contents from the file
of the same name in this folder.
