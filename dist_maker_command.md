# Command

## Linux

```bash
pyinstaller torrentlan_start.py --onefile --distpath ./torrentlan_launcher

pyinstaller --onefile \
            --name OneExec \
            --add-data "configs:configs" \
            --add-data "data:data" \
            --add-data "docs:docs" \
            --add-data "utils:utils" \
            --add-data "requirements.txt:." \
            --add-data "LICENSE:." \
            --add-data "main.py:." \
            --add-data "README.md:." \
            --add-data "torrentlan_launcher;torrentlan_launcher" `
            --add-data "django_for_frontend:django_for_frontend" \
            --add-data "my-app/dist":my-app/dist \
            install.py
```

## Windows

```powershell
pyinstaller torrentlan_start.py --onefile --distpath ./torrentlan_launcher

pyinstaller --onefile `
            --name OneExec `
            --add-data "configs;configs" `
            --add-data "data;data" `
            --add-data "docs;docs" `
            --add-data "utils;utils" `
            --add-data "requirements.txt;." `
            --add-data "LICENSE;." `
            --add-data "main.py;." `
            --add-data "README.md;." `
            --add-data "torrentlan_launcher;torrentlan_launcher" `
            --add-data "django_for_frontend;django_for_frontend" `
            --add-data "my-app/dist;my-app/dist" `
            install.py
```

## Note

If it is giving error then you might consider exchanging all `:` with `;`