# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['dist_maker.py'],
    pathex=[],
    binaries=[],
    datas=[('build', 'build'), ('configs', 'configs'), ('data', '.data'), ('data/.db', '.data/.db'), ('data/.logs', '.data/.logs'), ('data/Normal', 'data/Normal'), ('data/Normal/Games', 'data/Normal/Games'), ('data/Normal/Games/Game1', 'data/Normal/Games/Game1'), ('data/Normal/Games/Game1/sub1Game1', 'data/Normal/Games/Game1/sub1Game1'), ('data/Normal/Games/Game1/sub2Game1', 'data/Normal/Games/Game1/sub2Game1'), ('data/Normal/Movies', 'data/Normal/Movies'), ('data/Normal/Music', 'data/Normal/Music'), ('data/Web_downloader', 'data/Web_downloader'), ('data/Web_downloader/tmp', 'data/Web_downloader/tmp'), ('docs', 'docs'), ('utils', 'utils'), ('utils/db_manage', 'utils/db_manage'), ('utils/extra tools', 'utils/extra tools'), ('utils/extra tools/web_downloader', 'utils/extra tools/web_downloader'), ('utils/file_transfer', 'utils/file_transfer'), ('utils/identity', 'utils/identity'), ('utils/log', 'utils/log'), ('utils/tracker', 'utils/tracker'), ('utils/tracker/shared_util', 'utils/tracker/shared_util')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='dist_maker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='dist_maker',
)
