# Command

## Linux

```bash
pyinstaller torrentlan_start.py --onefile --distpath ./torrentlan_launcher

pyinstaller --onefile \
            --name OneExec \
            --add-data "default/configs:configs" \
            --add-data "default/data:data" \
            --add-data "docs:docs" \
            --add-data "utils:utils" \
            --add-data "requirements.txt:." \
            --add-data "LICENSE:." \
            --add-data "main.py:." \
            --add-data "README.md:." \
            --add-data "torrentlan_launcher;torrentlan_launcher" `
            --add-data "django_for_frontend:django_for_frontend" \
            --add-data "my-app/client/dist":my-app/client/dist \
            install.py
```

```bash
electron-packager . --out=pack/ --overwrite --ignore="(.git|.vscode|node_modules|src|.gitignore|README.md|LICENSE.md)" --asar
```

## Windows

```powershell
pyinstaller torrentlan_start.py --onefile --distpath ./torrentlan_launcher

pyinstaller --onefile `
            --name OneExec `
            --add-data "default/configs;configs" `
            --add-data "default/data;data" `
            --add-data "docs;docs" `
            --add-data "utils;utils" `
            --add-data "requirements.txt;." `
            --add-data "LICENSE;." `
            --add-data "main.py;." `
            --add-data "README.md;." `
            --add-data "torrentlan_launcher;torrentlan_launcher" `
            --add-data "django_for_frontend;django_for_frontend" `
            --add-data "my-app/client/dist;my-app/client/dist" `
            install.py

```

## Electron

Use one time only below command

``` powershell
npm run electron:build
```

then always use below command

```powershell
electron-packager . --out=pack/ --overwrite --ignore="(.git|.vscode|node_modules|src|.gitignore|README.md|LICENSE.md)" --asar
```

## Note

If it is giving error then you might consider exchanging all `:` with `;`
