# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['game.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('fonts/*', 'fonts'),
        ('images/background.png', 'images'),
        ('images/gun.png', 'images'),
        ('images/menu_bg.jpeg', 'images'),
        ('images/projectile.png', 'images'),
        ('images/clouds/*', 'images/clouds'),
        ('images/icons/*', 'images/icons'),
        ('maps/*', 'maps'),
        ('particles/leaf/*', 'particles/leaf'),
        ('particles/particle/*', 'particles/particle'),
        ('resources/decor/*', 'resources/decor'),
        ('resources/grass/*', 'resources/grass'),
        ('resources/large_decor/*', 'resources/large_decor'),
        ('resources/spawners/*', 'resources/spawners'),
        ('resources/stone/*', 'resources/stone'),
        ('entities/enemy/idle/*', 'entities/enemy/idle'),
        ('entities/enemy/run/*', 'entities/enemy/run'),
        ('entities/player/idle/*', 'entities/player/idle'),
        ('entities/player/jump/*', 'entities/player/jump'),
        ('entities/player/run/*', 'entities/player/run'),
        ('entities/player/slide/*', 'entities/player/slide'),
        ('entities/player/wall_slide/*', 'entities/player/wall_slide'),
        ('sfx/*', 'sfx')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='game',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
