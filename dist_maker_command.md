# # command

```bash
pyinstaller --onefile \
            --name OneExec \
            --add-data "configs:configs" \
            --add-data "data:data" \
            --add-data "docs:docs" \
            --add-data "utils:utils" \
            --add-data "requirements.txt:." \
            --add-data "LICENSE:." \
            --add-data "main.py:." \
            install.py
```

<!-- If it is giving error then you might consider exchanging all ':' with ';' -->
